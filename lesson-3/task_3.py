# Урок 3. Системы управления базами данных MongoDB и SQLite в Python
# 1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию, записывающую собранные
# вакансии в созданную БД.
# 2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введённой суммы.
# 3. Написать функцию, которая будет добавлять в вашу базу данных только новые вакансии с сайта.
#


import requests
from pymongo import MongoClient, TEXT
import pprint
from scarping_tools import scarp_vacancy_hh, scarp_vacancy_sjob


# База данных развернута локально на ПК, параметры доступа по умолчанию

def db_insert_vacancy(client_: MongoClient, data_):
    #
    # Запись значений в БД с проверкой уже существующих в ней
    # data_ - list данных в формате json
    #
    db = client_['vacancies']
    vacancy = db['vacancy']

    counter = 0
    for item in data_:
        # Поиск соответствующей вакансии по url
        test = vacancy.find_one({'url': item['url']})

        if test is None:
            vacancy.insert_one(item)
            counter += 1

    print(f'Из {len(data_)} вакансий переданных в db_insert_vacancy()\n\t{counter} добавлено в базу данных'
          f'\n\t{len(data_)-counter} совпадают с имеющимися в базе данных')


def db_find_vacancy(client_: MongoClient, title_='', city_='', salary_=0, salary_sign_=''):
    #
    # Поиск вакансии в БД по заданным параметрам
    # Дополнение по зарплате:
    #   more - найти вакансии с зарплатой больше, чем указана в salary_
    #   less - найти вакансии с зарплатой меньше, чем указана в salary_
    #   equ - найти вакансии с зарплатой как указана в salary_
    #
    assert salary_sign_ in ['', 'more', 'less', 'equ'], f"salary_sign_ most be in ['more', 'less', 'equ'], " \
                                                        f"but received {salary_sign_}"
    # assert title_ != '' and city_ != '' and salary_ != '', 'At least one parameter must be passed to the function'

    db = client_['vacancies']
    vacancy = db['vacancy']

    # Создаём базовые элементы для поиска по db
    list_params = []
    if title_ != '':
        vacancy.create_index([('title', TEXT)], default_language='russian')
        list_params.append({'$text': {'$search': title_}})
    if city_ != '':
        list_params.append({'city': city_})
    if salary_ != 0:
        if salary_sign_ == 'more':
            list_params.append({'$or': [{'salary': {'$gte': salary_}},
                                        {'salary_max': {'$gte': salary_}},
                                        {'salary_min': {'$gte': salary_}}]
                                })
        elif salary_sign_ == 'less':
            list_params.append({'$or': [{'salary': {'$lte': salary_}},
                                        {'salary_max': {'$lte': salary_}},
                                        {'salary_min': {'$lte': salary_}}]
                                })
        elif salary_sign_ == 'equ' or salary_sign_ == '':
            list_params.append({'$or': [{'salary': {'$eq': salary_}},
                                        {'$and': [{'salary_max': {'$gte': salary_}},
                                                  {'salary_min': {'$lte': salary_}}]
                                         }]
                                })
    if len(list_params) > 1:
        result = vacancy.find({'$and': list_params})
    else:
        result = vacancy.find(list_params[0])
    return result


# Получение актуальных данных с hh.ru и superjob.ru
vacancy_title = 'Data Scientist'
vacancy = scarp_vacancy_hh('Data Scientist')
vacancy.extend(scarp_vacancy_sjob('Data Scientist'))

# Подключение к локальной БД и запись данных
client = MongoClient('mongodb://localhost:27017/')
db_insert_vacancy(client, vacancy)

# Поиск по заданным критериям
find = db_find_vacancy(client, salary_=40000, salary_sign_='more')
if find.count() > 0:
    for item in find:
        pprint.pprint(item)
else:
    print(f'По запросу в БД ничего не найдено...')

client.close()
