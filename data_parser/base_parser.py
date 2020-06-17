import json
from queue import Queue

from selenium import webdriver


class BaseParser:
    def __init__(self, file: str, update=False, driver=False, threads=10):
        if driver:
            self.driver = webdriver.Chrome()
        self.file = file
        self.update = update
        self.data = {}
        self.queue = Queue()
        self.result_queue = Queue()
        self.threads = threads

    @staticmethod
    def key(el):
        return el['id']

    def add_item(self, item):
        self.data[item['id']] = item

    def load_file(self):
        if self.update:
            try:
                with open(self.file, "r", encoding="utf-8") as f:
                    raw_data = json.load(f)
                    for item in raw_data:
                        self.data[item['id']] = item
            except FileNotFoundError:
                pass

    def dump_file(self):
        raw_data = []
        for key in sorted(self.data):
            raw_data.append(self.data[key])
        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(raw_data, f, ensure_ascii=False)

    def process(self):
        raise NotImplementedError

    def run(self):
        self.load_file()
        self.process()
        self.dump_file()
