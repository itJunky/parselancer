import requests
from bs4 import BeautifulSoup

from datetime import datetime
from db import *
from common import job_exist

from sqlalchemy.orm import sessionmaker
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
            print(f"Не удалось найти проекты на странице: {url}")
            return
        
        for project in projects:
            t = project.find_all('h2')[0]
            title = t.find('a').text  ### title here !!!
            link = t.find('a')['href']
            descr_raw = project.find_all('script')
            for descr in descr_raw:
                sc_content = descr.string
                inner_html = sc_content.split("document.write('")[-1].split("');")[0]
                inner_soup = BeautifulSoup(inner_html, 'html.parser')
                

                span_raw = inner_soup.find('span')
                price = []
                if span_raw:
                    for span in span_raw:
                        price.append(span.text)
                        if len(price) > 1: break
                    break # stop looking price

            for descr in descr_raw:
                sc_content = descr.string
                inner_html = sc_content.split("document.write('")[-1].split("');")[0]
                inner_soup = BeautifulSoup(inner_html, 'html.parser')
                
                div_raw = inner_soup.find_all('div')[0]
                if div_raw:
                    div_raw2 = div_raw.find_all('div')
                    if not div_raw2: continue

                    div_text = div_raw2[0].text
                    if len(div_text) > 2:
                        description = div_raw2[0].text
                        break

            
            # Пытаемся найти стоимость (может быть не у всех проектов)
            try:
                cost = str(price[0] + price[1])
            except:
                cost = str(price[0])
            
            if job_exist(link): continue # skip to next url

            job_row = Job(
                title = title,
                date = datetime.now(), # TODO спарсить дату публикации
                price = cost,
                url = main_url + link,
                category = category,
                parse_date = datetime.now(),
                description = description
            )
            session.add(job_row)
            session.commit()

            print(f"Название: {title}")
            print(f"Описание: {description}")
            print(f"Стоимость: {cost}")
            print(main_url+link)
            print("-" * 50)
            #return
            
    except requests.RequestException as e:
        print(f"Ошибка при запросе к сайту: {e}")
#    except Exception as e:
#        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    for url in dev_urls:
        parse_fl_projects(url, 'dev')

    for url in design_urls:
        parse_fl_projects(url, 'design')

    parse_fl_projects(copywright_url, 'writing')
    parse_fl_projects(qa_url, 'qa')

