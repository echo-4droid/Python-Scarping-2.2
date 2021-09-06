# Необходимо собрать информацию о вакансиях на вводимую должность (используем input или через аргументы) с сайтов
# Superjob и HH. Приложение должно анализировать несколько страниц сайта (также вводим через input или аргументы).
# Получившийся список должен содержать в себе минимум:
#   Наименование вакансии.
#   Предлагаемую зарплату (отдельно минимальную и максимальную).
#   Ссылку на саму вакансию.
#   Сайт, откуда собрана вакансия.
#
# По желанию можно добавить ещё параметры вакансии (например, работодателя и расположение). Структура должна быть
# одинаковая для вакансий с обоих сайтов. Общий результат можно вывести с помощью dataFrame через pandas.
#

import datetime
import requests
import pandas as pd
from bs4 import BeautifulSoup, Tag


def scarp_vacancy(title: str):
    vacancy_hh = scarp_vacancy_hh(title)
    vacancy_sjob = scarp_vacancy_sjob(title)

    vacancy_hh.extend(vacancy_sjob)
    df = pd.DataFrame(vacancy_hh)
    df.to_csv('vacancy.csv', index=False)

    with open('vacancy.csv', 'r') as f:
        if f.readable():
            print('\nСобранные вакансии успешно записаны в vacancy.csv')
        else:
            print('\nНе удалось записать найденные вакансии в vacancy.csv')


def scarp_vacancy_hh(title_: str):
    base_url = 'https://hh.ru/search/vacancy'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; arm_64; Android 11; Redmi Note 8 Pro) AppleWebKit/537.36 (KHTML, like '
                      'Gecko) Chrome/86.0.4240.198 YaBrowser/20.11.3.88.00 SA/3 Mobile Safari/537.36',
        'Accept-Charset': 'utf-8',
        'Accept-Language': 'ru'
    }
    params = {
        'st': 'searchVacancy',
        'text': title_,
        'salary': '',
        'currency_code': 'RUR',
        'experience': 'noExperience',
        'employment': ['full', 'part', 'probation'],
        'schedule': ['fullDay', 'flexible', 'remote'],
        'order_by': 'relevance',
        'search_period': '0',
        'items_on_page': '20',
        'no_magic': 'true',
        'L_save_area': 'true',
        'page': '1'
    }

    print(f'\nЗапрос на {base_url}')
    response = requests.get(url=base_url, headers=headers, params=params)
    if not response.ok:
        print(f'Получен ответ сервера {response.status_code} на запрос \n{response.url} в функции scarp_vacancy_hh()')
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    # Определение количества страниц по результатам данного запроса
    vacancy_count = str.replace(soup.find('h1', attrs={'data-qa': 'bloko-header-3'}).text, '\xa0', '')
    vacancy_count = int(str.split(vacancy_count, ' ')[0])
    page_count = vacancy_count // 20 + 1 if vacancy_count % 20 > 0 else 0
    print(f'vacancy_count = {vacancy_count}', f'page_count = {page_count}')

    vacancy_hh = []
    # парсинг каждой страницы поочерёдно
    for i in range(0, page_count):
        params['page'] = i
        print(f'Запрос на {base_url}, page={i}')
        response = requests.get(url=base_url, headers=headers, params=params)
        if not response.ok:
            print(f'Получен ответ сервера {response.status_code} на запрос \n{response.url}\n В функции '
                  f'scarp_vacancy_hh()')
            break

        soup = BeautifulSoup(response.text, 'html.parser')

        for item in soup.select('div.vacancy-serp-item'):
            title = item.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-title'}).text
            url = item.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-title'})['href']
            city = item.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-address'}).text
            requirement = item.find('div', attrs={'data-qa': 'vacancy-serp__vacancy_snippet_requirement'}).text
            date_publication = item.find('span', attrs={'class': 'vacancy-serp-item__publication-date_long'}).text

            if item.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'}) is not None:
                salary = item.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'}).text
            else:
                salary = 'Не указана'
            if item.find('div', attrs={'data-qa': 'vacancy-serp__vacancy_snippet_responsibility'}) is not None:
                responsibility = item.find('div',
                                           attrs={'data-qa': 'vacancy-serp__vacancy_snippet_responsibility'}).text
            else:
                responsibility = 'Не указаны'

            vacancy_hh.append(
                {
                    'title': title,
                    'site': 'https://hh.ru/',
                    'url': url,
                    'salary': salary,
                    'city': city,
                    'responsibility': responsibility,
                    'requirement': requirement,
                    'date_publication': date_publication
                })
    print(f'В результате скарпинга hh.ru получено {len(vacancy_hh)} вакансий')
    return vacancy_hh


