import os
from dotenv import load_dotenv


def pytest_configure(config):
    """
    Checks if test.db exists, and if it does, deletes it.
    Also loads .env file.
    """
    load_dotenv()

    if os.path.exists("test.db"):
        os.remove("test.db")
