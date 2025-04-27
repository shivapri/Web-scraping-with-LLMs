from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import sys

def run(spider_class, spider_name):
    settings = get_project_settings()
    settings.set('FEEDS', {
        f'Data/{spider_name}.csv': {
            'format': 'csv',
            'overwrite': True,
        }
    })
    process = CrawlerProcess(settings)
    process.crawl(spider_class)
    process.start()

if __name__ == "__main__":
    from scrapwebsites.spiders.globenews import GlobenewsSpider
    from scrapwebsites.spiders.newswire2 import Newswire2Spider
    from scrapwebsites.spiders.prnewswire import PrnewswireSpider
    from scrapwebsites.spiders.prweb import PrwebSpider

    spider_mapping = {
        "globenews": GlobenewsSpider,
        "newswire2": Newswire2Spider,
        "prnewswire": PrnewswireSpider,
        "prweb":PrwebSpider
    }

    if len(sys.argv) > 1:
        spider_key = sys.argv[1]
        if spider_key in spider_mapping:
            run(spider_mapping[spider_key], spider_key)
        else:
            print(f"Spider '{spider_key}' not recognized.")
    else:
        print("Please provide a spider name.")
