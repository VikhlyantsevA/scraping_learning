# Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию, которая будет добавлять
# только новые вакансии/продукты в вашу базу.

from my_lib.operators.parse_utils import HHScrapper

if __name__ == '__main__':
    search_params = [
        ('area', 'Moscow'),
        ('experience', 'between1And3'),
        ('search_field', 'name'),
        ('search_field', 'company_name'),
        ('search_field', 'description'),
        ('text', 'data analyst')
    ]

    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36'

    hh_scrapper = HHScrapper(user_agent)
    hh_scrapper.parse_data(search_params, limit=3)
