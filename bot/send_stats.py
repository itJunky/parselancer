from db import *
import config
import telebot

from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
session = Session()

bot = telebot.TeleBot(config.token)

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

jobs_count = session.query(Job).count()
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


msg_text = f'{jobs_count}\t работ собрано за всё время \n' +\
           f'{jobs_at_this_day}\t задач собрано за последние сутки\n' +\
           f'{jobs_at_this_hour} задач собрано за последний час\n'+\
            '---\n' +\
           f'{jh_flru}/{jd_flru} задач опубликовали за час/день на fl.ru.\n' +\
           f'{jh_wbl}/{jd_wbl} задач опубликовали за час/день на weblancer.net.\n' +\
           f'{jh_guru}/{jd_guru} задач опубликовали за час/день на guru.com.\n'+\
           f'#stats #hourly'

bot.send_message(-1001420206323, msg_text, parse_mode='HTML')
#bot.send_message(6844185021, msg_text)

print(f'Всего работ собрано: {jobs_count}')
print(f'За последние сутки с фриланс бирж собрано задач: \t{jobs_at_this_day}')
print(f'За последний час с фриланс бирж собрано задач: \t\t{jobs_at_this_hour}')
print('-' * 30)
print(f'fl.ru опубликовало за день \t\t{jd_flru} \tи за час {jh_flru} работ.')
print(f'weblancer.net опубликовал за день \t{jd_wbl} \tи за час {jh_wbl} работ.')
print(f'guru.com опубликовал за день \t\t{jd_guru} \tи за час {jh_guru} работ.')
