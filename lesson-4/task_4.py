#
# Написать приложение, которое собирает основные новости с сайтов mail.ru, lenta.ru, yandex-новости.
# Для парсинга использовать XPath. Структура данных должна содержать:
#   - название источника;
#   - наименование новости;
#   - ссылку на новость;
#   - дата публикации.
#

import requests
import datetime
from lxml import html
import pandas as pd


def date_time_translate(dt_str: str):
    #
    # Преобразование даты и времени из строки
    # lenta.ru
    #     01:36
    #     20:29, 9 сентября 2021
    #     3 августа 2021
    #     Сегодня
    #
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
    time, date = None, None

    if len(dt_str) < 6 and ':' in dt_str:  # 01:36
        time = dt_str
        date = ' '.join(
            ((str(int(dt.strftime('%d')))),
             months[dt.strftime('%m')],
             dt.strftime('%Y'))
        )
    elif ',' in dt_str:  # 20:29, 9 сентября 2021
        time, date = dt_str.split(', ')
    elif 'егодня' in dt_str:  # Сегодня
        time = None
        date = ' '.join(
            ((str(int(dt.strftime('%d')))),
             months[dt.strftime('%m')],
             dt.strftime('%Y'))
        )
    elif len(dt_str.split(' ')[-1]) == 4:  # 3 августа 2021
        time = None
        date = dt_str

    return time, date


def scarp_lenta_news(headers_: dict):
    base_url = 'https://lenta.ru/'

    print(f'\nЗапрос GET на {base_url}')
    response = requests.get(url=base_url, headers=headers_)
    if not response.ok:
        print(
            f'Получен ответ сервера {response.status_code} на запрос GET по адресу \n{response.url} '
            f'в функции scarp_lenta_news()')
        return None

    root = html.fromstring(response.text)
    news = []

    # Парсинг первого блока новостей
    topics = root.xpath('//li[@class="main-header__topics-list-item"]')
    #     print(len(topics))
    for item in topics:
        url = item.xpath('.//a[@class="card-mini"]/@href')[0]
        title = item.xpath('.//div[@class="card-mini__title"]/text()')[0]
        date_time_str = item.xpath('.//time[@class="card-mini__date"]/text()')[0]
        time, date = date_time_translate(date_time_str)

        news.append({
            'source': base_url,
            'title': title,
            'url': url if 'http' in url else base_url[:-1] + url,
            'time': time,
            'date': date
        })

    # Парсинг второго блока новостей, элементы типа _mini и _big
    topics = root.xpath('//li[@class="tabloid__item _big"] | //li[@class="tabloid__item _mini"]')
    #     print(len(topics))
    for item in topics:
        url = item.xpath('./a/@href')[0]
        title = item.xpath(
            './/div[@class="card-big__info-block"]/span/text() | .//div[@class="card-mini__title"]/text()')
        date_time_str = \
            item.xpath('.//time[@class="card-big__date"]/text() | .//time[@class="card-mini__date"]/text()')[0]
        time, date = date_time_translate(date_time_str)

        news.append({
            'source': base_url,
            'title': title[0] if len(title) < 2 else ''.join(title),
            'url': url if 'http' in url else base_url[:-1] + url,
            'time': time,
            'date': date
        })

    # Парсинг второго блока новостей, элементы типа _photo
    topics = root.xpath('//li[@class="tabloid__item _photo"]')
    #     print(len(topics))
    for item in topics:
        url = item.xpath('./a/@href')[0]
        title = item.xpath('.//div[@class="card-feature__titles"]/span/text()')
        date_time_str = item.xpath('.//time[@class="card-feature__date"]/text()')[0]
        time, date = date_time_translate(date_time_str)

        news.append({
            'source': base_url,
            'title': title[0] if len(title) < 2 else ''.join(title),
            'url': url if 'http' in url else base_url[:-1] + url,
            'time': time,
            'date': date
        })

    return news


def scarp_mail_news(headers_: dict):
    def get_time(url_):
        # Для получения времени новости нужно запрашивать её страницу
        print(f'\nЗапрос GET на {url_}')
        response = requests.get(url=url_, headers=headers_)
        if not response.ok:
            print(
                f'Получен ответ сервера {response.status_code} на запрос GET по адресу \n{response.url} '
                f'в функции scarp_mail_news()')
            return None

        sub_root = html.fromstring(response.text)
        date_time_str = sub_root.xpath(
            '//meta[@property="article:published_time"]/@content')  # 2021-09-09T20:46:44+0300
        if len(date_time_str) == 0:
            return None, None
        else:
            return date_time_str[0].split('T')[1][:-8], date_time_str[0].split('T')[0]

    base_url = 'https://news.mail.ru/'
    print(f'\nЗапрос GET на {base_url}')
    response = requests.get(url=base_url, headers=headers_)
    if not response.ok:
        print(
            f'Получен ответ сервера {response.status_code} на запрос GET по адресу \n{response.url} '
            f'в функции scarp_mail_news()')
        return None

    root = html.fromstring(response.text)
    news = []

    # Парсинг первого блока новостей
    topics = root.xpath('//a[@class="item item_side_left entity"]')
    for item in topics:
        url = item.xpath('./@href')[0]
        url = url if 'http' in url else base_url[:-1] + url
        title = item.xpath('.//span[@class="item__title"]/span/text() | .//span[@class="item__text"]/text()')[0]
        time, date = get_time(url)

        news.append({
            'source': base_url,
            'title': title,
            'url': url if 'http' in url else base_url[:-1] + url,
            'time': time,
            'date': date
        })

    # Парсинг второго блока новостей
    topics = root.xpath('//div[@class="slider__item slider__item_photo js-slider__item"]')
    for item in topics:
        url = item.xpath('./div/a/@href')[0]
        url = url if 'http' in url else base_url[:-1] + url
        title = item.xpath('.//span[@class="photo__title"]/text()')[0]
        time, date = get_time(url)

        news.append({
            'source': base_url,
            'title': title,
            'url': url if 'http' in url else base_url[:-1] + url,
            'time': time,
            'date': date
        })

    return news


def scarp_yandex_news(headers_: dict):
    base_url = 'https://yandex.ru/news/'
    print(f'\nЗапрос GET на {base_url}')
    response = requests.get(url=base_url, headers=headers_)
    if not response.ok:
        print(
            f'Получен ответ сервера {response.status_code} на запрос GET по адресу \n{response.url} '
            f'в функции scarp_mail_news()')
        return None

    root = html.fromstring(response.text)
    news = []

    # Парсинг первого блока новостей
    topics = root.xpath('//article')
    print(len(topics))
    for item in topics:
        url = item.xpath('./h2/a/@href')[0]
        title = item.xpath('./h2/a/text()')[0]
        date_time_str = item.xpath('.//span[@class="mg-card-source__time"]/text()')[0]
        time, date = date_time_translate(date_time_str)

        news.append({
            'source': base_url,
            'title': title,
            'url': url if 'http' in url else base_url[:-1] + url,
            'time': time,
            'date': date
        })

    return news


headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; arm_64; Android 11; Redmi Note 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/86.0.4240.198 YaBrowser/20.11.3.88.00 SA/3 Mobile Safari/537.36',
    'Accept-Charset': 'utf-8',
    'Accept-Language': 'ru'
}

today_news = scarp_lenta_news(headers)
# today_news.extend(scarp_mail_news(headers)) # из-за запросов get к странице каждой новости работает долго
today_news.extend(scarp_yandex_news(headers))
df = pd.DataFrame(today_news)
print(df.describe())
print(df.tail())
