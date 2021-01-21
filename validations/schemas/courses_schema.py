from schema import Schema, And, Or, Regex

from validations.schemas.base_schema import BaseSchema


class CoursesSchema(BaseSchema):
    SCHEMA = Schema([{
        'id': str,
        'code': Or(And(str, BaseSchema.COURSE_CODE_LAMBDA), None),  # course code should be a string and of length 8
        'name': str,
        'description': Or(str, None),
        'division': str,
        'department': str,
        'prerequisites': Or(str, None),
        'corequisites': Or(str, None),
        'exclusions': Or(str, None),
        'recommended_preparation': Or(str, None),
        'level': Regex(r'^\d00(/(A|B|C|D))?$'),
        'campus': Or(*BaseSchema.VALID_CAMPUSES),
        'term': str,
        'arts_and_science_breadth': Or(str, None),
        'arts_and_science_distribution': Or(str, None),
        'utm_distribution': Or(str, None),
        'utsc_breadth': Or(str, None),
        'apsc_electives': Or(str, None),
        'meeting_sections': [{
            'code': str,
            'instructors': Schema([str]),
            'times': [{
                'day': str,
                'start': int,
                'end': int,
                'duration': int,
                'location': Or(str, None)
            }],
            'size': int,
            'enrollment': Or(int, None),
            'waitlist_option': bool,
            'delivery': str
        }],
        'last_updated': str
    }])
