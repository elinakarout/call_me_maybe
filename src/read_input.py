import json


def read_data():
    with open('data/input/function_calling_tests.json', 'r') as file:
        data = json.load(file)
    return (data)