# -*- coding: utf-8 -*-

from db import *
from common import job_exist

import requests, re
from datetime import datetime

from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
session = Session()

from bs4 import BeautifulSoup          # Для обработки HTML
default_url = "https://freelansim.ru/tasks/"
admin_url = "https://freelansim.ru/tasks?categories=admin_network,admin_servers,admin_databases,admin_design,admin_testing,admin_other"
webdev_url = "https://freelansim.ru/tasks?categories=web_programming,web_prototyping,web_test"
webdis_url = "https://freelansim.ru/tasks?categories=web_design,web_html"
dev_url = "https://freelansim.ru/tasks?categories=app_all_inclusive,app_scripts,app_bots,app_plugins,app_utilites,app_design,app_programming,app_prototyping,app_1c_dev,app_test,app_other"


def parse_category(url, category):
    page = requests.get(url).content
    soup = BeautifulSoup(page)
    all_jobs = soup.findAll('article', {"class": "task task_list"})

    for job in all_jobs:

        # print job
        title = job.find("div", "task__title").text
        print("Title:\t", title)
        
        url = 'http://freelansim.ru'+job.find("div", "task__title").find("a").get('href')
        print("Url:\t", url)
        
        if not job_exist(url):
         
            date = job.find("span", "params__published-at").text.splitlines()
            date = str(date[0])
            print("Date:\t", date)
            
            price_raw = job.find("div", "task__price")
            price = price_raw.find("span", "count")
            if price:
                price = price.text
            else: # if not exist, find another tag
                price = price_raw.find("span", "negotiated_price").text

            print("Price:\t", price)
            #raw = job.contents
            # category = 'admin'
            
            text_page = requests.get(url).content
            text_soup = BeautifulSoup(text_page)
            text = text_soup.find('div', {'class': 'task__description'}).text
            
            text_length = 320
            text = (text[:text_length] + '..') if len(text) > text_length else text

            print(text, "\n")

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


parse_category(admin_url, 'admin')
parse_category(webdev_url, 'webdev')
parse_category(webdis_url, 'webdis')
parse_category(dev_url, 'dev')
