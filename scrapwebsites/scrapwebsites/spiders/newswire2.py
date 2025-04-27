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
