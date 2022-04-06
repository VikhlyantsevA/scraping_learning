# Задание 1
'''
Посмотреть документацию к API GitHub.
Разобраться как вывести список наименований репозиториев для конкретного пользователя.
Сохранить JSON-вывод в файле *.json.
'''
import requests
import urllib
import json
import os
from dotenv import load_dotenv

load_dotenv()


def get_user_repo_info(username):
    host = 'https://api.github.com'
    endpoint = '/users/{name}/repos'
    url = urllib.parse.urljoin(host, endpoint.format(name=username))
    print('Try getting response without token')
    response = requests.get(url)
    if response.ok:
        print('SUCCESS')
    elif response.status_code == 403:
        print('FAIL', 'Try with token', sep='\n')
        token = os.getenv('API_TOKEN')
        headers = {'Authorization': f'token {token}'}
        response = requests.get(url, headers=headers)
    print(f'URL: {response.url}', f'Status: {response.status_code}', sep='\n', end='\n\n')
    return response.json()


if __name__ == '__main__':
    username = 'tcgmilan'
    json_content = get_user_repo_info(username)

    repo_names = [repo['name'] for repo in json_content]
    print(f'User_name: {username}',
          f'Repositories number: {len(repo_names)}',
          f'Repositories names: {repo_names}',
          sep='\n')

    with open('github_users_repos.json', 'w', encoding='utf-8') as fw:
        json.dump(json_content, fw, ensure_ascii=False, indent=2)
