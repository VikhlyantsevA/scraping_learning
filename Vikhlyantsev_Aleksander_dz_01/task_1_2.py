# Задание 2
'''
Изучить список открытых API (https://www.programmableweb.com/category/all/apis).
Найти среди них любое, требующее авторизацию (любого типа).
Выполнить запросы к нему, пройдя авторизацию.
Ответ сервера записать в файл.
'''
import urllib
import requests
import json
import os
from dotenv import load_dotenv


load_dotenv()


class GithubApiParser:
    def __init__(self, host='https://api.github.com'):
        self.host = host
        self.__token = os.getenv('API_TOKEN')

    def get_response(self, endpoint, **kwargs):
        url = urllib.parse.urljoin(self.host, endpoint)
        headers = {'Authorization': f'token {self.__token}'}
        response = requests.get(url, headers=headers, **kwargs)
        if not response.ok:
            raise Exception(f'Wrong response: {response.status_code}.\n{response.text}')
        return response.json()



if __name__ == '__main__':
    # Можно добавлять другие endpoint-ы чтобы парсить разные данные
    endpoints = {'users': '/users'}
    gh_parser = GithubApiParser()
    # Прерыватель процесса записи
    breaker = 100
    params = {
        'per_page': 100,
        'since': 0
    }

    with open('github_users.json', 'w', encoding='utf-8') as fw:
        for page in range(breaker):
            json_content = gh_parser.get_response(endpoints['users'], params=params)
            if not json_content:
                break
            json.dump(json_content, fw, ensure_ascii=False, indent=2)
            params['since'] = max(map(lambda x: x['id'], json_content))
