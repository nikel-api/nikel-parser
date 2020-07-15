from schema import Schema, And, Or

from validations.schemas.base_schema import BaseSchema


class TextbooksSchema(BaseSchema):
    SCHEMA = Schema([{
        'id': str,
        'isbn': str,
        'title': str,
        'edition': int,
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
                'instructors': Schema([str])
            }]
        }],
        'last_updated': str
    }])
