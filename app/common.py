from db import *

from sqlalchemy.sql import text
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
session = Session()


def job_exist(job_link):
    cur = session.execute(text("SELECT url FROM job"))
    links = cur.fetchall()
    # print links
    if any(job_link in s[0] for s in links):
       # print('-Job in DataBase-')
        return True
    else: return False
