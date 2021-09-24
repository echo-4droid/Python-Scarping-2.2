# Урок 8
# В ранее написанное приложение добавить класс с функциями, которые позволят собрать открытые данные по выбранной теме
# при помощи Python с сайта (выберите из списка известных источников данных).
#
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait as WDW
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
import wget
import multiprocessing


if __name__ == '__main__':
    driver = webdriver.Firefox()
    driver.maximize_window()
    driver.get('https://data.gov.ru/opendata')

    form = WDW(driver, 5).until(
        EC.element_to_be_clickable((By.ID, 'edit-query'))
    )
    form.send_keys('Федеральный список экстремистских материалов')
    element = WDW(driver, 5).until(
        EC.element_to_be_clickable((By.ID, 'edit-submit-datasets-search'))
    )
    sleep(1)
    element.click()
    sleep(1)
    WDW(driver, 20).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, 'throbber')))

    element = WDW(driver, 5).until(
        EC.visibility_of_element_located((By.XPATH, '//div[contains(@class, "field-items")]//a'))
    )
    driver.get(element.get_attribute('href'))

    urls = driver.find_elements_by_css_selector('div.download a')
    if urls:
        # попробовал многопоточность
        if multiprocessing.cpu_count() < len(urls):
            for url in urls:
                wget.download(url.get_attribute('href'))
        else:
            processes = []
            for url in urls:
                process = multiprocessing.Process(target=wget.download, args=(url.get_attribute('href'), ''))
                process.start()
                processes.append(process)

            for p in processes:
                p.join()

    # Завершение работы Selenium
    driver.quit()
