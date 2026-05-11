def get_valid_mask(
            generated_so_far: str,
            valid_names: list[str],
            id_to_token_array: list[str],
            target_vocab_size: int
        ) -> np.ndarray:

    candidates = np.char.add(generated_so_far, id_to_token_array)

    mask = np.zeros(target_vocab_size, dtype=bool)

    temp_mask = np.zeros(len(id_to_token_array), dtype=bool)
    for name in valid_names:
        temp_mask |= np.frompyfunc(
                lambda c: name.startswith(c), 1, 1
            )(candidates).astype(bool)

    mask[:len(temp_mask)] = temp_mask

    return mask


def format_functions_for_prompt(functions: list[dict[str, Any]]) -> str:
    """Format function definitions into a readable prompt block."""
    lines = []
    for fn in functions:
        # function name + description
        lines.append(f"- {fn['name']}: {fn['description']}")
        # parameters with types
        params = fn.get("parameters", {})
        for param_name, param_info in params.items():
            lines.append(f"    {param_name} ({param_info['type']})")
    return "\n".join(lines)


def get_parametters(
            model: Small_LLM_Model,
            function: dict[str, str | dict[str, str]],
            prompt: str,
        ) -> Any:
    full_prompt = f"""You are a function calling assistant. \
Your job is to return the parameters of the function in the \
prompt in a tupple format

function:
    name: {function['name']}
    description: {function['description']}
    parameters: {function['parameters']}

Rules:
    -Ouput the parameters in a tupple format, in parenthesis and \
only separated by a comas
    -In the tupple put only the value of the parameters separated \
by only a comas
    -If there is a single parameter put just it inside the parentheses
    -The parameters must have the corresponding type of the function \
parameters
    -The parameters must be in the order of the functions definition

User request: {prompt}

the parameters are: ("""

    token_ids: list[int] = model.encode(full_prompt)[0].tolist()
    number_regex: str = r"-?[\d]+(.[\d]+)?"
    number_gen: str = ""
    finished: bool = False
    while not finished:

        logits: list[float] = model.get_logits_from_input_ids(token_ids)
        sorted_indexes = np.argsort(logits)[::-1]

        for logit_id in sorted_indexes:

            decoded: str = model.decode([logit_id])

            if ")" in decoded:
                number_gen += decoded.split(")")[0]
                finished = True
                break

            elif (
                re.match(number_regex, (number_gen + decoded))
                or decoded == ","
                    ):
                number_gen += decoded
                token_ids.append(logit_id)
                break

    parameters: list[float] = [float(nb) for nb in number_gen.split(",") if nb.strip()]
    return parameters


def get_function_name(
                model: Small_LLM_Model,
                vocab: dict[str, Any],
                prompt: str,
                functions: list[dict[str, Any]]
        ) -> str:
    functions_name = [f["name"] for f in functions]
    functions_desc = format_functions_for_prompt(functions)

    full_prompt = f"""You are a function calling assistant. \
Your job is to select the most appropriate function for the user request.

Available functions:
{functions_desc}

Rules:
- Output ONLY the function name, nothing else.
- Pick the single most relevant function.
- Do not explain your choice.

User request: {prompt}

The most appropriate function name is: """

    name: str = ""
    tokens = model.encode(full_prompt)[0].tolist()

    while name not in functions_name:
        logits = np.array(model.get_logits_from_input_ids(tokens))

        mask = get_valid_mask(
                name,
                functions_name,
                list(vocab.keys()),
                len(logits)
            )
        logits[~mask] = -np.inf

        next_token_id = np.argmax(logits)

        name += model.decode([next_token_id])
        tokens.append(next_token_id)

    return name
