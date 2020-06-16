import json
from collections import OrderedDict
from datetime import datetime

import requests

from config.base_urls import BaseURls
from data_parser.base_parser import BaseParser


# This might not be used in the future
class AccessibilityParser(BaseParser):
    # currently redundant
    campus_map = {
        "utsg": "St. George",
        "utm": "Mississauga",
        "utsc": "Scarborough"
    }

    def __init__(self):
        super().__init__(BaseURls.PARKING)

    def process(self):
        accessibility = []

        for campus in AccessibilityParser.campus_map:
            page = requests.get(f"{self.base_url}/data/map/{campus}", headers={"Referer": self.base_url})
            response = page.json()
            for layer in response['layers']:
                if layer['title'] != 'Accessibility':
                    continue
                for item in layer['markers']:
                    entry = OrderedDict()
                    entry['id'] = str(self.process_field(item, 'id')).zfill(4)
                    entry['name'] = self.process_field(item, 'title')
                    entry['description'] = self.process_field(item, 'desc')
                    entry['building_id'] = self.process_field(item, 'building_code')
                    entry['campus'] = AccessibilityParser.campus_map[campus]
                    entry['image'] = f"{self.base_url}{self.process_field(item, 'image')}" \
                        if self.process_field(item, 'image') else None
                    coordinates = OrderedDict()
                    coordinates['latitude'] = self.process_field(item, 'lat')
                    coordinates['longitude'] = self.process_field(item, 'lng')
                    entry['coordinates'] = coordinates
                    if 'attribs' in item:
                        entry['attributes'] = self.process_attributes(layer['attribs'], item['attribs'])
                    date = datetime.now()
                    entry['last_updated'] = date.isoformat()
                    accessibility.append(entry)

        with open("../data/accessibility.json", "w", encoding="utf-8") as f:
            accessibility.sort(key=self.key)
            json.dump(accessibility, f, ensure_ascii=False)

    @staticmethod
    def process_field(el, field):
        if field in el:
            return el[field]
        return None

    @staticmethod
    def process_attributes(mapping, attributes):
        res = []
        for attribute in mapping:
            if attribute['id'] in attributes:
                res.append(attribute['title'])
        return res


if __name__ == "__main__":
    p = AccessibilityParser()
    p.process()
