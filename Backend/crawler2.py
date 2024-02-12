from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
app = Flask(__name__)
cors = CORS(app)
CORS(app, resources={r"/*": {"origins": "http://localhost:5673"}})
app.config['CORS_HEADERS'] = 'Content-Type'
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')


class YouTubeCrawler:
    def __init__(self):
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options) # You may need to specify the path to your chromedriver executable

    def scroll_down(self):
        # Scroll down the page to load more content
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Add a small delay to allow content to load

    def crawl(self, search_query):
        url = f"https://www.youtube.com/results?search_query={search_query}"
        self.driver.get(url)

        video_urls = []
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            # Scroll down to load more content
            self.scroll_down()
            
            # Get the new height of the page
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                # If no more content is loaded, break the loop
                break
            last_height = new_height

        # After scrolling, retrieve all video links
        video_links = self.driver.find_elements(By.CSS_SELECTOR, 'a.yt-simple-endpoint')
        for link in video_links:
            video_url = link.get_attribute('href')
            if video_url:
                video_urls.append(video_url)

        return video_urls

    def close(self):
        self.driver.quit()

@app.route('/', methods=['POST'])
def crawl_and_send():
    print('req')
    data = request.get_json()
    search_query = data.get('search_query')
    api_url = data.get('api_url')
    
    if not search_query:
        return jsonify({'error': 'Search query not provided'}), 400

    if not api_url:
        return jsonify({'error': 'API URL not provided'}), 400
    
    crawler = YouTubeCrawler()
    video_urls = crawler.crawl(search_query)
    crawler.close()
    payload = {
    "url": api_url,
    "video_url":"https://www.youtube.com/watch?v=92hHiiYxHZ4"
    }
    print(video_urls)
    response = requests.post('http://localhost:5000', json=payload , timeout= 9000)
    print(response)

    return jsonify({'message': 'Crawling complete and URLs sent to the API.'})

if __name__ == '__main__':
    app.run(debug=True, port=5001)

# Example usage
# search_query = input("Enter your YouTube search query: ")
# crawler = YouTubeCrawler()
# video_urls = crawler.crawl(search_query)
# print(video_urls)
# crawler.close()
# payload = {
#     "url": "https://www.youtube.com/@Childrenia",
#     "video_url":"https://www.youtube.com/watch?v=OUZSccFax34"
# }
# response = requests.post('http://localhost:5001', json=payload , timeout= 9000)
