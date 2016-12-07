# -*- coding: utf-8 -*-

import json
import config
import urllib, urllib2
OPENER = urllib2.build_opener()

from time import sleep
#https://api.telegram.org/bot{id}/sendMessage?chat_id={user_id}&text={text}&disable_web_page_preview

from db import *
from sqlalchemy.orm import sessionmaker, scoped_session
session = scoped_session(sessionmaker(bind=engine))


# TODO Получить список юзеров
cur = session.execute("SELECT * FROM users")
users = cur.fetchall()
print(users)

# У каждого пользователя
for user in users:
    # Получить последнюю работу
    # TODO Проверить появилась ли в его категории более новая работа
    username = user[1]
    print('Jobs for ' + username)
    print('Last job id: ' + str(user[5]))
    user_tele_id = user[4]
    saved_last_job_id = user[5]
    category = user[6]
    try:
        cur = session.execute("SELECT id FROM job WHERE category = '{}' ORDER BY id DESC LIMIT 100".format(category))
        print(cur.fetchone()[0])
        last_job_in_category = cur.fetchone()[0]
    except TypeError:
        print 'All categories'
        category = 'all'
        cur = session.execute("SELECT id FROM job ORDER BY id DESC")
        print(cur.fetchone()[0])
        last_job_in_category = cur.fetchone()[0]

    if saved_last_job_id < last_job_in_category:
        # TODO Если да, то отправить ему её
        if category == 'all':
            cur = session.execute("SELECT id, title, parse_date, price, url \
                                   FROM job \
                                   WHERE id > {} \
                                   ORDER BY date(parse_date) \
                                   LIMIT 3".format(saved_last_job_id))
        else:
            cur = session.execute("SELECT id, title, parse_date, price, url \
                                   FROM job \
                                   WHERE category = '{}' AND id > {} \
                                   ORDER BY date(parse_date) \
                                   LIMIT 3".format(category, saved_last_job_id))
        jobs = cur.fetchall()
        for job in jobs:
            job_text = "{} <b>{}</b>".format(str(job[0]),job[1].encode('utf-8').strip()) + \
                       "\n    🕑 {}".format(job[2]) + \
                       "\n    💰 {}".format(job[3].encode('utf-8').strip()) + \
                       "\n    🕸 <u>{}</u>".format(job[4].encode('utf-8').strip())

            url = "https://api.telegram.org/bot{}/sendMessage".format(config.token)
            req = urllib2.Request(url)
            req.add_header("Accept", "application/json")
            req.add_header('User-agent', 'FreeLance Bot')

            data = { 'chat_id': user_tele_id, 'disable_web_page_preview': 'true', 'parse_mode': 'HTML', 'text': job_text}
            req.add_data(json.dumps(data))

            try:
                last_id = job[0]
                print 'SENDING: ', last_id, url, '\n', job_text
            except:
                cur = session.execute("SELECT id \
                                       FROM job \
                                       ORDER BY id DESC \
                                       LIMIT 1")
                #last_id =  cur.fetchone()[0]
                last_id = saved_last_job_id
                print "Failed getting last job id", last_id

            try:
                OPENER.open(req).read()
                # TODO Поменять ему последнюю работу
                sql = "UPDATE users SET last_job = '{}' \
                       WHERE tele_id = '{}'".format(last_id, user_tele_id)
                session.execute(sql)
                session.commit()
            except urllib2.HTTPError, e:
                print 'HTTP ERROR -', e
            sleep(0.350)


