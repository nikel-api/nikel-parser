from selenium import webdriver


class BaseParser:
    def __init__(self, base_url: str, driver=False):
        if driver:
            self.driver = webdriver.Chrome()
        self.base_url = base_url

    def process(self):
        raise NotImplementedError
