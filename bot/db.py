from sqlalchemy import create_engine, select
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

Base = declarative_base()

from config import DB_PATH

import random
import string
from datetime import date, datetime, timedelta
import os
basedir = os.path.abspath(os.path.dirname(__file__))
# engine = create_engine('sqlite:///:memory:', echo=True)
db_path = 'sqlite:///' + os.path.join(basedir, DB_PATH) + '?charset=utf8mb4'
# engine = create_engine(db_path, echo=True)
engine = create_engine(db_path, echo=False, connect_args={"check_same_thread": False},)
session = scoped_session(sessionmaker(bind=engine))

class Job(Base):
    __tablename__ = 'job'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    date = Column(String)
    price = Column(String)
    url = Column(String)
    raw = Column(String)
    parse_date = Column(DateTime)
    category = Column(String)
    description = Column(String)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    # TODO сохранять и полное имя
    fullname = Column(String)
    password = Column(String)
    tele_id = Column(Integer)

    def add_new(self, user_name, tele_id, ref_id):
        user_row = User(name=user_name, tele_id=tele_id)
        session.add(user_row)
        session.commit()

        Referral().make_reflink(user_row.id, ref_id)
        #Bill().__init__(userid=user_row.id)
        Bill().create(user_row.id)
        
    def get_reflink(self):
        row = session.query(Referral).filter(Referral.id == self.id).first()
        return 'https://t.me/jobs_notify_bot?start=' + row.reflink

    def get_refnick(self):
        myref = session.query(Referral).filter(Referral.id == self.id).first()
        nick = session.query(User).filter(User.id == myref.referrer).first()
        return nick.name

    def get_refcount(self):
        all_refs = session.query(Referral).filter(Referral.referrer == self.id).all()
        return len(all_refs)

    def get_categories(self):
        text = f'DEBUG: Categories for: {self.tele_id} - '
        subs = []
        all_subs = session.query(Subscription).filter(Subscription.user_id == self.tele_id).all()
        for sub in all_subs:
            subs.append([sub.category, sub.last_job])
        text += f'{subs}'
        print(text)
        return subs

    def update_last_job(self, category, job_id):
        text = f'DEBUG: Update last job {job_id} in category {category} - '
        sub = session.query(Subscription).filter(Subscription.category == category, 
                                                 Subscription.user_id == self.tele_id).first()
        if sub:
            text += 'Ok'
        else:
            text += 'Fail\n'
            text += sub

        print(text)
        sub.last_job = job_id

        sended = False
        while not sended:
            try:
                session.commit()
                sended = True
            except sqlite3.OperationalError:
                sleep(0.300)

    def update_subscriptions(self, category):
        all_cats = self.get_categories()
        print(all_cats)
        cats = []
        for cat in all_cats:
            cats.append(cat[0])
        print(cats)

        print(f'DEBUG: Category {category} check in {cats}')
        if category in cats:
            print('DEBUG: Already have this subs')
            # TODO отписка
            self.unsubscribe(category)
        elif 'TESTSUBS' in cats:
            print('DEBUG TESTSUBS')
            stmt = select(Job).order_by(Job.id.desc()).limit(1)
            sub_last = session.scalars(stmt).first()
            print(f'Last id: {sub_last.id}')

            sub_test = session.query(Subscription).filter(Subscription.user_id == self.tele_id,
                                                         Subscription.category == 'TESTSUBS').first()
            sub = session.get(Subscription, [sub_test.id, self.tele_id])
            print(sub.id)
            sub.category = category
            sub.last_job = sub_last.id
        #elif not category in cats:
            #continue
        #    pass
        else:
            stmt = select(Job).order_by(Job.id.desc()).limit(1)
            sub_last = session.scalars(stmt).first()
                
            sub = session.query(Subscription).first()
            print('=============')
            print(sub.id)
            print(sub_last.id)
            new_sub = Subscription(user_id = self.tele_id,
                                   category = category,
                                   last_job = sub_last.id)
            session.add(new_sub)

        while True:
            try:
                session.commit()
                session.close()
                return True
            except sqlite3.OperationalError:
                sleep(0.300)

    def unsubscribe(self, category):
        print('Unsubscribing')
        subs = session.query(Subscription).filter(Subscription.user_id == self.tele_id,
                                                  Subscription.category == category).first()
        print(f'{subs.category} -- {subs.id}')
        session.delete(subs)
        while True:
            try:
                session.commit()
                session.close()
                return True
            except sqlite3.OperationalError:
                sleep(0.300)


