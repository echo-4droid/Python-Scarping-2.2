# Просмотреть документацию к API GitHub,
# разобраться как вывести список репозиториев для конкретного пользователя,
# сохранить JSON-вывод в файле *.json
#

import requests
import json


username = 'ele-droid'
response = requests.get('https://api.github.com/users/' + username + '/repos')

for response_json in response.json():
    print(response_json['name'])

with open('task_1_repo.json', 'w', encoding='utf8') as f:
    json.dump(response.json(), f)
