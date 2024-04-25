"""
Configuration details for the database.
"""

__author__ = "Justin B. (justin@justin.directory)"


from os import environ

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = environ.get(
    "DATABASE_URL", "sqlite:///shipping.db?check_same_thread=False")


engine: Engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    pool_recycle=60
)

Session = sessionmaker(engine)
session = Session()
