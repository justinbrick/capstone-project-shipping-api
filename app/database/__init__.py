from os import environ
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = environ.get("DATABASE_URL", "sqlite:///shipping.db?check_same_thread=False")

engine = create_engine(DATABASE_URL)
Session = sessionmaker(engine)
session = Session()
