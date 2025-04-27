# import scrapy
# from scrapy_playwright.page import PageMethod
# from datetime import datetime
# from scrapy.exceptions import CloseSpider


# class Newswire2Spider(scrapy.Spider):
#     name = "newswire2"

#     def start_requests(self):
#         yield scrapy.Request(
#             url='https://www.newswire.com/newsroom/business',
#             meta={
#                 'playwright': True,
#                 'playwright_page_methods': [
#                    PageMethod('wait_for_load_state', 'networkidle'),
#                    PageMethod('wait_for_selector', 'section.article-list',timeout=4000)
#                 ]
#                 ,
#                 'playwright_include_page': True  # so we can capture console logs if needed
#             },
#             callback=self.parse,
#             errback = self.errback
#         )

#     def parse_article(self,response):
#         page = response.meta["playwright_page"]
#         print("The article is loaded..")

#         page.close()  # Close the page to avoid memory leaks
#         print("The article is again loaded")

#         article_name = response.css('h1.headline::text').get()
#         published_date = response.css('time.ln-date::attr(datetime)').get()
#         source_url = response.url
#         source = "Newswire"

#         paragraphs = response.css('div.article-copy p::text').getall()
#         concatenated_paragraph = " ".join([p.strip() for p in paragraphs if p.strip()])

#         article_contacts_direct = response.css('div.contacts p::text').getall()
#         article_contacts_direct = " | ".join([c.strip() for c in article_contacts_direct if c.strip()])

#         company_name = response.css('div.company-profile__header h3::text').get()
#         if not company_name:
#             company_name = response.css('div.company-profile h3::text').get()

#         yield {
#             'article_name': article_name,
#             'published_date': published_date,
#             'source_url': source_url,
#             'source': source,
#             'articles_paragraph': concatenated_paragraph,
#             'article_contacts': article_contacts_direct,
#             'company_name': company_name,
#         }

    

#     def parse(self, response):
#         page = response.meta["playwright_page"]
#         print("The page is loaded..")
#         page.close()
#         print("The page is again loaded..")
#         self.logger.info(f"Response URL: {response.url}")
#         self.logger.info(f"Response status: {response.status}")
#         self.logger.info(f"Response length: {len(response.text)}")

#         businessitems = response.css("div.news-item-body")
#         self.logger.info(f"Found {len(businessitems)} business items")

#         for item in response.css('.news-item-body'):
#             title = item.css('a.content-link h3::text').get()
#             link = item.css('a.content-link::attr(href)').get()
#             category = item.css('.ln-category::text').get()
#             date_iso = item.css('time.ln-date::attr(datetime)').get()
#             date_text = item.css('time.ln-date::text').get()
#             if date_text:
#                 date_text = date_text.strip()

            
#             if not self.is_valid_date(date_text):
#                 self.logger.warning(f"Date {date_text} is out of range. Closing spider.")
#                 page.close()
#                 raise CloseSpider(reason=f"Date {date_text} is out of allowed range.")

#             if link:
#                 yield scrapy.Request(
#                     link,
#                     meta={
#                         'playwright': True,
#                         'playwright_page_methods': [
#                             PageMethod('wait_for_load_state', 'networkidle'),
#                             PageMethod('wait_for_selector', 'h1.headline',timeout=4000)
#                         ],
#                         'playwright_include_page': True
#                     },
#                     callback=self.parse_article,
#                     errback=self.errback
#                 )

#     # Close the page after processing valid articles
#         page.close()

#     # Continue to next page if no CloseSpider raised
#         next_page_url = response.css('.chunkination ul:last-child li a::attr(href)').get()
#         if next_page_url:
#             self.logger.info(f"Following next page: {next_page_url}")
#             yield scrapy.Request(
#                 url=response.urljoin(next_page_url),
#                 meta={
#                     'playwright': True,
#                     'playwright_page_methods': [
#                         PageMethod('wait_for_load_state', 'networkidle'),
#                         PageMethod('wait_for_selector', 'section.article-list',timeout=300)
#                     ],
#                     'playwright_include_page': True,
#                 },
#                 errback=self.errback,
#                 callback = self.parse
#             )
    
