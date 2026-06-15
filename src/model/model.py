from ..parser import Definitions
from llm_sdk import Small_LLM_Model
import torch
import json


class Model():
    def __init__(
        self,
        definitions: list[Definitions],
        requests: list[str],
        outfile: str
    ):
        self.llm = Small_LLM_Model()
        self.definitions = definitions
        self.requests = requests
        self.outfile = outfile
        self.token_to_value = self.get_token_to_value()
        self.value_to_token = self.get_value_to_token()
        self.prompt = self.get_model_prompt()

    def get_token_to_value(self):
        path = self.llm.get_path_to_vocab_file()
        vocab = {}
        with open(path, 'r') as fd:
            content = json.load(fd)
        for value, token in content.items():
            vocab[token] = value
        return vocab
    
    def get_value_to_token(self):
        path = self.llm.get_path_to_vocab_file()
        vocab = {}
        with open(path, 'r') as fd:
            content = json.load(fd)
        for value, token in content.items():
            vocab[value] = token
        return vocab

    def get_model_prompt(self) -> str:
        prompt = "Select the most appropriate function for this request."
        prompt += "\n\nAvailable functions:"
        i = 1
        for definition in self.definitions:
            prompt += f"\n\nfunction {i}:"
            prompt += f"\nfunction name: {definition.name}"
            prompt += f"\nfunction description: {definition.description}"
            prompt += f"\nfunction parameters:"
            for parameter, p_type in definition.parameters.items():
                prompt += f" {parameter}({p_type})"
            i += 1
        return prompt
    
    def function_calls(self):
        from .function_calls import FunctionCaller
        for request in self.requests:
            print(request)
            caller = FunctionCaller(self, request)
