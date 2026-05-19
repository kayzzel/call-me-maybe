*This project has been created as part of the 42 curriculum by gabach.*

# ---- CALL-ME-MAYBE ----

<details>
  <summary><h4>Description</h4></summary>

  ___

  ### Project Overview
  **CALL-ME-MAYBE** is an advanced function-calling system designed to seamlessly bridge the gap between human language and structured computer execution. It processes arbitrary natural language user prompts, dynamically selects the single most appropriate tool from an available function definition catalog, and extracts its parameters into a precise, typed, machine-executable structured JSON format. Rather than answering questions directly, it extracts structured information using a lightweight local 500-million parameter language model (`Qwen/Qwen3-0.6B`).

  ### Goal & Core Objectives
  The primary objective of this project is to build an implementation of **Constrained Decoding** from scratch to guarantee 100% structural and semantic schema adherence. Smaller language models are notoriously unreliable at natively generating well-formed JSON, frequently dropping brackets, generating trailing commas, or suffering from formatting failures. 

  This project circumvents these limitations by intercepting the model's text generation process token-by-token. By matching the accumulation buffer against schema constraints and adjusting logit distributions in real time (setting invalid token probabilities to negative infinity ($-\infty$)), the output is mathematically guaranteed to be fully parseable and compliant with the requested JSON schema.
 
</details>

<details>
  <summary><h4>Instructions</h4></summary>

  ___
  ### 1. Makefile
  + **Install project dependencies** using the isolated `uv` package synchronization utility: <br>
  ```make install```<br>

  + **Run the main function-calling pipeline** with default configuration paths: <br>
  ```make```<br>
  
  + **Alternative command** to execute the program with standard configuration paths: <br>
  ```make run```<br>

  + **Run the program with customized files** or additional testing arguments:<br>
  ```make run FUNCTIONS=<file> INPUT=<file> OUTPUT=<file> OTHER=<other flag(s)/info>```<br>

  + **Run the program inside the interactive debugger** using Python's built-in `pdb` module:<br>
  ```make debug```<br>

  + **Clean up temporary files and caches** (e.g., `__pycache__`, `.mypy_cache`, `.pytest_cache`):<br>
  ```make clean```<br>
  
  + **Completely remove all local caches** along with the isolated virtual environment (`.venv`):<br>
  ```make fclean```<br>

  + **Wipe the environment completely**, discard lockfiles, and perform a clean re-synchronization:<br>
  ```make reset```<br>

  + **Reinstall project dependencies** after cleaning up intermediate build assets:<br>
  ```make re```<br>

  + **Verify code compliance** with standard `flake8` styles and check default `mypy` typing definitions:<br>
  ```make lint```<br>

  + **Enforce enhanced verification rules** using strict static type check configurations (`mypy --strict`):<br>
  ```make lint-strict```<br>

  + **Display itemized documentation** explaining every automation rule available: <br>
  ```make help```

  ### 2. Execution and Arguments
  The program can be executed explicitly using the underlying dependency manager via the following syntax:
  ```bash
  uv run python -m src [--functions_definition <path_to_json>] [--input <path_to_json>] [--output <path_to_json>] [--verbose]
  ```
  * `--functions_definition`: Catalog of available tools containing descriptions, parameter schemas, and argument type rules. (Default: `data/input/functions_definition.json`)
  * `--input`: User prompts containing unstructured natural language requests. (Default: `data/input/function_calling_tests.json`)
  * `--output`: Targets where the final array of structured function calls is saved. (Default: `data/output/output.json`)
  * `--verbose`: Enables granular terminal logging to track token-by-token sequence completion and regex evaluations in real time.
  
</details>