#     def is_valid_date(self, date_text):
#         """
#         Check if the date is between 2025-01-01 and 2025-04-26
#         """
#         try:
#             parsed_date = datetime.strptime(date_text.strip(), "%b %d, %Y")  # Example: Apr 25, 2025
#             start_date = datetime(2025, 1, 1)
#             end_date = datetime(2025, 4, 26)
#             return start_date <= parsed_date <= end_date
#         except Exception as e:
#             self.logger.warning(f"Date parsing error for '{date_text}': {e}")
#             return False




#     async def errback(self,failure):
#         page = failure.request.meta["playwright_page"]
#         await page.close()
    
#     def is_valid_date(self, date_text):
#         """
#         Check if the date is between 2025-01-01 and 2025-04-26
#         """
#         try:
#             parsed_date = datetime.strptime(date_text.strip(), "%b %d, %Y")  # Example: Apr 25, 2025
#             start_date = datetime(2025, 1, 1)
#             end_date = datetime(2025, 4, 26)
#             return start_date <= parsed_date <= end_date
#         except Exception as e:
#             self.logger.warning(f"Date parsing error for '{date_text}': {e}")
#             return False




#     async def errback(self,failure):
#         page = failure.request.meta["playwright_page"]
#         await page.close()
             
    
#     def is_valid_date(self, date_text):
#         """
#         Check if the date is between 2025-01-01 and 2025-04-26
#         """
#         try:
#             parsed_date = datetime.strptime(date_text.strip(), "%b %d, %Y")  # Example: Apr 25, 2025
#             start_date = datetime(2025, 1, 1)
#             end_date = datetime(2025, 4, 26)
#             return start_date <= parsed_date <= end_date
#         except Exception as e:
#             self.logger.warning(f"Date parsing error for '{date_text}': {e}")
#             return False




#     async def errback(self,failure):
#         page = failure.request.meta["playwright_page"]
#         await page.close()

###### PLAYWRIGHT CODE FROM HERE

import scrapy
from scrapy_playwright.page import PageMethod
from datetime import datetime
from scrapy.exceptions import CloseSpider


