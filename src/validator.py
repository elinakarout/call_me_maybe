from pydantic import BaseModel, model_validator
from pydantic_core import PydanticCustomError
from typing import Literal, Self


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
