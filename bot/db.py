from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

Base = declarative_base()

from config import DB_PATH

import random
import string
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


class Subscription(Base):
    __tablename__ = 'subs'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
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
