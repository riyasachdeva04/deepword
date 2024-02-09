from flask import Flask, request, jsonify
import os
import moviepy.editor as mpy  
from pytube import YouTube
from pydub import AudioSegment
import requests
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
import speech_recognition as sr
import pandas as pd
import numpy as np 
from nltk.tokenize import word_tokenize
import gensim
from gensim.models import Word2Vec
from gensim.similarities import WmdSimilarity
from nltk.corpus import stopwords
from nltk import download
from sklearn.metrics.pairwise import cosine_similarity
import re
import gensim.downloader as api

app = Flask(__name__)

OUTPUT_PATH = "downloads"

# Initialize the speech recognizer
r = sr.Recognizer()

def download_audio(url):
    try:
        # Download the audio from the YouTube video
        yt = YouTube(url)
        audio_stream = yt.streams.filter(only_audio=True).first() 
        audio_stream.download(output_path=OUTPUT_PATH, filename=f"{yt.title}.mp3")
        print(f"Downloaded: {yt.title}.mp3")  
        return yt.title
    except Exception as e:
        print(f"Download Error: {str(e)}")
        return None

def get_transcript(audio_file_path):
    with sr.AudioFile(audio_file_path) as source:
        audio = r.record(source)
    try:
        transcript = r.recognize_google(audio)
    except Exception as e:
        transcript = str(e)
    return transcript

def audio_to_wav(audio_file_path, output_wav_file_path):
    sound = AudioSegment.from_file(audio_file_path)
    sound.export(output_wav_file_path, format="wav")

@app.route('/', methods=['POST'])
def home():
    if 'url' not in request.json:
        return jsonify({'error': 'URL not provided'}), 400
    
    url = request.json['url']
    
    # Scraping the channel URL to get the channel ID
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    canonical_tag = soup.find('link', attrs={'rel': 'canonical'})
    if canonical_tag:
        channel_url = canonical_tag['href']
        channel_id = channel_url.split("/")[-1]
    else:
        return jsonify({'error': 'Channel ID not found'}), 500
    
    # YouTube API setup
    API_KEY = 'AIzaSyCDWikYjZgY9jlEMVukD3b_L6-G4gc14fs'  # Replace with your API key
    MAX_RESULTS = 3
    youtube = build('youtube', 'v3', developerKey=API_KEY)

    # Retrieve videos from the specified channel
    try:
        videos_response = youtube.search().list(
            part='id',
            channelId=channel_id,
            order='viewCount',
            maxResults=MAX_RESULTS
        ).execute()
        # Extract video IDs
        video_ids = [item['id']['videoId'] for item in videos_response['items']]
    except KeyError as e:
        return jsonify({'error': f'Error accessing videoId from response: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Error retrieving videos: {str(e)}'}), 500

    transcripts = []

    for video_id in video_ids:
        video_url = f'https://www.youtube.com/watch?v={video_id}'
        audio_title = download_audio(video_url)
        
        if audio_title is None:
            return jsonify({'error': f'Failed to download audio for video {video_id}'}), 500
        
        mp3_file = os.path.join(OUTPUT_PATH, f"{audio_title}.mp3")
        wav_file = os.path.join(OUTPUT_PATH, "result.wav")

        # Convert audio to WAV format
        audio_to_wav(mp3_file, wav_file)
        os.remove(mp3_file)

        # Get transcript from the audio
        transcript = get_transcript(wav_file)
        transcripts.append({'video_id': video_id, 'transcript': transcript})
        os.remove(wav_file)

    # Preprocess the transcripts
    documents_df = pd.DataFrame(transcripts, columns=['transcript'])
    documents_df['transcript_cleaned'] = documents_df['transcript'].apply(lambda x: " ".join(re.sub(r'\W',' ',w).lower() for w in str(x).split()))

    # Remove NaN values
    documents_df.dropna(subset=['transcript_cleaned'], inplace=True)

    if documents_df.empty:
        return jsonify({'error': 'No valid transcripts found'}), 500

    # Train word2vec model
    w2v_model = gensim.models.Word2Vec(sentences=[row.split() for row in documents_df['transcript_cleaned']], vector_size=100, window=5, min_count=1, workers=4)

    # Calculate document vectors
    document_vectors = []
    for doc in documents_df['transcript_cleaned']:
        vec = np.zeros(100)
        count = 0
        for word in doc.split():
            if word in w2v_model.wv:
                vec += w2v_model.wv[word]
                count += 1
        if count > 0:
            vec /= count
        document_vectors.append(vec)
        
    document_vectors = np.array(document_vectors)

    # Calculate query vector
    query_sentence = "i am a young girl, i respect people"
    query_vec = np.zeros(100)
    count = 0
    for word in query_sentence.split():
        if word in w2v_model.wv:
            query_vec += w2v_model.wv[word]
            count += 1
    if count > 0:
        query_vec /= count

    # Calculate cosine similarity
    pairwise_cosine_similarities = cosine_similarity([query_vec], document_vectors)[0]

    
    def jaccard_similarity(query, document):
        query_tokens = set(word_tokenize(query))
        document_tokens = set(word_tokenize(document))
        intersection = query_tokens.intersection(document_tokens)
        union = query_tokens.union(document_tokens)
        return len(intersection) / len(union)

    jaccard_similarities = [jaccard_similarity(query_sentence, doc) for doc in documents_df['transcript_cleaned']]

    def wmd():
        download('stopwords')
        stop_words = stopwords.words('english')
        def preprocess(sentence):
            return [w for w in sentence.lower().split() if w not in stop_words]
        model = api.load('word2vec-google-news-300')
        distance = model.wmdistance(preprocess('hi'), preprocess('hello'))
        return distance
    word_movers_distance = wmd()
    
    # Function to print most similar documents
    def most_similar(similarity_scores, jaccard_similarities, wmd):
        result = []
        similar_ix = np.argsort(similarity_scores)[::-1]
        for ix in similar_ix:
            result.append({
                'transcript': documents_df.iloc[ix]['transcript'], 
                'similarity_score': similarity_scores[ix], 
                'jaccard_similarity': jaccard_similarities[ix], 
                'word_movers_distance': word_movers_distance  # Corrected variable name here
            })
        return result
        

    return jsonify(most_similar(pairwise_cosine_similarities, jaccard_similarities, wmd))

if __name__ == '__main__':
    app.run(debug=True, port=5001)