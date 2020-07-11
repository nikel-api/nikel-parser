from schema import Schema, And, Or
from schemas.base_schema import BaseSchema

class ExamsSchema(BaseSchema):
    SCHEMA = Schema([{
        'id': str,
        'course_id': str,
        'course_code': And(str, BaseSchema.COURSE_CODE_LAMBDA),
        'campus': Or(*BaseSchema.VALID_CAMPUSES),
        'date': str,
        'start': int,
        'end': int,
        'duration': int,
        'sections': [{
            'lecture_code': str,
            'split': str,
            'location': Or(str, None)
        }],
        'last_updated': Or(str, None)
    }])
    