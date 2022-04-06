import re
from bs4 import BeautifulSoup as bs
import requests
import time
from urllib.parse import urlencode, urljoin
import json
from tabulate import tabulate
from IPython.display import display
import pandas as pd

pd.set_option('display.max_columns', 20)
pd.set_option('display.max_colwidth', 100)


def get_response(url, max_retries=1, backoff_factor=1, **kwargs):
    for retry in range(max_retries):
        response = requests.get(url, **kwargs)
        if response.ok:
            return response
        time.sleep(backoff_factor * (2 ** (retry - 1)))
    raise Exception(f'Status: {response.status_code}')


if __name__ == '__main__':
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36'}
    base_url = 'https://hh.ru'

    params = [
        ('area', 'Moscow'),
        ('experience', 'between1And3'),
        ('search_field', 'name'),
        ('search_field', 'company_name'),
        ('search_field', 'description'),
        ('text', 'data analyst')
    ]

    url = f"{urljoin(base_url, '/search/vacancy')}?{urlencode(params)}"

    # Ограничение по количеству страниц для парсинга
    # Если не ввести ничего, спарсятся все страницы
    limit = input('Введите число страниц для парсинга: ')
    limit = int(limit) if limit else None

    page = 1
    res = list()
    while True:
        print(url)
        response = get_response(url, max_retries=8, headers=headers)

        dom = bs(response.text, 'html.parser')

        resume_windows = dom.find_all('div', {'class': 'vacancy-serp-item'})
        for resume in resume_windows:
            title = resume.find('a', {'data-qa': 'vacancy-serp__vacancy-title'})
            resume_url = title['href']
            position = title.getText()
            salaries_info = resume.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
            if salaries_info:
                salaries_info_text = salaries_info.getText().replace('\u202f', '').replace(' ', '')
                pattern_1 = re.compile('(?:(?P<min_salary>\d+)–)?(?P<max_salary>\d+)(?P<currency>\D+)')
                pattern_2 = re.compile('(?:от(?P<min_salary>\d+))?(?:до(?P<max_salary>\d+))?(?P<currency>\D+)',
                                       re.I | re.X)
                patterns = [pattern_1, pattern_2]
                for i, pattern in enumerate(patterns):
                    match = pattern.match(salaries_info_text)
                    if match:
                        break
                    elif not match and i == len(patterns) - 1:
                        raise Exception(f"There is a new pattern.\nSalaries info (text):{salaries_info_text}")

                salaries_info = {k: (v if not v else float(v) if v.isnumeric() else v) for k, v in
                                 match.groupdict().items()}

            res.append({
                'position': position,
                'salary_info': salaries_info,
                'resume_url': resume_url,
                'website_url': url
            })

        next_page = dom.find('a', {'class': 'bloko-button', 'data-qa': 'pager-next'})

        if limit:
            if page >= limit:
                break

        if not next_page:
            break

        url = urljoin(base_url, next_page['href'])
        page += 1

    df = pd.DataFrame(data=res)
    # # Вывод результата в виде пандасовской таблицы (красиво отображается в JupyterNotebook)
    # display(df.head(10))

    # Для отображения в табличном виде (дэшборд) в PyCharm, можно использовать пакет tabulate
    print(tabulate(df.head(10), headers='keys', tablefmt='psql', missingval='None'))

    with open('hh_jobs.json', 'w', encoding='utf-8') as fw:
        json.dump(res, fw, ensure_ascii=False, indent=2)
