# Изучить список открытых API (https://www.programmableweb.com/category/all/apis).
# Найти среди них любое, требующее авторизацию (любого типа).
# Выполнить запросы к нему пройдя авторизацию.
# Ответ сервера записать в файл.
#

import requests


baseurl = 'https://api.hh.ru/'
# получение токена авторизации
headers = {
    'User-Agent': 'MyScarpingJob',
    'Content-Type': 'application/x-www-form-urlencoded'
}
data = {
    'grand_type': 'client_credentials',
    'client_id': '0000',
    'client_secret': '0000'
}

response = requests.post(baseurl + 'oauth/token', data=data, headers=headers)
response_json = response.json()
access_token = response_json['access_token']

# Получение списка вакансий по запросу Data Scientist
headers = {
    'User-Agent': 'MyScarpingJob',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Authorization': 'Bearer ' + access_token
}
data = {
    'text': 'Data Scientist',
    'experience': 'noExperience',
    'employment': 'full',
    'schedule': 'remote',
    'industry': '7'
}

response = requests.get(url=baseurl + 'vacancies', data=data, headers=headers)
