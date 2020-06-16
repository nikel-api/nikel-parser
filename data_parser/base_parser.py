from selenium import webdriver
from queue import Queue


class BaseParser:
    def __init__(self, base_url: str, driver=False, threads=10):
        if driver:
            self.driver = webdriver.Chrome()
        self.base_url = base_url
        self.queue = Queue()
        self.result_queue = Queue()
        self.threads = threads

    @staticmethod
    def key(el):
        return el['id']

    def process(self):
        raise NotImplementedError
