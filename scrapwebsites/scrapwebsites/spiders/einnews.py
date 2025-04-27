# import scrapy
# from scrapy.linkextractors import LinkExtractor
# from scrapy.spiders import CrawlSpider, Rule

# # article xpath //div[contains(@class,'sidebar-pr-block')]//div[contains(@class,'article-content')]//h3//a
# # next page xpath //div[contains(@class,'text-center')]//ul//li/a[contains(text(),"»")]
# class EinnewsSpider(CrawlSpider):
#     name = "einnews"
#     allowed_domains = ["world.einnews.com"]
#     # start_urls = ["https://world.einnews.com/country/unitedstates"]
#     # user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
#     user_agent = "Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2600.1329 Mobile Safari/537.36"

#     def start_requests(self):
#         yield scrapy.Request(url="https://world.einnews.com/country/unitedstates",headers={'user-agent':self.user_agent})


#     def set_user_requests(self,request,spider):
#         request.headers['User-Agent'] = self.user_agent
#         return request


#     # rules = (Rule(LinkExtractor(restrict_xpath=("//div[contains(@class,'sidebar-pr-block')]//div[contains(@class,'article-content')]//h3//a")), callback="parse_item", follow=True),)

#     rules = (Rule(LinkExtractor(restrict_xpaths=("//div[contains(@class,'sidebar-pr-block')]//div[contains(@class,'article-content')]//h3//a")),callback='parse_item',follow=True,process_request='set_user_requests'),
#         Rule(LinkExtractor(restrict_xpaths=("//div[contains(@class,'text-center')]//ul//li/a[contains(text(),'»')]")),process_request='set_user_requests'),)


#     def parse_item(self, response):
#         print("The url is: ",response.url)

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class EinnewsSpider(CrawlSpider):
    name = "einnews"
    allowed_domains = ["world.einnews.com"]
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
    # start_urls = ["https://world.einnews.com/country/unitedstates"]
    def start_requests(self):
        yield scrapy.Request(
            url="https://world.einnews.com/country/unitedstates",
            headers={'User-Agent': self.user_agent}
        )

    def set_user_requests(self, request, spider):
        request.headers['User-Agent'] = self.user_agent
        return request

    rules = (
        Rule(
            LinkExtractor(restrict_xpaths="//div[contains(@class,'sidebar-pr-block')]//div[contains(@class,'article-content')]//h3//a"),
            callback='parse_item',
            follow=True,
            process_request='set_user_requests'
        ),
        Rule(
            LinkExtractor(restrict_xpaths="//div[contains(@class,'text-center')]//ul//li/a[contains(text(),'»')]"),
            follow=True,
            process_request='set_user_requests'
        ),
    )

    def _compile_rules(self):
        for rule in self.rules:
            if isinstance(rule.process_request, str):
                rule.process_request = getattr(self, rule.process_request)
        super()._compile_rules()

    def parse_item(self, response):
        print("The url is:", response.url)
