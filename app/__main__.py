import os

from database import Base
from parsers import FreelanceHabr, FreelanceRu, FreelanceUa
from sqlalchemy import create_engine

current_dir = os.getcwd()

# Получаем корневую директорию проекта
root_dir = os.path.abspath(os.path.join(current_dir, '.'))
db_path = 'sqlite:///' + os.path.join(root_dir, 'jobs.db') + '?charset=utf8mb4'
engine = create_engine(db_path, echo=True)

Base.metadata.create_all(engine)


FreelanceUa(engine).parse_all_categories()
FreelanceHabr(engine).parse_all_categories()
FreelanceRu(engine).parse_all_categories()