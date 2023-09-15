# -*- coding: utf-8 -*-

from datetime import datetime

import requests
from bs4 import BeautifulSoup  # Для обработки HTML
from database import Job

from .base import BaseParser


class FreelanceHabr(BaseParser):
    category_urls = {
        'admin': "https://freelance.habr.com/tasks?categories=admin_servers,admin_network,admin_databases,admin_security,admin_other",
        'webdev': "https://freelance.habr.com/tasks?categories=development_all_inclusive,development_backend,development_frontend,development_prototyping",
        'webdis': "https://freelance.habr.com/tasks?categories=design_sites,design_landings,design_logos,design_illustrations,design_mobile,design_icons,design_polygraphy,design_banners,design_graphics,design_corporate_identity,design_presentations,design_modeling,design_animation,design_photo,design_other",
        'dev': "https://freelance.habr.com/tasks?categories=development_ios,development_android,development_desktop,development_bots,development_games,development_1c_dev,development_scripts,development_voice_interfaces,development_other"
    }

    def parse_category(self, url, category):
        headers = {
            'Accept': 'application/json'
        }

        r = requests.get(url, headers=headers)

        jobs: list[dict] = r.json()
        for job in jobs:
            if self.db.job_exist(job['url']):
                continue
            date = datetime.strptime(job['published_at'], '%Y-%m-%dT%H:%M:%S.%f%z')
            text_page = requests.get(job['url']).content
            text_soup = BeautifulSoup(text_page, "html.parser")
            text = text_soup.find('div', {'class': 'task__description'}).text
            description = (text[:320] + '..') if len(text) > 320 else text
            print(Job(
                    title=job['title'],
                    date=date.strftime('%Y-%m-%d %H:%M:%S'),
                    price=job['price'],
                    link=job['url'],
                    category=category,
                    description=description
                ))
            self.db.append_job(
                Job(
                    title=job['title'],
                    date=date.strftime('%Y-%m-%d %H:%M:%S'),
                    price=job['price'],
                    link=job['url'],
                    category=category,
                    description=description
                )
            )
            break



