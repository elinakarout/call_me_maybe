from src.parser import parse_arguments
from src.model import function_call
from pydantic import ValidationError
import argparse


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--functions_definition",
        nargs="?",
        default='data/input/functions_definition.json'
        )
    parser.add_argument(
        "--input",
        nargs="?",
        default='data/input/function_calling_tests.json'
        )
    parser.add_argument(
        "--output",
        nargs="?",
        default='data/output/function_calling_results.json'
        )
    args = parser.parse_args()
    prompts, definitions = parse_arguments(args)
    function_call(definitions, prompts, args.output)


if __name__ == "__main__":
    # try:
    #     main()
    # except ValidationError as e:
    #     print(e.errors()[0]["msg"])
    # except Exception as e:
    #     print(e)
    main()
