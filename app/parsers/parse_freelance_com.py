# -*- coding: utf-8 -*-
from datetime import datetime

import feedparser
import requests
from database import Job

from .base import BaseParser


class FreelanceUa(BaseParser):
    category_urls = {
        'admin': "https://freelance.ua/ru/orders/rss?t=1&cat_id=21&sub_id=0",
        'webdev': "https://freelance.ua/ru/orders/rss?t=1&cat_id=19&sub_id=0",
        'webdis': "https://freelance.ua/ru/orders/rss?t=1&cat_id=9&sub_id=0",
        'dev': "https://freelance.ua/ru/orders/rss?t=1&cat_id=17&sub_id=0"
    }

    def parse_category(self, url, category) -> None:
        response = requests.get(url)
        feed = feedparser.parse(response.text)
        for entry in feed.entries:
            print(entry.title)
            if self.db.job_exist(entry.link):
                continue
            published = datetime.strptime(entry['published'], '%a, %d %b %Y %H:%M:%S %z')
            self.db.append_job(
                Job(
                    title=entry['title'],
                    description=entry['description'],
                    date=published.strftime('%Y-%m-%d %H:%M:%S'),
                    price='На сайте',
                    link=entry['link'],
                    category=category,
                )
            )





