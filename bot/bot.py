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

# Обработчик команд '/start' и '/help'.
@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    print('Have new user')
    try:
        referral = message.text.split('/start ')[1]
        print(referral)
        start_text = f'Похоже ты пришёл от {referral}.\n'
    except Exception as e:
        start_text = f'Мы уже познакомились\n'

    # Проверить что юзер новый.
    if user_exist(message.chat.id):
        start_text += 'Для оформления подписки необходимо пополнить баланс.\n'
    # Сообщить о тестовом периоде
    else:
        print('else here')
        start_text += 'Рад сообщить, что Вам доступен тестовый период длительностью в 7 дней.\n'
        start_text += 'За это время Вы можете изучить доступные биржи и категории работ, а так же подписаться на уведомления по ним в случае появления новых заданий.'
    # Либо предложить пополнить баланс

    markup = types.InlineKeyboardMarkup(row_width=3)
    btn1 = types.InlineKeyboardButton("📋 Подписки", callback_data='subscriptions')
    btn2 = types.InlineKeyboardButton("💵 Оплата", callback_data='payment')
    btn3 = types.InlineKeyboardButton("🪪 О боте", callback_data='about')
    markup.add(btn1, btn2, btn3)

    bot.send_message(message.chat.id, start_text, reply_markup=markup)


# === Приём сообщений от пользователей ===
@bot.message_handler(func=lambda message: message.chat.id != config.SUPPORT_CHAT_ID)
def handle_user_message(message):
    # Пересылаем сообщение в чат поддержки
    forwarded = bot.forward_message(config.SUPPORT_CHAT_ID, message.chat.id, message.id)

    # Сохраняем связь: id пересланного сообщения -> id пользователя
    message_to_user[forwarded.id] = message.chat.id

    bot.reply_to(message, "Спасибо за ваше сообщение! Мы постараемся ответить как можно скорее.")


# === Обработка ответов в чате поддержки ===
@bot.message_handler(func=lambda message: message.chat.id == config.SUPPORT_CHAT_ID and message.reply_to_message is not None)
def handle_support_reply(message):
    # Получаем ID сообщения, на которое ответили
    replied_message_id = message.reply_to_message.id

    # Ищем ID пользователя, которому нужно отправить ответ
    if replied_message_id in message_to_user:
        user_id = message_to_user[replied_message_id]

        try:
            # Отправляем текст ответа пользователю
            bot.send_message(user_id, f"Ответ от тех. поддержки бота:\n\n{message.text}")
        except Exception as e:
            bot.send_message(SUPPORT_CHAT_ID, f"[Ошибка] Не удалось отправить ответ пользователю: {e}")
    else:
        bot.send_message(SUPPORT_CHAT_ID, "[Ошибка] Не найдено сообщение для ответа.")


# Обработчик кнопок
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == 'subscriptions':
        subscriptions_handler(call.message.chat.id, call.id)
    elif call.data == 'payment':
        payments_handler(call.message.chat.id, call.id)
    elif call.data == 'about':
        about_handler(call.message.chat.id, call.id)
    elif call.data == 'category':
        category_handler(call.message.chat.id, call.id)
    elif call.data == 'jobcenter':
        jobcenter_handler(call.message.chat.id, call.id)
    elif call.data == 'feedback':
        feedback_handler(call.message.chat.id, call.id)
    elif call.data == 'creditcard':
        creditcard_handler(call.message.chat.id, call.id)
    elif call.data == 'cryptcoin':
        cryptcoin_handler(call.message.chat.id, call.id)
    elif call.data == 'tgstars':
        tgstars_handler(call.message.chat.id, call.id)


def subscriptions_handler(userid, callid):
    bot.answer_callback_query(callid, "Вы выбрали Подписки")

    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("📂 Выбрать категории", callback_data='category')
    btn2 = types.InlineKeyboardButton("🏢 Выбрать биржи", callback_data='jobcenter')
    markup.add(btn1, btn2)

    bot.send_message(userid, "Информация о подписках...", reply_markup=markup)

