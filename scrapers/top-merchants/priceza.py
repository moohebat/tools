# coding=utf-8
# scrapy runspider priceprice.py -o test.csv
import re, sys
from urlparse import urlparse, parse_qs
reload(sys)
sys.setdefaultencoding("utf-8")

import scrapy
import codecs

class StackOverflowSpider(scrapy.Spider):
    name = 'priceza'
    start_urls = [l.strip() for l in codecs.open("priceza4.txt", encoding="utf8").readlines()]
    #start_urls = ["http://www.priceza.co.id/p/harga/Acer-Liquid-Z5-(3G-AIS)/1392455"]

    def parse(self, response):
        i = 0
        for merchant in response.css('div.seller'):
            
            try:
                name = merchant.css('div.brand a img::attr(alt)').extract()[0],
            except IndexError:
                name = merchant.css('div.brand a span::text').extract()[0],
            
            i = i + 1            
                    
            yield {
                'position': i,
                'name': name,
                'price' : re.sub("[^0-9]", "", "".join(merchant.css('div.price a::text').extract())),
                'product': response.url,
                'domain' : urlparse(response.url).hostname
            }