class Newswire2Spider(scrapy.Spider):
    name = "newswire2"

    # custom_settings = {
    #     "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 30000,  # 30 seconds
    # }
    custom_settings = {
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 450000,
        "PLAYWRIGHT_NAVIGATION_WAIT_UNTIL": "networkidle",  # better than "load"
        "CONCURRENT_REQUESTS": 5,
        "PLAYWRIGHT_MAX_PAGES_PER_CONTEXT": 5,
        "RETRY_ENABLED": True,
        "RETRY_TIMES": 3,
        "RETRY_HTTP_CODES": [408, 429, 500, 502, 503, 504, 522, 524],
    }

    def start_requests(self):
        yield scrapy.Request(
            url='https://www.newswire.com/newsroom/business',
            meta={
                'playwright': True,
                'playwright_page_methods': [
                    PageMethod('wait_for_selector', '#ln-container', timeout=3000)
                ],
                'playwright_include_page': True
            },
            callback=self.parse,
            errback=self.errback
        )

    async def parse(self, response):
        page = response.meta["playwright_page"]
        self.logger.info(f"Loaded page: {response.url}")
        try:
            articles = response.css('div.news-item-body')
            self.logger.info(f"Found {len(articles)} articles")

            for article in articles:
                link = article.css('a::attr(href)').get()
                date_text = article.css('time::text').get()

                if date_text:
                    date_text = date_text.strip()

                if not self.is_valid_date(date_text):
                    self.logger.warning(f"Date {date_text} is out of range. Closing spider.")
                    raise CloseSpider(reason=f"Date {date_text} out of range")

                if link:
                    full_link = response.urljoin(link)
                    print("the full link: ",full_link)
                    yield scrapy.Request(
                        url=full_link,
                        meta={
                            'playwright': True,
                            'playwright_page_methods': [
                                PageMethod('wait_for_load_state', 'networkidle'),
                                PageMethod('wait_for_selector', "xpath=//div[@class='pr-html']", timeout=30000)
                            ],
                            'playwright_include_page': True
                        },
                        callback=self.parse_article,
                        errback=self.errback
                    )

            # Handle pagination
            next_page = response.css('.chunkination a[rel="next"]::attr(href)').get()
            if next_page:
                yield scrapy.Request(
                    url=response.urljoin(next_page),
                    meta={
                        'playwright': True,
                        'playwright_page_methods': [
                            PageMethod('wait_for_selector','#ln-container')
                        ],
                        'playwright_include_page': True
                    },
                    callback=self.parse,
                    errback=self.errback
                )

        finally:
            await page.close()

    async def parse_article(self, response):
        page = response.meta["playwright_page"]
        await page.close()
        try:
            self.logger.info(f"Loaded article page: {response.url}")
            article = response.xpath("//article[@class='pr-body']")
        
            article_name = article.xpath('./h1/text()').get()
            published_date = article.xpath(".//div[contains(@class,'article-info')]//span[contains(@class,'ai-date')]").get()
            paragraphs = article.xpath(".//div[contains(@class,'pr-html')]//p").getall()
            concatenated_paragraph = " ".join([p.strip() for p in paragraphs if p.strip()])
            article_url = response.xpath("//div[contains(@class,'pr-sidebar-wrapper')]//a[contains(@class,'pr-sidebar__link')]/@href").get()
            article_contacts = response.css('div.contacts p::text').getall()
            contacts_mail = response.xpath("//ul[contains(@class,'pr-contact-list')]//li//a/@href").get()
            contacts_name_title = response.xpath("//ul[contains(@class,'pr-contact-list')]//li//p").getall()
            street_address = response.xpath("//div[contains(@class,'pr-sidebar__address')]/text()").getall()

            company_name = response.css('div.company-profile__header h3::text').get()
            if not company_name:
                company_name = response.css('div.company-profile h3::text').get()
            print("The url is ",response.url)
            yield {
                'article_name': article_name,
                'published_date': published_date,
                'source_url': response.url,
                'source': "Newswire",
                'articles_paragraph': concatenated_paragraph,
                'article_contacts': article_contacts,
                'company_name': company_name,
                'mentioned_url': article_url,
                'contains_mail':contacts_mail,
                'contacts_name_title':contacts_name_title,
                'street_address':street_address

                }
        finally:
            await page.close()

    def is_valid_date(self, date_text):
        """
        Check if the article date is between 2025-01-01 and 2025-04-26
        """
        try:
            parsed_date = datetime.strptime(date_text.strip(), "%b %d, %Y")  # Example: Apr 25, 2025
            start_date = datetime(2025, 1, 1)
            end_date = datetime(2025, 4, 26)
            return start_date <= parsed_date <= end_date
        except Exception as e:
            self.logger.warning(f"Date parsing error for '{date_text}': {e}")
            return False

    async def errback(self, failure):
        self.logger.error(f"Request failed: {failure}")
        page = failure.request.meta.get("playwright_page")
        if page:
            await page.close()


# # import scrapy


# # class NewswireSpider(scrapy.Spider):
#     # name = "newswire_spider"
#     # allowed_domains = ["newswire.com"]
#     # start_urls = ["https://www.newswire.com/newsroom"]

#     # custom_settings = {
#     #     'ROBOTSTXT_OBEY': True,
#     #     'DOWNLOAD_DELAY': 5,
#     #     'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
#     #     'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
#     #     'AUTOTHROTTLE_ENABLED': True,
#     # }

#     # def parse(self, response):
#     #     # Extract article links from the listing page
#     #     article_links = response.xpath("//div[@class='news-item-body']/a[contains(@class,'content-link')]/@href").getall()
#     #     for link in article_links:
#     #         yield response.follow(link, self.parse_article)

