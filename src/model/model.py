from ..parser import Definitions
from llm_sdk import Small_LLM_Model
import torch


def tokenize(model: Small_LLM_Model, prompts: list[str]) -> list[torch.Tensor]:
    tokens = []
    for question in prompts:
        tokens.append(model.encode(question))
    return tokens


def function_call(definitions: list[Definitions],
                  prompts: list[str],
                  outfile: str) -> None:
    model = Small_LLM_Model()
    tokens = tokenize(model, prompts)
    print(tokens)
