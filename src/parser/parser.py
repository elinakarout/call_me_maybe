from .definitions import Definitions
import json
import argparse


class ArgumentsParser:
    def __init__(self, args: argparse.Namespace):
        self.args = args

    @staticmethod
    def check_prompts(data: list[dict[str, str]]) -> None:
        """Checks prompts data format"""
        i = 1
        for prompt in data:
            if not isinstance(prompt, dict):
                raise ValueError("Each prompt must be a dictionary"
                                 f" in prompt {i}")
            i += 1
        i = 1
        for prompt in data:
            for key in prompt:
                if key != 'prompt':
                    raise ValueError(f"in prompt {i} key must be 'prompt'")
            i += 1

    def get_prompts(self) -> list[str]:
        """Gets the prompts from file,
        Returns a list of prompts strings"""
        with open(self.args.input, 'r') as fd:
            data = json.load(fd)
        self.check_prompts(data)
        lst = [
            value
            for prompt in data
            for _, value in prompt.items()
            ]
        return lst

    def parse_arguments(self) -> tuple[list[str], list[Definitions]]:
        """Returns Definitions and prompts lists"""
        definitions = Definitions.from_file(self.args.functions_definition)
        prompts = self.get_prompts()
        return (prompts, definitions)
