from schema import Schema, And, Or

from validations.schemas.base_schema import BaseSchema


class BuildingsSchema(BaseSchema):
    SCHEMA = Schema([{
        'id': str,
        'code': Or(And(str, lambda code: len(code) == 2), None),  # building code should be a string and of length 2
        'tags': Or(str, None),
        'name': str,
        'short_name': Or(str, None),
        'address': {
            'street': Or(str, None),
            'city': Or(str, None),
            'province': Or(str, None),
            'country': Or(str, None),
            'postal': Or(str, None),
        },
        'coordinates': {
            'latitude': Or(float, None),
            'longitude': Or(float, None)
        },
        'last_updated': str
    }])
