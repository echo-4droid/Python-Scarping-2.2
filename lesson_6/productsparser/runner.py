#
# 1. Взять любую категорию товаров на сайте Леруа Мерлен. Собрать следующие данные:
#   - название;
#   - все фото;
#   - параметры товара в объявлении;
#   - ссылка;
#   - цена.
# 2. Реализуйте очистку и преобразование данных с помощью ItemLoader. Цены должны быть в виде числового значения.
# 3. Дополнительно:
# 3.1 Написать универсальный обработчик характеристик товаров, который будет формировать данные вне зависимости от их
#       типа и количества.
# 3.3 Реализовать хранение скачиваемых файлов в отдельных папках, каждая из которых должна соответствовать собираемому
#       товару
#
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from lesson_6.productsparser import settings
from lesson_6.productsparser.spiders.leroymerlin import LeroymerlinSpider


if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(crawler_settings)
    process.crawl(LeroymerlinSpider, query='освещение')

    process.start()
