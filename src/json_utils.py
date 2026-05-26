import regex

from os import makedirs, path
from typing import Any
from json import load, dump

from .get_function_info import FunctionDef, ParamType


def write_json_to_file(filename: str, json: Any) -> None:
    """
    Write a JSON-serializable object to a file, creating directories if needed.

    Parameters:
        filename: Path to the target output file.
        json: Any JSON-serializable data structure to dump.

    Returns:
        None
    """
    try:
        dirname = path.dirname(filename)

        if dirname and not path.exists(dirname):
            makedirs(dirname, exist_ok=True)

        with open(filename,  "w") as file:
            dump(json, file, indent=4)

    except Exception as err:
        raise ValueError(f"{err.__class__.__name__} Error: {err}")


def get_json_from_file(filename: str) -> Any | str:
    """
    Read and parse JSON content from a specified file.

    Parameters:
        filename: Path to the JSON file to read.

    Returns:
        The parsed JSON data structure, or an error message string
        if reading fails.
    """
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

    Parameters:
        function: The function definition schema containing parameters.
        prompt: The original user prompt to embed into the metadata.

    Returns:
        A strict regular expression string that matches the expected
        JSON structure.
    """
    NUMBER_RE = r'-?(?:0|[1-9]\d{0,100})(?:\.\d{1,100})?'
    INTEGER_RE = r'-?(?:0|[1-9]\d{0,100})'
    STRING_RE = r'"(?:[^"\\]|\\.){0,1000}"'
    BOOL_RE = r'(?:true|false)'

    TYPE_MAP = {
        ParamType.NUMBER: NUMBER_RE,
        ParamType.INTEGER: INTEGER_RE,
        ParamType.STRING: STRING_RE,
        ParamType.BOOL:   BOOL_RE,
    }

    # each tuple is (param_name, param_type)
    param_parts = []
    for param_name, param_type in function.parameters:
        param_parts.append(
            r'"' + regex.escape(
                param_name, special_only=True, literal_spaces=True
                ) +
            r'": ' + TYPE_MAP[param_type]
        )

    params_re = r', '.join(param_parts)

    return (str(
        r'^\{'
        r'"prompt": ' + prompt + r', '
        r'"name": "' + regex.escape(
            function.name, special_only=True, literal_spaces=True
            ) + r'", '
        r'"parameters": \{' + params_re + r'\}'
        r'\}$'
    ))
