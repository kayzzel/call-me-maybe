import regex

from os import path
from typing import Any
from json import load, dump

from .get_function_info import FunctionDef, ParamType


def write_json_to_file(filename: str, json: Any) -> None:
    try:
        dirname = path.dirname(filename)

        if dirname and not path.exists(dirname):
            raise FileNotFoundError(
                    "path to the file does not exist "
                    f"(path: {filename})"
                )

        with open(filename,  "w") as file:
            dump(json, file, indent=4)

    except Exception as err:
        raise ValueError(f"{err.__class__.__name__} Error: {err}")


def get_json_from_file(filename: str) -> Any | str:
    data: dict[str, Any]
    try:
        with open(filename, "r") as f:
            data = load(f)

    except Exception as err:
        return f"{err.__class__.__name__} Error: {err}"

    return data


def get_json_regex(function: FunctionDef, prompt: str) -> str:
    """
    Returns a regex that validates a complete JSON output
    for the given function definition.

    Matches:
    {
        "prompt": "...",
        "name": "fn_name",
        "parameters": {"param_name": <value>, ...}
    }
    """
    NUMBER_RE = r'-?(?:0|[1-9]\d*)(?:\.\d+)?'
    STRING_RE = r'"[^"\\]*"'
    BOOL_RE = r'(?:true|false)'

    TYPE_MAP = {
        ParamType.NUMBER: NUMBER_RE,
        ParamType.STRING: STRING_RE,
        ParamType.BOOL:   BOOL_RE,
    }

    # each tuple is (param_name, param_type)
    param_parts = []
    for param_name, param_type in function.parameters:
        param_parts.append(
            r'"' + regex.escape(param_name, special_only=True, literal_spaces=True) +
            r'": ' + TYPE_MAP[param_type]
        )

    params_re = r', '.join(param_parts)

    return (str(
        r'^\{'
        r'"prompt": "' + prompt.replace('"', '\\\\"') + r'", '
        r'"name": "' + regex.escape(function.name, special_only=True, literal_spaces=True) + r'", '
        r'"parameters": \{' + params_re + r'\}'
        r'\}$'
    ))
