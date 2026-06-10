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
    for i in range(80):
        answer = ""
        tokens = model.encode(prompt + answer)
        next_tokens = model.get_logits_from_input_ids(tokens[0].tolist())
        best_score = float("-inf")
        for function in available_functions:
            tokens = model.encode(function)
            print(f"token: {tokens}")
            # print(f"decoded token: {model.decode(token[i])}")
            # print(f"probability: {next_tokens[token[i]]}")
            # if [token[0]] > best_score:
                # best_score = score
                # best_token = next_token
        # next_token_word = model.decode(best_token)    
        # if any(
            # func.startswith(answer + next_token_word)
            # for func in available_functions
        # ):
            # answer += next_token_word
        # if answer.strip() in available_functions:
            # return answer.strip()
    # return ""


def function_call(definitions: list[Definitions],
                  prompts: list[str],
                  outfile: str) -> None:
    model = Small_LLM_Model()
    prompt = model_prompt(model, prompts[0], definitions)
    best_function = find_best_function(model, prompt, definitions)
    print(best_function)
    prompt += "\n\nBest function name: "
    # tokens = model.encode(prompt)
    # print(tokens)
    # next_token = model.get_logits_from_input_ids(tokens[0].tolist())
    # print(next_token)