#     #     # Follow pagination (Next button)
#     #     next_page = response.xpath("//div[@class='chunkination chunkination-centered']//ul[last()]/li/a[contains(text(), 'Next')]/@href").get()
#     #     if next_page:
#     #         yield response.follow(next_page, self.parse)

#     # def parse_article(self, response):
#     #     yield {
#     #         'url': response.url,
#     #         'title': response.xpath('//h1/text()').get(),
#     #         'date': response.xpath("//div[contains(@class, 'press-release-date')]/text()").get(),
#     #         'body': ' '.join(response.xpath("//div[contains(@class,'editor-content')]//text()").getall()).strip()
#     #     }

## START FROM HERE
# import scrapy
# from datetime import datetime
# import time

# class Newswire2Spider(scrapy.Spider):
#     name = "newswire2"
#     allowed_domains = ["newswire.com"]
#     start_urls = ["https://www.newswire.com/newsroom/business"]

#     user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'

#     def start_requests(self):
#         print("Starting Requests..")
#         request = scrapy.Request(
#             url=self.start_urls[0],
#             callback = self.parse,
#             headers={'User-Agent': self.user_agent}
#         )
#         print("Request response code is: ",request.meta)
#         yield scrapy.Request(
#             url=self.start_urls[0],
#             callback = self.parse,
#             headers={'User-Agent': self.user_agent}
#         )

#     def parse(self, response):
        
#         cutoff_date = datetime(2025, 1, 1)
#         found_old_article = False
#         print()
#         articles = response.xpath("//div[@class='news-item-body']")
#         print(f"Found {len(articles)} articles on the page.")

#         for article in articles:
#             link = article.xpath(".//a[contains(@class,'content-link')]/@href").get()
#             date_text = article.xpath(".//time[contains(@class,'ln-date')]/text()").get()

#             if date_text:
#                 date_text = date_text.strip()

#                 # Handle time-only format or invalid date formats
#                 if not any(month in date_text for month in [
#                     "January", "February", "March", "April", "May", "June",
#                     "July", "August", "September", "October", "November", "December"
#                 ]):
#                     today = datetime.today()
#                     date_text = f"{today.strftime('%B %d, %Y')}"

#                 try:
#                     pub_date = datetime.strptime(date_text, "%B %d, %Y")
#                     print("Publication_date:", pub_date)

#                     if pub_date < cutoff_date:
#                         found_old_article = True
#                         break
#                     else:
#                         full_url = response.urljoin(link)
#                         print("The URL after joining is:", full_url)
#                         time.sleep(2)
#                         yield scrapy.Request(
#                             url=full_url,
#                             callback=self.parse_article,
#                             headers={'User-Agent': self.user_agent},
#                             meta={'date': date_text}
#                         )
#                 except Exception as e:
#                     self.logger.warning(f"Date parse failed for '{date_text}': {e}")

#         if not found_old_article:
#             next_page = response.xpath("//div[contains(@class,'chunkination chunkination-centered')]//ul[last()]/li/a[contains(text(),'Next')]/@href").get()
#             print("The Next Page URL is:", next_page)

#             if next_page:
#                 yield scrapy.Request(
#                     url=response.urljoin(next_page),
#                     callback=self.parse,
#                     headers={'User-Agent': self.user_agent}
#                 )

#     def parse_article(self, response):
#         print("Parsing article:", response.url)

#         yield {
#             'url': response.url,
#             'title': response.xpath('//h1/text()').get(default='').strip(),
#             'date': response.meta['date'],
            
#         }


# import scrapy

# from scrapy_splash import SplashRequest
# from functools import reduce
# import time


# class GlobenewsSpider(scrapy.Spider):
#     name = "globenews"
#     allowed_domains = ["www.globenewswire.com","localhost"]
#     start_urls = ["https://www.globenewswire.com/newsroom"]

