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
dev_url = 'https://www.weblancer.net/jobs/programmirovanie-po-i-sistem-2/'
webdev_url = 'https://www.weblancer.net/jobs/veb-programmirovanie-i-sajty-3/'
webdis_url = 'https://www.weblancer.net/jobs/veb-dizajn-i-interfejsy-1/'


def parse_category(url, category):
    page = requests.get(url).content
    soup = BeautifulSoup(page, 'html.parser')

    all_jobs = soup.find_all('div', class_='row click_container-link set_href')

    for job in all_jobs:
        if job.find('span', class_='text-muted').text.startswith('Закрыт'):
            continue

        a = job.find('div', class_='title').find('a')

        title = a.text.strip()
        url = 'https://www.weblancer.net' + a.attrs['href']

        if not job_exist(url):
            date = int(job.find('span', class_='time_ago').attrs['data-timestamp'])

            try:
                text = job.find('span', class_='snippet').text.strip()
            except AttributeError:
                text = job.find('div', class_='text_field text-inline').text.strip()

            try:
                price = job.find('div', class_='float-right float-sm-none title amount indent-xs-b0').find('span').text.strip()
            except AttributeError:
                price = None

            print('\nDate:', date, \
                    '\nTitle:', title, \
                    '\nText:', text, \
                    '\nPrice:', price, \
                    '\nURL:', url
            )

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

        else:
            print(title)


for admin_url in admin_urls:
    parse_category(admin_url, 'admin')

parse_category(dev_url, 'dev')
parse_category(webdev_url, 'webdev')
parse_category(webdis_url, 'webdis')
