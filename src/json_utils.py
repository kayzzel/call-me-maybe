from typing import Any

from json import load
from .get_function_info import FunctionDef


def get_json_from_file(filename: str) -> Any | str:
    data: dict[str, Any]
    try:
        with open(filename, "r") as f:
            data = load(f)

    except Exception as err:
        return f"{err.__class__.__name__} Error: {err}"

    return data

def get_json_regex(function: FunctionDef) -> str:
    return ""
