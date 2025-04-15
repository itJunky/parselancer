# -*- coding: utf-8 -*-

import requests
import time
from datetime import datetime
from bs4 import BeautifulSoup  # Для обработки HTML

from db import *
from common import job_exist

from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
session = Session()

DEBUG = True

admin_urls = [
    'https://www.weblancer.net/jobs/napolnenie-sajtov-35/',
    'https://www.weblancer.net/jobs/sistemnoe-administrirovanie-54/',
    'https://www.weblancer.net/jobs/sluzhba-podderzhki-56/'
]
#dev_url = 'https://www.weblancer.net/jobs/programmirovanie-po-i-sistem-2/'
#TODO Добавить ещё 5 урлов про программирование
dev_urls = [
    'https://www.weblancer.net/freelance/prikladnoe-po-23/'
]
webdev_url = 'https://www.weblancer.net/jobs/veb-programmirovanie-i-sajty-3/'
webdis_url = 'https://www.weblancer.net/jobs/veb-dizajn-i-interfejsy-1/'


def parse_category(url, category):
    page = requests.get(url).content
    soup = BeautifulSoup(page, 'html.parser')

    all_jobs = soup.find_all('article')

    if DEBUG is True:
        # print(page)
        # print(all_jobs_content)
        # print(all_jobs[0])
        print(len(all_jobs))
        # return

    for job in all_jobs:
        # time.sleep(0.200)

        link = 'https://www.weblancer.net' + job.find('a').attrs['href']

        if job_exist(link): continue

        title = job.find('h2').text

        try:
            text = " ".join(job.find('div', class_='text-rich').text.strip().split(" ")[:-1])
        except AttributeError:
            # todo что-то не актуальное
            text = job.find('div', class_='text_field text-inline').text.strip()

        text = text.replace("\n", " ")
        
        try:
            price = job.find('div', class_='text-success').text
        except AttributeError:
            price = None

        try:
            # date = int(right.find('span', class_='time_ago').attrs['data-timestamp'])
            date_raw = job.find('span', class_='ms-1')
            date = date_raw.find('div').attrs['title']
        except:
            date = ''

        if DEBUG is True:
            print('\nDate:', date, \
                '\nTitle:', title, \
                '\nText:', text, \
                '\nPrice:', price, \
                '\nURL:', url
            )
            print('.' * 80)

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


        #else:
        #    print(title)


#for admin_url in admin_urls:
#    parse_category(admin_url, 'admin')
for url in dev_urls:
    parse_category(url, 'dev')

#parse_category(webdev_url, 'webdev')
#parse_category(webdis_url, 'webdis')


