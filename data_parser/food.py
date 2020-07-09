from collections import OrderedDict
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from data_parser.base_parser import BaseParser


class FoodParser(BaseParser):
    link = "http://map.utoronto.ca"

    campus_map = {
        "utsg": "St. George",
        "utm": "Mississauga",
        "utsc": "Scarborough"
    }

    def __init__(self):
        super().__init__(
            file="../data/food.json"
        )

    def process(self):
        for campus in FoodParser.campus_map:
            page = requests.get(f"{FoodParser.link}/data/map/{campus}", headers={"Referer": FoodParser.link})
            response = page.json()
            for layer in response['layers']:
                if layer['title'] != 'Food':
                    continue
                for item in layer['markers']:
                    food_item = OrderedDict()
                    food_item['id'] = str(self.process_field(item, 'id')).zfill(4)
                    food_item['name'] = self.process_field(item, 'title')
                    food_item['description'] = self.process_field(item, 'desc')
                    food_item['tags'] = self.process_field(item, 'tags')
                    food_item['campus'] = FoodParser.campus_map[campus]
                    food_item['address'] = self.process_field(item, 'address')

                    coordinates = OrderedDict()
                    coordinates['latitude'] = self.process_field(item, 'lat')
                    coordinates['longitude'] = self.process_field(item, 'lng')
                    food_item['coordinates'] = coordinates

                    food_item['hours'] = self.get_hours(food_item['id']) \
                        if self.process_field(item, 'has_hours') else None
                    food_item['image'] = f"{FoodParser.link}{self.process_field(item, 'image')}" \
                        if self.process_field(item, 'image') else None
                    food_item['url'] = self.process_field(item, 'url')
                    food_item['twitter'] = self.process_field(item, 'twitter')
                    food_item['facebook'] = self.process_field(item, 'facebook')
                    if 'attribs' in item:
                        food_item['attributes'] = self.process_attributes(layer['attribs'], item['attribs'])
                    date = datetime.now()
                    food_item['last_updated'] = date.isoformat()

                    self.add_item(food_item)

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

    # Use a modified version of cobalt's own timetable code
    @staticmethod
    def get_hours(food_id):
        """Parse and return the restaurant's opening and closing times."""

        def conv_time(t):
            """Convert time of form "HH:MM p.d." to seconds since midnight (p.d.
            is one of a.m./p.m.)"""

            time, period = t[:-4].strip(), t[-4:].strip()

            # for mistyped times (i.e. http://map.utoronto.ca/json/hours/1329)
            if t[0] == ':':
                time = time[1:len(time) - 2] + ':' + time[-2:]

            m = 0
            if ':' in time:
                h, m = [int(x) if x != "" else 0 for x in time.split(':')]
            else:
                h = int(time)

            h += 12 if period == 'p.m.' and h != 12 else 0
            return (60 * 60 * h) + (60 * m)

        html = requests.get(f"{FoodParser.link}/json/hours/{food_id}")
        soup = BeautifulSoup(html.content, 'lxml')
        hours = OrderedDict()

        if not soup.find('tbody').text == '':
            days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday',
                    'friday', 'saturday']

            timings = soup.find('tbody').find_all('td')

            for i in range(len(timings)):
                is_closed = True
                open_ = close = 0
                day, timing = days[i], timings[i].text

                if ('closed' not in timing) and (timing != ""):
                    is_closed = False
                    # timing is of form "HH:MM p.d. -HH:MM p.d."
                    open_, close = [conv_time(t) for t in timing.split(' -')]

                hours.update({day: OrderedDict([('closed', is_closed),
                                                ('open', open_ if open_ != 0 else None),
                                                ('close', close if close != 0 else None)])})
        return hours


if __name__ == "__main__":
    p = FoodParser()
    p.run()
