from typing import Any

from json import load
from .get_function_info import FunctionDef, ParamType


def get_json_from_file(filename: str) -> Any | str:
    data: dict[str, Any]
    try:
        with open(filename, "r") as f:
            data = load(f)

    except Exception as err:
        return f"{err.__class__.__name__} Error: {err}"

    return data


def get_json_full_regex(function: FunctionDef) -> str:
    """
    Returns a single regex that validates a complete JSON output
    for the given function definition.

    Matches the entire json_str including the parts already written:
    {
        "prompt": "...",
        "name": "fn_name",
        "parameters": {"a": 2.0, "b": 3.0}
    }
    """

    NUMBER_RE = r'-?(?:0|[1-9]\d*)(?:\.\d+)?'
    STRING_RE = r'"[^"]*"'
    BOOL_RE = r'(?:true|false)'

    TYPE_MAP = {
        ParamType.NUMBER: NUMBER_RE,
        ParamType.STRING: STRING_RE,
        ParamType.BOOL:   BOOL_RE,
    }

    # build each parameter fragment: "param_name": <value_regex>
    param_parts = []
    for param_name, param_type in function.parameters:
        param_parts.append(
            r'\s*"' + re.escape(param_name) + r'"\s*:\s*' + TYPE_MAP[param_type]
        )

    params_re = r',\s*'.join(param_parts)

    return (
        r'^\s*\{\s*\n'
        r'\s*"prompt"\s*:\s*"[^"]*"\s*,\s*\n'
        r'\s*"name"\s*:\s*"' + re.escape(function.name) + r'"\s*,\s*\n'
        r'\s*"parameters"\s*:\s*\{' + params_re + r'\s*\}\s*\n'
        r'\s*\}\s*$'
    )
