# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


import urllib2
import re
from BeautifulSoup import BeautifulSoup          # Для обработки HTML\

admin_url = 'https://www.weblancer.net/jobs/administrirovanie-sajtov-6/'

page = urllib2.urlopen(admin_url)
soup = BeautifulSoup(page)

all_jobs = soup.findAll('div', {'class': 'row'})

for job in all_jobs:
	title = job.find('h1')
	print title