import threading
from selenium import webdriver

class Driver:
    _instance = None
    _lock = threading.Lock()
    driver = webdriver.Chrome()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
