from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# Get environment variables
from os import environ

# Get the database URL from the environment variables, or get the default database.
DATABASE_URL = environ.get("DATABASE_URL", "sqlite:///./shipping.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()