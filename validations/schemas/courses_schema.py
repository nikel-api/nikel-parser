from schema import Schema, And, Or

class CoursesSchema:
    VALID_CAMPUSES = ['St. George', 'Scarborough', 'Mississauga']

    SCHEMA = Schema([{
        'id': str,
        'code': Or(And(str, lambda code: len(code) == 8), None),   # Building code should be a string and of length 2
        'name': str,
        'description': str,
        'division': str,
        'department': str,
        'prerequisites': Or(str, None),
        'corequisites': Or(str, None),
        'exclusions': Or(str, None),
        'recommended_preparation': Or(str, None),
        'level': str,
        'campus': Or(*VALID_CAMPUSES),
        'term': str,
        'arts_and_science_breadth': Or(str, None),
        'arts_and_science_distribution': Or(str, None),
        'utm_distribution': Or(str, None),
        'utsc_breadth': Or(str, None),
        'apsc_electives': Or(str, None),
        'meeting_sections': [{
            'code': str,
            'instructors': list,
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
        'last_updated': Or(str, None)
    }])
    