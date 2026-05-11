import re


def pars_params(params: list[str]) -> dict[str, str]:

    PATH_REGEX = re.compile(
        r'^'
        r'(?:'
            r'(?:[a-zA-Z]:\\|\\\\)'  # Windows absolute: C:\ or \\server
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

    files: dict[str, str | None] = {
            "--functions_definition": None,
            "--input": None,
            "--ouput": None,
    }

    while param_index < 6:
        if params[param_index] not in files.keys():
            raise ValueError("Invalid usage")

        if params[param_index] is not None:
            raise ValueError("Redefinition of a param")

        if len(params) <= param_index + 1:
            raise ValueError("No value after a flag")

        if (
                not PATH_REGEX.match(params[param_index]) or
                not params[param_index] or params[param_index].isspace()
                ):
            raise ValueError("Invalid file format")

        files[params[param_index]] = params[param_index + 1]

    return {
            "--functions_definition": (
                    "data/input/functions_definition.json"
                    if not files["--functions_definition"]
                    else files["--functions_definition"]
                ),
            "--input": (
                    "data/input/function_calling_tests.json"
                    if not files["--input"]
                    else files["--input"]
                ),
            "--ouput": (
                    "data/ouput/ouput.json"
                    if not files["--ouput"]
                    else files["--ouput"]
                ),
    }
