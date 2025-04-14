from db import *

from sqlalchemy.sql import text
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
session = Session()


def job_exist(job_link):
    cur = session.execute(text("SELECT url FROM job"))
    links = cur.fetchall()
    if any(job_link in s[0] for s in links):
   #    print(f'-Job in DataBase- {job_link}')
        return True
    else: return False
