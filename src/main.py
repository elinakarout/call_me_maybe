from .read_input import read_data
from llm_sdk import Small_LLM_Model

model = Small_LLM_Model()

def main():
    test_cases = read_data()
    for test_case in test_cases:
        prompt = test_case["prompt"]
        print(model.encode(prompt))


if __name__ == "__main__":
    main()