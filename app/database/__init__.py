from os import environ
import sqlite3

DATABASE_URL = environ.get("DATABASE_URL", "./shipping.db")
connection: sqlite3.Connection = sqlite3.connect(DATABASE_URL, check_same_thread=False, )


# Do we need this? What disadvantages could there be to not passing the SQLite3 errors?
# My thoughts are, this is agnostic of any database engine. This means we can simply change the implementing code in
# the database side, and then we can change it whenever we switch to MSSQL.

class ColumnNotFoundException(Exception):
    pass

class ColumnInsertionException(Exception):
    pass