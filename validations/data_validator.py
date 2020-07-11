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
        'buildings':    {'file': 'data/buildings.json', 'klass': BuildingsSchema},
        'courses':      {'file': 'data/courses.json', 'klass': CoursesSchema},
        'evals':        {'file': 'data/evals.json', 'klass': EvalsSchema},
        'exams':        {'file': 'data/exams.json', 'klass': ExamsSchema},
        'food':         {'file': 'data/food.json', 'klass': FoodSchema},
        'parking':      {'file': 'data/parking.json', 'klass': ParkingSchema},
        'services':     {'file': 'data/services.json', 'klass': ServicesSchema},
        'textbooks':    {'file': 'data/textbooks.json', 'klass': TextbooksSchema},
    }

    def __init__(self):
        self.failed = []

    def run_all_validations(self):
        mapping = DataValidator.json_mapping

        for data_type in mapping:
            with open(mapping[data_type]['file'], 'r', encoding='utf8') as f:
                data = json.load(f)
                print(f'Validating {data_type}...', end='', flush=True)

                result = self.run_validation(data, mapping[data_type]['klass'])

                # If we get something back, it means it wasn't successful
                if(result):
                    self.failed.append({ 'course': data_type, 'error': result })
                    print('Failed')
                else:
                    print('Passed')
        
        for failure in self.failed:
            print("\n" + ('*' * 10))
            print(f'Validation failed for {failure["course"]}')
            print(f"Stacktrace:\n{failure['error']}\n")

            
        print(f'\nValidated {len(mapping)} schemas. {len(mapping) - len(self.failed)} passed, {len(self.failed)} failed.')
    
    def run_validation(self, obj, schema):
        try:
            DataValidator.validate_with_exception(obj, schema)
        except BaseException as error:
            return error

    @staticmethod
    def validate_with_exception(json_data, schema):
        return schema.SCHEMA.validate(json_data)

    @staticmethod
    def is_valid(json_data, schema):
        return schema.SCHEMA.is_valid(json_data)

if(__name__ == "__main__"):
    v = DataValidator()
    v.run_all_validations()


