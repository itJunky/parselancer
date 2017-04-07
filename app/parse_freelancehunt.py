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

admin_url = 'https://freelancehunt.com/projects?skills%5B%5D=22&skills%5B%5D=48&skills%5B%5D=6&skills%5B%5D=39'

def parse_category(url, category):
    page = requests.get(url).content
    soup = BeautifulSoup(page)
    # all_jobs = soup.findAll('td', class_='left')
    all_jobs = soup.findAll('tr')
    for job in all_jobs:
        url = 'https://freelancehunt.com'+job.find('a').attrs['href']
        title = job.find('a').text
        text = job.find('a').attrs['title']
        date = job.attrs['data-published']
        # from IPython import embed; embed()
        try: price = job.find('div', class_='price').text.split('\n')[1]
        except AttributeError: pass
        # print(job)
        print('\nDate:', date,\
              '\nTitle:', title,\
              '\nText:', text,\
              '\nPrice:', price,\
              '\nURL:', url, '\n\n'
        )
        if not job_exist(url):
            job_row = Job(
                title=title,
                date=date,
                price=price,
                url=url,
                category=category,
                parse_date=datetime.now()
            )
            session.add(job_row)

    session.commit()

parse_category(admin_url, 'admin')