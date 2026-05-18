from llm_sdk.llm_sdk import Small_LLM_Model
from .json_utils import get_json_from_file, write_json_to_file
from .get_function_info import (
        FunctionDef,
        get_function_name,
        get_function_json,
)


class App:
    def __init__(
            self,
            prompts: list[str],
            functions: list[FunctionDef],
            output_file: str
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

    def write_functions_info(self) -> None:

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
        for prompt in self.__prompts:
            fn_name: str = get_function_name(
                    self.__model, self.__vocab, prompt, self.__functions
            )

            function = [fn for fn in self.__functions if fn.name == fn_name][0]
            function_json = get_function_json(
                    self.__model, self.__vocab, prompt, function
            )

            self.__functions_info.append(function_json)


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
