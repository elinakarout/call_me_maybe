def main() -> None:
    """Main Function running all scripts"""
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
    args_parser = ArgumentsParser(args)
    prompts, definitions = args_parser.parse_arguments()
    model = Model(definitions, prompts, args.output)
    model.function_calls()


if __name__ == "__main__":
    try:
        from pydantic import ValidationError
        from src.parser import ArgumentsParser
        from src.model import Model
        import argparse
        main()
    except KeyboardInterrupt:
        print("Stopped by user")
    except ValidationError as e:
        print(e.errors()[0]["msg"])
    except Exception as e:
        print(e)
    finally:
        print("Thank you for checking my project :)")
