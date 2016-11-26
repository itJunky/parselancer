from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

import os
basedir = os.path.abspath(os.path.dirname(__file__))
# engine = create_engine('sqlite:///:memory:', echo=True)
db_path = 'sqlite:///' + os.path.join(basedir, '../jobs.db')
engine = create_engine(db_path, echo=True)

class Job(Base):
    __tablename__ = 'job'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    date = Column(String)
    price = Column(String)
    url = Column(String)
    raw = Column(String)
    category = Column(String)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    password = Column(String)