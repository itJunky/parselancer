# -*- coding: utf-8 -*-

import requests
from datetime import datetime
from bs4 import BeautifulSoup  # Для обработки HTML

from db import *
from common import job_exist

from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
session = Session()

admin_urls = [
    'https://www.weblancer.net/jobs/napolnenie-sajtov-35/',
    'https://www.weblancer.net/jobs/sistemnoe-administrirovanie-54/',
    'https://www.weblancer.net/jobs/sluzhba-podderzhki-56/'
]
dev_urls = [
    'https://www.weblancer.net/jobs/html-verstka-32/',
    'https://www.weblancer.net/jobs/veb-programmirovanie-31/',
    'https://www.weblancer.net/jobs/sajty-pod-klyuch-58/'
    ]
webdev_urls = [
    'https://www.weblancer.net/jobs/html-verstka-32/',
    'https://www.weblancer.net/jobs/veb-programmirovanie-31/',
    'https://www.weblancer.net/jobs/sajty-pod-klyuch-58/'
    ]
webdis_urls = [
        'https://www.weblancer.net/jobs/dizajn-sajtov-9/',
        'https://www.weblancer.net/jobs/bannery-8/'
    ]



def parse_category(url, category):
    page = requests.get(url).content
    soup = BeautifulSoup(page, 'html.parser')

    all_jobs = soup.find_all('div', class_='row click_container-link set_href')

    for job in all_jobs:
        try:
            right = job.find('div', class_='col-sm-4 text-sm-end').find('span')
            if right.text.startswith('Закрыт'):
                continue

        except:
            pass

        a = job.find('div', class_='title').find('a')

        title = a.text.strip()
        url = 'https://www.weblancer.net' + a.attrs['href']

        if not job_exist(url):
            try:
                date = job.find('div', class_='col-sm-4 text-sm-end').find('span',class_='text-muted').find('span')['title']
                date = date[3:].replace('.','').replace(':','').replace(' ','')
            except:
                date = ''
            try:
                text = " ".join(job.find('div', class_='collapse').text.strip().split(" ")[:-1])
            except AttributeError:
                text = job.find('div', class_='text_field text-inline').text.strip()

            text = text.replace("\n", " ")

            try:
                price = job.find('div', class_='float-right float-sm-none title amount indent-xs-b0').find('span').text.strip()
            except AttributeError:
                price = None

            job_row = Job(
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



for admin_url in admin_urls:
    parse_category(admin_url, 'admin')

for dev_url in dev_urls:
    parse_category(dev_url, 'dev')

for webdev_url in webdev_urls:
    parse_category(webdev_url, 'webdev')

for webdis_url in webdis_urls:
    parse_category(webdis_url, 'webdis')
