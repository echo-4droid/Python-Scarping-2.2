# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import TakeFirst, MapCompose, Compose, Join
from itemloaders.utils import arg_to_iter
from lxml import html
import re


class ProductsparserItem(scrapy.Item):
    @staticmethod
    def process_digit(values, only_digit=True):
        # Функция для приведения сток к числовым переменным
        # Если в строке содержаться недопустимые для чисел символы
        # Не останавливает выполнение программы. В случае исключения
        # сохраняет None если only_digit=True или исходную строку.
        # Всегда возвращает список
        values = arg_to_iter(values)
        for i, value in enumerate(values):
            value = value.replace(' ', '').replace(',', '.')
            if '.' in value:
                try:
                    values[i] = float(value)
                except Exception as e:
                    if only_digit:
                        print("Error in ProductsparserItem with %s value=%r error='%s: %s'" %
                              ('process_digit', value, type(e).__name__, str(e)))
                        values[i] = None
            else:
                try:
                    values[i] = int(value)
                except Exception as e:
                    if only_digit:
                        print("Error in ProductsparserItem with %s value=%r error='%s: %s'" %
                              ('process_digit', value, type(e).__name__, str(e)))
                        values[i] = None
        return values

    @staticmethod
    def process_store_stocks(value):
        # Функция для обработки списка наличия товара в магазинах
        value = html.fromstring(value)
        store_name = str(value.xpath('./span/text()')[0])
        store_code = str(value.xpath('./@store-code')[0])
        store_unit = str(value.xpath('./@unit')[0])
        store_stock = str(value.xpath('./@stock')[0])
        return {
            'store_name': store_name,
            'store_code': ProductsparserItem.process_digit(store_code)[0],
            'store_unit': store_unit,
            'store_stock': ProductsparserItem.process_digit(store_stock)[0]
        }

    @staticmethod
    def process_specifications(value):
        # Функция для обработки параметров товара
        value = html.fromstring(value)
        term = str(value.xpath('./dt/text()')[0])
        definition = re.sub('\s{2,}', '', value.xpath('./dd/text()')[0])  # очистка повторяющихся пробельных символов
        return {
            'term': term,
            'definition': ProductsparserItem.process_digit(definition, False)[0]
        }

    @staticmethod
    def process_photos_url(values):
        # Функция для обработки ссылок на изображения.
        # Здесь выбираются ссылки на изображения в наибольшем разрешении
        size_w_max, size_h_max = 0, 0
        for item in values:
            size = re.findall('w_\d+,h_\d+', item)[0]
            size_w, size_h = int(size.split(',')[0][2:]), \
                             int(size.split(',')[1][2:])
            if size_w > size_w_max or size_h > size_h_max:
                size_w_max, size_h_max = size_w, size_h
        size_max = f'w_{size_w_max},h_{size_h_max}'
        return [item for item in values if size_max in item]

    @staticmethod
    def process_description(values):
        results = []
        for value in values:
            if not re.match('^\n\s*', value):
                results.append(value)
        return results

    _id = scrapy.Field()
    url = scrapy.Field(output_processor=TakeFirst())
    name = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(input_processor=MapCompose(process_digit.__get__(object, None)),
                         output_processor=TakeFirst())
    currency = scrapy.Field(output_processor=TakeFirst())
    unit = scrapy.Field(output_processor=TakeFirst())
    description = scrapy.Field(input_processor=Compose(process_description.__get__(object, None)),
                               output_processor=Join('\n'))
    store_stocks = scrapy.Field(input_processor=MapCompose(process_store_stocks.__get__(object, None)))
    specifications = scrapy.Field(input_processor=MapCompose(process_specifications.__get__(object, None)))
    photos = scrapy.Field(input_processor=Compose(process_photos_url.__get__(object, None)))
