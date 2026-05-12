from src.parser import read_definitions
from pydantic import ValidationError


def main() -> None:
    definitions = read_definitions('data/input/functions_definition.json')
    print(definitions)


if __name__ == "__main__":
    try:
        main()
    except ValidationError as e:
        print(e.errors()[0]["msg"])
    except Exception as e:
        print(e)
