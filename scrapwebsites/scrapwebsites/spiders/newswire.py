import scrapy


class NewswireSpider(scrapy.Spider):
    name = "newswire"
    allowed_domains = ["www.newswire.com"]
    start_urls = ["https://www.newswire.com/newsroom","localhost"]

    def parse(self, response):
        pass
