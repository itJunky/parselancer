# -*- coding: utf-8 -*-

from db import *
import time
import telebot
from telebot import types
import config

bot = telebot.TeleBot(config.token_prod)

from sqlalchemy import text
from sqlalchemy.orm import sessionmaker, scoped_session
session = scoped_session(sessionmaker(bind=engine))

from get_stats import get_stats_by, get_stats_subscribers


text = '''
Привет друг!

Бот для уведомлений, который не уведомляет ни о чём, совсем бесполезен. )
Поэтому тебе стоит выбрать категорию, о работе в которой будут приходить уведомления. Жми /start и забудь о том, что надо перезагружать странички 15ти бирж, тратя на это всё своё свободное время в ожидании нового заказа.

Как автор бота, буду рад так же и обратной связи о том, почему ты до сих пор не сделал такого выбора или о чём-то ещё, что бросилось тебе в глаза. В меню "О боте" можно найти чат или обратную связь.
'''

users = session.query(User).all()
for user in users:
    all_categories = user.get_categories()
    for category, last_job in all_categories:
        if category == 'TESTSUBS':
            try:
                sent = bot.send_message(user.tele_id, text)
            except Exception as e:
                print(f'Error when sending message: {e}')

