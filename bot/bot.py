# -*- coding: utf-8 -*-

from db import *
import telebot
import config

bot = telebot.TeleBot(config.token)
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
session = Session()

print("Started")

# Обработчик команд '/start' и '/help'.
@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    start_text = 'hello\nsay /list for site list'
    bot.send_message(message.chat.id, start_text)

@bot.message_handler(commands=['wrk', 'list', 'cmd'])
def handle_list(message):
    text = '\U0001f1f7\U0001f1fa /freelansim -- Last job from freelansim'
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['freelansim', 'f'])
def handle_freelansim(message):
    output = '\u2328 /freelansim_adm - Last jobs for sysadmins\n'+\
             '\u2692 /freelansim_webdev - Last jobs for Web Developers\n'+\
             '\U0001f307 /freelansim_webdis - Last jobs for Web Designers\n'+\
             '\U0001f6e0 /freelansim_dev - Last jobs for Developers'
    bot.send_message(message.chat.id, output)

#"select * from job order by date(parse_date)"
@bot.message_handler(commands=['freelansim_adm', 'fa'])
def handle_freelansim_adm(message):
    cur = session.execute("SELECT * FROM job WHERE category = 'admin' ORDER BY date(parse_date) DESC LIMIT 3")
    jobs = cur.fetchall()
    for job in jobs:
        output = '**' + str(job.id) + '** ' + job[4] + \
                 '\n   \U0001f551 ' + job[2] + \
                 '\n    💰 ' + job[3]
        bot.send_message(message.chat.id, output)

    output = 'You can subscribe for updates in this category by /subscribe_adm'
    bot.send_message(message.chat.id, output)

@bot.message_handler(commands=['freelansim_webdev', 'fw'])
def handle_freelansim_webdev(message):
    cur = session.execute("SELECT * FROM job WHERE category = 'webdev' ORDER BY date(parse_date) DESC LIMIT 3")
    jobs = cur.fetchall()
    for job in jobs:
        output = str(job.id) + ' ' + job[4] + \
                 '\n    \U0001f551 ' + job[2] + \
                 '\n    💰 ' + job[3]
        bot.send_message(message.chat.id, output)

@bot.message_handler(commands=['freelansim_webdis', 'fwd'])
def handle_freelansim_webdis(message):
    cur = session.execute("SELECT * FROM job WHERE category = 'webdis' ORDER BY date(parse_date) DESC LIMIT 3")
    jobs = cur.fetchall()
    for job in jobs:
        output = str(job.id) + ' ' + job[4] + \
                 '\n    \U0001f551 ' + job[2] + \
                 '\n    💰 ' + job[3]
        bot.send_message(message.chat.id, output)

@bot.message_handler(commands=['freelansim_dev', 'fd'])
def handle_freelansim_dev(message):
    cur = session.execute("SELECT * FROM job WHERE category = 'dev' ORDER BY date(parse_date) LIMIT 3")
    jobs = cur.fetchall()
    for job in jobs:
        output = str(job.id) + ' ' + job[4] + \
                 '\n     \U0001f551 ' + job[2] + \
                 '\n    💰 ' + job[3]
        bot.send_message(message.chat.id, output)

@bot.message_handler(commands=['subscribe_adm', 'sa'])
def handle_freelansim_adm_subscribe(message):
    # if user doesn't exist
    if not user_exist(message.chat.id):
        # can add new subscription
        user_row = User(name=message.from_user.username,
                        tele_id=message.from_user.id,
                        last_job=get_last_job('admin'),
                        category='admin')
        session.add(user_row)
        session.commit()
    else: # else can update existing subscription
        sql = "UPDATE users SET last_job = '{}', category = '{}' \
               WHERE tele_id = '{}'".format(get_last_job('admin'), 'admin', message.from_user.id)
        session.execute(sql)
        session.commit()

    output = 'Chat ID: ' + str(message.chat.id) + \
             '\nUser ID: ' + str(message.from_user.id) + \
             '\nNick: ' + str(message.from_user.username) + \
             '\nLast JOB ID in this category: ' + str(get_last_job('admin')) + \
             '\nYou subscribed on Administration category'
    bot.send_message(message.chat.id, output)

@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):  # Название функции не играет никакой роли, в принципе
    print(message.chat.id)
    print(message)
    if not message.chat.id == config.freelance_chan_id:
        text = str(message.chat.id) + '\n' + message.text
        bot.send_message(message.chat.id, text)

#####################################################################
def user_exist(user_id):
    cur = session.execute("SELECT id FROM users WHERE tele_id = '{}'".format(user_id))
    output = 'Checked ID: {} \
             \nExisted User ID: {} \
             \n__DEBUG__ _MESSAGE_'.format(user_id, cur.fetchone()[0])
    bot.send_message(user_id, output)
    if cur.fetchone(): return True
    return False

def get_last_job(category):
    cur = session.execute("SELECT id FROM job WHERE category = '{}' ORDER BY id DESC".format(category))
    return cur.fetchone()[0]

if __name__ == '__main__':
    bot.polling(none_stop=True)
