from scrapy import cmdline

a = cmdline.execute("scrapy crawl quotes -o result.json -t json".split())
print(a)