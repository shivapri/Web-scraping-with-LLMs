import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from functools import reduce
## articles xpath //div[contains(@class,'col-md-8 col-sm-8 ')]//div[contains(@class,'row newsCards')]//a
## next page path //div[contains(@class,'pagination-bar')]//ul[contains(@class,'pagination')]//a[@aria-label="Next"]

# class PrnewswireSpider(CrawlSpider):
#     name = "prnewswire"
#     allowed_domains = ["www.prnewswire.com"]
#     # start_urls = ["https://www.prnewswire.com/news-releases/news-releases-list"]
#     user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'

#     def start_requests(self):
#         yield scrapy.Request(url='https://www.prnewswire.com/news-releases/news-releases-list', headers={
#             'user-agent':self.user_agent
#         })
#     def set_user_agent(self, request, spider):
#         request.headers['User-Agent'] = self.user_agent
#         return request

#     rules = (Rule(LinkExtractor(restrict_xpaths=("//div[contains(@class,'col-md-8 col-sm-8 ')]//div[contains(@class,'row newsCards')]//a")), callback="parse_item", follow=True,process_request='set_user_agent'),
#             #  Rule(LinkExtractor(allow=("//div[contains(@class,'col-md-8 col-sm-8 ')]//div[contains(@class,'row newsCards')]//a")), callback="parse_item", follow=True,process_request='set_user_agent'),
#         Rule(LinkExtractor(restrict_xpaths=("//div[contains(@class,'pagination-bar')]//ul[contains(@class,'pagination')]//a[@aria-label='Next']")),process_request='set_user_agent'))

#     def parse_item(self, response): 
#         print("The url is: ",response.url)

from datetime import datetime

import time

class PrnewswireSpider(scrapy.Spider):
    name = "prnewswire"
    allowed_domains = ["prnewswire.com"]
    start_urls = ["https://www.prnewswire.com/news-releases/news-releases-list"]

    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'

    def start_requests(self):
        yield scrapy.Request(
            url=self.start_urls[0], 
            headers={'User-Agent': self.user_agent}
        )

    def parse(self, response):
        cutoff_date = datetime(2025, 1, 1)
        found_old_article = False

        articles = response.xpath("//div[contains(@class,'row newsCards')]")

        for article in articles:
            link = article.xpath(".//a/@href").get()
            date_text = article.xpath(".//h3//small/text()").get()
            # print("Date text is ",date_text)
            
            
            if date_text:
                date_text = date_text.strip()

            # Handle time-only format (e.g. '07:00 ET') by appending today's date
                if not any(month in date_text for month in [
                    "January", "February", "March", "April", "May", "June",
                    "July", "August", "September", "October", "November", "December"
                ]):
                    today = datetime.today()
                    date_text = f"{today.strftime('%B %d, %Y')}"
                try:
                    pub_date = datetime.strptime(date_text.strip(), "%B %d, %Y")
                    print("Publication_date",pub_date)
                    if pub_date < cutoff_date:
                        found_old_article = True
                        break  # break the loop early
                    else:
                        full_url = response.urljoin(link)
                        print("The URL after joining is: ",full_url)
                        time.sleep(4)
                        yield scrapy.Request(
                            url=full_url,
                            callback=self.parse_article,
                            headers={'User-Agent': self.user_agent},
                            meta={'date': date_text}
                        )
                except Exception as e:
                    self.logger.warning(f"Date parse failed: {date_text} ({e})")

        if not found_old_article:
            # keep going to the next page
            next_page = response.xpath("//a[@aria-label='Next']/@href").get()
            print("The Next Page URl is : ",next_page)
            if next_page:
                yield scrapy.Request(
                    url=response.urljoin(next_page),
                    callback=self.parse,
                    headers={'User-Agent': self.user_agent}
                )

    def parse_article(self, response):
        # article_lang = response.xpath("//button[contains(@class,'btn dropdown-toggle btn-default btn-xs')]")
        article_languages = response.xpath("//div[contains(@class,'dropdown lang-switch open')]//li/a[contains(text(),'English')]/@href").get()

        # print("The URL is: ",response.url)
        article_name = response.xpath("//div[contains(@class,'custom-container')]//h1/text()").get()
        article_provider_url = response.xpath("//div[contains(@class,'swaping-class-left')]//a/@href").get()

        published_date = response.xpath("//div[contains(@class,'swaping-class-left')]/p/text()").get()
        articles_listing = response.xpath("//section[contains(@class,'release-body container ')]//ul//li/text()").getall()
        articles_paragraph = response.xpath("//section[contains(@class,'release-body container ')]//p/text()").getall()
        overall_articles_listing = reduce(lambda x, y: x + "\n" + y, articles_listing) if articles_listing else ""
        overall_articles_paragraph = reduce(lambda x, y: x + "\n" + y, articles_paragraph) if articles_paragraph else ""
        overall_paragraph = overall_articles_listing+"\n"+overall_articles_paragraph
        print("The article languages: ",article_languages)
        # 'article_name': article_name,
        #     'published_date': published_date,
        #     'source_url': response.urljoin(source_url) if source_url else None,
        #     'source': source,
        #     'articles_paragraph': concatenated_paragraph,
        #     'article_contacts': article_contacts_direct,
        #     'company_name': company_name,
        

        yield {
            'url': response.url,
            'title': response.xpath('//h1/text()').get(default='').strip(),
            'date': response.meta['date'],
            'published_date':published_date,
            'article_paragraph':articles_paragraph
        }
