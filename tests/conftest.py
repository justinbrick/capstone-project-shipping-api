import os

def pytest_configure(config):
    """
    Checks if test.db exists, and if it does, deletes it.
    """
    if os.path.exists("test.db"):
        os.remove("test.db")