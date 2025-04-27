import scrapy
from scrapy_splash import SplashRequest
from functools import reduce
from datetime import datetime

class GlobenewsSpider(scrapy.Spider):
    name = "globenews"
    allowed_domains = ["www.globenewswire.com", "localhost"]
    start_urls = ["https://www.globenewswire.com/newsroom"]

    # Lua script to render article pages
    splash_script = '''
    function main(splash, args)
        splash.private_mode_enabled = false
        assert(splash:go(args.url))
        assert(splash:wait(7))
        splash:set_viewport_full()
        return {
            html = splash:html(),
            url = splash:url()
        }
    end
    '''

    # Lua script to handle "Next" click in listing pages
    click_script = '''
    function main(splash, args)
        splash.private_mode_enabled = false
        assert(splash:go(args.url))
        assert(splash:wait(5))

        local clicked = false
        local next_button = splash:select("div.pagnition-next a")

        if next_button then
            next_button:mouse_click()
            clicked = true
            assert(splash:wait(5))  -- Wait for the next page to load after click
        end

        splash:set_viewport_full()
        return {
            html = splash:html(),
            url = splash:url(),
            clicked = clicked
        }
    end
    '''

    def start_requests(self):
        yield SplashRequest(
            url=self.start_urls[0],
            callback=self.parse,
            endpoint='execute',
            args={'lua_source': self.click_script, 'url': self.start_urls[0]},
            dont_filter=True
        )

    def parse(self, response):
        self.logger.info(f"Scraping page: {response.url}")
        cutoff_date = datetime(2025, 1, 1)
        found_old_article = False

        articles = response.xpath("//div[contains(@class,'mainLink')]/a")
        self.logger.info(f"Found {len(articles)} articles.")

        for article in articles:
            link = article.xpath("./@href").get()
            date_text = response.xpath("//div[contains(@class,'newsLink pl-0')]//div[contains(@class,'date-source')]//span[contains(text(),'ET')]/text()").get()

            if date_text:
                date_text = date_text.strip()
                clean_date_text = date_text.split()[0:3]  # ["April", "25,", "2025"]
                clean_date_text = " ".join(clean_date_text).replace(",", "")
                try:
                    
                    pub_date = datetime.strptime(clean_date_text, "%B %d %Y")
                    self.logger.info(f"Parsed date: {pub_date}")

                    if pub_date < cutoff_date:
                        self.logger.info(f"Skipping older article: {pub_date}")
                        found_old_article = True
                        break  # Stop further pagination
                    else:
                        yield SplashRequest(
                            url=response.urljoin(link),
                            callback=self.parse_article,
                            endpoint='execute',
                            args={'lua_source': self.splash_script, 'url': response.urljoin(link)},
                            meta={'date': pub_date.strftime("%Y-%m-%d")}
                        )
                except Exception as e:
                    self.logger.warning(f"Date parse failed: '{date_text}' — {e}")

        # Handle pagination only if all articles were recent
        clicked = response.data.get('clicked', False)
        if clicked and not found_old_article:
            self.logger.info("Following to next page...")
            yield SplashRequest(
                url=response.url,
                callback=self.parse,
                endpoint='execute',
                args={'lua_source': self.click_script, 'url': response.url},
                dont_filter=True
            )
        else:
            self.logger.info("Stopping pagination due to old articles or no Next button.")

    def parse_article(self, response):
        article_name = response.xpath("//h1[contains(@class,'article-headline')]/text()").get()
        published_date = response.meta.get('date')
        source = response.xpath("//span[contains(@class,'article-source')]//a/text()").getall()
        source_url = response.xpath("//span[contains(@class,'article-source')]//a/@href").get()
        main_article = response.xpath("//div[contains(@class,'main-body-container article-body ')]")
        articles_paragraphs = main_article.xpath("./p/text()").getall()
        article_contacts_direct = response.xpath("//div[contains(@class,'main-tags-attachments-container')]//pre/text()").get()
        tags = response.xpath("//div[contains(@class,'main-tags-attachments-container')]//div[contains(@class,'tags-container')]//span/a/@href").getall()

        company_profile = response.xpath("//div[@class='company-profile']")
        company_name = company_profile.xpath(".//span[@class='company-profile-sub-header']/text()").get()
        company_website = company_profile.xpath(".//div[@class='company-output']//a/@href").get()

        concatenated_paragraph = reduce(lambda x, y: x + "\n" + y, articles_paragraphs) if articles_paragraphs else ""

        yield {
            'article_name': article_name,
            'published_date': published_date,
            'source_url': response.urljoin(source_url) if source_url else None,
            'source': source,
            'articles_paragraph': concatenated_paragraph,
            'article_contacts': article_contacts_direct,
            'company_name': company_name,
        }