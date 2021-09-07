import re
import datetime
import requests
from bs4 import BeautifulSoup, Tag


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

    vacancy = []
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
            date_publication = item.find('span', attrs={'class': 'vacancy-serp-item__publication-date_long'}).text

            # salary and currency
            if item.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'}) is not None:
                currency_str = item.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'}).text
                salary_str = currency_str.replace('\xa0', '').replace('\u202f', '')  # замена неразрывного пробела

                salary, salary_max, salary_min = 0, 0, 0
                if 'от' in salary_str:
                    salary_min = int(salary_str.split(' ')[1])
                elif 'до' in salary_str:
                    salary_max = int(salary_str.split(' ')[1])
                elif '–' in salary_str:
                    temp_list = salary_str.split('–')
                    salary_min = int(temp_list[0].split(' ')[0])
                    salary_max = int(temp_list[1].split(' ')[1])
                else:
                    salary = int(salary_str.split(' ')[0])

                currency = currency_str.split(' ')[-1]
            else:
                salary, salary_max, salary_min = 0, 0, 0
                currency = None

            # responsibility
            if item.find('div', attrs={'data-qa': 'vacancy-serp__vacancy_snippet_responsibility'}) is not None:
                responsibility = item.find('div',
                                           attrs={'data-qa': 'vacancy-serp__vacancy_snippet_responsibility'}).text
            else:
                responsibility = 'Не указаны'

            # requirement
            if item.find('div', attrs={'data-qa': 'vacancy-serp__vacancy_snippet_requirement'}) is not None:
                requirement = item.find('div', attrs={'data-qa': 'vacancy-serp__vacancy_snippet_requirement'}).text
            else:
                requirement = 'Не указаны'

            vacancy.append(
                {
                    'title': title,
                    'site': 'https://hh.ru/',
                    'url': url,
                    'salary': salary,
                    'salary_min': salary_min,
                    'salary_max': salary_max,
                    'currency': currency,
                    'city': city,
                    'responsibility': responsibility,
                    'requirement': requirement,
                    'date_publication': date_publication
                })
    print(f'В результате скарпинга hh.ru получено {len(vacancy)} вакансий')
    return vacancy


def scarp_vacancy_sjob(title_: str):
    base_url = 'https://russia.superjob.ru/vacancy/search/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; arm_64; Android 11; Redmi Note 8 Pro) AppleWebKit/537.36 (KHTML, like '
                      'Gecko) Chrome/86.0.4240.198 YaBrowser/20.11.3.88.00 SA/3 Mobile Safari/537.36',
        'Accept-Charset': 'utf-8',
        'Accept-Language': 'ru'
    }
    params = {
        'keywords': title_,
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
    response = requests.get(url=base_url, headers=headers, params=params)
    if not response.ok:
        print(f'Получен ответ сервера {response.status_code} на запрос \n{response.url} в функции scarp_vacancy_sjob()')
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    # Определение количества страниц по результатам данного запроса
    vacancy_count = soup.select('h2 span')
    if len(vacancy_count) > 0:
        vacancy_count = int(vacancy_count[0].text.split(' ')[1].replace('\xa0', '').replace('\u202f', ''))
    else:
        vacancy_count = 0
    page_count = vacancy_count // 20 + 1 if vacancy_count % 20 > 0 else 0
    print(f'vacancy_count = {vacancy_count}', f'page_count = {page_count}')

    vacancy = []
    # парсинг каждой страницы поочерёдно
    for i in range(1, page_count + 1):
        params['page'] = i
        print(f'Запрос на {base_url}, page={i}')
        response = requests.get(url=base_url, headers=headers, params=params)
        if not response.ok:
            print(f'Получен ответ сервера {response.status_code} на запрос \n{response.url}\n В функции '
                  f'scarp_vacancy_sjob()')
            break

        soup = BeautifulSoup(response.text, 'html.parser')

        for item in soup.select('div.f-test-vacancy-item'):
            title = item.select('div._2g1F- div div div a')[0].text
            url = 'https://www.superjob.ru' + item.select('div._2g1F- div div div a')[0]['href']
            city = item.select('span.f-test-text-company-item-location span')[2].text

            # requirement and responsibility
            soup_part = item.select('div.HSTPm span')[0]
            if len(soup_part.select('div')):
                soup_part.div.extract()
            requirement = ''.join(
                [i.text if isinstance(i, Tag) else i for i in soup_part.select('br')[0].next_siblings])
            responsibility = ''.join(
                [i.text if isinstance(i, Tag) else i for i in soup_part.select('br')[0].previous_siblings])

            # date_publication
            # Из-за особенностей SuperJob необходимо сразу привести время в единообразную форму
            date_publication = item.select('span.f-test-text-company-item-location span')[0].text
            if date_publication == 'Вчера':
                date_publication = str(int(dt.strftime('%d')) - 1) + ' ' + months[dt.strftime('%m')]
            elif ':' in date_publication:
                date_publication = str(int(dt.strftime('%d'))) + ' ' + months[dt.strftime('%m')]

            # salary
            currency_str = item.select('span.f-test-text-company-item-salary span')[0].text
            salary_str = currency_str.replace('\xa0', '').replace('\u202f', '')  # замена неразрывного пробела
            salary, salary_max, salary_min = 0, 0, 0
            if 'от' in salary_str:
                salary_min = int(re.sub('\D', '', salary_str))
            elif 'до' in salary_str and re.match('\d', salary_str[2:]) is not None:
                salary_max = int(re.sub('\D', '', salary_str))
            elif '—' in salary_str:
                temp_list = salary_str.split('—')
                salary_min = int(re.sub('\D', '', temp_list[0]))
                salary_max = int(re.sub('\D', '', temp_list[1]))
            elif re.match('\d', salary_str) is not None:
                salary = int(re.sub('\D', '', salary_str))
            else:
                salary = salary_str

            # currency
            if re.match('\d', salary_str) or re.match('\d', salary_str[2:]):
                currency = currency_str.split('\xa0')[-1]
            else:
                currency = None

            vacancy.append(
                {
                    'title': title,
                    'site': 'https://www.superjob.ru/',
                    'url': url,
                    'salary': salary,
                    'salary_min': salary_min,
                    'salary_max': salary_max,
                    'currency': currency,
                    'city': city,
                    'responsibility': responsibility,
                    'requirement': requirement,
                    'date_publication': date_publication
                })

    print(f'В результате скарпинга superjob.ru получено {len(vacancy)} вакансий')
    return vacancy