def payments_handler(userid, callid):
    bot.answer_callback_query(callid, "Вы выбрали Оплату")

    markup = types.InlineKeyboardMarkup(row_width=3)
    btn1 = types.InlineKeyboardButton("💳 Картой", callback_data='creditcard')
    btn2 = types.InlineKeyboardButton("🏵 Криптой", callback_data='cryptcoin')
    btn3 = types.InlineKeyboardButton("⭐️ ТГ звёздами", callback_data='tgstars')
    markup.add(btn1, btn2, btn3)

    bot.send_message(userid, "Информация об оплате...", reply_markup=markup)

def about_handler(userid, callid):
    bot.answer_callback_query(callid, "Вы выбрали О боте")
    
    markup = types.InlineKeyboardMarkup(row_width=3)
    btn1 = types.InlineKeyboardButton("📢 Канал", url='https://t.me/FreeLanceGet')
    btn2 = types.InlineKeyboardButton("👥 Чат", url='https://t.me/getFreelanceChat')
    btn3 = types.InlineKeyboardButton("👨‍👧‍👧 Связаться с автором", callback_data='feedback')
    markup.add(btn1, btn2, btn3)

    bot.send_message(userid, "Информация о боте...", reply_markup=markup)

def category_handler(userid, callid):
    bot.answer_callback_query(callid, 'Выбранo Категории')
    bot.send_message(userid, 'Выберите подходящую категорию работ, о которых хтите узнавать первым.')

def jobcenter_handler(userid, callid):
    bot.answer_callback_query(callid, 'Выбрана Обратная связь')
    bot.send_message(userid, 'Выберите биржи, с которых хотите получать актуальные задачи.')

# Словарь для хранения связи: {message_id_в_чате_поддержки: user_id}
# TODO перенести в БД
message_to_user = {}
def feedback_handler(userid, callid):
    bot.answer_callback_query(callid, 'Выбрана Обратная связь')
    bot.send_message(userid, 'Я готов передать все ваши сообщения своему владельцу.')

def creditcard_handler(userid, callid):
    bot.answer_callback_query(callid, 'Выбрана Оплата картой')
    bot.send_message(userid, 'Этот функционал ещё разрабатывается.')

def cryptcoin_handler(userid, callid):
    bot.answer_callback_query(callid, 'Выбрана Оплата криптой')
    bot.send_message(userid, 'Этот функционал ещё разрабатывается.')

def tgstars_handler(userid, callid):
    bot.answer_callback_query(callid, 'Выбрана Оплата ТГ звёздами')
    bot.send_message(userid, 'Этот функционал ещё разрабатывается.')




### OLD CODE ###

@bot.message_handler(commands=['wrk', 'list', 'cmd'])
def handle_list(message):
    if message.chat.id < 0:
        bot.send_message(message.chat.id, 'Please use private messages')
        return
    text = '\U0001f1f7\U0001f1fa /freelansim -- Last job from freelansim.ru\n'+\
           '\U0001f1f7\U0001f1fa /freelancehunt -- Last job from freelansim.ru\n'+\
           '\U0001f1fa\U0001f1f8 /freelancecom -- Last job from freelance.com'

    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['stats', 'st'])
def handle_stats(message):
    
    text = '📈 Statistics by category of job'
    text = text+'\n'+'``` Time            ( 1   /7   /30 days)```'
    categories = ['admin', 'webdev', 'dev', 'webdis']
    for category in categories:
        # print(category)
        day, week, month = get_stats_by(category)
        text = text+'\n'+'``` Jobs in {:8s}: {:,d}  {:,d}  {:,d}```'.format(category, day, week, month) 
        # print(text)

    text = text+'\n👥 '+'_Subscribed users:_ *'+str(get_stats_subscribers())+'*'
    print(text)
    bot.send_message(message.chat.id, text, parse_mode='MARKDOWN')


@bot.message_handler(commands=['freelancecom', 'fc'])
def handle_freelancecom(message):
    if message.chat.id < 0:
        bot.send_message(message.chat.id, 'Please use private messages')
        return
    output = '\u2328 /freelance_adm - Last jobs for sysadmins\n'+\
             '\u2692 /freelance_webdev - Last jobs for Web Developers\n'+\
             '\U0001f307 /freelance_webdis - Last jobs for Web Designers\n'+\
             '\U0001f6e0 /freelance_dev - Last jobs for Developers'
    bot.send_message(message.chat.id, output)

