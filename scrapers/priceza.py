# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import scrapy

class StackOverflowSpider(scrapy.Spider):
    name = 'priceza'
    start_urls = ['http://www.priceza.com/search']

    def parse(self, response):
        for item in response.css('div.products div.item.group'):

            prices = item.css('small a::text').extract()[0]
            prices = prices.strip("dari").strip("TOKO").strip(" ").strip("จาก").strip("ร้านค้า")

            try:
                prices = int(prices)

                if prices > 0:
                    yield {
                        'name': item.css('h3::text').extract()[0],
                        'prices': prices
                    }
            except:
                pass


        next_page = response.css('div.paging a.next::attr(href)')
        if len(next_page) > 0:
            full_url = response.urljoin(next_page[0].extract())
            yield scrapy.Request(full_url, callback=self.parse)
