import json


def read_json_file(file):
    with open(file, encoding='utf8') as f:
        return json.load(f)
