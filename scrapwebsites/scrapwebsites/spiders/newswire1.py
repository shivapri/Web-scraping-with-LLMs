import scrapy


class Newswire1Spider(scrapy.Spider):
    name = "newswire1"
    allowed_domains = ["www.newswire.com"]
    start_urls = ["https://www.newswire.com/newsroom"]

    def parse(self, response):
        pass
