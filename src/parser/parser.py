from .definitions import Definitions
import json
import argparse


def check_prompts(data: list[dict[str, str]]) -> None:
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


def get_prompts(file_path: str) -> list[str]:
    with open(file_path, 'r') as fd:
        data = json.load(fd)
    check_prompts(data)
    lst = [
        value
        for prompt in data
        for _, value in prompt.items()
        ]
    return lst


def parse_arguments(args: argparse.Namespace) -> None:
    definitions = Definitions.from_file(args.functions_definition)
    prompts = get_prompts(args.input)
    print(prompts, definitions)
