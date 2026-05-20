# -*- coding: utf-8 -*-

import requests
import argparse
from datetime import datetime
from bs4 import BeautifulSoup

from db import *
from common import job_exist

from sqlalchemy.orm import sessionmaker

parser = argparse.ArgumentParser()
parser.add_argument('-q', '--quiet', action='store_true', help='Suppress output')
args = parser.parse_args()

Session = sessionmaker(bind=engine)
session = Session()

admin_urls = [
    'https://www.weblancer.net/jobs/napolnenie-sajtov-35/',
    'https://www.weblancer.net/jobs/sistemnoe-administrirovanie-54/',
    'https://www.weblancer.net/jobs/sluzhba-podderzhki-56/'
]
dev_urls = [
    'https://www.weblancer.net/freelance/veb-programmirovanie-31/',
    'https://www.weblancer.net/freelance/html-verstka-32/',
    'https://www.weblancer.net/freelance/internet-magazini-61/',
    'https://www.weblancer.net/freelance/saiti-pod-klyuch-58/',
    'https://www.weblancer.net/freelance/1s-programmirovanie-83/',
    'https://www.weblancer.net/freelance/mobilnie-prilozheniya-28/',
    'https://www.weblancer.net/freelance/prikladnoe-po-23/',
    'https://www.weblancer.net/freelance/razrabotka-igr-26/',
    'https://www.weblancer.net/freelance/sistemnoe-programmirovanie-24/'
]
qa_urls = [
    'https://www.weblancer.net/freelance/testirovanie-po-29/',
    'https://www.weblancer.net/freelance/testirovanie-saitov-37/'
]
#webdev_url = 'https://www.weblancer.net/jobs/veb-programmirovanie-i-sajty-3/'
#webdis_url = 'https://www.weblancer.net/jobs/veb-dizajn-i-interfejsy-1/'
design_urls = [
    'https://www.weblancer.net/freelance/banneri-8/',
    'https://www.weblancer.net/freelance/dizain-interfeisov-i-igr-13/',
    'https://www.weblancer.net/freelance/dizain-mobilnikh-prilozhenii-82/',
    'https://www.weblancer.net/freelance/dizain-saitov-9/',
    'https://www.weblancer.net/freelance/ikonki-i-piksel-art-14/',
    'https://www.weblancer.net/freelance/3d-grafika-12/',
    'https://www.weblancer.net/freelance/illyustratsii-i-risunki-11/',
    'https://www.weblancer.net/freelance/obrabotka-fotografii-21/',
    'https://www.weblancer.net/freelance/verstka-poligrafii-10/',
    'https://www.weblancer.net/freelance/dizain-produktsii-18/',
    'https://www.weblancer.net/freelance/logotipi-i-znaki-7/',
    'https://www.weblancer.net/freelance/naruzhnaya-reklama-17/',
    'https://www.weblancer.net/freelance/firmennii-stil-19/',
    'https://www.weblancer.net/freelance/prezentatsii-60/',
    'https://www.weblancer.net/freelance/animatsiya-39/',
    'https://www.weblancer.net/freelance/videomontazh-41/'
]


def parse_category(url, category):
    page = requests.get(url).content
    soup = BeautifulSoup(page, 'html.parser')

    all_jobs = soup.find_all('article')
    if not args.quiet:
        print(f"[{category}] Found {len(all_jobs)} jobs on page")

    new_count = 0
    for job in all_jobs:
        a = job.find('h2').find('a')
        link = 'https://www.weblancer.net' + a['href']

        if job_exist(link):
            continue

        title = a.text.strip()

        p = job.find('p', class_=lambda c: c and 'text-gray-600' in c)
        text = p.get_text(strip=True) if p else ''

        price_span = job.find('span', class_=lambda c: c and 'text-green-600' in c)
        price = price_span.get_text(strip=True) if price_span else None

        try:
            bottom = job.find('div', class_=lambda c: c and 'text-slate-400' in c)
            date_div = bottom.find('div', class_=lambda c: c and 'whitespace-nowrap' in c)
            date = date_div.find('span').text.strip()
        except Exception:
            date = ''

        job_row = Job(
            title=title,
            date=date,
            price=price,
            url=link,
            category=category,
            parse_date=datetime.now(),
            description=text
        )
        session.add(job_row)
        session.commit()
        new_count += 1
        if not args.quiet:
            print(f"  + {title} | {price} | {link}")

    if not args.quiet:
        print(f"[{category}] Saved {new_count} new jobs")


for admin_url in admin_urls:
    parse_category(admin_url, 'admin')

for url in dev_urls:
    parse_category(url, 'dev')

for url in design_urls:
    parse_category(url, 'design')

for url in qa_urls:
    parse_category(url, 'qa')

#parse_category(webdev_url, 'webdev')
#parse_category(webdis_url, 'webdis')