def scarp_vacancy_sjob(title_: str):
    base_url = 'https://russia.superjob.ru/vakansii/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; arm_64; Android 11; Redmi Note 8 Pro) AppleWebKit/537.36 (KHTML, like '
                      'Gecko) Chrome/86.0.4240.198 YaBrowser/20.11.3.88.00 SA/3 Mobile Safari/537.36',
        'Accept-Charset': 'utf-8',
        'Accept-Language': 'ru'
    }
    params = {
        'page': ''
    }
    months = {
        '01': 'января',
        '02': 'февраля',
        '03': 'марта',
        '04': 'апреля',
        '05': 'мая',
        '06': 'июня',
        '07': 'июля',
        '08': 'августа',
        '09': 'сентября',
        '10': 'октября',
        '11': 'ноября',
        '12': 'декабря'
    }
    dt = datetime.datetime.now()

    print(f'\nЗапрос на {base_url}')
    response = requests.get(url=base_url + '-'.join(title_.split(' ')) + '.html', headers=headers, params=params)
    if not response.ok:
        print(f'Получен ответ сервера {response.status_code} на запрос \n{response.url} в функции scarp_vacancy_sjob()')
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    # Определение количества страниц по результатам данного запроса
    vacancy_count = soup.select('h2 span')
    vacancy_count = int(vacancy_count[0].text.split(' ')[1]) if len(vacancy_count) > 0 else 0
    page_count = vacancy_count // 20 + 1 if vacancy_count % 20 > 0 else 0
    print(f'vacancy_count = {vacancy_count}', f'page_count = {page_count}')

    vacancy = []
    # парсинг каждой страницы поочерёдно
    for i in range(1, page_count + 1):
        params['page'] = i
        print(f'Запрос на {base_url}, page={i}')
        response = requests.get(url=base_url + '-'.join(title_.split(' ')) + '.html', headers=headers, params=params)
        if not response.ok:
            print(f'Получен ответ сервера {response.status_code} на запрос \n{response.url}\n В функции '
                  f'scarp_vacancy_sjob()')
            break

        soup = BeautifulSoup(response.text, 'html.parser')

        for item in soup.select('div.f-test-vacancy-item'):
            title = item.select('div._2g1F- div div div a')[0].text
            url = 'https://www.superjob.ru' + item.select('div._2g1F- div div div a')[0]['href']
            city = item.select('span.f-test-text-company-item-location span')[2].text

            soup_part = item.select('div.HSTPm span')[0]
            if len(soup_part.select('div')):
                soup_part.div.extract()
            requirement = ''.join(
                [i.text if isinstance(i, Tag) else i for i in soup_part.select('br')[0].next_siblings])
            responsibility = ''.join(
                [i.text if isinstance(i, Tag) else i for i in soup_part.select('br')[0].previous_siblings])

            # Из-за особенностей SuperJob необходимо сразу привести время в единообразную форму
            date_publication = item.select('span.f-test-text-company-item-location span')[0].text
            if date_publication == 'Вчера':
                date_publication = str(int(dt.strftime('%d')) - 1) + ' ' + months[dt.strftime('%m')]
            elif ':' in date_publication:
                date_publication = str(int(dt.strftime('%d'))) + ' ' + months[dt.strftime('%m')]

            salary = item.select('span.f-test-text-company-item-salary span')[0].text

            vacancy.append(
                {
                    'title': title,
                    'site': 'https://www.superjob.ru/',
                    'url': url,
                    'salary': salary,
                    'city': city,
                    'responsibility': responsibility,
                    'requirement': requirement,
                    'date_publication': date_publication
                })

    print(f'В результате скарпинга superjob.ru получено {len(vacancy)} вакансий')
    return vacancy


scarp_vacancy('Data scientist')
