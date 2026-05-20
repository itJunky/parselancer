# -*- coding: utf-8 -*-

import requests
import time
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

admin_url = 'https://freelancehunt.com/projects?skills%5B%5D=22&skills%5B%5D=86&skills%5B%5D=83&skills%5B%5D=78&skills%5B%5D=48&skills%5B%5D=6&skills%5B%5D=39'
dev_url = 'https://freelancehunt.com/projects?skills%5B%5D=24&skills%5B%5D=2&skills%5B%5D=5&skills%5B%5D=54&skills%5B%5D=13&skills%5B%5D=1&skills%5B%5D=22&skills%5B%5D=23&skills%5B%5D=160&skills%5B%5D=88&skills%5B%5D=169&skills%5B%5D=103&skills%5B%5D=85'
webdev_url = 'https://freelancehunt.com/projects?skills%5B%5D=28&skills%5B%5D=1&skills%5B%5D=99&skills%5B%5D=124&skills%5B%5D=96'
webdis_url = 'https://freelancehunt.com/projects?skills%5B%5D=41&skills%5B%5D=42&skills%5B%5D=43&skills%5B%5D=93&skills%5B%5D=17&skills%5B%5D=151'

def parse_category(url, category):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:136.0) Gecko/20100101 Firefox/136.0',
    }
    page = requests.get(url, headers=headers).content
    soup = BeautifulSoup(page, "html.parser")

    all_jobs = [tr for tr in soup.find_all('tr') if tr.get('data-published')]
    if not args.quiet:
        print(f"[{category}] Found {len(all_jobs)} jobs on page")

    new_count = 0
    for job in all_jobs:
        time.sleep(0.400)
        a = job.find('a', class_='biggest')
        if a is None:
            continue
        title = a.text.strip()
        job_url = a.attrs['href']

        if not job_exist(job_url):
            text_tag = job.find('p', {"style": "word-break: break-word"})
            text = text_tag.text.strip() if text_tag else ''
            date = int(job.attrs['data-published'])

            price_div = job.find('div', class_=lambda c: c and 'price' in c)
            price = price_div.text.strip() if price_div else None

            job_row = Job(
                title=title,
                date=date,
                price=price,
                url=job_url,
                category=category,
                parse_date=datetime.now(),
                description=text
            )
            session.add(job_row)
            session.commit()
            new_count += 1
            if not args.quiet:
                print(f"  + {title} | {price} | {job_url}")

    if not args.quiet:
        print(f"[{category}] Saved {new_count} new jobs")


parse_category(admin_url, 'admin')
parse_category(dev_url, 'dev')
parse_category(webdev_url, 'webdev')
parse_category(webdis_url, 'webdis')
