import numpy as np
import regex

from enum import Enum
from json import loads
from typing import Any
from pydantic import BaseModel

from llm_sdk.llm_sdk import Small_LLM_Model


class ParamType(Enum):
    """Parameter type enumeration for function definitions."""
    NUMBER = "number"
    STRING = "string"
    BOOL = "bool"


class FunctionDef(BaseModel):
    """
    Function definition schema.

    Attributes:
        name: Function name.
        description: Function description.
        parameters: List of (parameter_name, parameter_type) tuples.
        returns: Return type of the function.
    """
    name: str
    description: str
    parameters: list[tuple[str, ParamType]]
    returns: ParamType


def get_valid_mask(
            generated_so_far: str,
            valid_names: list[str],
            id_to_token_array: list[str],
            target_vocab_size: int
        ) -> np.ndarray:
    """
    Create a mask for valid next tokens based on valid function names.

    Parameters:
        generated_so_far: String generated so far.
        valid_names: List of valid function names.
        id_to_token_array: Array mapping token IDs to token strings.
        target_vocab_size: Size of the vocabulary.

    Returns:
        Boolean array mask indicating valid tokens.
    """

    candidates = np.char.add(generated_so_far, id_to_token_array)

    mask = np.zeros(target_vocab_size, dtype=bool)

    temp_mask = np.zeros(len(id_to_token_array), dtype=bool)
    for name in valid_names:
        temp_mask |= np.frompyfunc(
                lambda c: name.startswith(c), 1, 1
            )(candidates).astype(bool)

    mask[:len(temp_mask)] = temp_mask

    return mask


def format_functions_for_prompt(functions: list[FunctionDef]) -> str:
    """
    Format function definitions into a readable prompt block.

    Parameters:
        functions: List of function definitions.

    Returns:
        Formatted string with function names, descriptions, and parameters.
    """
    lines = []
    for fn in functions:
        # function name + description
        lines.append(f"- {fn.name}: {fn.description}")
        # parameters with types
        params = fn.parameters
        for param_name, param_info in params:
            lines.append(f"    {param_name} ({param_info})")
    return "\n".join(lines)


def get_function_name(
                model: Small_LLM_Model,
                vocab: dict[str, int],
                prompt: str,
                functions: list[FunctionDef]
        ) -> str:
    """
    Identify the most appropriate function name for a given prompt.

    Parameters:
        model: Language model instance.
        vocab: Token vocabulary dictionary.
        prompt: User prompt to process.
        functions: Available function definitions.

    Returns:
        Name of the selected function.
    """

    functions_name = [f.name for f in functions]
    functions_desc = format_functions_for_prompt(functions)

    full_prompt = f"""You are a function calling assistant. \
Your job is to select the most appropriate function for the user request.

Available functions:
{functions_desc}

Rules:
- Output ONLY the function name, nothing else.
- Pick the single most relevant function.
- Do not explain your choice.

User request: {prompt}

The most appropriate function name is: """

    name: str = ""
    tokens = model.encode(full_prompt)[0].tolist()

    while name not in functions_name:
        logits = np.array(model.get_logits_from_input_ids(tokens))

        mask = get_valid_mask(
                name,
                functions_name,
                list(vocab.keys()),
                len(logits)
            )
        logits[~mask] = -np.inf

        next_token_id = int(np.argmax(logits))

        name += model.decode([next_token_id])
        tokens.append(next_token_id)

    return name


def get_function_json(
                model: Small_LLM_Model,
                prompt: str,
                function: FunctionDef,
                verbose: bool
          ) -> dict[str, str | dict[str, str | int | float | bool]]:
    """
    Extract function parameters from prompt as JSON.

    Parameters:
        model: Language model instance.
        prompt: User prompt to extract parameters from.
        function: Function definition to match against.
        verbose: Enable verbose output.

    Returns:
        Dictionary with prompt, function name, and extracted parameters.
    """

    json_prompt: str = regex.escape(
            prompt, special_only=True, literal_spaces=True
    )
    if verbose:
        print("\n\n\033[96mGeting function for prompt:", prompt, "\033[0m\n")

    if not function.parameters:
        return {
            "prompt": json_prompt,
            "name": function.name,
            "parameter": {}
        }

    from .json_utils import get_json_regex
    json_regex = get_json_regex(function, json_prompt)

    json_str: str = ""
    full_prompt: str = (
            f"""Prompt: {prompt}
Description: {function.description}
Output: json with literal strings, complex numbers (float priority) \
        and simple regex.
Answer:
{json_str}"""
    )

    tokens: list[int] = model.encode(full_prompt).tolist()[0]

    while not regex.match(json_regex, json_str):
        logits = np.array(model.get_logits_from_input_ids(tokens))

        next_token_id = -1
        for token in np.argsort(logits)[::-1]:
            token_str = model.decode([token])
            if not token_str:
                continue
            candidate = json_str + token_str
            if regex.match(json_regex, candidate, partial=True):
                next_token_id = token
                next_token_str = token_str
                break

        if next_token_id == -1:
            raise ValueError(
                f"No valid tokens found at: {repr(json_str)}"
            )

        json_str += next_token_str
        if verbose:
            print(json_str)
        tokens.append(next_token_id)

    parsed: dict[str, Any] = loads(json_str)
    return parsed
