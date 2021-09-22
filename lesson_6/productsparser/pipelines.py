# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import scrapy
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient
from datetime import datetime
import hashlib
from scrapy.utils.python import to_bytes


class ProductsparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        date_today = datetime.today().strftime('_on_%d_%m_%Y')
        self.mongo_db = client['products' + date_today]

    def __del__(self):
        self.mongo_db.logout()

    def process_item(self, item, spider):
        collection = self.mongo_db[spider.name]

        # Избегаем повторений в БД
        if not collection.find_one({'url': item['url']}):
            return collection.insert_one(item)
        else:
            print(f'Product {item["name"]} already exists in collection {collection}')
            return None


class ProductsPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                try:
                    yield scrapy.Request(img)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        if results:
            item['photos'] = [{'checksum': i[1]['checksum'],
                               'path': i[1]['path'],
                               'url': i[1]['url']
                               } for i in results if results[0]]
        return item

    def file_path(self, request, response=None, info=None, item=None):
        image_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        folder = f'{item["name"].replace(" ", "_").replace(",", "").replace(".", "")}'[:128]
        return f'{folder}/{image_guid}.jpg'
