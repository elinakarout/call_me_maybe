import json
from src.validator import Definitions


# def read_data(file: str) -> list[dict[str:str]]:
#     try:
#         with open(file, 'r') as file:
#             data = json.load(file)
#         validate_data(data)
#         return (data)
#     except Exception as e:
#         print(e)

def mandatory_fields(data: list) -> None:
    i = 1
    for function in data:
        if "name" not in function:
            raise ValueError(f"Missing 'name' field in function {i}")
        if "description" not in function:
            raise ValueError(f"Missing 'description' field in function {i}")
        if "parameters" not in function:
            raise ValueError(f"Missing 'parameters' field in function {i}")
        if "returns" not in function:
            raise ValueError(f"Missing 'returns' field in function {i}")
        i += 1


def function_values(data: list) -> None:
    i = 1
    for function in data:
        if not isinstance(function["parameters"], dict):
            raise ValueError("Parameters field must be a dictionary"
                             f" in function {i}")
        for key, value in function["parameters"].items():
            if not isinstance(value, dict):
                raise ValueError("Each parameter must be a dictionary"
                                 f" in function {i}")
        if not isinstance(function["returns"], dict):
            raise ValueError(f"Returns field must be a dictionary"
                             f" in function {i}")
        if not isinstance(function["returns"], dict):
            raise ValueError(f"Each return must be a dictionary"
                             f" in function {i}")
        i += 1


def read_definitions(file: str) -> list[Definitions]:
    with open(file, 'r') as fd:
        data = json.load(fd)
    mandatory_fields(data)
    function_values(data)
    for function in data:
        for key in function["parameters"]:
            function["parameters"][key] = function[
                            "parameters"][key]["type"]
        function["returns"] = function["returns"]["type"]
    definition = [Definitions(**item) for item in data]
    return (definition)
