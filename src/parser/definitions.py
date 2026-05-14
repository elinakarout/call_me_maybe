from pydantic import BaseModel, model_validator
from pydantic_core import PydanticCustomError
from typing import Literal, Self
import json


class Definitions(BaseModel):
    name: str
    description: str
    parameters: dict[str, Literal["string", "number", "boolean"]]
    returns: Literal["string", "number", "boolean"]

    @model_validator(mode="after")
    def definition_validation(self) -> Self:
        if not self.name.startswith("fn_"):
            raise PydanticCustomError(
                "ValueError",
                "function name must start with 'fn_'"
            )
        return self

    @staticmethod
    def mandatory_fields(data: list) -> None:
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

    @classmethod
    def from_file(cls, file_path: str) -> list["Definitions"]:
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
