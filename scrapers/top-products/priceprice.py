# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import scrapy

class StackOverflowSpider(scrapy.Spider):
    name = 'priceprice'
    start_urls = ['http://ph.priceprice.com/', 'http://id.priceprice.com/', 'http://th.priceprice.com/']

    def parse(self, response):
        for href in response.css('div.topCatInfo > span > a::attr(href)'):
            full_url = response.urljoin(href.extract())
            yield scrapy.Request(full_url, callback=self.parse_category)

    def parse_category(self, response):
        for item in response.css('div.itemBoxIn'):
            prices = item.css('span.pricenum::text').extract()[0]
            prices = prices.strip(")").strip("(").strip("harga").strip("Prices").strip("ราคา").strip("รายการ").strip(" ")

            try:
                prices = int(prices)

                if prices > 1:
                    yield {
                        'category': response.css('#breadCrumbs span::text').extract()[1].strip("\n"),
                        'name': item.css('h3 > a::text').extract()[0],
                        'prices': prices,
                        'url' : response.urljoin(item.css('h3 > a::attr(href)').extract()[0])
                    }
            except:
                pass

        next_page = response.css('.last a::attr(href)')
        if len(next_page) > 0:
            full_url = response.urljoin(next_page[0].extract())
            yield scrapy.Request(full_url, callback=self.parse_category)
