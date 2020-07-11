from schema import Schema

class BaseSchema:
    SCHEMA = Schema({})

    # Constants
    VALID_CAMPUSES = ['St. George', 'Scarborough', 'Mississauga']

    # Lambda Methods
    COURSE_CODE_LAMBDA = lambda code: 7 <= len(code) <= 10

    # Static Helpers