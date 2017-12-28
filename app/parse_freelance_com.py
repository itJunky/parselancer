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

import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

admin_url = 'https://secure.app.freelance.com/en/search/mission?filter.searchLanguageCode=EN&filter.location.country=&filter.location.region1=&filter.location.city=&filter.duration=ALL&missionStartDateYear=2016&missionStartDateMonth=11&query='
webdis_url = 'https://secure.app.freelance.com/en/search/mission?filter.searchLanguageCode=EN&filter.location.country=&filter.location.region1=&filter.location.city=&filter.duration=ALL&missionStartDateYear=2016&missionStartDateMonth=11&selSkills%5B0%5D=261&selSkills%5B1%5D=259&selSkills%5B2%5D=264&selSkills%5B3%5D=265&selSkills%5B4%5D=242&selSkills%5B5%5D=191&selSkills%5B6%5D=180&query='
dev_url = 'https://secure.app.freelance.com/en/search/mission?filter.searchLanguageCode=EN&filter.location.country=&filter.location.region1=&filter.location.city=&filter.duration=ALL&missionStartDateYear=2016&missionStartDateMonth=11&selSkills%5B0%5D=176&selSkills%5B1%5D=255&selSkills%5B2%5D=200&selSkills%5B3%5D=173&selSkills%5B4%5D=253&selSkills%5B5%5D=225&selSkills%5B6%5D=252&query=&page=1&order=1&sort=POST_DATE'
webdev_url = 'https://secure.app.freelance.com/en/search/mission?filter.searchLanguageCode=EN&filter.location.country=&filter.location.region1=&filter.location.city=&filter.duration=ALL&missionStartDateYear=2016&missionStartDateMonth=12&selSkills%5B0%5D=181&query='

def parse_category(url, category):
    page = urllib2.urlopen(url, context=ctx)
    soup = BeautifulSoup(page)
    all_jobs = soup.findAll('div', {'class': 'jobsearch-result-list'})

    for job in all_jobs:
        # print job
        title = job.find('a', {'style': 'color: #000;'}).text
        print title
        url = 'http://www.freelance.com' + job.find('a', {'style': 'color: #000;'}).get('href')
        print url
        
        if not job_exist(url):
            date_raw = job.find('div', {'class': 'col-xs-6 col-md-2 col-lg-2 lefttop'})
            date = date_raw.find('b').text.split()[0]
            print date
            price = job.find('div', {'class': 'col-xs-6 col-md-2 col-lg-2 leftbottom'}).text.split()[2]
            print price
            text_page = urllib2.urlopen(url, context=ctx)
            text_soup = BeautifulSoup(text_page)
            text = text_soup.find('div', {'class': 'col-md-9 col-lg-9 description'}).text[11:]
            # text = job.find('div', { 'class': 'col-xs-12 col-md-4 col-lg-4 center'}).text
            
            text_length = 320
            text = (text[:text_length] + '..') if len(text) > text_length else text
            print text

            print '=========\n\n'

            job_row = Job(
                title=unicode(title),
                date=unicode(date),
                price=price,
                url=url,
                category=category,
                parse_date=datetime.now(),
                description=text
            )
            session.add(job_row)
            session.commit()


parse_category(admin_url, 'admin')
parse_category(webdis_url, 'webdis')
parse_category(dev_url, 'dev')
parse_category(webdev_url, 'webdev')