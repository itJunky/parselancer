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
        # print('LIMIT:', limit)
        # res.append(session.query(Job).\
        #            filter(
        #                 # Job.category == category,
        #                 # and_(Job.date.between(func.date(limit), func.date(now)))
        #                 # Job.date.between(func.date(limit), func.date(now))
        #                 Job.date.between(limit, now)
        #             )
        # )
        res.append(session.query(Job).\
                   filter(Job.category == category).\
                   filter(Job.parse_date > func.date(limit))
        )
    return res

def get_all_stats():
    categories = ['admin', 'webdev', 'dev', 'webdis']
    for category in categories:
        get_stats_by_category(category)

    # return res
        
def get_stats_by_category(category):
    print('Category:', category)
    stats = get_selecet(category)
    for stat in stats:
        print('Count:',len(stat.all()))
        jobs = stat.all()
        length = len(jobs)


if __name__ == '__main__':
    print("ParceLancer Stats")
    get_all_stats()