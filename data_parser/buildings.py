import json
import re
from collections import OrderedDict
from datetime import datetime

import requests

from config.base_urls import BaseURls
from data_parser.base_parser import BaseParser
from bs4 import BeautifulSoup


class BuildingsParser(BaseParser):
    campuses = ["utsg", "utm", "utsc"]
    city_map = {
        "utsg": "Toronto",
        "utm": "Mississauga",
        "utsc": "Scarborough"
    }
    campus_map = {
        "utsg": "St. George",
        "utm": "Mississauga",
        "utsc": "Scarborough"
    }

    def __init__(self):
        super().__init__(BaseURls.BUILDINGS)

    def process(self):
        buildings = OrderedDict()

        id = 1
        for campus in BuildingsParser.campuses:
            page = requests.get(f"{self.base_url}/{campus}/c/buildings")
            parsed_page = BeautifulSoup(page.content, "html.parser")
            inner_page = parsed_page.find("ul", {"class": "buildinglist"})
            dts = inner_page.find_all("dt")

            # I have committed a crime here but don't care right now
            for dt in dts:
                building = OrderedDict()
                dt_res = re.search(r"(.*)\s\|\s(.*)", dt.text)
                building['id'] = id
                building['code'] = self.process_field(dt_res.group(2))
                building['name'] = self.process_field(dt_res.group(1))
                building['campus'] = BuildingsParser.campus_map[campus]
                dd = dt.find_next('dd')
                dd_res = re.search(r"(\d+\w?)\s+(.+),\s*(\w\d\w\s\d\w\d)", dd.text)
                if dd_res:
                    address = OrderedDict()
                    address['street_number'] = self.process_field(dd_res.group(1))
                    address['street_name'] = self.process_field(dd_res.group(2))
                    address['city'] = BuildingsParser.city_map[campus]
                    address['province'] = 'ON'
                    address['country'] = 'Canada'
                    address['postal_code'] = self.process_field(dd_res.group(3))
                    building['address'] = address
                else:
                    dd_res = re.search(r"(\d+\w?)\s+(.+)", dd.text)
                    address = OrderedDict()
                    if dd_res is not None:
                        address['street_number'] = self.process_field(dd_res.group(1))
                        address['street_name'] = self.process_field(dd_res.group(2))
                        address['city'] = BuildingsParser.city_map[campus]
                        address['province'] = 'ON'
                        address['country'] = 'Canada'
                        address['postal_code'] = None
                        building['address'] = address
                    else:
                        address['street_number'] = None
                        address['street_name'] = None
                        address['city'] = BuildingsParser.city_map[campus]
                        address['province'] = 'ON'
                        address['country'] = 'Canada'
                        address['postal_code'] = None
                        building['address'] = address

                date = datetime.now()
                building['last_updated'] = date.strftime("%Y-%m-%d %H:%M:%S.0")
                buildings[building['id']] = building
                id += 1

        with open("../data/buildings.json", "w", encoding="utf-8") as f:
            json.dump(buildings, f, ensure_ascii=False)

    @staticmethod
    def process_field(string):
        string = string.strip()
        if len(string) == 0:
            return None
        return string


if __name__ == "__main__":
    p = BuildingsParser()
    p.process()