@bot.message_handler(commands=['freelansim', 'fr'])
def handle_freelansim(message):
    if message.chat.id < 0:
        bot.send_message(message.chat.id, 'Please use private messages')
        return
    output = '\u2328 /freelansim_adm - Last jobs for sysadmins\n'+\
             '\u2692 /freelansim_webdev - Last jobs for Web Developers\n'+\
             '\U0001f307 /freelansim_webdis - Last jobs for Web Designers\n'+\
             '\U0001f6e0 /freelansim_dev - Last jobs for Developers'
    bot.send_message(message.chat.id, output)

@bot.message_handler(commands=['freelancehunt', 'fch'])
def handle_freelancehunt(message):
    if message.chat.id < 0:
        bot.send_message(message.chat.id, 'Please use private messages')
        return
    output = '\u2328 /freelancehunt_adm - Last jobs for sysadmins\n'+\
             '\u2692 /freelancehunt_webdev - Last jobs for Web Developers\n'+\
             '\U0001f307 /freelancehunt_webdis - Last jobs for Web Designers\n'+\
             '\U0001f6e0 /freelancehunt_dev - Last jobs for Developers'
    bot.send_message(message.chat.id, output)


@bot.message_handler(commands=['freelansim_adm', 'fra'])
def handle_freelansim_adm(msg):
    send_jobs('freelansim', 'admin', msg.chat.id)

@bot.message_handler(commands=['freelansim_webdev', 'frw'])
def handle_freelansim_webdev(msg):
    send_jobs('freelansim', 'webdev', msg.chat.id)

@bot.message_handler(commands=['freelansim_webdis', 'frwd'])
def handle_freelansim_webdis(msg):
    send_jobs('freelansim', 'webdis', msg.chat.id)

@bot.message_handler(commands=['freelansim_dev', 'frd'])
def handle_freelansim_dev(msg):
    send_jobs('freelansim', 'dev', msg.chat.id)

@bot.message_handler(commands=['freelance_adm', 'fca'])
def handle_freelansim_adm(msg):
    send_jobs('freelance.com', 'admin', msg.chat.id)

@bot.message_handler(commands=['freelance_webdev', 'fcw'])
def handle_freelance_webdev(msg):
    send_jobs('freelance', 'webdev', msg.chat.id)

@bot.message_handler(commands=['freelance_webdis', 'fcwd'])
def handle_freelance_webdis(msg):
    send_jobs('freelance', 'webdis', msg.chat.id)

@bot.message_handler(commands=['freelance_dev', 'fcd'])
def handle_freelance_dev(msg):
    send_jobs('freelance', 'dev', msg.chat.id)

@bot.message_handler(commands=['freelancehunt_adm', 'fcha'])
def handle_freelancehunt_dev(msg):
    send_jobs('freelancehunt', 'admin', msg.chat.id)

@bot.message_handler(commands=['freelancehunt_webdev', 'fchw'])
def handle_freelancehunt_dev(msg):
    send_jobs('freelancehunt', 'webdev', msg.chat.id)

@bot.message_handler(commands=['freelancehunt_webdis', 'fchwd'])
def handle_freelancehunt_dev(msg):
    send_jobs('freelancehunt', 'webdis', msg.chat.id)

@bot.message_handler(commands=['freelancehunt_dev', 'fchd'])
def handle_freelancehunt_dev(msg):
    send_jobs('freelancehunt', 'dev', msg.chat.id)

@bot.message_handler(commands=['subscribe_adm', 'sa'])
def handle_admin_subscribe(message):
    # if user doesn't exist
    if not user_exist(message.from_user.id):
        Subscription().add_new(message.from_user.username, message.from_user.id, 'admin', session)
    else: # else update existing subscription
        try:
            Subscription().update(message.from_user.id, 'admin', session)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    output = 'Chat ID: ' + str(message.chat.id) + \
             '\nUser ID: ' + str(message.from_user.id) + \
             '\nNick: ' + str(message.from_user.username) + \
             '\nLast JOB ID in this category: ' + str(get_last_job('admin')) + \
             '\n*You subscribed on Administration category*'
    bot.send_message(message.chat.id, output)