class Subscription(Base):
    __tablename__ = 'subs'
    id = Column(Integer, autoincrement=True, primary_key=True)
    user_id = Column(Integer, primary_key=True)
    category = Column(String)
    last_job = Column(Integer)

    # TODO придумать как делать подписку на несколько категорий
    def add_new(self, tele_id, category):
        subs_row = Subscription(user_id=tele_id,
                   last_job=self.get_last_job(tele_id, category),
                   category=category)
        session.add(subs_row)
        session.commit()

    # TODO устарело переписать
    def update(self, tele_id, category):
        session.query(User).\
            filter(User.tele_id == tele_id).\
            update({"last_job": self.get_last_job(tele_id, category),
                    "category": category})

    def get_last_job(self, tele_id, category):
        row = Subscription(user_id=tele_id, category=category)
        if row:
            return row.last_job
        else:
            return None


class Referral(Base):
    __tablename__ = 'referrals'
    # user id
    id = Column(Integer, primary_key=True)
    # referrer id
    referrer = Column(Integer)
    reflink = Column(String, unique=True, nullable=False)
    # how many get from referrals
    refmoney = Column(Integer)

    def make_reflink(self, user_id, ref_id):
        self.id = user_id
        self.referrer = ref_id
        self.reflink = self.generate_reflink(20)
        self.refmoney = 0

        session.add(self)
        session.commit()

    def generate_reflink(self, length):
        # это 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        letters = string.ascii_letters
        return ''.join(random.choice(letters) for _ in range(length))

    # TODO подумать как начислять остаток когда рефералов меньше 10
    def get_ref_parents(self, userid):
        res = []
        ref = self.get_ref_parrent_by_id(userid) 
        res.append(ref.referrer)
        for i in range(0,9):
            print(f'REF parents: {ref.id}, {ref.referrer}')
            ref = self.get_ref_parrent_by_id(ref.referrer) 
            if ref.referrer == 0:
                break
            if ref:
                res.append(ref.referrer)
            else:
                break
        return res

    def get_ref_parrent_by_id(self, userid):
        ref = session.query(Referral).filter(Referral.id==userid).first()
        return ref

class Bill(Base):
    __tablename__ = 'bill'
    # user id
    id = Column(Integer, primary_key=True)
    money_count = Column(Integer)
    payed_till = Column(DateTime, default=datetime.utcnow())
    
    def create(self, userid):
        self.id = userid
        self.money_count = 0
        # TODO прибавлять неделю тестового периода
        self.payed_till = datetime.utcnow()

        session.add(self)
        session.commit()
    
    def payweek(self, userid):
        user = session.query(User).filter(User.tele_id==userid).first()
        bill = session.query(Bill).filter(Bill.id==user.id).first()
        print(f'Bill: {bill.id}, {bill.payed_till}')

        if self.enough_money(userid, 7):
            bill.money_count -= 7
            bill.payed_till = datetime.utcnow() + timedelta(weeks=1)
            session.commit()
            # TODO посчитать реферальные отчисления
            self.pay_to_refs(user.id, 7)
            return True
        else:
            return False

    def paymonth(self, userid):
        user = session.query(User).filter(User.tele_id==userid).first()
        bill = session.query(Bill).filter(Bill.id==user.id).first()
        print(f'Bill: {bill.id}, {bill.payed_till}')

        if self.enough_money(userid, 30):
            bill.money_count -= 30
            bill.payed_till = datetime.utcnow() + timedelta(weeks=4)
            session.commit()
            # TODO посчитать реферальные отчисления
            self.pay_to_refs(user.id, 30)
            return True
        else:
            return False

    def payyear(self, userid):
        user = session.query(User).filter(User.tele_id==userid).first()
        bill = session.query(Bill).filter(Bill.id==user.id).first()
        print(f'Bill: {bill.id}, {bill.payed_till}')

        if self.enough_money(userid, 350):
            bill.money_count -= 350
            bill.payed_till = datetime.utcnow() + timedelta(weeks=53)
            session.commit()
            # TODO посчитать реферальные отчисления
            self.pay_to_refs(user.id, 350)
            return True
        else:
            return False

    def pay_to_refs(self, userid, count):
        parents = Referral().get_ref_parents(userid)
        # На старте 2/3 отдаём в реф программу
        stack = (count/3)*2
        print(stack)
        # TODO выплатить всем рефам
        for parent in parents:
            # Половину стакана отсыпаем старшему рефу 
            print(parent)
            bill = session.query(Bill).filter(Bill.id==parent).first()
            bill.money_count += stack/2
            stack = stack/2

        session.commit()

    def enough_money(self, tguserid, min_money):
        user = session.query(User).filter(User.tele_id==tguserid).first()
        bill = session.query(Bill).filter(Bill.id==user.id).first()
        print(f'enough: {bill.id}')
        if bill.money_count > min_money:
            return True
        else:
            return False

