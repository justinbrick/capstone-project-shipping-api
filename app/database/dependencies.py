"""
FastAPI Dependencies for database
"""


from app.database import Session


def get_db():
    """
    Creates a database session from the database engine.


    """
    db = Session()
    try:
        yield db
    finally:
        db.close()
