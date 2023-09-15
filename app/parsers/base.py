from abc import ABC, abstractmethod
from database import App
from pydantic import AnyHttpUrl
from sqlalchemy.engine import Engine

class BaseParser(ABC):
	category_urls: dict
	def __init__(self, engine: Engine):
		self.db = App(engine)
		# self.category_urls: dict = {}

	@abstractmethod
	def parse_category(self, url: AnyHttpUrl, category: str)->None:
		pass
	def parse_all_categories(self):
		for category, url in self.category_urls.items():
			self.parse_category(url, category)
