from schema import Schema, And, Or, Optional
from validations.schemas.base_schema import BaseSchema

class ServicesSchema(BaseSchema):
    SCHEMA = Schema([{
        'id': str,
        'name': str,
        'alias': Or(str, None),
        'building_id': Or(str, None),
        'description': Or(str, None),
        'campus': Or(*BaseSchema.VALID_CAMPUSES),
        'address': Or(str, None),
        'image': Or(str, None),
        'coordinates': {
            'latitude': float,
            'longitude': float
        },
        'tags': Or(str, None),
        Optional('attributes'): list,
        'last_updated': Or(str, None)
    }])
    