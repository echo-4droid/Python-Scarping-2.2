from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from lesson_5.jobparser import settings
from lesson_5.jobparser.spiders.hhru import HhruSpider
from lesson_5.jobparser.spiders.superjobru import SuperjobruSpider


if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(HhruSpider)
    process.crawl(SuperjobruSpider)

    process.start()
