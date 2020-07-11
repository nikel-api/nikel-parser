from schema import Schema, And, Or, Optional
from validations.schemas.base_schema import BaseSchema

class TextbooksSchema(BaseSchema):
    SCHEMA = Schema([{
        'id': str,
        'isbn': str,
        'title': str,
        'edition': Or(str, int),
        'author': str,
        'image': str,
        'price': float,
        'url': str,
        'courses': [{
            'id': str,
            'code': And(str, BaseSchema.COURSE_CODE_LAMBDA),
            'requirement': str,
            'meeting_sections': [{
                'code': str,
                'instructors': list
            }]
        }],
        'last_updated': Or(str, None)
    }])
    