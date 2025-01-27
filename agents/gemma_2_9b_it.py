#%%
import os
import re

#%%
from transformers import AutoTokenizer, AutoModelForCausalLM
from textgames import THE_GAMES, GAME_NAMES, LEVEL_IDS
from agents import run_with_agent


#%%
def gemma_postproc(response_txt, game_name, difficulty_level):
    # if game_name in [THE_GAMES[i] for i in ["1", "7"]]:  # crossword
    pat = re.compile(r'^```\n?([^\n`]*)\n?```')
    match = pat.search(response_txt)
    if match:
        return match.group(1).strip().replace(" ", "")

    # elif game_name == THE_GAMES["6"]:  # anagram
    pat = re.compile(r'\*\*\"?([^\"*]*)\"?\*\*')
    match = pat.search(response_txt)
    if match:
        return match.group(1)

    return response_txt or ""


#%%
def get_gemma_response(texts, game_name, difficulty_level, turn):
    # global gen_model, tokenizer
    messages = [
        {"role": ("model" if i % 2 else "user"), "content": text}
        for i, text in enumerate(texts)
    ]

    input_ids = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        return_tensors="pt"
    ).to(gen_model.device)

    terminators = [
        tokenizer.eos_token_id,
        tokenizer.convert_tokens_to_ids("<|eot_id|>")
    ]

    outputs = gen_model.generate(
        input_ids,
        max_new_tokens=100,
        eos_token_id=terminators,
        do_sample=True,
        temperature=.001,
        top_p=1,
    )

    response = outputs[0][input_ids.shape[-1]:]
    return tokenizer.decode(response, skip_special_tokens=True).strip()


#%%
def _getenv_as_int(attr, default=None):
    ret = os.getenv(attr, default)
    return None if ret is None else int(ret)


GAME_ST, GAME_ED = _getenv_as_int("TG_GAME_ST", None), _getenv_as_int("TG_GAME_ED", None)
LVL_ST, LVL_ED = _getenv_as_int("TG_LEVEL_ST", None), _getenv_as_int("TG_LEVEL_ED", '3')
SID_ST, SID_ED = _getenv_as_int("TG_SID_ST", None), _getenv_as_int("TG_SID_ED", None)
ONE_SHOT = bool(int(os.getenv("TG_ONESHOT", "0")))


#%%
if __name__ == "__main__":
    fp_out = (f"model_outputs/results_gemma-2-9b-it"
              f"{'' if ONE_SHOT else '.zs'}"
              f"{'' if GAME_ST is None else f'.{GAME_ST}'}"
              f"{'' if LVL_ST is None else f'.{LVL_ST}'}"
              f".jsonl")
    gen_model_checkpoint = "google/gemma-2-9b-it"

    quantize = True
    _kwargs = {
        "device_map": "auto",
    } if quantize else {}

    gen_model = AutoModelForCausalLM.from_pretrained(gen_model_checkpoint, **_kwargs)
    tokenizer = AutoTokenizer.from_pretrained(gen_model_checkpoint, **_kwargs)

    run_with_agent(
        fp_out,
        get_gemma_response,
        gemma_postproc,
        game_names_list=GAME_NAMES[GAME_ST:GAME_ED],
        level_ids_list=LEVEL_IDS[LVL_ST:LVL_ED],
        sid_indices=(list(map(lambda r: f"session_{r:04}", range(SID_ST or 0, SID_ED or 1000)))
                     if SID_ST or SID_ED else None),
        prepend_example=ONE_SHOT,
        # remove_if_output_file_exist=False,
    )
