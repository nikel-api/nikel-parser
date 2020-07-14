from collections import OrderedDict
from datetime import datetime

import requests

from data_parser.base_parser import BaseParser
from validations.schemas.parking_schema import ParkingSchema


class ParkingParser(BaseParser):
    link = "http://map.utoronto.ca"

    campus_map = {
        "utsg": "St. George",
        "utm": "Mississauga",
        "utsc": "Scarborough"
    }

    def __init__(self):
        super().__init__(
            file="../nikel-datasets/data/parking.json",
            schema=ParkingSchema
        )

    def process(self):
        for campus in ParkingParser.campus_map:
            page = requests.get(f"{ParkingParser.link}/data/map/{campus}", headers={"Referer": ParkingParser.link})
            response = page.json()
            for layer in response['layers']:
                if campus == 'utsg':
                    if layer['title'] != 'Parking Lots':
                        continue
                else:
                    if layer['title'] != 'Transportation':
                        continue
                for item in layer['markers']:
                    if campus != 'utsg':
                        if "parking" not in self.process_field(item, 'title').lower():
                            continue
                    parking_spot = OrderedDict()
                    parking_spot['id'] = str(self.process_field(item, 'id')).zfill(4)
                    parking_spot['name'] = self.process_field(item, 'title')
                    parking_spot['alias'] = self.process_field(item, 'aka')
                    parking_spot['building_id'] = self.process_field(item, 'building_code')
                    parking_spot['description'] = self.process_field(item, 'desc')
                    parking_spot['campus'] = ParkingParser.campus_map[campus]
                    parking_spot['address'] = self.process_field(item, 'address')

                    coordinates = OrderedDict()
                    coordinates['latitude'] = self.process_field(item, 'lat')
                    coordinates['longitude'] = self.process_field(item, 'lng')
                    parking_spot['coordinates'] = coordinates

                    date = datetime.now()
                    parking_spot['last_updated'] = date.isoformat()

                    self.add_item(parking_spot)

    @staticmethod
    def process_field(el, field):
        if field in el:
            return el[field]
        return None


if __name__ == "__main__":
    p = ParkingParser()
    p.run()
