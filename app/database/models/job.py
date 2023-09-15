from sqlalchemy import Column, Integer, String, DateTime, func
from ..base import Base

class Job(Base):
    __tablename__ = 'job'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    price = Column(String)
    description = Column(String)
    link = Column(String)
    date = Column(String)
    category = Column(String)
    parse_date = Column(DateTime(timezone=True), server_default=func.now())

