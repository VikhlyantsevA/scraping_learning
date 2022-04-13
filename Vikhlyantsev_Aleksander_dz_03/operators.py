from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from abc import ABC, abstractmethod

from bs4 import BeautifulSoup as bs
from urllib.parse import urlencode, urljoin
import requests
import time
import re
from typing import List, Dict

from my_lib.utils import hash_struct


class WebsiteScrapper(ABC):
    def get_response(self, url: str, max_retries: int = 1, backoff_factor: float = 1, **kwargs):
        for retry in range(max_retries):
            response = requests.get(url, **kwargs)
            if response.ok:
                return response
            time.sleep(backoff_factor * (2 ** (retry - 1)))
        raise Exception(f'Status: {response.status_code}')

    @abstractmethod
    def parse_data(self, *args, **kwargs): ...

    def save_to_mongodb(self, database, collection, data: List[Dict]):
        client = MongoClient('localhost', 27017)
        db = client[database]
        collection = db[collection]
        for document in data:
            document_id = hash_struct(document)
            try:
                collection.insert_one({'_id': document_id, **document})
            except DuplicateKeyError:
                print(f'Document with key {document_id} already exists.')


class HHScrapper(WebsiteScrapper):
    def __init__(self,
                 user_agent: str,
                 base_url: str = 'https://hh.ru',
                 endpoint: str = '/search/vacancy'):
        self._headers = {'user-agent': user_agent}
        self._base_url = base_url
        self._endpoint = endpoint

    def parse_data(self, search_params: dict, limit: int = None, **kwargs):
        max_retries = kwargs.get('max_retries', 8)
        headers = kwargs.get('headers', self._headers)
        url = f"{urljoin(self._base_url, self._endpoint)}?{urlencode(search_params)}"
        limit = int(limit) if limit else None
        page = 1
        while True:
            print(f'Getting data from: {url}')
            page_res = list()
            response = self.get_response(url=url, max_retries=max_retries, headers=headers)

            dom = bs(response.text, 'html.parser')
            resume_windows = dom.find_all('div', {'class': 'vacancy-serp-item'})
            for resume in resume_windows:
                title = resume.find('a', {'data-qa': 'vacancy-serp__vacancy-title'})
                if not title:
                    continue
                position = title.getText()
                resume_url = title['href']
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

                    salaries_info = {k: (v if not v else float(v) if v.isnumeric() else v.lower()) for k, v in
                                     match.groupdict().items()}

                page_res.append({
                    'position': position,
                    'salary_info': salaries_info,
                    'resume_url': resume_url,
                    'website_url': url
                })

            self.save_to_mongodb('vacancies', 'hh', page_res)

            if limit:
                if page >= limit:
                    return

            next_page = dom.find('a', {'class': 'bloko-button', 'data-qa': 'pager-next'})
            if not next_page:
                return

            url = urljoin(self._base_url, next_page['href'])
            page += 1
