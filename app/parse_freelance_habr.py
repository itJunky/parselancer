# -*- coding: utf-8 -*-

import requests
from datetime import datetime
from bs4 import BeautifulSoup  # Для обработки HTML

from db import *
from common import job_exist

from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
session = Session()

default_url = "https://freelance.habr.com/tasks/"
admin_url = "https://freelance.habr.com/tasks?categories=admin_network,admin_servers,admin_databases,admin_design,admin_testing,admin_other"
webdev_url = "https://freelance.habr.com/tasks?categories=web_programming,web_prototyping,web_test"
webdis_url = "https://freelance.habr.com/tasks?categories=web_design,web_html"
dev_url = "https://freelance.habr.com/tasks?categories=app_all_inclusive,app_scripts,app_bots,app_plugins,app_utilites,app_design,app_programming,app_prototyping,app_1c_dev,app_test,app_other"


def parse_category(url, category):
    page = requests.get(url).content
    soup = BeautifulSoup(page, "html.parser")
    all_jobs = soup.findAll('article', {"class": "task task_list"})

    for job in all_jobs:
        title = job.find("div", "task__title").text
        url = 'http://freelance.habr.com' + job.find("div", "task__title").find("a").get('href')

        if not job_exist(url):
            date = job.find("span", "params__published-at").text.splitlines()
            date = str(date[0])

            price_raw = job.find("div", "task__price")

            try:
                price = price_raw.find("span", "count").text
            except:
                price = price_raw.find("span", "negotiated_price").text

            text_page = requests.get(url).content
            text_soup = BeautifulSoup(text_page, "html.parser")
            text = text_soup.find('div', {'class': 'task__description'}).text

            text_length = 320
            text = (text[:text_length] + '..') if len(text) > text_length else text

            #print(text, "\n")

            job_row = Job(
                title = title,
                date = date,
                price = price,
                url = url,
                category = category,
                parse_date = datetime.now(),
                description = text
            )

            session.add(job_row)
            session.commit()

        #else:
        #    print(title)


parse_category(admin_url, 'admin')
parse_category(webdev_url, 'webdev')
parse_category(webdis_url, 'webdis')
parse_category(dev_url, 'dev')
