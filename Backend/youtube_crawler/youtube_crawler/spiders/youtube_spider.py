import scrapy

class YouTubeSpider(scrapy.Spider):
    name = 'youtube'
    allowed_domains = ['www.youtube.com']
    
    def start_requests(self):
        search_query = input("Enter your YouTube search query: ")
        search_query = search_query.strip().replace(" ", "+")
        url = f"https://www.youtube.com/results?search_query={search_query}"
        yield scrapy.Request(url=url, callback=self.parse)
    
    def parse(self, response):
        video_links = response.css('a.yt-simple-endpoint.style-scope.ytd-video-renderer')
        for link in video_links:
            video_title = link.css('h3::text').get()
            video_url = response.urljoin(link.attrib['href'])
            yield {
                'Title': video_title,
                'URL': video_url
            }
