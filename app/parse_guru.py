import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime

from db import *
from common import job_exist

from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
session = Session()

dev_url = "https://www.guru.com/d/jobs/c/programming-development/"
admin_url = "https://www.guru.com/d/jobs/c/programming-development/sc/database-design-administration/"
design_url = "https://www.guru.com/d/jobs/c/design-art/"
copywright_url = "https://www.guru.com/d/jobs/c/writing-translation/"
infosec_url = "https://www.guru.com/d/jobs/c/programming-development/sc/information-security/"

def parse_guru_jobs(url, category):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        # Отправляем GET-запрос к сайту
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Проверяем на ошибки
        
        # Парсим HTML-контент
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Находим все карточки с вакансиями
        job_cards = soup.find_all('div', class_='jobRecord')
        
        if not job_cards:
            print(f"Не удалось найти вакансии на странице. {url}")
            return
        
       #print(f"Найдено {len(job_cards)} вакансий:\n")
        
        # Извлекаем информацию о каждой вакансии
        for index, job in enumerate(job_cards, start=1):
            #print(job)

            # Название вакансии
            title = job.find('h2').text
            #print(title)
            #title = job.find('a', class_='jobTitle').text.strip()
            
            # Ссылка на вакансию
            link = "https://www.guru.com" + job.find('h2').find('a')['href']
            
            if job_exist(link): continue # skip to next url

            # Описание вакансии
            #description = job.find('div', class_='jobDescription').text.strip()
            description = job.find('div', class_='jobRecord__body').text.strip()
            
            # Информация о бюджете и сроках
            budget_info = job.find('div', class_='jobRecord__budget').text.strip()
            
            # Навыки (теги)
            skills = [skill.text.strip() for skill in job.find_all('a', class_='skillName')]
            
            # Выводим информацию о вакансии
            print(f"{index}. {title}")
            print(f"   Ссылка: {link}")
           #print(f"   Описание: {description[:150]}...")  # Ограничиваем длину описания
           #print(f"   Бюджет/Сроки: {budget_info}")
           #print(f"   Навыки: {', '.join(skills)}")
            print("-" * 80)

            job_row = Job(
                title = title,
                date = datetime.now(), # TODO спарсить дату публикации
                price = budget_info,
                url = link,
                category = category,
                parse_date = datetime.now(),
                description = description
            )
            session.add(job_row)
            session.commit()
            
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к сайту: {e}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    parse_guru_jobs(admin_url, 'admin')
    parse_guru_jobs(dev_url, 'webdev')
    parse_guru_jobs(design_url, 'webdis')
    parse_guru_jobs(copywright_url, 'writing')
    parse_guru_jobs(infosec_url, 'infosec')