#     splash_script = '''
#     function main(splash, args)
#         splash.private_mode_enabled = false
#         assert(splash:go(args.url))
#         assert(splash:wait(7))
#         splash:set_viewport_full()
#         return {
#             html = splash:html(),
#             url = splash:url()
#         }
#     end
#     '''
#     click_script = '''
#     function main(splash, args)
#         splash.private_mode_enabled = false
#         assert(splash:go(args.url))
#         assert(splash:wait(7))

#         local clicked = false
#         local all_matches = splash:select_all(".pagnition-arrow")
#         if all_matches and #all_matches > 0 then
#             all_matches[1]:mouse_click()
#             clicked = true
#             assert(splash:wait(5))
#         end

#         splash:set_viewport_full()
#         return {
#             html = splash:html(),
#             url = splash:url(),
#             clicked = clicked
#         }
#     end
#     '''

#     script = '''
#     function main(splash, args)
#         splash.private_mode_enabled = false
#         local first_page = true
#         assert(splash:go(args.url))
#         assert(splash:wait(5))
#         splash:set_viewport_full()
#         return {html = splash:html(),url = splash:url(),first_page=first_page}
#     end
#     '''

    
#     def start_requests(self):
#         print("Inside Start Requests")
#         print(SplashRequest(url='https://www.globenewswire.com/newsroom', callback=self.parse,
#                             endpoint='execute', args={'lua_source':self.script,'headers': {
#                 'My-Custom-Header': 'Custom-Header-Content',
#             }}))
#         yield SplashRequest(url='https://www.globenewswire.com/newsroom', callback=self.parse,
#                             endpoint='execute', args={'lua_source':self.script,'url': 'https://www.globenewswire.com/newsroom'})

#     def parse(self, response):
#         print("Response URL is: ",response.url)
#         article_links = response.xpath("//div[contains(@class,'mainLink')]/a/@href").getall()
#         print("Article Links are: ",article_links)
#         for link in article_links:
#             print("Scrapping Link ",link)
#             yield SplashRequest(
#                 url=response.urljoin(link),
#                 callback=self.parse_article,
#                 endpoint='execute',
#                 args={'lua_source': self.splash_script, 'url': response.urljoin(link)}
#             )

#         clicked = response.data.get('clicked',False)
#         print("Whether Clicked or not: ",clicked)
#         first_page = response.data.get('first_page',False)
#         print("Whether first page or not: ",clicked)
#         time.sleep(4)
#         if (clicked or first_page):
        
#             yield SplashRequest(
#                 url=response.url,
#                 callback=self.parse,
#                 endpoint='execute',
#                 args={'lua_source': self.click_script, 'url': response.url},
#                 dont_filter = True
#             )
        


#     def parse_article(self, response):
#         article_name = response.xpath("//h1[contains(@class,'article-headline')]/text()").get()
#         published_date = response.xpath("//time/text()").get()
#         source = response.xpath("//span[contains(@class,'article-source')]//a/text()").getall()
#         source_url = response.xpath("//span[contains(@class,'article-source')]//a/@href").get()
#         main_article = response.xpath("//div[contains(@class,'main-body-container article-body ')]")
#         articles_paragraphs = main_article.xpath("./p/text()").getall()
#         article_contacts_direct = response.xpath("//div[contains(@class,'main-tags-attachments-container')]//pre/text()").get()
#         tags = response.xpath("//div[contains(@class,'main-tags-attachments-container')]//div[contains(@class,'tags-container')]//span/a/@href").getall()

#         company_profile = response.xpath("//div[@class='company-profile']")
#         company_name = company_profile.xpath(".//span[@class='company-profile-sub-header']").get()
#         company_website = company_profile.xpath(".//div[@class='company-output']//a/@href").get()

#         concatenated_paragraph = reduce(lambda x, y: x + "\n" + y, articles_paragraphs) if articles_paragraphs else ""

#         yield {
#             # 'article_name': article_name,
#             'published_date': published_date,
#             # 'source_url': response.urljoin(source_url),
#             # 'source': source,
#             # 'articles_paragraph': concatenated_paragraph,
#             # 'article_contacts': article_contacts_direct,
#             # 'company_name': company_name,
#             # 'company_website': company_website,
#             # 'tags':tags,
#             'url': response.url
#         }

