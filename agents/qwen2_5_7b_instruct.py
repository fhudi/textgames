#%%
import os
import re

#%%
from transformers import AutoTokenizer, AutoModelForCausalLM
from textgames import THE_GAMES, GAME_NAMES, LEVEL_IDS
from agents import run_with_agent


#%%
def _getenv_as_int(attr, default=None):
    ret = os.getenv(attr, default)
    return None if ret is None else int(ret)


GAME_ST, GAME_ED = _getenv_as_int("TG_GAME_ST", None), _getenv_as_int("TG_GAME_ED", None)
LVL_ST, LVL_ED = _getenv_as_int("TG_LEVEL_ST", None), _getenv_as_int("TG_LEVEL_ED", '3')
SID_ST, SID_ED = _getenv_as_int("TG_SID_ST", None), _getenv_as_int("TG_SID_ED", None)
N_TURNS = _getenv_as_int("TG_N_TURNS", 3)
ONE_SHOT = bool(int(os.getenv("TG_ONESHOT", "0")))
QWEN_SIZE = int(os.getenv("TG_QWEN_SIZE", "32"))    # {3, 7, 14, 32, 72}  unsupported: {0.5, 1.5}


#%%
def qwen_postproc(response_txt, game_name, difficulty_level, *args, **kwargs):
    # # if game_name in [THE_GAMES[i] for i in ["1", "7"]]:  # crossword
    # pat = re.compile(r'^```\n?([^`]*)\n?```')
    # match = pat.search(response_txt)
    # if match:
    #     return match.group(1).strip().replace(" ", "")
    #
    # # elif game_name == THE_GAMES["6"]:  # anagram
    # pat = re.compile(r'\*\*\"?([^\"*]*)\"?\*\*')
    # match = pat.search(response_txt)
    # if match:
    #     return match.group(1).strip()
    return response_txt or ""


#%%
def get_qwen_response(texts, game_name, difficulty_level, turn, *args, **kwargs):
    # global model, tokenizer
    messages = [
        {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."},
        *[{"role": ("assistant" if i % 2 else "user"), "content": text} for i, text in enumerate(texts)]
    ]

    text_inputs = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    model_inputs = tokenizer([text_inputs], return_tensors="pt").to(model.device)

    model.generation_config.temperature = None
    model.generation_config.top_k = None
    model.generation_config.top_p = None
    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=128,
        do_sample=False,
    )
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]

    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return response.strip()


#%%
if __name__ == "__main__":
    fp_out = (f"model_outputs/__runs__/results_qwen2-5-{QWEN_SIZE}b-instruct"
              f"{'.1s' if ONE_SHOT else '.zs'}"
              f"{'' if GAME_ST is None else f'.{GAME_ST}'}"
              f"{'' if LVL_ST is None else f'.{LVL_ST}'}"
              f".jsonl")

    model_name = f"Qwen/Qwen2.5-{QWEN_SIZE}B-Instruct"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto",
        torch_dtype="auto",
        # **({"torch_dtype": "auto"} if QWEN_SIZE > 7 else {}),
    )
    print(f"    > model.dtype: {model.dtype}")

    run_with_agent(
        fp_out,
        get_qwen_response,
        qwen_postproc,
        n_turns=N_TURNS,
        game_names_list=GAME_NAMES[GAME_ST:GAME_ED],
        level_ids_list=LEVEL_IDS[LVL_ST:LVL_ED],
        sid_indices=(list(map(lambda r: f"session_{r:04}", range(SID_ST or 0, SID_ED or 1000)))
                     if SID_ST or SID_ED else None),
        prepend_example=ONE_SHOT,
        # remove_if_output_file_exist=False,
    )
