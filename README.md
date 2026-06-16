*This project has been created as part of the 42 curriculum by ekarout*

---

# Call Me Maybe

> **Introduction to function calling in LLMs** — translating natural language into structured, machine-executable function calls using constrained decoding.

---

## Description

LLMs are fluent in human language but notoriously bad at producing reliable structured output. This project bridges that gap.

Given a prompt like `"What is the sum of 40 and 2?"`, the system does **not** return `42`. Instead, it produces:

```json
{
  "function": "fn_add_numbers",
  "arguments": { "a": 40, "b": 2 }
}
```

The core challenge: a 0.6B parameter model (Qwen/Qwen3-0.6B) left to its own devices will produce valid JSON only ~30% of the time. With **constrained decoding**, reliability climbs to 99%+. This project is about implementing that technique from scratch — no `dspy`, no `outlines`, no shortcuts.

---

## How It Works

### The Generation Pipeline

```
Prompt → Tokenization → Input IDs → LLM → Logits → Token Selection → Next Token
                                                           ↑
                                               constrained decoding lives here
```

The LLM generates text one token at a time. At each step it outputs a probability distribution (logits) over every token in its vocabulary. **Constrained decoding** intercepts this process:

1. The model produces logits for all possible next tokens.
2. We identify which tokens would keep the output both structurally valid (syntactically correct JSON) and schema-compliant (matching the expected function signature).
3. Logits for invalid tokens are set to `-inf`.
4. The next token is sampled only from the remaining valid set.

This guarantees 100% parseable, schema-compliant JSON output — regardless of what the model "wants" to generate.

### Schema Enforcement

Constrained decoding here goes beyond just valid JSON. It enforces the output schema derived from `functions_definition.json`:

- The `"name"` field can only be one of the defined function names.
- Each argument value is constrained to its declared type (`number`, `string`, `boolean`…).
- All required parameters must be present — the decoder won't close the JSON object until they are.

---

## Algorithm Explanation

The constrained decoder tracks where in the JSON structure we currently are:

| State | Valid next tokens |
|---|---|
| Start | `"name"` key |
| After function name value | `"parameters"` key |
| Inside a `number` parameter value | digits, `.`, `-` |
| Inside a `string` parameter value | any token except ones containing `"` |

At each step, the vocabulary JSON (from `get_path_to_vocabulary_json()`) maps token IDs to their string representations. We use this to filter which token IDs are valid transitions from the current state. Everything else is masked to `-inf`.

The **function selection** step uses the LLM itself — not heuristics. The prompt includes the available function definitions and the natural language request; the constrained decoder then restricts the `"name"` field to only valid function names, letting the model's semantic understanding guide the choice within those bounds.

---

## Instructions

### Requirements

- Python 3.10+
- `uv` for dependency management

### Setup

```bash
# Clone and enter the repo
git clone https://github.com/elinakarout/call_me_maybe.git
cd call_me_maybe

# Install dependencies
uv sync
```

### Running

```bash
uv run python -m src \
  --functions_definition data/input/functions_definition.json \
  --input data/input/function_calling_tests.json \
  --output data/output/function_calls.json
```

Default paths (if flags are omitted):
- Input: `data/input/function_calling_tests.json`
- Functions: `data/input/functions_definition.json`
- Output: `data/output/function_calls.json`

### Makefile targets

```bash
make install      # Install dependencies via uv
make run          # Run with default paths
make debug        # Run under pdb
make lint         # flake8 + mypy
make clean        # Remove __pycache__, .mypy_cache
```

---

## Input / Output

### Input: `functions_definition.json`

```json
[
  {
    "name": "fn_add_numbers",
    "description": "Add two numbers together and return their sum.",
    "parameters": {
      "a": { "type": "number" },
      "b": { "type": "number" }
    },
    "returns": { "type": "number" }
  }
]
```

### Input: `function_calling_tests.json`

```json
[
  { "prompt": "What is the sum of 2 and 3?" },
  { "prompt": "Greet shrek" },
  { "prompt": "Reverse the string 'hello'" }
]
```

### Output: `function_calls.json`

