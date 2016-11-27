# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


from db import *

import urllib2
import re

from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
session = Session()

from BeautifulSoup import BeautifulSoup          # Для обработки HTML
default_url = "https://freelansim.ru/tasks/"
admin_url = "https://freelansim.ru/tasks?categories=admin_network,admin_servers,admin_databases,admin_design,admin_testing,admin_other"
webdev_url = "https://freelansim.ru/tasks?categories=web_programming,web_prototyping,web_test"
webdis_url = "https://freelansim.ru/tasks?categories=web_design,web_html"


def job_exist(job_link):
    cur = session.execute("SELECT url FROM job")
    links = cur.fetchall()
    # print links
    if any(job_link in s[0] for s in links): return True
    else: return False

def parse_category(url, category):
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page)
    all_jobs = soup.findAll('article', {"class": "task task_list"})

    for job in all_jobs:

        title = job.find("div", "task__title").text
        print "Title:\t", title
        url = 'http://freelansim.ru'+job.find("div", "task__title").find("a").get('href')
        print "Url:\t", url
        date = job.find("span", "params__published-at").text.splitlines()
        date = str(date[0]+' '+date[1])
        print "Date:\t", date
        price_raw = job.find("div", "task__price")
        price = price_raw.find("span", "count")
        if price:
            price = price.text
        else: # if not exist, find another tag
            price = price_raw.find("span", "negotiated_price").text

        print "Price:\t", price, "\n"
        #raw = job.contents
        # category = 'admin'

    if not job_exist(url):
        sql = "INSERT INTO job (title, date, price, url, category) \
                VALUES ('{}', '{}', '{}', '{}', '{}');".format(title, date, price, url, category)
        session.execute(sql)

    session.commit()

parse_category(admin_url, 'admin')
parse_category(webdev_url, 'webdev')
parse_category(webdis_url, 'webdis')
