from ..parser import Definitions
from llm_sdk import Small_LLM_Model
import torch

def model_prompt(
    model: Small_LLM_Model,
    prompt: str,
    definitions: list[Definitions]
) -> str:
    question = "Select the most appropriate function for this request."
    question += "\n\nAvailable functions:"
    i = 1
    for definition in definitions:
        question += f"\n\nfunction {i}:"
        question += f"\nfunction name: {definition.name}"
        question += f"\nfunction description: {definition.description}"
        question += f"\nfunction parameters:"
        for parameter, p_type in definition.parameters.items():
            question += f" {parameter}({p_type})"
        i += 1
    question += f"\n\nRequest: {prompt}"
    return question


def find_best_function(
    model: Small_LLM_Model,
    prompt: str,
    definitions: list[Definitions]
) -> str:
    available_functions = [definition.name for definition in definitions]
    prompt += "\n\nBest function name: "
    answer = ""
    for i in range(50):
        tokens = model.encode(prompt + answer)
        scores = model.get_logits_from_input_ids(tokens[0].tolist())
        best_score = float("-inf")
        best_answer = ""
        for function in available_functions:
            tokens = model.encode(function)[0].tolist()
            if i < len(tokens):
                score = scores[tokens[i]]
                if score > best_score:
                    best_score = score
                    best_answer = model.decode([tokens[i]])
        answer += best_answer
        if answer in available_functions:
            return answer
    return ""


def function_call(definitions: list[Definitions],
                  prompts: list[str],
                  outfile: str) -> None:
    model = Small_LLM_Model()
    for question in prompts:
        prompt = model_prompt(model, question, definitions)
        name = find_best_function(model, prompt, definitions)
        # parameters = find_parameters(model, prompt, definitions, name)
    # tokens = model.encode(prompt)
    # print(tokens)
    # next_token = model.get_logits_from_input_ids(tokens[0].tolist())
    # print(next_token)
