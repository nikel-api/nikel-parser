from schema import Schema, And, Or
from validations.schemas.base_schema import BaseSchema

class EvalsSchema(BaseSchema):
    SCHEMA = Schema([{
        'id': str,
        'name': str,
        'campus': Or(*BaseSchema.VALID_CAMPUSES),
        'terms': [{
            'term': str,
            'lectures': [{
                'lecture_code': str,
                'firstname': str,
                'lastname': str,
                's1': Or(float, None),
                's2': Or(float, None),
                's3': Or(float, None),
                's4': Or(float, None),
                's5': Or(float, None),
                's6': Or(float, None),
                'invited': Or(int, None),
                'responses': int
            }]
        }],
        'last_updated': Or(str, None)
    }])
    