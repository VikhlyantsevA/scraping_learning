from urllib.parse import urljoin, urlparse
from lxml import html
from datetime import datetime
import requests
import locale

from my_lib.operators.db_utils import MongodbUtils


if __name__ == '__main__':
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
    m_utils = MongodbUtils()

    base_url = 'https://lenta.ru/'

    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'}
    news_response = requests.get(base_url, headers=headers)
    news_dom = html.fromstring(news_response.text)

    topnews_cards = news_dom.xpath('//div[contains(@class, "topnews")]//a[contains(@class, "card")]')
    for news_card in topnews_cards:
        url_raw = news_card.xpath('./@href')[0]
        url = urljoin(base_url, url_raw) if url_raw.startswith('/') else url_raw

        parsed_url = urlparse(url)
        hostname = parsed_url.hostname
        protocol = parsed_url.scheme
        source = f'{protocol}://{hostname}/'

        title = news_card.xpath('.//*[contains(@class, "title")]/text()')[0]

        date_info = news_card.xpath('.//time[contains(@class, "date")]/text()')[0].replace(' ', '').split(',')
        if not date_info:
            date_info = None
        else:
            date_ = datetime.strptime(date_info[1], '%d%B%Y') if len(date_info) > 1 else datetime.now().date()
            time_ = datetime.strptime(date_info[0], '%H:%M').time()
            created_at = datetime.strftime(datetime.combine(date_, time_), '%Y-%m-%d %H:%M')

        data = [{
            'source': source,
            'url': url,
            'title': title,
            'created_at': created_at
        }]

        m_utils.save_documents('lenta_news', 'topnews', data)

    # Сделать вывод записанных в lenta_news.topnews данных
    m_utils.show_documents('lenta_news', 'topnews')