from database import Base, Database
from model import *

engine = Database().engine
Base.metadata.create_all(engine)