<details>
  <summary><h4>Usage Example</h4></summary>

  ### Command
  ```bash
  make run FUNCTIONS=example_func.json INPUT=example_input.json
  ```

  ### Catalog Definition (`example_func.json`)
  ```json
  [
    {
      "name": "fn_add_numbers",
      "description": "Add two numbers together and return their sum.",
      "parameters": {
        "a": {
          "type": "number"
        },
        "b": {
          "type": "number"
        }
      },
      "returns": {
        "type": "number"
      }
    },
    {
      "name": "fn_greet",
      "description": "Generate a greeting message for a person by name.",
      "parameters": {
        "name": {
          "type": "string"
        }
      },
      "returns": {
        "type": "string"
      }
    }
  ]
  ```

  ### Unstructured Input (`example_input.json`)
  ```json
  [
    {"prompt": "What is the sum of 2 and 3?"},
    {"prompt": "What is the sum of 265 and 345?"},
    {"prompt": "Greet shrek"},
    {"prompt": "Greet john"}
  ]
  ```

  ### Generated Structured Output
  ```json
  [
    {
      "prompt": "What is the sum of 2 and 3?",
      "name": "fn_add_numbers",
      "parameters": {"a": 2.0, "b": 3.0}
    },
    {
      "prompt": "What is the sum of 265 and 345?",
      "name": "fn_add_numbers",
      "parameters": {"a": 265.0, "b": 345.0}
    },
    {
      "prompt": "Greet shrek",
      "name": "fn_greet",
      "parameters": {"name": "shrek"}
    },
    {
      "prompt": "Greet john",
      "name": "fn_greet",
      "parameters": {"name": "john"}
    }
  ]
  ```

</details>

<details>
  <summary><h4>Algorithm Explanation</h4></summary>

  ___
  The execution core operates via a decoupled multi-tiered pipeline that executes structured inference across separate discrete generation stages:

  ### 1. Classification Phase (Function Selection)
  To determine which function fits an arbitrary user query, the pipeline reads all available schemas and builds an itemized prompt indexing names and technical definitions. The system then forces a bounded iterative matching sequence:
  * **Vector Prefix Masking:** Instead of sampling vocabulary probabilities freely, the application extracts raw logit scores from the model using `model.get_logits_from_input_ids()`.
  * **Prefix Trees (Tries) via Numpy:** The current partially generated token string is appended element-wise to every single candidate token string inside the model vocabulary using accelerated matrix operations (`np.char.add`). A boolean mask is computed to keep only tokens that represent valid character prefixes for the functional components defined in the input catalog.
  * **Logit Suppression:** Invalid indices are masked out by assigning them a value of $-\infty$, ensuring the argmax operation selects exclusively from valid tokens, terminating immediately when an exact string match is established.

  ### 2. Extraction Phase (Constrained Parameter Decoding)
  Once a target function is locked, a custom schema-to-regex engine maps the structured constraints into a single hyper-strict regular expression. For instance, given `fn_add_numbers`, a regular expression is compiled to enforce matching structure down to literal field placement:
  ```regex
  ^\{"prompt": "What is the sum of 2 and 3\?", "name": "fn_add_numbers", "parameters": \{"a": -?(?:0|[1-9]\d*)(?:\.\d+)?, "b": -?(?:0|[1-9]\d*)(?:\.\d+)?\}\}$
  ```
  The inference pipeline leverages **Partial Regular Expression Matching**:
  1.  **Logit Retrieval:** Next-token logit weights are requested from the causal network wrapper.
  2.  **Lookahead Validation Sequence:** Tokens are evaluated in descending probability order (`np.argsort(logits)[::-1]`). The model decodes a candidate token string, appends it to the accumulation buffer, and tests it against the strict schema using partial regex matching rules (`regex.match(json_regex, candidate, partial=True)`).
  3.  **Selection & Commit:** The highest probability candidate that satisfies partial structural validity is committed to the active sequence tensor. This sequence iterates token-by-token until a full match is reached, completely eliminating syntax, type, and punctuation errors.

</details>

