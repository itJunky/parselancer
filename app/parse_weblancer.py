# -*- coding: utf-8 -*-

import requests
from datetime import datetime
from bs4 import BeautifulSoup          # Для обработки HTML

from db import *
from common import job_exist

from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
session = Session()

admin_url = 'https://www.weblancer.net/jobs/administrirovanie-sajtov-6/'
dev_url = 'https://www.weblancer.net/jobs/programmirovanie-po-i-sistem-2/'
webdev_url = 'https://www.weblancer.net/jobs/veb-programmirovanie-i-sajty-3/'
webdis_url = 'https://www.weblancer.net/jobs/veb-dizajn-i-interfejsy-1/'


def parse_category(url, category):
    page = requests.get(url).content
    soup = BeautifulSoup(page, 'html.parser')
    all_jobs = soup.findAll('div', {'class': 'row'})
    for job in all_jobs:
        title_raw = job.find('div', class_='col-sm-10')
        try:  # to get Title
            title = title_raw.find('h2').text
            url = 'https://www.weblancer.net' + title_raw.find('a').attrs['href']
            if not job_exist(url):
                text = title_raw.find('p').text
                try:  # to get date
                    date = job.find('span', class_='time_ago').attrs['data-timestamp']
                    # from IPython import embed; embed(); import sys; sys.exit()
                except AttributeError:
                    date = job.find('span', class_='time_ago').attr['data-timestamp']

                print(date)
                try:  # to get price
                    price = job.find('div', class_='amount').text
                except AttributeError:
                    price = None

                print('\nDate:', date, \
                      '\nTitle:', title, \
                      '\nText:', text, \
                      '\nPrice:', price, \
                      '\nURL:', url)
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

        except:
            pass



parse_category(admin_url, 'admin')
parse_category(dev_url, 'dev')
parse_category(webdev_url, 'webdev')
parse_category(webdis_url, 'webdis')
