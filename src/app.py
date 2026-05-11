from typing import Any

from llm_sdk.llm_sdk import Small_LLM_Model
from .get_function_info import FunctionDef


class App:
    def __init__(
            self,
            prompts: list[str],
            functions: list[FunctionDef],
            output_file: str
            ) -> None:
        self.__model: Small_LLM_Model = Small_LLM_Model()

        self.__prompts: list[str] = prompts
        self.__functions: list[FunctionDef] = functions

        self.__functions_info: list[dict[str, str | dict[str, str]]] = []
        self.__output_file: str = output_file

    def get_function_from_prompt(self) -> None:
        pass

    def format_function_info(self) -> list[dict[str, Any]]:
        return [{}]


def app_usage(usage: str) -> str:
    if usage == "params":
        return (
                """
usage:
    uv run python -m src [--functions_definition <function_definition_file>] \
[--input <input_file>] [-- output <output_file>]

    --functions_definition : the functions that will be picked to find \
the right one
    --input                : the file that contain the prompts
    --output               : the file in wich all the function chosen \
will be put
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
              "type": <'string' or 'number'>
            },
            ...
        }
        "returns": {
          "type": <'string' or 'number'>
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
