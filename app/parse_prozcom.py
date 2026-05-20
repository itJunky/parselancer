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

base_url = "https://www.proz.com/language-jobs"
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:136.0) Gecko/20100101 Firefox/136.0'
}


def parse_proz_jobs():
    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        job_cards = soup.find_all('div', class_='jobs__result-wrap')

        if not job_cards:
            if not args.quiet:
                print("No jobs found on page.")
            return

        if not args.quiet:
            print(f"[proz] Found {len(job_cards)} jobs on page")

        new_count = 0
        for job in job_cards:
            a = job.find('a', href=lambda h: h and '/translation-jobs/' in h)
            if not a:
                continue

            title = a.text.strip()
            link = a['href']

            if job_exist(link):
                continue

            reqs = job.find('div', class_='jobs__post-requirements')
            description = reqs.get_text(strip=True) if reqs else ''

            job_row = Job(
                title=title,
                date=datetime.now(),
                price=None,
                url=link,
                category='translation',
                parse_date=datetime.now(),
                description=description
            )
            session.add(job_row)
            session.commit()
            new_count += 1
            if not args.quiet:
                print(f"  + {title} | {link}")

        if not args.quiet:
            print(f"[proz] Saved {new_count} new jobs")

    except requests.exceptions.RequestException as e:
        if not args.quiet:
            print(f"[proz] Request error: {e}")
    except Exception as e:
        if not args.quiet:
            print(f"[proz] Error: {e}")


if __name__ == "__main__":
    parse_proz_jobs()