<details>
  <summary><h4>Design Decisions</h4></summary>

  ___
  * **Pydantic Structural Enforcement:** Selected schemas and structural JSON validations are backed entirely by Pydantic models (`FunctionDef`), ensuring that inputs are safe and clear prior to kicking off resource-heavy inference loops.
  * **Numpy Matrix Parallelism:** Vectorized string primitives (`np.char.add` and `np.frompyfunc`) handle lookahead generation matches over vocabulary files. This replaces slow Python loops with high-performance native calculations, keeping execution times under control.
  * **Decoupled Multi-Tier Architecture:** Splitting the execution flow into an isolated function classification phase followed by a separate parameter extraction phase prevents cross-talk and drastically minimizes overall token generation depth compared to monolithic end-to-end extraction approaches.
  * **Strict Standard Compliance:** Built to run under explicit type systems (`mypy --strict`), fully adhering to `flake8` clean code guidelines, and implementing robust context management tools to eliminate resource leaking.

</details>

<details>
  <summary><h4>Performance Analysis</h4></summary>

  ___
  * **Structural Reliability:** Achieves exactly **100% syntactical validation** on all tests. Because arbitrary token strings that breach JSON grammar or argument formatting specifications are dropped at the logit level, malformed outputs, missing curly braces, trailing commas, and structural breaks are completely prevented.
  * **Classification Accuracy:** The `Qwen3-0.6B` model demonstrates over **95% semantic matching precision** across both standard testing sets and more advanced scenarios (such as discounts, currency conversion, and palindrome evaluations), proving that structured constraints unlock high-end reliability from compact models.
  * **Operational Execution Efficiency:** Standard evaluations process and export multi-prompt records in less than a minute on normal hardware setups, comfortably meeting the performance benchmarks.

</details>

<details>
  <summary><h4>Challenges Faced & Mitigations</h4></summary>

  ___
  * **The Blank Token Trapping Issue:** The tokenizer often produces empty decoded string matches (`""`) for specific special character flags or internal control tokens. If chosen, these would cause the program to stall out in endless generation loops. 
  * *Mitigation:* Added a guard condition (`if not token_str: continue`) directly inside the token validation loop to instantly ignore empty string tokens and preserve progress.
  * **Partial Token Boundaries:** Standard BPE tokens routinely split single words across structural markers (e.g., matching a portion of a parameter name string along with an opening bracket).
  * *Mitigation:* Leveraged the specialized `regex` package's partial matching support (`partial=True`). This allows the lookahead engine to successfully validate fractional token states before the entire sequence finishes rendering.
  * **High Inference Latency:** Running iterative lookahead evaluations across an entire vocabulary vocabulary using unoptimized code causes severe compute bottlenecks.
  * *Mitigation:* Replaced slow standard loops with highly parallelized Numpy matrix calculations inside the token verification stages (`get_valid_mask`).

</details>

<details>
  <summary><h4>Testing Strategy</h4></summary>

  ___
  The framework handles automated cross-validation using comprehensive regression parameters:
  * **Standard Validation Runs:** Automated integration checks are performed using baseline configurations:
      ```bash
      make run FUNCTIONS=data/input/functions_definition.json INPUT=data/input/function_calling_tests.json
      ```
  * **Complex Functional Validation:** Pipeline limits are tested against distinct financial calculations, regex string substitutions, and conditional state modifications using customized test files:
      ```bash
      make run FUNCTIONS=data/input/new_fn_def.json INPUT=data/input/new_prompts.json
      ```
  * **Boundary & Input Error Recovery:** Validated error boundaries by testing against truncated files, missing dictionary parameters, fields with incorrect data types, and entirely missing target assets.

</details>

<details>
  <summary><h4>Resources</h4></summary>

  ___
  ### 1. Links
  + [Pydantic Core Concepts](https://docs.pydantic.dev/latest/)
  + [Numpy Reference Guide](https://numpy.org/doc/stable/)
  + [Python regular expressions (regex package)](https://pypi.org/project/regex/)

  ### 2. AI Usage
  * **Debuging**: used claud and gemini to help me solve some errors regarding th constrain decoding
  * **Optimisation**: used the same AIs to help improve my code speed
</details>
