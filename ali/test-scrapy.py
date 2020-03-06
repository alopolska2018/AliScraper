# from scrapy import cmdline
#
# a = cmdline.execute("scrapy crawl quotes".split())
# print('ss')

# for item in range(0,5):
#     print(item)
#     for item in range(10,15):
#         print(item)
#         for item in range(20,25):
#             print(item)

# import itertools
#
# list1 = [1,2,3]
# list2 = [1,2,3]
# list3 = [1,2,3]
#
# result = itertools.product(list1, repeat=3)
# for item in result:
#     print(item)

import itertools

stuff1 = [1, 2, 3]
stuff2 = [4, 5, 6]
stuff3 = [7, 8, 9]

for item in stuff1:
  for a in stuff2:
    for b in stuff3:
      print(item, a, b)
# from scrapy.crawler import CrawlerProcess
#
# from ali.spiders.quotes_spider import QuotesSpider
# from ali.pipelines import AliPipeline
# if __name__ == "__main__":
#     # os.remove('result.json')
#
#     test = {}
#
#     process = CrawlerProcess({
#         'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
#     })
#     process.crawl(QuotesSpider)
#     process.start()