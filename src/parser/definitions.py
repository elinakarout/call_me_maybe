from pydantic import BaseModel
from typing import Literal, Self, Any
import json


class Definitions(BaseModel):
    """Class to store all function definitions"""
    name: str
    description: str
    parameters: dict[str, Literal["string", "number", "boolean", "integer"]]
    returns: Literal["string", "number", "boolean", "integer"]

    @staticmethod
    def mandatory_fields(data: list[dict[str, Any]]) -> None:
        """Checks if all mandatory fields are available"""
        i = 1
        for function in data:
            if "name" not in function:
                raise ValueError("Missing 'name' field"
                                 f" in function {i}")
            if "description" not in function:
                raise ValueError("Missing 'description' field"
                                 f" in function {i}")
            if "parameters" not in function:
                raise ValueError("Missing 'parameters' field"
                                 f" in function {i}")
            if "returns" not in function:
                raise ValueError(f"Missing 'returns' field"
                                 f" in function {i}")
            i += 1

    @staticmethod
    def function_values(data: list[dict[str, Any]]) -> None:
        """Checks the formating of the json file"""
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

    @classmethod
    def from_file(cls, file_path: str) -> list[Self]:
        """Reads the file, checks all constraints
        Returns a list of Definitions objects
        """
        with open(file_path, 'r') as fd:
            data = json.load(fd)
        Definitions.mandatory_fields(data)
        Definitions.function_values(data)
        for function in data:
            for key in function["parameters"]:
                function["parameters"][key] = (
                    function["parameters"][key]["type"]
                    )
            function["returns"] = function["returns"]["type"]
        return [cls(**item) for item in data]
