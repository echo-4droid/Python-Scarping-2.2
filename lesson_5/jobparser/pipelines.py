# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
import re


class JobparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_db = client['vacancy_14_09_21']

    def process_item(self, item, spider):
        collection = self.mongo_db[spider.name]
        if spider.name == 'hhru':
            self.process_salary_hh(item)
        elif spider.name == 'superjobru':
            self.process_salary_sj(item)
        else:
            print(f'Oops! spider {spider.name} not found in pipelines')
        del item['salary']

        # Избегаем повторений в БД
        if collection.find_one({'url': item['url']}):
            return None
        else:
            return collection.insert_one(item)

    def process_salary_hh(self, item):
        salary = item['salary'].replace('\xa0', '').replace('\u202f', '')  # замена неразрывного пробела

        salary_up, salary_from, currency = None, None, None
        if 'до' in salary and 'от' in salary:
            salary_from = int(salary.split(' ')[1])
            salary_up = int(salary.split(' ')[3])
            currency = salary.split(' ')[-1]
        elif 'от' in salary:
            salary_from = int(salary.split(' ')[1])
            currency = salary.split(' ')[-1]
        elif 'до' in salary:
            salary_up = int(salary.split(' ')[1])
            currency = salary.split(' ')[-1]

        item['salary_from'] = salary_from
        item['salary_up'] = salary_up
        item['currency'] = currency

    def process_salary_sj(self, item):
        salary = ' '.join(item['salary'])
        salary = salary.replace('\xa0', '').replace('\u202f', '')  # замена неразрывного пробела
        salary = salary.split('/')[0].strip()   # удаление '/месяц' и пробелов в начале и конце строки
        salary = re.sub('\s+', ' ', salary)  # удаление повторяющихся пробельных символов в строке

        salary_up, salary_from, currency = None, None, None
        if 'от ' in salary:
            salary_from = int(re.sub('\D', '', salary.split(' ')[1]))
            currency = salary.split(' ')[-1] if len(salary.split(' ')) > 2 else re.sub('\d', '', salary.split(' ')[-1])
        elif 'до ' in salary:
            salary_up = int(re.sub('\D', '', salary.split(' ')[1]))
            currency = salary.split(' ')[-1] if len(salary.split(' ')) > 2 else re.sub('\d', '', salary.split(' ')[-1])
        elif '—' in salary:
            temp_list = salary.split('—')
            salary_from = int(temp_list[0].split(' ')[0])
            salary_up = int(re.sub('\D', '', temp_list[1].split(' ')[1]))
            currency = temp_list[1].split(' ')[-1] if len(temp_list[1].split(' ')) > 2 else re.sub('\d', '', temp_list[1].split(' ')[-1])
        elif 'договорённости' in salary:
            pass
        else:
            salary_up = int(salary.split(' ')[0])
            currency = salary.split(' ')[-1] if len(salary.split(' ')) > 2 else re.sub('\d', '', salary.split(' ')[-1])

        item['salary_from'] = salary_from
        item['salary_up'] = salary_up
        item['currency'] = currency

