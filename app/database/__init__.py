"""
Configuration details for the database.
"""

__author__ = "Justin B. (justin@justin.directory)"

from os import environ
from sys import modules
import warnings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = environ.get(
    "DATABASE_URL", "sqlite:///shipping.db?check_same_thread=False")

# If pytest is running, use an in-memory database
if "pytest" in modules:
    print("Using in-memory database for testing.")
    DATABASE_URL = "sqlite:///:memory:?check_same_thread=False"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(engine)
session = Session()
