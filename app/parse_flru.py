import requests
import argparse
from bs4 import BeautifulSoup

from datetime import datetime
from db import *
from common import job_exist

from sqlalchemy.orm import sessionmaker

parser = argparse.ArgumentParser()
parser.add_argument('-q', '--quiet', action='store_true', help='Suppress output')
args = parser.parse_args()

Session = sessionmaker(bind=engine)
session = Session()

main_url = 'https://www.fl.ru'

dev_urls = [
    'https://www.fl.ru/projects/category/programmirovanie/',
    'https://www.fl.ru/projects/category/saity/',
    'https://www.fl.ru/projects/category/crypto-i-blockchain/',
    'https://www.fl.ru/projects/category/ai-iskusstvenniy-intellekt/',
    'https://www.fl.ru/projects/category/internet-magaziny/',
    'https://www.fl.ru/projects/category/games/unity/',
    'https://www.fl.ru/projects/category/games/unreal-engine/',
    'https://www.fl.ru/projects/category/games/heroengine/',
    'https://www.fl.ru/projects/category/brauzery/'
]
design_urls = [
    'https://www.fl.ru/projects/category/dizajn/',
    'https://www.fl.ru/projects/category/risunki-i-illustracii/',
    'https://www.fl.ru/projects/category/3d-grafika/',
    'https://www.fl.ru/projects/category/audio-video-photo/',
    'https://www.fl.ru/projects/category/firmennyi-stil/'
]
copywright_url = 'https://www.fl.ru/projects/category/teksty/'
qa_url = 'https://www.fl.ru/projects/category/games/testirovanie-igr-qa/'

def parse_fl_projects(url, category):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Проверяем, что запрос успешен
        
        soup = BeautifulSoup(response.text, 'html.parser')
        projects = soup.find_all('div', class_='b-post__grid')
        
        if not projects:
            if not args.quiet:
                print(f"[{category}] No projects found: {url}")
            return

        if not args.quiet:
            print(f"[{category}] Found {len(projects)} jobs on page")
        
        for project in projects:
            t = project.find('h2')
            if not t:
                continue
            a = t.find('a')
            if not a:
                continue
            title = a.text.strip()
            link = a['href']

            price_span = project.find('span', class_='text-4')
            cost = price_span.get_text(strip=True) if price_span else None

            descr_div = project.find('div', class_='text-5')
            description = descr_div.get_text(strip=True) if descr_div else ''

            if job_exist(link):
                continue

            job_row = Job(
                title=title,
                date=datetime.now(),
                price=cost,
                url=main_url + link,
                category=category,
                parse_date=datetime.now(),
                description=description
            )
            session.add(job_row)
            session.commit()

            if not args.quiet:
                print(f"  + {title} | {cost} | {main_url + link}")
            #return
            
    except requests.RequestException as e:
        if not args.quiet:
            print(f"[{category}] Request error: {e}")
#    except Exception as e:
#        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    for url in dev_urls:
        parse_fl_projects(url, 'dev')

    for url in design_urls:
        parse_fl_projects(url, 'design')

    parse_fl_projects(copywright_url, 'writing')
    parse_fl_projects(qa_url, 'qa')

