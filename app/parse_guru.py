# DISABLED: guru.com migrated to SPA (Vue.js) — job listings require JS rendering.
# Requests-based scraping returns empty HTML. RSS feeds require authentication.
# To restore: use Selenium/Playwright or the official guru.com API.

# import requests
# import argparse
# from bs4 import BeautifulSoup
# from datetime import datetime
#
# from db import *
# from common import job_exist
#
# from sqlalchemy.orm import sessionmaker
#
# parser = argparse.ArgumentParser()
# parser.add_argument('-q', '--quiet', action='store_true', help='Suppress output')
# args = parser.parse_args()
#
# Session = sessionmaker(bind=engine)
# session = Session()
#
# dev_url = "https://www.guru.com/d/jobs/c/programming-development/"
# admin_url = "https://www.guru.com/d/jobs/c/programming-development/sc/database-design-administration/"
# design_url = "https://www.guru.com/d/jobs/c/design-art/"
# copywright_url = "https://www.guru.com/d/jobs/c/writing-translation/"
# infosec_url = "https://www.guru.com/d/jobs/c/programming-development/sc/information-security/"
#
# def parse_guru_jobs(url, category):
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
#     }
#
#     try:
#         response = requests.get(url, headers=headers)
#         response.raise_for_status()
#
#         soup = BeautifulSoup(response.text, 'html.parser')
#         job_cards = soup.find_all('div', class_='jobRecord')
#
#         if not job_cards:
#             if not args.quiet:
#                 print(f"[{category}] No jobs found: {url}")
#             return
#
#         if not args.quiet:
#             print(f"[{category}] Found {len(job_cards)} jobs on page")
#
#         new_count = 0
#         for job in job_cards:
#             a = job.find('h2').find('a')
#             link = "https://www.guru.com" + a['href'].split('&')[0]
#
#             if job_exist(link):
#                 continue
#
#             title = job.find('h2').text.strip()
#
#             desc_div = job.find('div', class_='jobRecord__body')
#             description = desc_div.text.strip() if desc_div else ''
#
#             budget_div = job.find('div', class_='jobRecord__budget')
#             budget_info = budget_div.text.strip() if budget_div else None
#
#             job_row = Job(
#                 title=title,
#                 date=datetime.now(),
#                 price=budget_info,
#                 url=link,
#                 category=category,
#                 parse_date=datetime.now(),
#                 description=description
#             )
#             session.add(job_row)
#             session.commit()
#             new_count += 1
#             if not args.quiet:
#                 print(f"  + {title} | {budget_info} | {link}")
#
#         if not args.quiet:
#             print(f"[{category}] Saved {new_count} new jobs")
#
#     except requests.exceptions.RequestException as e:
#         if not args.quiet:
#             print(f"[{category}] Request error: {e}")
#     except Exception as e:
#         if not args.quiet:
#             print(f"[{category}] Error: {e}")
#
# if __name__ == "__main__":
#     parse_guru_jobs(admin_url, 'admin')
#     parse_guru_jobs(dev_url, 'webdev')
#     parse_guru_jobs(design_url, 'webdis')
#     parse_guru_jobs(copywright_url, 'writing')
#     parse_guru_jobs(infosec_url, 'infosec')
