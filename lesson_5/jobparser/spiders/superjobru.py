import scrapy
from scrapy.http import HtmlResponse
from lesson_5.jobparser.items import JobparserItem


class SuperjobruSpider(scrapy.Spider):
    name = 'superjobru'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://russia.superjob.ru/vacancy/search/?keywords=Python']
    add_url = 'https://russia.superjob.ru'

    def parse(self, response):
        links = response.xpath('//div[@class="f-test-search-result-item"]//div/div/a/@href').extract()

        for link in links:
            yield response.follow(self.add_url + link, callback=self.parse_vacancy)

        next_page = response.xpath('//a[contains(@class,"f-test-button-dalshe")]/@href').extract_first()
        if next_page:
            yield response.follow(self.add_url + next_page, self.parse)

    def parse_vacancy(self, response: HtmlResponse):
        vacancy_name = response.xpath('//h1//text()').extract_first()
        vacancy_salary = response.xpath('//span[contains(@class, "_1OuF_ ZON4b")]//text()').extract()
        vacancy_url = response.url
        vacancy_site = self.allowed_domains[0]

        yield JobparserItem(name=vacancy_name, salary=vacancy_salary, url=vacancy_url, site=vacancy_site)
