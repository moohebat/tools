# coding=utf-8
import re, sys
reload(sys)
sys.setdefaultencoding("utf-8")

import scrapy

class StackOverflowSpider(scrapy.Spider):
    name = 'priceza'
    start_urls = ['http://www.priceza.com.my/search', 'http://www.priceza.com.sg/search', 'http://www.priceza.com.ph/search', 'http://www.priceza.com.vn/search', 'http://www.priceza.com/search', 'http://www.priceza.co.id/search']

    def parse(self, response):
        for item in response.css('div.products div.item.group'):

            prices = item.css('small a::text').extract()[0]
            prices = re.sub("[^0-9]", "", prices)

            try:
                prices = int(prices)

                if prices > 1:
                    yield {
                        'name': item.css('h3::text').extract()[0],
                        'prices': prices,
                        'url' : response.urljoin(item.css('a::attr(href)').extract()[0])
                    }
            except:
                pass


        next_page = response.css('div.paging a.next::attr(href)')
        if len(next_page) > 0:
            full_url = response.urljoin(next_page[0].extract())
            yield scrapy.Request(full_url, callback=self.parse)
