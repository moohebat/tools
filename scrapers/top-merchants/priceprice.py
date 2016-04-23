# coding=utf-8
# scrapy runspider priceprice.py -o test.csv
import re, sys
from urlparse import urlparse, parse_qs
reload(sys)
sys.setdefaultencoding("utf-8")

import scrapy

class StackOverflowSpider(scrapy.Spider):
    name = 'priceprice'
    start_urls = [l.strip() for l in open("priceprice.txt").readlines()]
    #start_urls = ["http://id.priceprice.com/Xiaomi-Redmi-Note-2-15625/"]

    def parse(self, response):
        i = 0
        for merchant in response.css('#price_list > div.itemBox, #price_list > div.itemGrp > div.itemBox'):

            url = merchant.css('div.itmBtn a::attr(href)').extract()[0]
            try: 
                domain = urlparse(parse_qs(urlparse(url).query)['url'][0]).hostname
            except KeyError:
                # offline merchant
                continue
            
            try: 
                name = merchant.css('div.itmShop img::attr(alt)').extract()[0],
            except IndexError:
                # no logo
                name = merchant.css('div.itmShop > div > a > span::text').extract()[0],
            i = i + 1
                    
            yield {
                'position': i,
                'name': name,
                'price' : re.sub("[^0-9]", "", merchant.css('p.price::text').extract()[0]),
                'product': response.url,
                'domain' : urlparse(response.url).hostname
            }
