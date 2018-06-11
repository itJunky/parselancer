# -*- coding: utf-8 -*-

import requests
import re
from datetime import datetime
from bs4 import BeautifulSoup  # Для обработки HTML\

from db import *
from common import job_exist

from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
session = Session()

admin_url = 'https://freelancehunt.com/projects?skills%5B%5D=22&skills%5B%5D=86&skills%5B%5D=83&skills%5B%5D=78&skills%5B%5D=48&skills%5B%5D=6&skills%5B%5D=39'
dev_url = 'https://freelancehunt.com/projects?skills%5B%5D=24&skills%5B%5D=2&skills%5B%5D=5&skills%5B%5D=54&skills%5B%5D=13&skills%5B%5D=1&skills%5B%5D=22&skills%5B%5D=23&skills%5B%5D=160&skills%5B%5D=88&skills%5B%5D=169&skills%5B%5D=103&skills%5B%5D=85'
webdev_url = 'https://freelancehunt.com/projects?skills%5B%5D=28&skills%5B%5D=1&skills%5B%5D=99&skills%5B%5D=124&skills%5B%5D=96'
webdis_url = 'https://freelancehunt.com/projects?skills%5B%5D=41&skills%5B%5D=42&skills%5B%5D=43&skills%5B%5D=93&skills%5B%5D=17&skills%5B%5D=151'

def parse_category(url, category):
    page = requests.get(url).content
    soup = BeautifulSoup(page, 'lxml')
    # all_jobs = soup.findAll('td', class_='left')
    all_jobs = soup.findAll('tr')
    for job in all_jobs:
        title = job.find('a').text
        url = 'https://freelancehunt.com'+job.find('a').attrs['href']
        
        if not job_exist(url):
            text = job.find('a').attrs['title']
            date = job.attrs['data-published']
            # from IPython import embed; embed()
            try: price = job.find('div', class_='price').text.split('\n')[1]
            except AttributeError: price = None
            # print(job)
            print('\nDate:', date,\
                  '\nTitle:', title,\
                  '\nText:', text,\
                  '\nPrice:', price,\
                  '\nURL:', url, '\n\n'
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

parse_category(admin_url, 'admin')
parse_category(dev_url, 'dev')
parse_category(webdev_url, 'webdev')
parse_category(webdis_url, 'webdis')
