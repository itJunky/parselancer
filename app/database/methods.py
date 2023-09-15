from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from .models import Job


class Gateway:
	def __init__(self, engine):
		self.Session = sessionmaker(bind=engine)
    
class App(Gateway):
	def job_exist(self, job_link):
		with self.Session() as session:
			cur = session.execute(text("SELECT link FROM job"))
			links = cur.fetchall()
		return any(job_link in s[0] for s in links)
	
	def append_job(self, job: Job):
		with self.Session() as session:
			session.add(job)
			session.commit()
			print('Добавленно')

class Bot(Gateway):
	pass
