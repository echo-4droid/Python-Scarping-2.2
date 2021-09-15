import scrapy
from scrapy.http import HtmlResponse
from lesson_5.jobparser.items import JobparserItem


class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = ['https://novosibirsk.hh.ru/search/vacancy?st=searchVacancy&text=Python&currency_code=RUR&order_by=relevance&search_period=0&items_on_page=20&no_magic=true&L_save_area=true&area=1217&area=1932&area=1008&area=1505',
                  'https://novosibirsk.hh.ru/search/vacancy?st=searchVacancy&text=Python&currency_code=RUR&order_by=relevance&search_period=0&items_on_page=20&no_magic=true&L_save_area=true&area=1817&area=1828',
                  'https://novosibirsk.hh.ru/search/vacancy?st=searchVacancy&text=Python&currency_code=RUR&order_by=relevance&search_period=0&items_on_page=20&no_magic=true&L_save_area=true&area=1716&area=1511&area=1739&area=1844',
                  'https://novosibirsk.hh.ru/search/vacancy?st=searchVacancy&text=Python&currency_code=RUR&order_by=relevance&search_period=0&items_on_page=20&no_magic=true&L_save_area=true&area=1192&area=1754&area=1124',
                  'https://novosibirsk.hh.ru/search/vacancy?st=searchVacancy&text=Python&currency_code=RUR&order_by=relevance&search_period=0&items_on_page=20&no_magic=true&L_save_area=true&area=1463&area=1020&area=1859&area=1943&area=1471&area=1229&area=1661&area=1771&area=1438&area=1146&area=1308&area=1880',
                  'https://novosibirsk.hh.ru/search/vacancy?st=searchVacancy&text=Python&currency_code=RUR&order_by=relevance&search_period=0&items_on_page=20&no_magic=true&L_save_area=true&area=145&area=1890&area=1946&area=2019&area=1061',
                  'https://novosibirsk.hh.ru/search/vacancy?st=searchVacancy&text=Python&currency_code=RUR&order_by=relevance&search_period=0&items_on_page=20&no_magic=true&L_save_area=true&area=1679&area=1051&area=1202&area=1249&area=1563&area=1898',
                  'https://novosibirsk.hh.ru/search/vacancy?st=searchVacancy&text=Python&currency_code=RUR&order_by=relevance&search_period=0&items_on_page=20&no_magic=true&L_save_area=true&area=1422&area=1347&area=1118&area=1424&area=1434&area=1553&area=1077&area=1041&area=2114&area=1620&area=1556&area=1174&area=1475&area=1624&area=1169&area=1187&area=1530',
                  'https://novosibirsk.hh.ru/search/vacancy?st=searchVacancy&text=Python&currency_code=RUR&order_by=relevance&search_period=0&items_on_page=20&no_magic=true&L_save_area=true',
                  'https://novosibirsk.hh.ru/search/vacancy?st=searchVacancy&text=Python&currency_code=RUR&order_by=relevance&search_period=0&items_on_page=20&no_magic=true&L_save_area=true',
                  'https://novosibirsk.hh.ru/search/vacancy?st=searchVacancy&text=Python&currency_code=RUR&order_by=relevance&search_period=0&items_on_page=20&no_magic=true&L_save_area=true',
                  'https://novosibirsk.hh.ru/search/vacancy?st=searchVacancy&text=Python&currency_code=RUR&order_by=relevance&search_period=0&items_on_page=20&no_magic=true&L_save_area=true',
                  'https://novosibirsk.hh.ru/search/vacancy?st=searchVacancy&text=Python&currency_code=RUR&order_by=relevance&search_period=0&items_on_page=20&no_magic=true&L_save_area=true&area=2',
                  'https://novosibirsk.hh.ru/search/vacancy?st=searchVacancy&text=Python&currency_code=RUR&order_by=relevance&search_period=0&items_on_page=20&no_magic=true&L_save_area=true&area=2&experience=between1And3',
                  'https://novosibirsk.hh.ru/search/vacancy?st=searchVacancy&text=Python&currency_code=RUR&order_by=relevance&search_period=0&items_on_page=20&no_magic=true&L_save_area=true&area=2&experience=between3And6',
                  'https://novosibirsk.hh.ru/search/vacancy?st=searchVacancy&text=Python&currency_code=RUR&order_by=relevance&search_period=0&items_on_page=20&no_magic=true&L_save_area=true&area=2&experience=noExperience',
                  'https://novosibirsk.hh.ru/search/vacancy?st=searchVacancy&text=Python&currency_code=RUR&order_by=relevance&search_period=0&items_on_page=20&no_magic=true&L_save_area=true&experience=moreThan6',
                  'https://novosibirsk.hh.ru/search/vacancy?st=searchVacancy&text=Python&currency_code=RUR&order_by=relevance&search_period=0&items_on_page=20&no_magic=true&L_save_area=true&area=1&experience=moreThan6',
                  'https://novosibirsk.hh.ru/search/vacancy?st=searchVacancy&text=Python&currency_code=RUR&order_by=relevance&search_period=0&items_on_page=20&no_magic=true&L_save_area=true&area=1&experience=noExperience',
                  'https://novosibirsk.hh.ru/search/vacancy?st=searchVacancy&text=Python&currency_code=RUR&order_by=relevance&search_period=0&items_on_page=20&no_magic=true&L_save_area=true&area=1&industry=7&industry=51&industry=45&industry=36&industry=50&industry=15&industry=52&industry=19&industry=48&industry=24&industry=47&industry=39&industry=37&industry=5&experience=between1And3',
                  'https://novosibirsk.hh.ru/search/vacancy?st=searchVacancy&text=Python&currency_code=RUR&order_by=relevance&search_period=0&items_on_page=20&no_magic=true&L_save_area=true&area=1&industry=7&industry=51&industry=45&industry=36&industry=50&industry=15&industry=52&industry=19&industry=48&industry=24&industry=47&industry=39&industry=37&industry=5&industry=27&industry=388&industry=41&industry=11&experience=between1And3']

    def parse(self, response:HtmlResponse):
        links = response.xpath('//span[@class="resume-search-item__name"]//a/@href').extract()

        for link in links:
            yield response.follow(link, callback=self.parse_vacancy)

        next_page = response.xpath('//a[contains(@data-qa, "pager-next")]/@href').extract_first()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_vacancy(self, response:HtmlResponse):
        vacancy_name = response.xpath('//h1[contains(@data-qa, "vacancy-title")]//text()').extract_first()
        vacancy_salary = response.xpath('//p[contains(@class, "vacancy-salary")]/span/text()').extract_first()
        vacancy_url = response.url
        vacancy_site = self.allowed_domains[0]

        yield JobparserItem(name=vacancy_name, salary=vacancy_salary, url=vacancy_url, site=vacancy_site)
