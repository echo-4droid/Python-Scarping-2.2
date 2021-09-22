import scrapy
from scrapy.http import HtmlResponse
from lesson_6.productsparser.items import ProductsparserItem
from scrapy.loader import ItemLoader


class LeroymerlinSpider(scrapy.Spider):
    name = 'leroymerlin'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, query):
        super(LeroymerlinSpider, self).__init__()
        self.start_urls = [f'https://leroymerlin.ru/search/?q={query}']

    def parse(self, response: HtmlResponse):
        links = response.xpath('//div[contains(@class, "phytpj4_plp")]/a/@href').extract()
        for link in links:
            yield response.follow(link, callback=self.parse_product)

        next_page = response.xpath('//a[contains(@data-qa-pagination-item, "right")]/@href').extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_product(self, response: HtmlResponse):
        loader = ItemLoader(item=ProductsparserItem(), response=response)
        loader.add_value('url', response.url)
        loader.add_xpath('name', '//h1/text()')
        loader.add_xpath('price', '//span[contains(@slot, "price")]/text()')
        loader.add_xpath('currency', '//span[contains(@slot, "currency")]/text()')
        loader.add_xpath('unit', '//span[contains(@slot, "unit")]/text()')
        loader.add_xpath('description', '//section[contains(@id, "nav-description")]//text()')
        loader.add_xpath('store_stocks', '//uc-elbrus-pdp-stocks-list//uc-store-stock')
        loader.add_xpath('specifications', '//div[@class="def-list__group"]')
        loader.add_xpath('photos', '//uc-pdp-media-carousel[contains(@slot, "media-content")]//source/@srcset')
        yield loader.load_item()
