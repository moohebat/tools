# coding=utf-8
# scrapy runspider priceprice.py -o test.csv
import re, sys
from urlparse import urlparse, parse_qs
reload(sys)
sys.setdefaultencoding("utf-8")

import scrapy
import codecs

class StackOverflowSpider(scrapy.Spider):
    name = 'websosanh'
    start_urls = [l.strip() for l in codecs.open("websosanh.txt", encoding="utf8").readlines()]
    #start_urls = ["http://websosanh.vn/sua-icreo-so-9-nhat/1013028935/so-sanh.htm"]

    def parse(self, response):
        i = 0
        for merchant in response.css('#all-section > div.store-item'):
       
            i = i + 1            
                    
            yield {
                'position': i,
                'name': merchant.css('div.store-item-col1 > a > p::text').extract()[0],
                'price' : re.sub("[^0-9]", "", "".join(merchant.css('div.store-item-col2 > p > strong::text').extract()[0])),
                'product': response.url,
                'domain' : urlparse(response.url).hostname
            }
