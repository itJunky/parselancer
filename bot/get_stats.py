# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from db import *
from sqlalchemy.orm import sessionmaker, scoped_session
session = scoped_session(sessionmaker(bind=engine))
from sqlalchemy.sql.expression import func
from sqlalchemy import between, and_

def get_selecet(category):
    now = datetime.now()
    limits = [ now - timedelta(days=1), now - timedelta(days=7), now - timedelta(days=30) ]
    res = []
    for limit in limits:
   
        res.append(session.query(Job).\
                   filter(Job.category == category).\
                   filter(Job.parse_date > func.date(limit))
        )
    return res

def get_all_stats():
    categories = ['admin', 'webdev', 'dev', 'webdis']
    res = []
    for category in categories:
        day, week, month = get_stats_by(category)
        text = 'Jobs in '+category+':\t'+str(day)+'\t'+str(week)+'\t'+str(month) 
        res.append(text)
        # print(text)

    return res
        
def get_stats_by(category):
    # print('Category:', category)
    res = []
    stats = get_selecet(category)
    for stat in stats:
        # print('Count:',len(stat.all()))
        jobs = stat.all()
        length = len(jobs)
        res.append(length)

    return res

if __name__ == '__main__':
    print("ParceLancer Stats")
    print('Time \t\t-1-\t-7-\t-30- days')
    for category in get_all_stats():
        print(category)