from db import *

from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
session = Session()

def job_is_newer_than_day(date):
    now = datetime.now()
    difference = abs(now - date)
    return difference <= timedelta(days=1)

def job_is_newer_than_hour(date):
    now = datetime.now()
    difference = abs(now - date)
    return difference <= timedelta(hours=1)

jobs_at_this_day = 0
jobs_at_this_hour = 0
jd_flru = 0
jh_flru = 0
jd_wbl = 0
jh_wbl = 0
jd_guru = 0
jh_guru = 0
j = session.query(Job.id, Job.parse_date, Job.url).all()
for i in j:
    if job_is_newer_than_day(i[1]): 
        jobs_at_this_day += 1
        if 'fl.ru' in i[2]:
            jd_flru += 1
        if 'weblancer.net' in i[2]:
            jd_wbl += 1
        if 'guru.com' in i[2]:
            jd_guru += 1
    if job_is_newer_than_hour(i[1]):
        jobs_at_this_hour += 1
        if 'fl.ru' in i[2]:
            jh_flru += 1
        if 'weblancer.net' in i[2]:
            jh_wbl += 1
        if 'guru.com' in i[2]:
            jh_guru += 1


print(f'За последние сутки с фриланс бирж собрано задач: \t{jobs_at_this_day}')
print(f'За последний час с фриланс бирж собрано задач: \t\t{jobs_at_this_hour}')
print('-' * 30)
print(f'fl.ru опубликовало за день \t\t{jd_flru} \tи за час {jh_flru} работ.')
print(f'weblancer.net опубликовал за день \t{jd_wbl} \tи за час {jh_wbl} работ.')
print(f'guru.com опубликовал за день \t\t{jd_guru} \tи за час {jh_guru} работ.')
