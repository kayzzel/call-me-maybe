from typing import Any

from json import load


def get_json_from_file(filename: str) -> Any | str:
    data: dict[str, Any]
    try:
        with open(filename, "r") as f:
            data = load(f)

    except Exception as err:
        return f"{err.__class__.__name__} Error: {err}"

    return data
