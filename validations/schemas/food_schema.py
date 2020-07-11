from schema import Schema, And, Or, Optional
from schemas.base_schema import BaseSchema

class FoodSchema(BaseSchema):
    SCHEMA = Schema([{
        'id': str,
        'name': str,
        'description': Or(str, None),
        'campus': Or(*BaseSchema.VALID_CAMPUSES),
        'tags': Or(str, None),
        'address': Or(str, None),
        'coordinates': {
            'latitude': float,
            'longitude': float
        },
        'hours': Or(None, {}, {
            'sunday': {
                'closed': bool,
                'open': Or(int, None),
                'close': Or(int, None)
            },
            'monday': {
                'closed': bool,
                'open': Or(int, None),
                'close': Or(int, None)
            },
            'tuesday': {
                'closed': bool,
                'open': Or(int, None),
                'close': Or(int, None)
            },
            'wednesday': {
                'closed': bool,
                'open': Or(int, None),
                'close': Or(int, None)
            },
            'thursday': {
                'closed': bool,
                'open': Or(int, None),
                'close': Or(int, None)
            },
            'friday': {
                'closed': bool,
                'open': Or(int, None),
                'close': Or(int, None)
            },
            'saturday': Or(None, {
                'closed': bool,
                'open': Or(int, None),
                'close': Or(int, None)
            }),
        }),
        'image': Or(str, None),
        'url': Or(str, None),
        'twitter': Or(str, None),
        'facebook': Or(str, None),
        Optional('attributes'): list,       # attributes is optional. If it exists, it should be a list
        'last_updated': Or(str, None)
    }])
    