@bot.message_handler(commands=['subscribe_dev', 'sd'])
def handle_develop_subscribe(message):
    # if user doesn't exist
    if not user_exist(message.from_user.id):
        Subscription().add_new(message.from_user.username, message.from_user.id, 'dev', session)
    else: # else update existing subscription
        try:
            Subscription().update(message.from_user.id, 'dev', session)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    output = 'Chat ID: ' + str(message.chat.id) + \
             '\nUser ID: ' + str(message.from_user.id) + \
             '\nNick: ' + str(message.from_user.username) + \
             '\nLast JOB ID in this category: ' + str(get_last_job('dev')) + \
             '\nYou subscribed on Development category'
    bot.send_message(message.chat.id, output)

@bot.message_handler(commands=['subscribe_webdev', 'swd'])
def handle_webdevelop_subscribe(message):
    # if user doesn't exist
    if not user_exist(message.from_user.id):
        Subscription().add_new(message.from_user.username, message.from_user.id, 'webdev', session)
    else: # else update existing subscription
        try:
            Subscription().update(message.from_user.id, 'webdev', session)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    output = 'Chat ID: ' + str(message.chat.id) + \
             '\nUser ID: ' + str(message.from_user.id) + \
             '\nNick: ' + str(message.from_user.username) + \
             '\nLast JOB ID in this category: ' + str(get_last_job('webdev')) + \
             '\nYou subscribed on Web Development category'
    bot.send_message(message.chat.id, output)

@bot.message_handler(commands=['subscribe_webdis', 'swds'])
def handle_webdesign_subscribe(message):
    # if user doesn't exist
    if not user_exist(message.from_user.id):
        Subscription().add_new(message.from_user.username, message.from_user.id, 'webdis', session)
    else: # else update existing subscription
        try:
            Subscription().update(message.from_user.id, 'webdis', session)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    output = 'Chat ID: ' + str(message.chat.id) + \
             '\nUser ID: ' + str(message.from_user.id) + \
             '\nNick: ' + str(message.from_user.username) + \
             '\nLast JOB ID in this category: ' + str(get_last_job('webdis')) + \
             '\nYou subscribed on Web Design category'
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
    cur = session.execute(text("SELECT id FROM users WHERE tele_id = '{}'".format(user_id)))
    try:
        output = 'Checked ID: {} \
                 \nExisted User ID: {} \
                 \n__DEBUG__ __MESSAGE__'.format(user_id, cur.fetchone()[0])
        bot.send_message(user_id, output)
        return True
    except TypeError: # if not in DB
        return False

class Subscription(object):
    def add_new(self, user_name, tele_id, category, session):
        # add new subscription
        user_row = User(name=user_name,
                        tele_id=tele_id,
                        last_job=get_last_job(category),
                        category=category)
        session.add(user_row)
        session.commit()

    def update(self, tele_id, category, session):
        session.query(User).\
            filter(User.tele_id == tele_id).\
            update({"last_job": get_last_job(category),
                    "category": category})

def get_last_job(category):
    cur = session.execute("SELECT id \
                           FROM job \
                           WHERE category = '{}' \
                           ORDER BY id DESC \
                           LIMIT 1".format(category))
    return cur.fetchone()[0]

def send_jobs(site, category, user_id):
    output = fetch_jobs(site, category)
    for msg in output:
        bot.send_message(user_id, msg, parse_mode='HTML', disable_web_page_preview=True)

    output = 'You can subscribe for updates in this category by /subscribe_{}'.format(category) + \
             '\nOnly one category can be subscribed'
    bot.send_message(user_id, output)

def fetch_jobs(site, category):
    output = []
    messages_limit = 5
    cur = session.execute("SELECT * \
                           FROM job \
                           WHERE url like '%{}%' \
                           AND category = '{}' \
                           ORDER BY id \
                           DESC LIMIT {}".format(site, category, messages_limit))
    jobs = cur.fetchall()
    for job in jobs:
        text = str(job.description)
        if text == None: text = '-'
        
        price = job.price
        if job.price == None: price = '-+-'

        output.append("    🛠 <b>{}</b>".format(str(job.title))  + \
                    "\n    🕰 {} #️⃣ {}".format(job[7], job[0]) + \
                    "\n    💰 {}".format(price) + \
                    "\n    🌐 <a href='{}'>Подробнее</a>".format(job[4]) + \
                    "\n    🗒 {}".format(text))

    return output


if __name__ == '__main__':

    while True:
        print("ParceLancer Started")
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(f'Сломался: {e} : {e.__cause__}')

        time.sleep(1)
