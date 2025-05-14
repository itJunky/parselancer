# -*- coding: utf-8 -*-

import json
import html
import config
import sqlalchemy
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
bot = telebot.TeleBot(config.token)

from time import sleep, strftime
from datetime import datetime

from db import *
from sqlalchemy.orm import sessionmaker, scoped_session
session = scoped_session(sessionmaker(bind=engine))
from sqlalchemy import desc


# TODO Получить список юзеров
users = session.query(User).all()
# from IPython import embed; embed()

# У каждого пользователя
for user in users:
    if user.category == 'unsubscribed' or user.category == 'deleted': continue

    try: # Получить последнюю работу
        # from IPython import embed; embed()
        last_job_in_category = session.query(Job).\
                               filter(Job.category == user.category).\
                               order_by(Job.id.desc()).first().id
    except AttributeError:
        #print('All categories')
        category = 'all'
        cur = session.execute(sqlalchemy.sql.text("SELECT id FROM job ORDER BY id DESC"))
        #print(cur.fetchone()[0])
        last_job_in_category = cur.fetchone()[0]
        
    # Проверить появилась ли в его категории более новая работа
    if user.last_job < last_job_in_category:

        print('\nNAME:\t\t', user.name)
        print('ID:\t\t', user.tele_id)
        print('LAST JOB\t', user.last_job)
        print('CATEGORY:\t', user.category)
        print('LAST IN CATEGORY', last_job_in_category)

        # Если в категории появилась новая работа, то отправить юзеру её
        if user.category == 'all':
            cur = session.execute(sqlalchemy.sql.text("SELECT id, title, parse_date, price, url, description, category \
                                   FROM job \
                                   WHERE id > {} \
                                   ORDER BY date(parse_date) \
                                   LIMIT 3".format(user.last_job)))
        else:
            cur = session.execute(sqlalchemy.sql.text("SELECT id, title, parse_date, price, url, description \
                                   FROM job \
                                   WHERE category = '{}' AND id > {} \
                                   ORDER BY date(parse_date) \
                                   LIMIT 3".format(user.category, user.last_job)))
        jobs = cur.fetchall()

        for job in jobs:

            # print(len(job))
            dscr = html.escape(job.description[:300]).replace('\xa0', ' ')\
                                               .replace('\n', ' ')\
                                               .replace('\r', ' ')\
                                               .replace('…', ' ')\
                                               .replace('&amp;', ' ')
                               
            #dscr = job.description[:200]
            #print(f'DSCR: {dscr}')
            #print(repr(dscr))
            if not dscr: text_descr = '-'
            else:
                text_descr = str(dscr)

            price = job.price
            if job.price == None: price = '-+-'

            job_date = datetime.strptime(job[2], "%Y-%m-%d %H:%M:%S.%f")

            #print(job[2], job_date)
            #print(type(job_date))
            job_text = "⛏ <b>{}</b>".format(str(job[1].strip())  + \
                       "\n\n💎 Награда: {}".format(price) + \
                       "\n⏳ Публикация: {} #️⃣ {}".format(job_date.strftime("%Y-%m-%d %H:%M:%S"), job[0])) + \
                       "\n📜 {}".format(text_descr) #+ \
                       #"\n🌐 <a href='{}'>Подробнее</a>".format(job.url.strip())
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🌐 Подробнее", url=job.url.strip()))

            try: # Отправить работу юзеру
                print(f'DEBUG: User id - {user.tele_id}')
                bot.send_message(user.tele_id, job_text, parse_mode='HTML', reply_markup=markup, disable_web_page_preview=True)
                print(job_text)
            except telebot.apihelper.ApiException as e:
                print('HTTP ERROR -', e.result.text)
                #if '403' in e.result.text:
                #    # Если юзер отрубил бота, пометить в базе и не пытаться слать
                #    # Поменяв категорию на unsubscribed
                #    print('NEED UNSUBSCRIBE for:', user.tele_id)
                #    session.query(User).\
                #            filter(User.tele_id == user.tele_id).\
                #            update({'category': 'unsubscribed'})
                if '400' in e.result.text:
                    # Если юзера больше не существует (какой-то глюк и много юзеров улетает в эту категорию)
                    print('NEED DELETE for:', user.tele_id)
                    # session.query(User).\
                    #         filter(User.tele_id == user.tele_id).\
                    #         update({'category': 'deleted'})

                # session.commit()
            #print(f'DSCR: {dscr}')
            last_id = job[0]
            print('SENDING: ', last_id, job[4], '\n')
            query = sqlalchemy.sql.text(
                    """
                    SELECT id FROM job ORDER BY id DESC
                    """
            )
            #print(query)

            # TODO Поменять ему последнюю работу
            #cur = session.execute(sqlalchemy.sql.text("SELECT id FROM job ORDER BY id DESC"))
            cur = session.execute(query)
            #print(cur.fetchone()[0])
            query = sqlalchemy.sql.text(
                    """
                    UPDATE users SET last_job = '{}'
                    WHERE tele_id = '{}'
                    """.format(last_id, user.tele_id)
                    
            )
            sended = False
            while not sended:
                try:
                    session.execute(query)
                    session.commit()
                    sended = True
                except sqlite3.OperationalError:
                    sleep(0.300)

############################            
#       break
#   break
############################

session.close()

            # # pause
            # sleep(0.300)

    # break # for sending only to me
