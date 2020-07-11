import json
from schemas.buildings_schema import BuildingsSchema
from schemas.courses_schema import CoursesSchema
from schemas.evals_schema import EvalsSchema
from schemas.exams_schema import ExamsSchema
from schemas.food_schema import FoodSchema
from schemas.parking_schema import ParkingSchema
from schemas.services_schema import ServicesSchema
from schemas.textbooks_schema import TextbooksSchema

class DataValidator:
    json_mapping = {
        'buildings': { 'file': '../data/buildings.json', 'klass': BuildingsSchema },
        'courses': '../data/courses.json',
        'evals': '../data/evals.json',
        'exams': '../data/exams.json',
        'food': '../data/food.json',
        'parking': '../data/parking.json',
        'services': '../data/services.json',
        'textbooks': '../data/textbooks.json',
    }

    def __init__(self):
        pass

    @staticmethod
    def validate(json_data, schema):
        return schema.SCHEMA.validate(json_data)
    
    @staticmethod
    def is_valid(json_data, schema):
        return schema.SCHEMA.is_valid(json_data)

if(__name__ == "__main__"):

    with open('data/textbooks.json', 'r', encoding='utf8') as f:
        data = json.load(f)

        print(DataValidator.validate(data, TextbooksSchema))
        print(DataValidator.is_valid(data, TextbooksSchema))


