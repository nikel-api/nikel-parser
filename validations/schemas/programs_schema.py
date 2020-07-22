from schema import Schema, Or

from validations.schemas.base_schema import BaseSchema


class ProgramsSchema(BaseSchema):
    SCHEMA = Schema([{
        'id': str,
        'name': str,
        'type': str,
        'campus': Or(*BaseSchema.VALID_CAMPUSES),
        'description': Or(str, None),
        'enrollment': Or(str, None),
        'completion': str,
        'last_updated': str
    }])
