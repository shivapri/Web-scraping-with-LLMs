import scrapy


class YahooSpider(scrapy.Spider):
    name = "yahoo"
    allowed_domains = ["www.yahoo.com"]
    start_urls = ["https://www.yahoo.com/news/us"]

    def parse(self, response):
        pass
