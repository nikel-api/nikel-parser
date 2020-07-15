import json


def read_file_as_json(file):
    with open(file, encoding='utf8') as f:
        return json.load(f)
