import json
from schemas.buildings_schema import BuildingsSchema
from schemas.courses_schema import CoursesSchema

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

    def validate_json(self, json_data, schema):
        pass

if(__name__ == "__main__"):
    v = DataValidator()

    with open('data/buildings.json', 'r', encoding='utf8') as f:
        data = json.load(f)

        print(BuildingsSchema.is_valid(data))


