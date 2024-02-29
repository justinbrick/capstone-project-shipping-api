from os import environ
import sqlite3

DATABASE_URL = environ.get("DATABASE_URL", "sqlite:///./shipping.db")
connection: sqlite3.Connection = sqlite3.connect(DATABASE_URL, check_same_thread=False)