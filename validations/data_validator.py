import json

from schema import SchemaError

from validations.schemas.buildings_schema import BuildingsSchema
from validations.schemas.courses_schema import CoursesSchema
from validations.schemas.evals_schema import EvalsSchema
from validations.schemas.exams_schema import ExamsSchema
from validations.schemas.food_schema import FoodSchema
from validations.schemas.parking_schema import ParkingSchema
from validations.schemas.services_schema import ServicesSchema
from validations.schemas.textbooks_schema import TextbooksSchema


class DataValidator:
    json_mapping = {
        'buildings': {'file': '../nikel-datasets/data/buildings.json', 'klass': BuildingsSchema},
        'courses': {'file': '../nikel-datasets/data/courses.json', 'klass': CoursesSchema},
        'evals': {'file': '../nikel-datasets/data/evals.json', 'klass': EvalsSchema},
        'exams': {'file': '../nikel-datasets/data/exams.json', 'klass': ExamsSchema},
        'food': {'file': '../nikel-datasets/data/food.json', 'klass': FoodSchema},
        'parking': {'file': '../nikel-datasets/data/parking.json', 'klass': ParkingSchema},
        'services': {'file': '../nikel-datasets/data/services.json', 'klass': ServicesSchema},
        'textbooks': {'file': '../nikel-datasets/data/textbooks.json', 'klass': TextbooksSchema},
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
                if result:
                    self.failed.append({'type': data_type, 'error': result})
                    print('Failed')
                else:
                    print('Passed')

        for failure in self.failed:
            print("\n" + ('*' * 10))
            print(f'Validation failed for {failure["type"]}')
            print(f"Stacktrace:\n{failure['error']}\n")

        print(
            f'\nValidated {len(mapping)} schemas. {len(mapping) - len(self.failed)} passed, {len(self.failed)} failed.'
        )

    @staticmethod
    def run_validation(obj, schema):
        """Returns truthy object if failed, None if passed.
        """
        try:
            DataValidator.validate_with_exception(obj, schema)
        except SchemaError as error:
            return error

    @staticmethod
    def validate_with_exception(json_data, schema):
        return schema.SCHEMA.validate(json_data)

    @staticmethod
    def is_valid(json_data, schema):
        return schema.SCHEMA.is_valid(json_data)


if __name__ == "__main__":
    v = DataValidator()
    v.run_all_validations()
