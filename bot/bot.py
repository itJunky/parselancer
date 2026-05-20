# -*- coding: utf-8 -*-

from db import *
import time
from datetime import datetime, timezone
import telebot
from telebot import types
import config

bot = telebot.TeleBot(config.token_prod)

try:
    from tun_config import CONFIG
    from tunnel_telebot import SSHTunnelTeleBotAPI
    from telebot import apihelper
    _tunnel = SSHTunnelTeleBotAPI(CONFIG)
    _tunnel.start()
    apihelper.proxy = {'http': _tunnel._build_proxy_url(), 'https': _tunnel._build_proxy_url()}
    print("SSH tunnel started")
except Exception as _e:
    print(f"Tunnel not available, using direct connection: {_e}")

from sqlalchemy import text
from sqlalchemy.orm import sessionmaker, scoped_session
session = scoped_session(sessionmaker(bind=engine))

from get_stats import get_stats_by, get_stats_subscribers

# Обработчик команд '/start' и '/help'.
@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message, callid=None):
    print(f'Have new user? {message.chat.id}')
    if callid:
        bot.answer_callback_query(callid, "Вы выбрали Меню")
    ref_id = 0 # Если рефералов нет
    try:
        reflink = message.text.split('/start ')[1]
        ref_id, ref_name = get_referral_id_by_reflink(reflink)
        print(f'REF: {reflink}')
        print(f'ID: {ref_id}')
        start_text = f'Похоже ты пришёл от {ref_name}.\n'
    except Exception as e:
        #start_text = f'Мы уже познакомились\n'
        start_text = f'Рад приветствовать тебя вновь, дорогой фрилансер. 🙏\n'

    # Проверить что юзер новый.
    if user_exist(message.chat.id):
        print('Юзер уже есть')
        start_text += 'Для оформления подписки необходимо пополнить баланс.\n'
    # Сообщить о тестовом периоде
    else:
        print('Юзерa ещё нет')
        User().add_new(message.from_user.username, message.from_user.id, ref_id)
        Subscription().add_new(message.from_user.id, 'TESTSUBS')
        # TODO функция создания юзера (сохранение в БД, создание рефлинка)
        start_text += 'Рад сообщить, что тебе доступен тестовый период длительностью в 7 дней.\n'
        start_text += 'За это время ты сможешь изучить доступные биржи и категории работ, а так же подписаться на уведомления по ним в случае появления новых заданий.'
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
    elif call.data == 'menu':
        handle_start_help(call.message, call.id) 
    elif call.data == 'payment':
        payments_handler(call.message.chat.id, call.id)
    elif call.data == 'payweek':
        payweek_handler(call.message.chat.id, call.id)
    elif call.data == 'paymonth':
        paymonth_handler(call.message.chat.id, call.id)
    elif call.data == 'payyear':
        payyear_handler(call.message.chat.id, call.id)
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
    elif call.data == 'referral':
        referral_handler(call.message.chat.id, call.id)
    elif call.data == 'dev':
        sub_dev_handler(call.message.chat.id, call.id)
    elif call.data == 'webdev':
        sub_webdev_handler(call.message.chat.id, call.id)
    elif call.data == 'admin':
        sub_admin_handler(call.message.chat.id, call.id)
    elif call.data == 'infosec':
        sub_infosec_handler(call.message.chat.id, call.id)
    elif call.data == 'qa':
        sub_qa_handler(call.message.chat.id, call.id)
    elif call.data == 'wrining':
        sub_writing_handler(call.message.chat.id, call.id)
    elif call.data == 'design':
        sub_design_handler(call.message.chat.id, call.id)
    elif call.data == 'webdis':
        sub_webdis_handler(call.message.chat.id, call.id)


def subscriptions_handler(userid, callid):
    bot.answer_callback_query(callid, "Вы выбрали Подписки")

    btns = [[ types.InlineKeyboardButton("📂 Выбрать категории", callback_data='category'),
             types.InlineKeyboardButton("🏢 Выбрать биржи", callback_data='jobcenter')
    ]]
    btns.extend([[
        types.InlineKeyboardButton("⬅️ Назад", callback_data='menu'),
        types.InlineKeyboardButton("💳 Меню", callback_data='menu')
    ]])
    markup = types.InlineKeyboardMarkup(btns)

    bot.send_message(userid, "Информация о подписках...", reply_markup=markup)


