import re

from typing import Any
from pydantic import ValidationError

from .get_function_info import FunctionDef, ParamType
from .json_utils import get_json_from_file


def pars_params(params: list[str]) -> dict[str, str]:
    """
    Parse command-line parameters into a dictionary of configuration paths.

    Parameters:
        params: List of raw command-line argument strings (typically sys.argv).

    Returns:
        Dictionary containing parsed or default file paths and verbosity
        flag status.
    """
    params = params[1::]

    PATH_REGEX = re.compile(
        r'^'
        r'(?:'
        r'(?:[a-zA-Z]:\\|\\\\)'
        r'|'
        r'/{1,2}'                 # Unix absolute: / or //
        r'|'
        r'\.{1,2}/'              # relative: ./ or ../
        r')?'
        r'(?:[^\\/:*?"<>|\r\n]+[/\\])*'  # intermediate directories
        r'[^\\/:*?"<>|\r\n]*'            # filename (no illegal chars)
        r'(?:\.[a-zA-Z0-9]{1,10})?'      # optional extension
        r'$'
    )

    param_index: int = 0

    parameters: dict[str, str | None] = {
            "--functions_definition": None,
            "--input": None,
            "--output": None,
            "--verbose": None
    }

    while param_index < len(params):
        if params[param_index] == "--verbose":
            parameters["--verbose"] = "True"
            param_index += 1
            continue

        if params[param_index] not in parameters.keys():
            print(params[param_index])
            raise ValueError("Invalid usage")

        if parameters[params[param_index]] is not None:
            raise ValueError("Redefinition of a param")

        if len(params) <= param_index + 1:
            raise ValueError("No value after a flag")

        if (
                not PATH_REGEX.match(params[param_index]) or
                not params[param_index] or params[param_index].isspace()
                ):
            raise ValueError("Invalid file format")

        parameters[params[param_index]] = params[param_index + 1]
        param_index += 2

    return {
            "--functions_definition": (
                    "data/input/functions_definition.json"
                    if not parameters["--functions_definition"]
                    else parameters["--functions_definition"]
                ),
            "--input": (
                    "data/input/function_calling_tests.json"
                    if not parameters["--input"]
                    else parameters["--input"]
                ),
            "--output": (
                    "data/output/output.json"
                    if not parameters["--output"]
                    else parameters["--output"]
                ),
            "--verbose": (
                    ""
                    if not parameters["--verbose"]
                    else parameters["--verbose"]
                )
    }


def get_functions_from_file(filename: str) -> list[FunctionDef]:
    """
    Load and validate function definitions from a specified JSON file.

    Parameters:
        filename: Path to the JSON file containing function definitions.

    Returns:
        List of validated FunctionDef schemas.
    """

    functions_def: list[FunctionDef] = []
    functions: Any | str = get_json_from_file(filename)

    if isinstance(functions, str):
        raise ValueError(functions)

    if not isinstance(functions, list):
        raise ValueError("The functions must be an array of dict")

    for fn in functions:
        params: list[tuple[str, ParamType]] = []

        if not isinstance(fn, dict):
            raise ValueError("each function must be a dict")

        if (
                {'name', 'description', 'parameters', 'returns'}
                != set(fn.keys())
        ):
            raise ValueError("Wrong function definition keys format")

        if not isinstance(fn["parameters"], dict):
            raise ValueError("The parameters must be a dict")
        for key, value in fn["parameters"].items():
            if (
                    not isinstance(value, dict) or
                    len(value.items()) != 1 or
                    list(value.keys())[0] != "type"
                    ):
                raise ValueError("Wrong parameters format")
            else:
                params.append((key, value["type"]))

        if not isinstance(fn["returns"], dict):
            raise ValueError("The return values must be a dict")

        if len(fn["returns"]) != 1 or not fn["returns"].get("type"):
            raise ValueError("There must be one type for the retunr value")

        try:
            function = FunctionDef(
                        name=fn["name"],
                        description=fn["description"],
                        parameters=params,
                        returns=fn["returns"]["type"]
                    )

        except ValidationError as err:
            error_message = ""
            for error in err.errors():
                error_message += error["msg"] + "\n"
            raise ValueError(error_message)

        else:
            functions_def.append(function)

    return functions_def


def get_prompts_from_file(filename: str) -> list[str]:
    """
    Extract a list of raw user prompts from a structured JSON file.

    Parameters:
        filename: Path to the JSON file containing wrapped prompt objects.

    Returns:
        List of extracted prompt strings.
    """

    prompts: list[str] = []
    prompts_info: Any | str = get_json_from_file(filename)

    if isinstance(prompts_info, str):
        raise ValueError(prompts_info)

    if not isinstance(prompts_info, list):
        raise ValueError("The prompts must be an array of dict")

    for pr in prompts_info:

        if not isinstance(pr, dict):
            raise ValueError("each prompt must be a dict")

        if len(pr.keys()) != 1 or not pr.get("prompt"):
            raise ValueError("Wrong format for prompt")

        if not isinstance(pr["prompt"], str):
            raise ValueError("The prompt must be a str")

        prompts.append(pr["prompt"])

    return prompts
