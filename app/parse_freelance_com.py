# -*- coding: utf-8 -*-
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

import urllib2, re
from datetime import datetime
from BeautifulSoup import BeautifulSoup  # Для обработки HTML\

from db import *
from common import job_exist

from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
session = Session()

admin_url = 'http://www.freelance.com/en/search/mission?filter.searchLanguageCode=EN&filter.location.country=&filter.location.region1=&filter.location.city=&filter.duration=ALL&missionStartDateYear=2016&missionStartDateMonth=11&query='
webdis_url = 'http://www.freelance.com/en/search/mission?filter.searchLanguageCode=EN&filter.location.country=&filter.location.region1=&filter.location.city=&filter.duration=ALL&missionStartDateYear=2016&missionStartDateMonth=11&selSkills%5B0%5D=261&selSkills%5B1%5D=259&selSkills%5B2%5D=264&selSkills%5B3%5D=265&selSkills%5B4%5D=242&selSkills%5B5%5D=191&selSkills%5B6%5D=180&query='
dev_url = 'http://www.freelance.com/en/search/mission?filter.searchLanguageCode=EN&filter.location.country=&filter.location.region1=&filter.location.city=&filter.duration=ALL&missionStartDateYear=2016&missionStartDateMonth=11&selSkills%5B0%5D=176&selSkills%5B1%5D=255&selSkills%5B2%5D=200&selSkills%5B3%5D=173&selSkills%5B4%5D=253&selSkills%5B5%5D=225&selSkills%5B6%5D=252&query='

def parse_category(url, category):
    page = urllib2.urlopen(admin_url)
    soup = BeautifulSoup(page)
    all_jobs = soup.findAll('div', {'class': 'jobsearch-result-list'})

    for job in all_jobs:
        title = job.find('a', {'style': 'color: #000;'}).text
        print title
        date_raw = job.find('div', {'class': 'col-xs-6 col-md-2 col-lg-2 lefttop'})
        date = date_raw.find('b').text.split()[0]
        print date
        price = job.find('div', {'class': 'col-xs-6 col-md-2 col-lg-2 leftbottom'}).text.split()[2]
        print price
        url = 'http://www.freelance.com' + job.find('a', {'style': 'color: #000;'}).get('href')
        print url

        if not job_exist(url):
            job_row = Job(
                title=unicode(title),
                date=unicode(date),
                price=price,
                url=url,
                category=category,
                parse_date=datetime.now()
            )
            session.add(job_row)

    session.commit()


parse_category(admin_url, 'admin')
parse_category(webdis_url, 'webdis')
parse_category(dev_url, 'dev')
