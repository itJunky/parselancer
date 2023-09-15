# -*- coding: utf-8 -*-


from datetime import datetime

import feedparser
import requests
from bs4 import BeautifulSoup
from database import Job
from fake_useragent import UserAgent

from .base import BaseParser

dev_url = 'https://freelance.ru/rss/feed/list/s.4'


class FreelanceRu(BaseParser):
    category_urls = {
        'admin': "https://freelance.ru/rss/feed/list/s.663.673.117",
        'webdev': "https://freelance.ru/rss/feed/list/s.116",
        'webdis': "https://freelance.ru/rss/feed/list/s.577.40.716",
        'dev': "https://freelance.ru/rss/feed/list/s.4"
    }
    def parse_category(self, url, category):
        ua = UserAgent()
        response = requests.get(url, headers={'User-Agent': ua.random})
        feed = feedparser.parse(response.text)
        for entry in feed.entries:
            soup = BeautifulSoup(entry['content'][0]['value'], 'html.parser')
            p_blocks = soup.find_all('p')
            if p_blocks:
                p_blocks[0].decompose()
            a_blocks = soup.find_all('a')
            if a_blocks:
                p_blocks[-1].decompose()
            content = soup.get_text().strip()
            published = datetime.strptime(entry['published'], '%a, %d %b %Y %H:%M:%S %z')
            self.db.append_job(
                Job(
                    title=entry['title'],
                    description=content,
                    date=published.strftime('%Y-%m-%d %H:%M:%S'),
                    price='На сайте',
                    link=entry['link'],
                    category=category,
                )
            )
           

