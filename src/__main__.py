from sys import argv

from .app import app_usage, App
from .get_files import (
        pars_params,
        get_prompts_from_file,
        get_functions_from_file
    )


def main() -> None:
    try:
        params = pars_params(argv)
    except ValueError as err:
        print(f"Error: {err}")
        print(app_usage("params"))
        return

    try:
        functions = get_functions_from_file(params["--functions_definition"])
    except ValueError as err:
        print(f"Error: {err}")
        print(app_usage("functions"))
        return

    try:
        promps = get_prompts_from_file(params["--input"])
    except ValueError as err:
        print(f"Error: {err}")
        print(app_usage("promps"))
        return

    try:
        app: App = App(
                promps,
                functions,
                output_file=params["--output"]
            )
    except ValueError as err:
        print(f"Error: {err}")

    app.get_function_from_prompt()

    try:
        app.write_functions_info()
    except ValueError as err:
        print(f"Error: {err}")


if __name__ == "__main__":
    main()
