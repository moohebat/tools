import scrapy

class StackOverflowSpider(scrapy.Spider):
    name = 'websosanh'
    start_urls = ['http://websosanh.vn/']

    def parse(self, response):
        for href in response.css('div.cate > a::attr(href)'):
            full_url = response.urljoin(href.extract())
            yield scrapy.Request(full_url, callback=self.parse_category)

    def parse_category(self, response):
        for item in response.css('div.thumbnail'):

            prices = item.css('p.merchant span::text').extract();
            if prices:
                prices = prices[0]
                yield {
                    'category': response.css('.breadCrumb .current a::text').extract()[0],
                    'name': item.css('h3 > a::text').extract()[0],
                    'prices': prices,
                    'url' : response.urljoin(item.css('h3 > a::attr(href)').extract()[0])
                }

        next_page = response.css('link[rel="next"]::attr(href)')
        if len(next_page) > 0:
            full_url = next_page[0].extract()
            yield scrapy.Request(full_url, callback=self.parse_category)
