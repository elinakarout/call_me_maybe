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
            scores = self.model.llm.get_logits_from_input_ids(tokens[0].tolist())
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
                print(answer)
                return answer
        return ""

    def find_parameters(self) -> list[str]:
        prompt = "Select the most appropriate parameters for this request."
        params = []
        for definition in self.definitions:
            if definition.name == self.function_name:
                function = definition
        prompt += f"\n\nfunction name: {function.name}"
        prompt += f"\nfunction description: {function.description}"
        prompt += f"\nfunction parameters:"
        for parameter, p_type in function.parameters.items():
            prompt += f" {parameter}({p_type})"
        prompt += f"\n\nRequest: {self.request}"
        prompt += f"\n\nParameters:"
        for parameter, p_type in function.parameters.items():
            prompt += f"\n\n{parameter}: "
            print(parameter)
            if p_type == "number":
                param = self.find_number(prompt)
                prompt += param
                params.append(param)
            if p_type == "boolean":
                param = self.find_bool(prompt)
                prompt += param
                params.append(param)
            if p_type == "string":
                param = self.find_string(prompt)
                prompt += param
                params.append(param)
            print(param)
        return params

    def find_number(self, prompt: str) -> str:
        valid_tokens = [i for i in range(15, 25)]
        valid_tokens.append(13)
        valid_tokens.append(12)
        answer = ""
        for i in range(50):
            tokens = self.model.llm.encode(prompt + answer)
            scores = self.model.llm.get_logits_from_input_ids(tokens[0].tolist())
            best_score = float("-inf")
            best_answer = ""
            for token in valid_tokens:
                    if scores[token] > best_score:
                        best_score = scores[token]
                        best_answer = self.model.llm.decode([token])
            answer += best_answer
            if ("." in answer and answer.endswith("0")):
                return answer
        return answer

    def find_bool(self, prompt: str) -> str:
        valid_tokens = [
            self.model.llm.encode("true")[0].tolist(),
            self.model.llm.encode("false")[0].tolist()
        ]
        answer = ""
        for i in range(50):
            tokens = self.model.llm.encode(prompt + answer)
            scores = self.model.llm.get_logits_from_input_ids(tokens[0].tolist())
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
        valid_words = self.request.split(" ")
        answer = ""
        for i in range(50):
            tokens = self.model.llm.encode(prompt + answer)
            scores = self.model.llm.get_logits_from_input_ids(tokens[0].tolist())
            best_score = float("-inf")
            best_answer = ""
            for word in valid_words:
                tokens = self.model.llm.encode(word)[0].tolist()
                if i < len(tokens):
                    score = scores[tokens[i]]
                    if score > best_score:
                        best_score = score
                        best_answer = self.model.llm.decode([tokens[i]])
            answer += best_answer
            if answer in valid_words:
                return answer
        return answer
