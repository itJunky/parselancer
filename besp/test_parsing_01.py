# -*- coding: utf-8 -*-

from besp.db import *

import urllib2
import re

from sqlalchemy.orm import sessionmaker
session = sessionmaker(bind=engine)

from BeautifulSoup import BeautifulSoup          # Для обработки HTML
page = urllib2.urlopen("https://freelansim.ru/tasks/")
soup = BeautifulSoup(page)


# print soup.contents

all_jobs = soup.findAll('div', {"class": "jobs-item"})

for job in all_jobs:

    title = job.find("div", "job_title")
    company = Column(String)
    city = Column(String)
    salary = Column(String)
    url = Column(String)
    raw = job