def payments_handler(userid, callid):
    bot.answer_callback_query(callid, "Вы выбрали Оплату")
    # Вывод баланса в тугриках
    # Отображение даты до которой оплачен тариф
    user = session.query(User).filter(User.tele_id == userid).first()
    bill = session.query(Bill).filter(Bill.id == user.id).first()
    payed_till = str(bill.payed_till).split(".")[0]
    # Подсвечивать красным или зелёным, если оплачено
    text = 'Информация о балансе.\n\n' + \
           f'Баланс: {bill.money_count} ➿ фланков\n' + \
           f'Оплачено до: {payed_till}'  

    markup_list = [
            [
                types.InlineKeyboardButton("💳 Картой", callback_data='creditcard'),
                types.InlineKeyboardButton("🏵 Криптой", callback_data='cryptcoin'),
                types.InlineKeyboardButton("⭐️ ТГ звёздами", callback_data='tgstars')
            ]]
    if bill.payed_till.astimezone(timezone.utc) < datetime.now(timezone.utc):
        markup_list.extend([
            [
                types.InlineKeyboardButton("--- Выберите подписку: ---", callback_data=' ')
            ],
            [
                types.InlineKeyboardButton("На неделю (➿ 7)", callback_data='payweek'),
                types.InlineKeyboardButton("На месяц (➿ 25)", callback_data='paymonth'),
                types.InlineKeyboardButton("На год (➿ 350)", callback_data='payyear')
            ]
        ])
    else:
        print('DOESNT NEED TO PAY')
        print(f'{bill.payed_till.astimezone(timezone.utc)} < {datetime.now(timezone.utc)}')

    markup_list.extend([
            [
                types.InlineKeyboardButton("📇 Реферальная программа", callback_data='referral')
            ],
            [
                types.InlineKeyboardButton("⬅️ Назад", callback_data='menu'),
                types.InlineKeyboardButton("💳 Меню", callback_data='menu'),
            ]
    ])

    markup = types.InlineKeyboardMarkup(markup_list)
    bot.send_message(userid, text, reply_markup=markup)

def payweek_handler(userid, callid):
    bot.answer_callback_query(callid, "Приобретаю неделю премиума")
    Bill().payweek(userid)
    payments_handler(userid, callid)

def paymonth_handler(userid, callid):
    bot.answer_callback_query(callid, "Приобретаю месяц премиума")
    Bill().paymonth(userid)
    payments_handler(userid, callid)

def payyear_handler(userid, callid):
    bot.answer_callback_query(callid, "Приобретаю год премиума")
    Bill().payyear(userid.id)
    payments_handler(userid, callid)

def referral_handler(tguserid, callid):
    bot.answer_callback_query(callid, "Выбрана реферрвльная прогграмма")
    # получить ник моего реферала
    user = session.query(User).filter(User.tele_id == tguserid).first()
    nick_name = user.get_refnick()
    # TODO получить число моих рефералов
    ref_count = user.get_refcount()
    # TODO показать сколько закинули все рефералы
    money_get = 0
    # показать мою реф. ссылку
    reflink = user.get_reflink()
    text = f'Меня привёл: {nick_name}\n' + \
           f'Моих реферралов: {ref_count}\n' + \
           'Получено от реферралов: тугрики\n' + \
           f'Моя реферральная ссылка: {reflink}'

    markup = types.InlineKeyboardMarkup([
        [
            types.InlineKeyboardButton("⬅️ Назад", callback_data='payment')
        ]
    ])

    bot.send_message(tguserid, text, reply_markup=markup)


def about_handler(userid, callid):
    bot.answer_callback_query(callid, "Вы выбрали О боте")
    
    markup = types.InlineKeyboardMarkup(row_width=3)
    btn1 = types.InlineKeyboardButton("📢 Канал", url='https://t.me/FreeLanceGet')
    btn2 = types.InlineKeyboardButton("👥 Чат", url='https://t.me/getFreelanceChat')
    btn3 = types.InlineKeyboardButton("👨‍👧‍👧 Связаться с автором", callback_data='feedback')
    markup.add(btn1, btn2, btn3)

    bot.send_message(userid, "Информация о боте...", reply_markup=markup)


