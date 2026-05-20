from time import time
from typing import Any, Callable
from functools import wraps
from rich.progress import track

from llm_sdk.llm_sdk import Small_LLM_Model
from .json_utils import get_json_from_file, write_json_to_file
from .get_function_info import (
        FunctionDef,
        get_function_name,
        get_function_json,
)


def timing_decorator(appear: bool) -> Callable[[Any], Any]:
    """
    Decorator that measures function execution time.

    Parameters:
        appear: If True, prints execution time in minutes and seconds.

    Returns:
        Decorator function that wraps the target function with timing.
    """

    def decorator(func: Callable[[Any], Any]) -> Any:

        @wraps(func)
        def wrapper(*args: list[Any], **kwargs: list[Any]) -> Any:
            start = time()
            result = func(*args, **kwargs)
            end = time()
            taken = end - start
            minuntes = int(taken // 60)
            seconds = int(taken % 60)
            if appear:
                print(
                    f"\033[92m{func.__name__} took",
                    f"{minuntes} min and" if minuntes else "",
                    f"{seconds} seconds\033[0m"
                )
            return result
        return wrapper

    return decorator


class App:
    """
    Processes prompts to match them with functions using a language model.

    Attributes:
        __model: Small language model for function matching.
        __vocab: Token vocabulary dictionary.
        __prompts: User prompts to process.
        __functions: Available function definitions.
        __functions_info: Generated function call information.
        __output_file: Output JSON file path.
        __verbose: Enable verbose output.
    """
    def __init__(
            self,
            prompts: list[str],
            functions: list[FunctionDef],
            output_file: str,
            verbose: bool
            ) -> None:
        self.__model: Small_LLM_Model = Small_LLM_Model()

        vocab_file = self.__model.get_path_to_vocab_file()
        vocab = get_json_from_file(vocab_file)
        if isinstance(vocab, str):
            raise ValueError(vocab)
        self.__vocab: dict[str, int] = vocab

        self.__prompts: list[str] = prompts
        self.__functions: list[FunctionDef] = functions

        self.__functions_info: list[
                dict[str, str | dict[str, str | int | float | bool]]
                                    ] = []
        self.__output_file: str = output_file

        self.__verbose = verbose

    def write_functions_info(self) -> None:
        """
        Write generated function information to output file.
        """

        if not self.__functions_info:
            raise ValueError("The functions info has not been loaded")

        try:
            write_json_to_file(
                    self.__output_file,
                    self.__functions_info
                )

        except Exception as err:
            raise ValueError(err)

    def get_function_from_prompt(self) -> None:
        """
        Process prompts to identify matching functions and extract parameters.
        and set them in self.__functions_info
        """

        @timing_decorator(self.__verbose)
        def get_function_info_from_prompt() -> None:

            for prompt in track(self.__prompts, description="Processing..."):
                fn_name: str = get_function_name(
                        self.__model,
                        self.__vocab,
                        prompt,
                        self.__functions
                )

                function = [
                        fn for fn in self.__functions if fn.name == fn_name
                    ][0]

                function_json = get_function_json(
                        self.__model,
                        prompt,
                        function,
                        self.__verbose
                )

                self.__functions_info.append(function_json)

        get_function_info_from_prompt()


def app_usage(usage: str) -> str:
    """
    Return usage documentation for the application.

    Parameters:
        usage: Type of documentation ("params", "functions", or "prompts").

    Returns:
        Formatted usage string, or empty string if type not recognized.
    """

    if usage == "params":
        return (
                """
usage:
    uv run python -m src [--functions_definition <function_definition_file>] \
[--input <input_file>] [--output <output_file>] [--verbose]

    --functions_definition : the functions that will be picked to find \
the right one
    --input                : the file that contain the prompts
    --output               : the file in wich all the function chosen \
will be put
    --verbose              : activate verbose mode
"""
            )

    if usage == "functions":
        return (
                """
usage:
[
    {
        "name"
        "description"
        "parameters": {
            <param name in str>: {
              "type": <'string' or 'number' or 'integer' or 'bool'>
            },
            ...
        }
        "returns": {
          "type": <'string' or 'number' or 'integer' or 'bool'>
        }
    },
    ...
]
"""
        )
    if usage == "prompts":
        return (
                """
usage:
[
    {
         "prompt": <a prompt in string format>
    },
    ...
]
"""
        )

    return ""
