from sqlalchemy import Column, Integer, String
from ..base import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    password = Column(String)
    tele_id = Column(Integer)
    last_job = Column(Integer)
    category = Column(String)