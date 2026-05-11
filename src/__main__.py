from llm_sdk.llm_sdk import Small_LLM_Model


def main() -> None:
    model = Small_LLM_Model()

    user_prompt = "what is the square root of 81"

    vocab = get_json_from_file(model.get_path_to_vocab_file())
    functions = get_json_from_file("data/input/functions_definition.json")
    if isinstance(vocab, str) or isinstance(functions, str):
        return
    func_name = (get_function_name(model, vocab, user_prompt, functions))
    function = [f for f in functions if f['name'] == func_name][0]
    print(list(function['parameters'].values())[0]['type'])
    print("name:", func_name)
    parameters = get_parametters(model, function, user_prompt)
    print("parameters:", parameters)


if __name__ == "__main__":
    main()
