import scrapy
from scrapy_playwright.page import PageMethod
from datetime import datetime, timedelta
from scrapy.exceptions import CloseSpider
#css selectors div.col-start-2.col-end-4'

#articles xpath //div[contains(@class,'flex min-w-0 grow self-center')]
# //footer[contains(@class,'text-small-2-r')]//span[contains(@class,'whitespace-nowrap sa-circle-divider')]/text()
#articles url //div[contains(@class,'flex min-w-0 grow self-center')]//a[contains(@class,'text-share-text visited:text-share-text hover:text-share-text focus:text-share-text')]
class SalphaSpider(scrapy.Spider):
    name = "salpha"
    allowed_domains = ["seekingalpha.com"]
    # start_urls = ["https://seekingalpha.com/market-news/technology"]
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
            url='https://seekingalpha.com/market-news/technology',
            meta={
                'playwright': True,
                'playwright_page_methods': [
                    PageMethod('wait_for_selector', 'div.col-start-2.col-end-4', timeout=300000)
                ],
                'playwright_include_page': True,
                'errback':self.errback
            },
            callback=self.parse
        )   
    async def parse(self, response):
        page = response.meta["playwright_page"]
        articles = response.xpath("//div[contains(@class,'flex min-w-0 grow self-center')]")
        print("Articles are: ",articles)
        for article in articles:
            articles_url = article.xpath(".//a[contains(@class,'text-share-text visited:text-share-text hover:text-share-text focus:text-share-text')]/@href").get()
            article_date = article.xpath(".//footer[contains(@class,'text-small-2-r')]//span[contains(@class,'whitespace-nowrap sa-circle-divider')]/text()").get()
            if article_date:
                    article_date = article_date.strip()
            if not self.is_valid_date(article_date):
                    self.logger.warning(f"Date {article_date} is out of range. Closing spider.")
                    await page.close()   
                    raise CloseSpider(reason=f"Date {article_date} out of range")
            if articles_url:
                    full_link = response.urljoin(articles_url)
                    print("the full link: ",full_link)
                    # request =  scrapy.Request(
                    #     url=full_link,
                    #     meta={
                    #         'playwright': True,
                    #         'playwright_page_methods': [
                    #             PageMethod('wait_for_load_state', 'networkidle'),
                    #             PageMethod('wait_for_selector', "h1.mb-18.break-words", timeout=30000)
                    #         ],
                    #         'playwright_include_page': True
                    #     },
                    #     callback=self.parse_article,
                    #     errback=self.errback
                    # )
                    # print("The request is: ",request.body)
                    yield scrapy.Request(
                        url=full_link,
                        meta={
                            'playwright': True,
                            'playwright_page_methods': [
                                PageMethod('wait_for_load_state', 'networkidle'),
                                PageMethod('wait_for_selector', 'h1[data-test-id="post-title"]', timeout=30000)
                            ],
                            'playwright_include_page': True
                        },
                        callback=self.parse_article,
                        errback=self.errback
                    )
            # await page


        
        # if date
        # await 
    async def parse_article(self,response):
        page = response.meta["playwright_page"]
        
        try:
            paywall_detected = response.xpath("//div[contains(@class,'text-5x-large-b')]/text()").get()
            print("The paywall detected is: ",paywall_detected)
            if paywall_detected and 'Unlock' in paywall_detected:
                print("Paywall found. Skipping article.")
                return 
            article_title = response.xpath("//header/div[contains(@class,'flex w-full justify-between')]//h1/text()").get()
            print("Article Title is: ",article_title)
            yield {
             'article_title':article_title
            }
        finally:
            await page.close()



    def is_valid_date(self,date_str):
        today = datetime.today()
        start_of_year = datetime(today.year, 1, 1)

    # Normalize date string
        date_str = date_str.strip()

        if date_str.startswith("Today"):
            # Example: "Today, 8:00 AM"
            time_part = date_str.split(",")[1].strip()
            article_datetime = datetime.strptime(time_part, "%I:%M %p")
            article_datetime = article_datetime.replace(
                year=today.year, month=today.month, day=today.day
            )
        elif date_str.startswith("Yesterday"):
            # Example: "Yesterday, 5:43 PM"
            time_part = date_str.split(",")[1].strip()
            article_datetime = datetime.strptime(time_part, "%I:%M %p")
            article_datetime = (today - timedelta(days=1)).replace(
                hour=article_datetime.hour,
                minute=article_datetime.minute,
                second=0,
                microsecond=0
            )
        else:
            # Example: "Thu, Apr. 24" or "Sun, Apr. 13"
            try:
                # First, remove weekday name
                parts = date_str.split(",")
                if len(parts) == 2:
                    date_part = parts[1].strip()
                else:
                    date_part = parts[0].strip()

                # Handle formats like "Apr. 24" or "Apr 24"
                date_part = date_part.replace(".", "")  # Remove dot if exists
                article_datetime = datetime.strptime(date_part, "%b %d")
                article_datetime = article_datetime.replace(year=today.year)
            except Exception as e:
                print(f"Failed to parse: {date_str}. Error: {e}")
                return False
        print("Article Datetime is ",article_datetime)

        return article_datetime >= start_of_year
    
    async def errback(self,failure):
        page = failure.request.meta.get('playwright_page')
        print("Closing Page after error")
        if page:
            await page.close()