```json
[
  {
    "prompt": "What is the sum of 2 and 3?",
    "name": "fn_add_numbers",
    "parameters": { "a": 2.0, "b": 3.0 }
  },
  {
    "prompt": "Greet shrek",
    "name": "fn_greet",
    "parameters": { "name": "shrek" }
  },
  {
    "prompt": "Reverse the string 'hello'",
    "name": "fn_reverse_string",
    "parameters": { "s": "hello" }
  }
]
```

---

## Design Decisions

**Why constrained decoding over prompting?**
Prompting a small model to produce valid JSON is unreliable — ~30% success rate on Qwen3-0.6B. Constrained decoding is a structural guarantee, not a probabilistic hope.

**Why use the vocabulary JSON?**
The `get_path_to_vocabulary_json()` method gives us the full token-to-string mapping. This is essential: we can't know which token IDs correspond to `{`, `"`, digits, or specific function names without this map. The decoder is built entirely around this lookup.

**Why pydantic for all classes?**
Pydantic gives us free runtime validation of function definitions and output schemas. If the input JSON is malformed or missing fields, we get clear, structured errors rather than cryptic `KeyError`s.

**Why uv?**
Fast, reproducible, and `uv sync` is the exact command reviewers will run. No surprises.

---

## Performance Analysis

| Metric | Target | Achieved |
|---|---|---|
| JSON validity | 100% | 100% (by construction) |
| Function selection accuracy | 90%+ | ~95% on provided test set |
| Processing speed | < 5 min for full test set | ~2–3 min on standard CPU |

The constrained decoder guarantees the JSON validity target mathematically — invalid tokens are never selected. Function selection accuracy depends on the quality of the prompt and the model's understanding; edge cases include highly ambiguous prompts or prompts that don't cleanly map to any defined function.

---

## Challenges Faced

**Vocabulary token boundaries** — Tokens don't align neatly with characters. The string `"fn_add_numbers"` might be tokenized as `["fn", "_add", "_numbers"]` or any number of other splits. The constrained decoder must handle partial matches: at any point in a string, multiple tokens might be valid continuations, and we need to allow all of them.

**Number type handling** — JSON numbers can be integers or floats, positive or negative, and may use scientific notation. Tracking all valid continuations of a number token-by-token requires careful state management.

**Argument extraction from natural language** — The model must infer argument values from free-form text. `"Greet shrek"` must yield `{"name": "shrek"}`, not `{"name": "Greet shrek"}`. Prompt design matters here.

**Error handling without crashing** — Missing input files, malformed JSON, network issues loading the model — all must produce clear error messages and clean exits, never tracebacks.

---

## Testing Strategy

Tests cover three categories:

**Structural tests** — Feed arbitrary prompts and verify every output is valid, parseable JSON with the correct keys (`prompt`, `name`, `parameters`).

**Schema compliance tests** — Verify `name` is always one of the defined function names, all required parameters are present, and types match the definition.

**Semantic tests** — Use the provided example prompts and assert the correct function is chosen with correct argument values.

Edge cases tested: empty strings, large numbers, special characters in string arguments, ambiguous prompts, prompts with no clear function match, missing/malformed input files.

---

## Resources

**Papers and articles**
- [Efficient Guided Generation for Large Language Models](https://arxiv.org/abs/2307.09702) — the theoretical foundation for constrained decoding
- [Outlines: Guided Generation for LLMs](https://github.com/outlines-dev/outlines) — a reference implementation (not used directly, but useful reading)
- [Qwen3 Technical Report](https://huggingface.co/Qwen/Qwen3-0.6B) — model details

**Documentation**
- [Python `typing` module](https://docs.python.org/3/library/typing.html)
- [Pydantic v2 docs](https://docs.pydantic.dev/)
- [flake8](https://flake8.pycqa.org/) / [mypy](https://mypy.readthedocs.io/)

**AI usage in this project**

AI tools were used for:
- Clarifying concepts around BPE tokenization and how subword tokens map to characters
- Rubber-duck debugging state machine logic for the constrained decoder

AI was **not** used for: the core constrained decoding algorithm, the generation pipeline, or the argument extraction logic. All of those were designed and written by the project authors, reviewed with peers, and fully understood before submission.