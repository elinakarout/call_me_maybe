from .model import Model


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
        prompt = "Select the most appropriate parameters for this request."
        prompt += "\nAdd a double quote (\") at the end of string parameters,"
        prompt += "to be later used in a json file"
        prompt += "\nAnswer with only  the parameter, Nothing else"
        params = []
        for definition in self.definitions:
            if definition.name == self.function_name:
                function = definition
        prompt += f"\n\nRequest: {self.request}"
        prompt += f"\n\nfunction name: {function.name}"
        prompt += f"\nfunction description: {function.description}"
        prompt += "\nfunction parameters:"
        for parameter, p_type in function.parameters.items():
            prompt += f" {parameter}({p_type})"
        prompt += "\nThe correct parameters for the function call are:"
        self.model.output += "        \"parameters\": {\n"
        for parameter, p_type in function.parameters.items():
            prompt += f"\n\n{parameter}: \""
            self.model.output += f"            \"{parameter}\": "
            if p_type == "number":
                param = self.find_number(prompt)
                prompt += param
                params.append(param)
            if p_type == "boolean":
                param = self.find_bool(prompt)
                prompt += param
                params.append(param)
            if p_type == "string":
                self.model.output += "\""
                param = self.find_string(prompt)
                prompt += param
                params.append(param)
            self.model.output += f"{param},\n"
        self.model.output = self.model.output[:-2]
        self.model.output += "\n        }\n    },\n"
        return params

    def find_number(self, prompt: str) -> str:
        tokens = self.model.llm.encode(prompt)[0].tolist()
        prompt_len = len(tokens)
        valid_answers = [str(i) for i in range(10)]
        valid_answers.append(".")
        valid_answers.append("-")
        answer = ""
        for i in range(30):
            scores = self.model.llm.get_logits_from_input_ids(tokens)
            best_score = float("-inf")
            for token, value in self.model.token_to_value.items():
                if value not in valid_answers:
                    scores[token] = float("-inf")
                else:
                    if scores[token] > best_score:
                        best_score = scores[token]
                        best_token = token
            print(f"score of -: {scores[self.model.value_to_token['-']]}")
            print(f"score of {self.model.token_to_value[best_token]}: {best_score}")
            tokens.append(best_token)
            if "." not in  valid_answers:
                break
            if i == 0:
                valid_answers.remove("-")
            if best_token == self.model.value_to_token["."]:
                valid_answers.remove('.')
        answer_tokens = tokens[prompt_len:]
        answer = str(self.model.llm.decode(answer_tokens))
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

