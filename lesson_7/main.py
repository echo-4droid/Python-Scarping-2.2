# Вариант I
# Написать программу, которая собирает входящие письма из своего или тестового почтового ящика и сложить данные
# о письмах в базу данных (от кого, дата отправки, тема письма, текст письма полный)
#   Логин тестового ящика: study.ai_172@mail.ru
#   Пароль тестового ящика: NextPassword172???
#
# Вариант II
# Написать программу, которая собирает «Новинки» с сайта техники mvideo и складывает данные в БД. Сайт можно выбрать
# и свой. Главный критерий выбора: динамически загружаемые товары
#
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait as WDW
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
from pymongo import MongoClient
from datetime import datetime
import re


def parse_mail():
    mongo_db = MongoClient('localhost', 27017)['lesson_6']
    collection = mongo_db['mailru' + datetime.today().strftime('_on_%d_%m_%Y')]

    driver = webdriver.Firefox()
    driver.maximize_window()
    driver.get('https://mail.ru/')

    # Авторизация
    # Логин
    form = WDW(driver, 5).until(
        EC.element_to_be_clickable((By.NAME, 'login'))
    )
    form.send_keys('study.ai_172@mail.ru')
    # Чекбокс "запомнить"
    button = WDW(driver, 5).until(
        EC.element_to_be_clickable((By.NAME, 'saveauth'))
    )
    button.click()
    # Кнопка "ввести пароль"
    button = WDW(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, '//button[contains(@data-testid, "enter-password")]'))
    )
    button.click()
    # Пароль
    form = WDW(driver, 5).until(
        EC.element_to_be_clickable((By.NAME, 'password'))
    )
    form.send_keys('NextPassword172???')
    # Кнопка "войти"
    button = WDW(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, '//button[contains(@data-testid, "login-to-mail")]'))
    )
    button.click()

    # Переход в первое письмо в первое письмо
    button = WDW(driver, 20).until(
        EC.visibility_of_element_located((By.XPATH, '//a[contains(@class, "js-letter-list-item")]'))
    )
    driver.get(button.get_attribute('href'))

    while True:
        from_user = WDW(driver, 10).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, 'span.letter-contact'))
                    ).get_attribute('title')
        sent_date = WDW(driver, 10).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.letter__date'))
                    ).text
        subject = WDW(driver, 10).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, 'h2.thread__subject'))
                    ).text
        text = WDW(driver, 10).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.letter-body'))
                    ).text
        text = re.sub('^\s+', '', re.sub('\s{2,}', ' ', text))

        collection.insert_one({
            'from_user': from_user,
            'sent_date': sent_date,
            'subject': subject,
            'text': text
        })
        # К следующему письму
        try:
            button = WDW(driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//span[contains(@title, "Следующее")] | //span[contains(@data-title, "Следующее")]')
                )
            )
            button.click()
            WDW(driver, 15).until(EC.url_changes(driver.current_url))
        except:
            print(f'С почтового ящика study.ai_172@mail.ru собрано {collection.count_documents()} писем')
            break

    # Завершение работы Selenium
    driver.quit()


def parse_mvideo():
    mongo_db = MongoClient('localhost', 27017)['lesson_6']
    collection = mongo_db['mvideo' + datetime.today().strftime('_on_%d_%m_%Y')]

    driver = webdriver.Firefox()
    driver.maximize_window()
    driver.get('https://www.mvideo.ru/')

    button = driver.find_element_by_xpath(
        '//h2[contains(text(), "Самые просматриваемые")]/../../..//a[contains(@class, "i-icon-fl-arrow-right")]'
    )
    # Товары ленты "Новинки" после загрузки также хранятся в переменной impressions в формате JSON
    goods, goods_len = driver.execute_script('return impressions;'), 0
    while goods_len < len(goods):
        goods_len = len(goods)
        button.click()
        sleep(5)
        goods = driver.execute_script('return impressions;')

    if goods:
        collection.insert_many(goods)
    driver.quit()


if __name__ == '__main__':
    parse_mvideo()
    # parse_mail()
