import numpy as np
import re

from enum import Enum
from typing import Any
from pydantic import BaseModel

from llm_sdk.llm_sdk import Small_LLM_Model


class ParamType(Enum):
    NUMBER = "number"
    STRING = "string"
    BOOL = "bool"


class FunctionDef(BaseModel):
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
    """Format function definitions into a readable prompt block."""
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
                vocab: dict[str, Any],
                prompt: str,
                functions: list[FunctionDef]
        ) -> str:
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
                prompt: str,
                function: FunctionDef
          ) -> dict[str, str | dict[str, str | int | float]]:

    from .json_utils import get_json_regex
    json_regex = get_json_regex(function)

    json_prompt: str = prompt.replace('"]', "'")
    json_str: str = (
        "{"
        f'"prompt": "{json_prompt}",'
        f'"name": "{function.name}",'
        '"parameters": {'
        f'"{function.parameters[0][0]}": '
    )

    full_prompt: str = (
        "you are a function calling assistant. "
        "Your job is to create a json that represent a function\n\n"
        "json format:\n"
        "{"
        '"prompt": <the given prompt>,'
        '"name": <the name of the function>,'
        '"parameters": {"<parm name>": <param value>, ...}'
        "}\n\n"
        "function info:\n"
        f"    name: {function.name}\n"
        f"    description: {function.description}\n"
        f"    parameters: {function.parameters}\n\n"
        f"use prompt: {prompt}\n\n"
        "json:\n"
        f"{json_str}"
    )
