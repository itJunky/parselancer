# -*- coding: utf-8 -*-

import re
from time import sleep
import requests
from datetime import datetime
from bs4 import BeautifulSoup  # Для обработки HTML
from db import *
from common import job_exist

from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
session = Session()

dev_url = 'https://freelance.ru/project/search/pro?c=&c%5B%5D=4&q=&m=or&e=&a=0&a=1&v=0&f=&t=&o=0&o=1&b='
webdev_url = 'https://freelance.ru/project/search/pro?c=&c%5B%5D=116&q=&m=or&e=&a=0&a=1&v=0&f=&t=&o=0&o=1&b='



def parse_category(url, category):
    sleep(0.1)
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.2675.135 Safari/537.36',
    }
    page = requests.get(url,headers=headers).content

    soup = BeautifulSoup(page, "html.parser")
    all_jobs = soup.find_all('div', class_='project')
    for job in all_jobs:  
        a = job.find('a',title='Название')
        url = 'https://freelance.ru' + a.attrs['href']
        if not job_exist(url):
            title = a.text.strip()
            date = job.find('div', class_='publish-time').attrs['title']
            date = re.sub("[-| |:|в]","",date)
            price = job.find('div', class_='cost').text.strip()
            if price.strip() == 'Договорная':
                price=''
            text = job.find('a', class_='description').text.strip()

            job_row=Job(
                title=title,
                date=date,
                price=price,
                url=url,
                category=category,
                parse_date=datetime.now(),
                description=text
            )

            session.add(job_row)
            session.commit()

parse_category(dev_url, 'dev')
parse_category(webdev_url, 'webdev')