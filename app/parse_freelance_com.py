# -*- coding: utf-8 -*-

from datetime import datetime

import requests
from bs4 import BeautifulSoup  # Для обработки HTML

from common import job_exist
from db import Job, engine
from sqlalchemy.orm import sessionmaker

dev_url = "https://freelance.ua/ru/orders/?orders=web-development%2Cprikladnoj-programmist%2Cdatabases%2C1c-programming%2Cqa-testing%2Cgame-programming%2Cembedded-systems%2Cdata-protection%2Cplugins-scripts-utilities%2Cweb-proektirovanie%2Cdevelopment-crm-erp%2Csystem-programming%2Cproject-management-development%2Candroid-development%2Cios-development&st=2&pc=1"
webdev_url = "https://freelance.ua/ru/orders/?orders=sajt-pod-kljuch%2Conline-shops%2Crefinement-sites%2Cverstka%2Cwap-pda-sites%2Cusability&st=2&pc=1"
webdis_url = "https://freelance.ua/ru/orders/?orders=site-design%2Clogo%2Cbanners%2Cpackaging-design%2Coutdoor-advertising%2Cdesign-of-exhibition-stands%2Cinfographics%2Ctechnical-design%2Ccorporate-identity%2Cdesign-application-interfaces%2CDesign-of-mobile-applications%2Cprinting-layout%2Cinterface-design%2Cprint-design%2Cpresentations%2Cindustrial-design%2Ctype-design%2Cprepress&pc=1"
admin_url = "https://freelance.ua/ru/orders/?orders=devops%2Csystem-administrator%2Cdatabase-administration%2Cnetwork-administration%2Cerp-and-crm-integration%2Cip-telefoniya-voip&pc=1"

Session = sessionmaker(bind=engine)
session = Session()


def parse_category(url, category):
    page = requests.get(url).content
    soup = BeautifulSoup(page, "html.parser")

    all_jobs = soup.find_all("li", class_="j-order")

    for job in all_jobs:
        header = job.find("header", class_="l-project-title").find("a")
        title = header.text.strip()
        url = header.attrs["href"]
        if job_exist(url):
            continue
        
        try:
            clock_tag = job.find("i", {"class": "fa fa-clock-o"})
            date = clock_tag.find_next_sibling(text=True).strip()
            text = job.find("article").text.strip()
            price = job.find("span", "l-price").text.strip()
        except Exception as e:
            print(e)
            continue
        else:
            job_row = Job(
                title=title,
                date=date,
                price=price,
                url=url,
                category=category,
                parse_date=datetime.now(),
                description=text,
            )
        session.add(job_row)
        session.commit()


parse_category(admin_url, "admin")
parse_category(dev_url, "dev")
parse_category(webdev_url, "webdev")
parse_category(webdis_url, "webdis")