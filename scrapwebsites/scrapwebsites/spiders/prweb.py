import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from functools import reduce
from datetime import datetime

import time
class PrwebSpider(CrawlSpider):
    name = "prweb"
    allowed_domains = ["www.prweb.com"]
    # start_urls = ["https://www.prweb.com/releases/news-releases-list"]
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
    cutoff_date = datetime(2025, 1, 1)

    def start_requests(self):
        yield scrapy.Request(url="https://www.prweb.com/releases/news-releases-list",headers={'user-agent':self.user_agent})


    def set_user_requests(self,request,spider):
        request.headers['User-Agent'] = self.user_agent
        return request

    rules = (Rule(LinkExtractor(restrict_xpaths=("//div[contains(@class,'card-list card-list-hr nativo-section')]//a")),callback='parse_item',follow=True,process_request='set_user_requests'),
        Rule(LinkExtractor(restrict_xpaths=("//ul[@class='pagination']//a[span[contains(text(), '»')]]")),process_request='set_user_requests'),)

    def parse_item(self, response):
        print("The url is: ",response.url)
        provided_news_details = response.xpath("//div[contains(@class,'custom-container')]//div[contains(@class,'col-lg-8')]")
        provider_name = provided_news_details.xpath("./strong/text()").get()
        published_date = provided_news_details.xpath("./p/text()").get()
        if published_date:
            published_date = published_date.strip()
        if not self.is_valid_date(published_date):
            self.logger.warning(f"Found an old article dated {published_date}. Stopping spider.")
            raise scrapy.exceptions.CloseSpider(reason=f"Found old article {published_date}")

        contents = response.xpath("//div[contains(@class,'col-sm-10 col-sm-offset-1')]/p")
        main_contents = contents.xpath("./text()").getall()
        article_urls = contents.xpath("./a/@href").getall()
        article_contents = main_contents[:-2]
        overall_content = reduce(lambda x,y:x+"\n"+y,article_contents)
        article_contacts = main_contents[-2]
        time.sleep(4)
        yield {

            'provider_name':provider_name,
            'published_date':published_date,
            'article_contents':overall_content,
            'article_contacts':article_contacts,
            'article_urls':article_urls,
            'url':response.url
        }
    
    def is_valid_date(self, date_text):
        if not date_text:
            return False

        try:
            # Clean timezone abbreviation if exists
            for tz in [' ET', ' PT', ' CT', ' MT']:
                if tz in date_text:
                    date_text = date_text.replace(tz, '')

        # Try parsing without timezone
            pub_date = datetime.strptime(date_text.strip(), "%b %d, %Y, %H:%M")
            print(f"Parsed publication date: {pub_date}")

            return pub_date >= self.cutoff_date

        except Exception as e:
            self.logger.warning(f"Failed to parse publication date '{date_text}': {e}")
            return False