def category_handler(tguserid, callid):
    bot.answer_callback_query(callid, 'Выбранo Категории')
    print(tguserid)
    user = session.query(User).filter(User.tele_id == tguserid).first()
    print(user.id)
    all_cats = []
    for cat in user.get_categories():
        all_cats.append(cat[0])

    if 'dev' in all_cats:
        l1 = [types.InlineKeyboardButton('+Development', callback_data='dev')]
    else:
        l1 = [types.InlineKeyboardButton('-Development', callback_data='dev')]

    if 'webdev' in all_cats:
        l1.append(types.InlineKeyboardButton('+Web Development', callback_data='webdev'))
    else:
        l1.append(types.InlineKeyboardButton('-Web Development', callback_data='webdev'))

    if 'admin' in all_cats:
        l1.append(types.InlineKeyboardButton('+Admin', callback_data='admin'))
    else:
        l1.append(types.InlineKeyboardButton('-Admin', callback_data='admin'))

    if 'infosec' in all_cats:
        l1.append(types.InlineKeyboardButton('+InfoSec', callback_data='infosec'))
    else:
        l1.append(types.InlineKeyboardButton('-InfoSec', callback_data='infosec'))
        
    if 'qa' in all_cats:
        l2 = [types.InlineKeyboardButton('+Q & A', callback_data='qa')]
    else:
        l2 = [types.InlineKeyboardButton('-Q & A', callback_data='qa')]

    if 'writing' in all_cats:
        l2.append(types.InlineKeyboardButton('+Writing', callback_data='writing'))
    else:
        l2.append(types.InlineKeyboardButton('-Writing', callback_data='writing'))

    if 'design' in all_cats:
        l2.append(types.InlineKeyboardButton('+Design', callback_data='design'))
    else:
        l2.append(types.InlineKeyboardButton('-Design', callback_data='design'))

    if 'webdis' in all_cats:
        l2.append(types.InlineKeyboardButton('+Web Design', callback_data='webdis'))
    else:
        l2.append(types.InlineKeyboardButton('-Web Design', callback_data='webdis'))

    l3 = [
        types.InlineKeyboardButton("⬅️ Назад", callback_data='subscriptions'),
        types.InlineKeyboardButton("💳 Меню", callback_data='menu')
    ]
    markup = types.InlineKeyboardMarkup([l1, l2, l3])
    bot.send_message(tguserid, 'Выберите подходящую категорию работ, о которых хотите узнавать первым.', reply_markup=markup)

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


def get_referral_id_by_reflink(reflink: str):
    referral = session.query(Referral).filter(Referral.reflink == reflink).first()
    if referral:
        user = session.query(User).filter(User.id == referral.id).first()
        return referral.id, user.name
    else:
        return None

def sub_dev_handler(tguserid, callid):
    bot.answer_callback_query(callid, "Вы Подписались на Development")

    user = session.query(User).filter(User.tele_id == tguserid).first()
    user.update_subscriptions('dev')

    category_handler(tguserid, callid)

def sub_webdev_handler(tguserid, callid):
    bot.answer_callback_query(callid, "Вы Подписались на Web Development")

    user = session.query(User).filter(User.tele_id == tguserid).first()
    user.update_subscriptions('webdev')

    category_handler(tguserid, callid)

def sub_admin_handler(tguserid, callid):
    bot.answer_callback_query(callid, "Вы Подписались на Administration")

    user = session.query(User).filter(User.tele_id == tguserid).first()
    user.update_subscriptions('admin')

    category_handler(tguserid, callid)

def sub_infosec_handler(tguserid, callid):
    bot.answer_callback_query(callid, "Вы Подписались на InfoSec")

    user = session.query(User).filter(User.tele_id == tguserid).first()
    user.update_subscriptions('infosec')

    category_handler(tguserid, callid)

def sub_qa_handler(tguserid, callid):
    bot.answer_callback_query(callid, "Вы Подписались на Q & A")

    user = session.query(User).filter(User.tele_id == tguserid).first()
    user.update_subscriptions('qa')

    category_handler(tguserid, callid)

def sub_writing_handler(tguserid, callid):
    bot.answer_callback_query(callid, "Вы Подписались на CopyWriting")

    user = session.query(User).filter(User.tele_id == tguserid).first()
    user.update_subscriptions('writing')

    category_handler(tguserid, callid)

def sub_design_handler(tguserid, callid):
    bot.answer_callback_query(callid, "Вы Подписались на Design")

    user = session.query(User).filter(User.tele_id == tguserid).first()
    user.update_subscriptions('design')

    category_handler(tguserid, callid)

def sub_webdis_handler(tguserid, callid):
    bot.answer_callback_query(callid, "Вы Подписались на Web Design")

    user = session.query(User).filter(User.tele_id == tguserid).first()
    user.update_subscriptions('webdis')

    category_handler(tguserid, callid)

### OLD CODE ###
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


#####################################################################
def user_exist(user_id):
    cur = session.execute(text("SELECT id FROM users WHERE tele_id = '{}'".format(user_id)))
    try:
        output = 'Checked ID: {} \
                 \nExisted User ID: {} \
                 \n__DEBUG__ __MESSAGE__'.format(user_id, cur.fetchone()[0])
        # Fetch but send only if DEBUG
       # bot.send_message(user_id, output)
        return True
    except TypeError: # if not in DB
        return False


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

    #from IPython import embed

    while True:
        print("ParceLancer Started")
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(e.with_traceback(True))
            print(f'Сломался: {e} : {e.__cause__}')
            #embed()

        time.sleep(1)
