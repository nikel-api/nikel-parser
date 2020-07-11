import json
from schemas.buildings_schema import BuildingsSchema

# from data_parser.food import FoodParser
# from data_parser.evals import EvalsParser
# from data_parser.exams import ExamsParser
# from data_parser.courses import CoursesParser
# from data_parser.parking import ParkingParser
# from data_parser.services import ServicesParser
# from data_parser.buildings import BuildingsParser
# from data_parser.textbooks import TextbooksParser

class DataValidator:
    json_mapping = {
        'buildings': '../data/buildings.json',
        'courses': 'courses.json',
    }

    def __init__(self):
        pass

    def validate_json(self, json_data, schema):
        pass

if(__name__ == "__main__"):
    v = DataValidator()

    with open('data/buildings.json', 'r') as f:
        data = json.load(f)

        # for b in data:
        #     if b['tags'] is None:
        #         print(b['code'])
        print(BuildingsSchema.is_valid(data))


