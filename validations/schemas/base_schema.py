class BaseSchema:
    # Constants
    VALID_CAMPUSES = ['St. George', 'Scarborough', 'Mississauga']

    # Lambda Methods
    COURSE_CODE_LAMBDA = lambda code: 7 <= len(code) <= 9

    # Static Helpers