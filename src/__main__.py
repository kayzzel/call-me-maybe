from typing import Any
from json import load

import numpy as np

from llm_sdk.llm_sdk import Small_LLM_Model


def get_json_from_file(filename: str) -> dict[str, Any] | str:
    data: dict[str, Any]
    try:
        with open(filename, "r") as f:
            data = load(f)

    except Exception as err:
        return f"{err.__class__.__name__} Error: {err}"

    return data


def get_valid_mask(
            generated_so_far: str,
            valid_names: list[str],
            id_to_token_array: list[str]
        ) -> np.ndarray:

    vocab_size: int = len(id_to_token_array)
    candidates = np.char.add(generated_so_far, id_to_token_array)

    mask = np.zeros(vocab_size, dtype=bool)

    for name in valid_names:
        mask |= np.frompyfunc(
                lambda c: name.startswith(c), 1, 1
            )(candidates).astype(bool)

    return mask


def get_function_name(
                model: Small_LLM_Model,
                vocab: dict[str, Any],
                prompt: str,
                functions_name: list[str]
              ) -> str:

    prompt = f"""You are a function calling assistant.
Available functions: {functions_name}
User request: {prompt}
Call the most appropriate function.
Function name: """

    name: str = ""
    tokens = model.encode(prompt)[0].tolist()

    while name not in functions_name:
        mask = get_valid_mask(name, functions_name, list(vocab.keys()))

        logits = np.array(model.get_logits_from_input_ids(tokens))
        logits[~mask] = -np.inf

        next_token_id = np.argmax(logits)

        name += model.decode([next_token_id])

    return name


def main() -> None:
    model = Small_LLM_Model()

    user_prompt = "how can I add 2 and 3 ?"

    vocab = get_json_from_file(model.get_path_to_vocab_file())
    if isinstance(vocab, str):
        return

    print(get_function_name(model, vocab, user_prompt, ["fn_add", "fn_test"]))


if __name__ == "__main__":
    main()
