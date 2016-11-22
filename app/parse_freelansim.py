# -*- coding: utf-8 -*-

from db import *

import urllib2
import re

from sqlalchemy.orm import sessionmaker
session = sessionmaker(bind=engine)

from BeautifulSoup import BeautifulSoup          # Для обработки HTML
page = urllib2.urlopen("https://freelansim.ru/tasks/")
soup = BeautifulSoup(page)


# print soup.contents

all_jobs = soup.findAll('article', {"class": "task task_list"})

for job in all_jobs:

    title = job.find("div", "task__title").text
    print title
    url = 'http://freelansim.ru'+job.find("div", "task__title").find("a").get('href')
    print url
    data = job.find("span", "params__published-at").text
    print data
    price_raw = job.find("div", "task__price")
    price = price_raw.find("span", "count")
    if price:
        price = price.text
    else:
        price = price_raw.find("span", "negotiated_price").text

    print price
    raw = job.contents