from .model import Model
import re


class FunctionCaller():
    def __init__(self, model: Model, request: str) -> None:
        self.model = model
        self.request = request
        self.prompt = model.prompt + f"\n\nUser Request: {request}"
        self.definitions = model.definitions
        self.function_name = self.find_best_function()
        self.parameters = self.find_parameters()

    def find_best_function(self) -> str:
        available_functions = [
            definition.name
            for definition in self.definitions
        ]
        prompt = self.prompt
        prompt += "\n\nBest function name: "
        answer = ""
        for i in range(50):
            tokens = self.model.llm.encode(prompt + answer)
            scores = self.model.llm.get_logits_from_input_ids(
                tokens[0].tolist()
            )
            best_score = float("-inf")
            best_answer = ""
            for function in available_functions:
                tokens = self.model.llm.encode(function)[0].tolist()
                if i < len(tokens):
                    score = scores[tokens[i]]
                    if score > best_score:
                        best_score = score
                        best_answer = self.model.llm.decode([tokens[i]])
            answer += best_answer
            if answer in available_functions:
                self.model.output += f"        \"name\": \"{answer}\",\n"
                return answer
        return ""

    def find_parameters(self) -> list[str]:
        params = []
        for definition in self.definitions:
            if definition.name == self.function_name:
                function = definition
        prompt = f"Request: {self.request}"
        prompt += f"\n\nfunction name: {function.name}"
        prompt += f"\nfunction description: {function.description}"
        prompt += "\nfunction parameters:"
        for parameter, p_type in function.parameters.items():
            prompt += f" {parameter}({p_type})"
            types = p_type
        if types == "number" or types == "integer":
            prompt += "\nSelect the most appropriate "
            prompt += "parameters for this request"
            prompt += "\nAnswer with only the parameter, Nothing else"
        else:
            prompt += "Select the most appropriate "
            prompt += "parameters for this request."
            prompt += "\nAdd a double quote (\") at the end of string"
            prompt += " parameters, to be later used in a json file"
            prompt += "\nAnswer with only  the parameter, Nothing else"
            prompt += "\nThe correct parameters for the function call are:"
        self.model.output += "        \"parameters\": {\n"
        number_idx = 0
        for parameter, p_type in function.parameters.items():
            prompt += f"\n\n{parameter} = "
            self.model.output += f"            \"{parameter}\": "
            if p_type == "number" or p_type == "integer":
                param = self.find_number(prompt, parameter, number_idx)
                number_idx += 1
                prompt += param
                if p_type == "integer":
                    param = param[:-2]
                params.append(param)
            elif p_type == "boolean":
                param = self.find_bool(prompt)
                prompt += param
                params.append(param)
            elif p_type == "string":
                self.model.output += "\""
                param = self.find_string(prompt + '"')
                prompt += param
                params.append(param)
            self.model.output += f"{param},\n"
        self.model.output = self.model.output[:-2]
        self.model.output += "\n        }\n    },\n"
        return params

    def find_number(self, prompt: str, parameter: str, number_idx: int) -> str:
        tokens = self.model.llm.encode(prompt)[0].tolist()
        prompt_len = len(tokens)
        request_numbers = re.findall(r"-?\d+(?:\.\d+)?", self.request)
        is_negative = False
        if number_idx < len(request_numbers):
            is_negative = request_numbers[number_idx].startswith("-")
        valid_first_answer = []
        for token, value in self.model.token_to_value.items():
            cleaned = value.replace('Ġ', ' ').replace(' ', ' ').strip()
            if not cleaned:
                continue
            if is_negative:
                if cleaned == "-":
                    if "\n" not in value and "\r" not in value:
                        valid_first_answer.append(value)
            else:
                if cleaned == "+" or cleaned[0] in "0123456789":
                    if "\n" not in value and "\r" not in value:
                        valid_first_answer.append(value)
        valid_answers = [str(i) for i in range(10)]
        valid_answers.append(".")
        scores = self.model.llm.get_logits_from_input_ids(tokens)
        for token, value in self.model.token_to_value.items():
            if value not in valid_first_answer:
                scores[token] = float("-inf")
        best_token = scores.index(max(scores))
        tokens.append(best_token)
        for i in range(30):
            scores = self.model.llm.get_logits_from_input_ids(tokens)
            for token, value in self.model.token_to_value.items():
                if value not in valid_answers:
                    scores[token] = float("-inf")
            best_token = scores.index(max(scores))
            tokens.append(best_token)
            if "." not in valid_answers:
                break
            if best_token == self.model.value_to_token["."]:
                valid_answers.remove('.')
        answer_tokens = tokens[prompt_len:]
        answer = str(self.model.llm.decode(answer_tokens)).strip()
        if answer.startswith("+"):
            answer = answer[1:]
        return answer

    def find_bool(self, prompt: str) -> str:
        valid_tokens = [
            self.model.llm.encode("true")[0].tolist(),
            self.model.llm.encode("false")[0].tolist()
        ]
        answer = ""
        for i in range(50):
            tokens = self.model.llm.encode(prompt + answer)
            scores = self.model.llm.get_logits_from_input_ids(
                tokens[0].tolist()
            )
            best_score = float("-inf")
            best_answer = ""
            for token in valid_tokens:
                if i < len(token):
                    score = scores[token[i]]
                    if score > best_score:
                        best_score = score
                        best_answer = self.model.llm.decode([token[i]])
            answer += best_answer
            if answer == "false" or answer == "true":
                return answer
        return answer

    def find_string(self, prompt: str) -> str:
        tokens = self.model.llm.encode(prompt)[0].tolist()
        prompt_len = len(tokens)
        answer = ""
        for _ in range(30):
            scores = self.model.llm.get_logits_from_input_ids(tokens)
            best_score = float("-inf")
            for token, value in self.model.token_to_value.items():
                if token == self.model.value_to_token['"']:
                    continue
                if '"' in value:
                    scores[token] = float("-inf")
            for i in range(len(scores)):
                if scores[i] > best_score:
                    best_score = scores[i]
                    best_token = i
            tokens.append(best_token)
            if best_token == self.model.value_to_token['"']:
                break
        answer_tokens = tokens[prompt_len:]
        answer = str(self.model.llm.decode(answer_tokens))
        if not answer.endswith('"'):
            answer += '"'
        return answer