### START FROM HERE
# import scrapy
# from scrapy_splash import SplashRequest
# from functools import reduce


# class GlobenewsSpider(scrapy.Spider):
#     name = "newswire2"
#     allowed_domains = ["www.globenewswire.com", "localhost"]
#     start_urls = ["https://www.globenewswire.com/newsroom"]

#     splash_script = '''
#     function main(splash, args)
#         splash.private_mode_enabled = false
#         assert(splash:go(args.url))
#         assert(splash:wait(7))
#         splash:set_viewport_full()
#         return {
#             html = splash:html(),
#             url = splash:url()
#         }
#     end
#     '''

#     click_script = '''
#     function main(splash, args)
#         splash.private_mode_enabled = false
#         assert(splash:go(args.url))
#         assert(splash:wait(5))

#         local clicked = false
#         local next_button = splash:select("span.pagnition-text.pagnition-active")

#         if next_button then
#             next_button:mouse_click()
#             clicked = true
#             assert(splash:wait(5))  -- Wait for the next page to load after click
#         end

#         splash:set_viewport_full()
#         return {
#             html = splash:html(),
#             url = splash:url(),            
#             clicked = clicked
#         }
#     end
#     '''

#     def start_requests(self):
#         yield SplashRequest(
#             url='https://www.globenewswire.com/newsroom',
#             callback=self.parse,
#             endpoint='execute',
#             args={'lua_source': self.click_script, 'url': 'https://www.globenewswire.com/newsroom'},
#             dont_filter=True
#         )

#     def parse(self, response):
#         self.logger.info(f"Scraping page: {response.url}")
#         article_links = response.xpath("//div[contains(@class,'mainLink')]/a/@href").getall()

#         for link in article_links:
#             yield SplashRequest(
#                 url=response.urljoin(link),
#                 callback=self.parse_article,
#                 endpoint='execute',
#                 args={'lua_source': self.splash_script, 'url': response.urljoin(link)}
#             )

#         # Continue to the next page only if a "Next" button was clicked
#         print("Clicked or not: ",response.data.get('clicked', False))
#         if response.data.get('clicked', False):
#             yield SplashRequest(
#                 url=response.url,
#                 callback=self.parse,
#                 endpoint='execute',
#                 args={'lua_source': self.click_script, 'url': response.url},
#                 dont_filter=True
#             )

#     def parse_article(self, response):
#         article_name = response.xpath("//h1[contains(@class,'article-headline')]/text()").get()
#         published_date = response.xpath("//time/text()").get()
#         source = response.xpath("//span[contains(@class,'article-source')]//a/text()").getall()
#         source_url = response.xpath("//span[contains(@class,'article-source')]//a/@href").get()
#         main_article = response.xpath("//div[contains(@class,'main-body-container article-body ')]")
#         articles_paragraphs = main_article.xpath("./p/text()").getall()
#         article_contacts_direct = response.xpath("//div[contains(@class,'main-tags-attachments-container')]//pre/text()").get()
#         tags = response.xpath("//div[contains(@class,'main-tags-attachments-container')]//div[contains(@class,'tags-container')]//span/a/@href").getall()

#         company_profile = response.xpath("//div[@class='company-profile']")
#         company_name = company_profile.xpath(".//span[@class='company-profile-sub-header']/text()").get()
#         company_website = company_profile.xpath(".//div[@class='company-output']//a/@href").get()

#         concatenated_paragraph = reduce(lambda x, y: x + "\n" + y, articles_paragraphs) if articles_paragraphs else ""

#         yield {
#             'article_name': article_name,
#             'published_date': published_date,
#             'source_url': response.urljoin(source_url),
#             'source': source,
#             'articles_paragraph': concatenated_paragraph,
#             'article_contacts': article_contacts_direct,
#             'company_name': company_name,
#             'company_website': company_website,
#             'tags': tags,
#             'url': response.url
#         }
