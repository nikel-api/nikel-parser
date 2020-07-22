import unittest

from tests.helpers.utils import read_json_file
from validations.data_validator import DataValidator


class TestDataSets(unittest.TestCase):
    """
    Test all existing JSON data against their respective schema.
    """

    def test_buildings(self):
        file = '../' + DataValidator.json_mapping['buildings']['file']
        schema = DataValidator.json_mapping['buildings']['klass']
        data = read_json_file(file)

        self.assertTrue(DataValidator.is_valid(data, schema))

    def test_courses(self):
        file = '../' + DataValidator.json_mapping['courses']['file']
        schema = DataValidator.json_mapping['courses']['klass']
        data = read_json_file(file)

        self.assertTrue(DataValidator.is_valid(data, schema))

    def test_programs(self):
        file = '../' + DataValidator.json_mapping['programs']['file']
        schema = DataValidator.json_mapping['programs']['klass']
        data = read_json_file(file)

        self.assertTrue(DataValidator.is_valid(data, schema))

    def test_evals(self):
        file = '../' + DataValidator.json_mapping['evals']['file']
        schema = DataValidator.json_mapping['evals']['klass']
        data = read_json_file(file)

        self.assertTrue(DataValidator.is_valid(data, schema))

    def test_exams(self):
        file = '../' + DataValidator.json_mapping['exams']['file']
        schema = DataValidator.json_mapping['exams']['klass']
        data = read_json_file(file)

        self.assertTrue(DataValidator.is_valid(data, schema))

    def test_food(self):
        file = '../' + DataValidator.json_mapping['food']['file']
        schema = DataValidator.json_mapping['food']['klass']
        data = read_json_file(file)

        self.assertTrue(DataValidator.is_valid(data, schema))

    def test_parking(self):
        file = '../' + DataValidator.json_mapping['parking']['file']
        schema = DataValidator.json_mapping['parking']['klass']
        data = read_json_file(file)

        self.assertTrue(DataValidator.is_valid(data, schema))

    def test_services(self):
        file = '../' + DataValidator.json_mapping['services']['file']
        schema = DataValidator.json_mapping['services']['klass']
        data = read_json_file(file)

        self.assertTrue(DataValidator.is_valid(data, schema))

    def test_textbooks(self):
        file = '../' + DataValidator.json_mapping['textbooks']['file']
        schema = DataValidator.json_mapping['textbooks']['klass']
        data = read_json_file(file)

        self.assertTrue(DataValidator.is_valid(data, schema))


if __name__ == '__main__':
    unittest.main()
