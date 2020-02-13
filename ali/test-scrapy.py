# from scrapy import cmdline
#
# a = cmdline.execute("scrapy crawl quotes".split())
# print('ss')
from scrapy.crawler import CrawlerProcess

from ali.spiders.quotes_spider import QuotesSpider

if __name__ == "__main__":
    # os.remove('result.json')

    test = {}

    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    })
    process.crawl(QuotesSpider)
    process.start()