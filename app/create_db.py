from db import *

metadata = Base.metadata
metadata.create_all(engine)
