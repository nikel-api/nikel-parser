from collections import OrderedDict
from datetime import datetime

import requests

from data_parser.base_parser import BaseParser


class ServicesParser(BaseParser):
    link = "http://map.utoronto.ca"

    campus_map = {
        "utsg": "St. George",
        "utm": "Mississauga",
        "utsc": "Scarborough"
    }

    def __init__(self):
        super().__init__(
            file="../data/services.json"
        )

    def process(self):
        for campus in ServicesParser.campus_map:
            page = requests.get(f"{ServicesParser.link}/data/map/{campus}", headers={"Referer": ServicesParser.link})
            response = page.json()
            for layer in response['layers']:
                if layer['title'] != 'Student Services' and layer['title'] != 'Student Spaces':
                    continue
                for item in layer['markers']:
                    service = OrderedDict()
                    service['id'] = str(self.process_field(item, 'id')).zfill(4)
                    service['name'] = self.process_field(item, 'title')
                    service['alias'] = self.process_field(item, 'aka')
                    service['building_id'] = self.process_field(item, 'building_code')
                    service['description'] = self.process_field(item, 'desc')
                    service['campus'] = ServicesParser.campus_map[campus]
                    service['address'] = self.process_field(item, 'address')

                    service['image'] = \
                        f"{ServicesParser.link}" \
                        f"{self.process_field(item, 'image')}" if self.process_field(item, 'image') else None

                    coordinates = OrderedDict()
                    coordinates['latitude'] = self.process_field(item, 'lat')
                    coordinates['longitude'] = self.process_field(item, 'lng')
                    service['coordinates'] = coordinates

                    service['tags'] = self.process_field(item, 'tags')
                    if 'attribs' in item:
                        service['attributes'] = self.process_attributes(layer['attribs'], item['attribs'])
                    date = datetime.now()
                    service['last_updated'] = date.isoformat()

                    self.add_item(service)

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
    p = ServicesParser()
    p.run()
