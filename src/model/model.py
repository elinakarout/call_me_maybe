from ..parser import Definitions
from llm_sdk import Small_LLM_Model
from pathlib import Path
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
        self.output = ""

    def get_token_to_value(self) -> dict[int, str]:
        """Returns a dict of format {token_id: value}"""
        path = self.llm.get_path_to_vocab_file()
        vocab = {}
        with open(path, 'r') as fd:
            content = json.load(fd)
        for value, token in content.items():
            vocab[token] = value
        return vocab

    def get_value_to_token(self) -> dict[str, int]:
        """Returns a dict of format {value: token_id}"""
        path = self.llm.get_path_to_vocab_file()
        vocab = {}
        with open(path, 'r') as fd:
            content = json.load(fd)
        for value, token in content.items():
            vocab[value] = token
        return vocab

    def get_model_prompt(self) -> str:
        """Returns starting system prompt"""
        prompt = "Select the most appropriate function for this request."
        prompt += "\n\nAvailable functions:"
        i = 1
        for definition in self.definitions:
            prompt += f"\n\nfunction {i}:"
            prompt += f"\nfunction name: {definition.name}"
            prompt += f"\nfunction description: {definition.description}"
            prompt += "\nfunction parameters:"
            for parameter, p_type in definition.parameters.items():
                prompt += f" {parameter}({p_type})"
            i += 1
        return prompt

    @staticmethod
    def remove_double_quotes(s: str) -> str:
        """Changes double quotes to single quote for json"""
        return s.replace('"', '\'')

    def function_calls(self) -> None:
        """Loops throught the prompts, and
        calls FunctionCaller class for each.
        Finally writes the output
        to the specified file
        """
        from .function_calls import FunctionCaller
        self.output += "[\n"
        for request in self.requests:
            if not request.strip():
                continue
            self.output += "    {\n"
            prompt = self.remove_double_quotes(request)
            self.output += f"        \"prompt\": \"{prompt}\",\n"
            FunctionCaller(self, request)
        self.output = self.output[:-2]
        self.output += "\n]"
        path = Path(self.outfile)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as fd:
            fd.write(self.output)
