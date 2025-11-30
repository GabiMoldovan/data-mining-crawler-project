from database import Base, Database
from model import *

# Class for creating the database tables for the models

engine = Database().engine
Base.metadata.create_all(engine)
