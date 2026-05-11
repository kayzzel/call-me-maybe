from typing import Any

from llm_sdk.llm_sdk import Small_LLM_Model


class  App:
    def __init__(self):
        self.model: Small_LLM_Model = Small_LLM_Model

        self.loaded: bool = False
        self.promps: list[dict[str, str]]
        self.functions: list[dict[str, str | dict[str, str]]]

        self.functions_info: list[dict[str, str | dict[str, str]]] = []
        self.output_file: str
