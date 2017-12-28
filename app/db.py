from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

import os
basedir = os.path.abspath(os.path.dirname(__file__))
# engine = create_engine('sqlite:///:memory:', echo=True)
db_path = 'sqlite:///' + os.path.join(basedir, '../jobs.db')
# engine = create_engine(db_path, echo=True)
engine = create_engine(db_path, echo=False)

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
    fullname = Column(String)
    password = Column(String)
    tele_id = Column(Integer)
    last_job = Column(Integer)
    category = Column(String)