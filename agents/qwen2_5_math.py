#%%
import os
import re

#%%
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForCausalLM, set_seed, BitsAndBytesConfig
from textgames import GAME_NAMES, LEVEL_IDS
from agents import run_with_agent


#%%
def set_all_seed(seed=42):
    set_seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


#%%
def _getenv_as_int(attr, default=None):
    ret = os.getenv(attr, default)
    return None if ret is None else int(ret)


GAME_ST, GAME_ED = _getenv_as_int("TG_GAME_ST", None), _getenv_as_int("TG_GAME_ED", None)
LVL_ST, LVL_ED = _getenv_as_int("TG_LEVEL_ST", None), _getenv_as_int("TG_LEVEL_ED", '3')
SID_ST, SID_ED = _getenv_as_int("TG_SID_ST", None), _getenv_as_int("TG_SID_ED", None)
N_TURNS = _getenv_as_int("TG_N_TURNS", 3)
ONE_SHOT = bool(int(os.getenv("TG_ONESHOT", "0")))
# MAX_NEW_TOKENS = _getenv_as_int("TG_MAX_NEW_TOKENS", 4096)
QWEN_MATH_SIZE = os.getenv("TG_QWEN_MATH_SIZE", "7")    # {1.5, 7, 72}
QUANTIZE = _getenv_as_int("TG_QUANTIZE", 4)


#%%
def qwenmath_postproc(response_txt_batch, *args, **kwargs):
    response_txt_batch = [response_txt_batch]
    ret = []
    for response_txt in response_txt_batch:
        _match = None
        for pat in [
            re.compile(r'\\boxed\{([\s\S]*)}'),
            re.compile(r'^```\n?([^`]*)\n?```'),
            # re.compile(r'</think>\n([\s\S]*)$'),
        ]:
            matches = pat.search(response_txt)
            if matches:
                _match = matches.group(1).strip()
                break
        if _match is not None:
            ret.append(_match)
        else:
            ret.append(response_txt if response_txt else "")
    return ret[0]


#%%
def get_qwenmath_response(texts_batch, *args, **kwargs):
    # global model, tokenizer
    texts_batch = [texts_batch]
    for texts in texts_batch:
        if (len(texts) > 1) and texts[2].startswith('Correct guess.'):    # assert len(texts) % 2 == 1
            texts[1] = f"\\boxed{{{texts[1]}}}"
    messages = [
        [
            {"role": "system", "content": "Please reason step by step, and put your final answer within \\boxed{} as plain text."},
            *[{"role": ("user" if i % 2 == 0 else "assistant"), "content": text} for i, text in enumerate(texts)],
        ]
        for texts in texts_batch
    ]
    # print(f"\n{messages[0]}", end="\n=====\n\n")

    text_inputs = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    model_inputs = tokenizer(text_inputs, return_tensors="pt", add_special_tokens=False).to(model.device)

    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=512,
        do_sample=False,
    )
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]

    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return response.strip()


#%%
if __name__ == "__main__":
    fp_out = (f"model_outputs/__runs__/results_qwen2-5-math-{QWEN_MATH_SIZE}b-instruct_{QUANTIZE}bit"
              f"{'.1s' if ONE_SHOT else '.zs'}"
              f"{'' if GAME_ST is None else f'.{GAME_ST}'}"
              f"{'' if LVL_ST is None else f'.{LVL_ST}'}"
              f".jsonl")

    set_all_seed()
    if QWEN_MATH_SIZE in ['72'] and QUANTIZE < 16:
        _additional_kwargs = {
            "quantization_config": (
                BitsAndBytesConfig(load_in_8bit=True)
                if QUANTIZE == 8 else
                BitsAndBytesConfig(load_in_4bit=True)
            ),
            "low_cpu_mem_usage": True,
        }
    else:
        _additional_kwargs = {"device_map": "auto"}

    model_name = f"Qwen/Qwen2.5-Math-{QWEN_MATH_SIZE}B-Instruct"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype="auto",
        **_additional_kwargs,
    )
    print(f"    > model.dtype: {model.dtype}")

    run_with_agent(
        fp_out,
        get_qwenmath_response,
        qwenmath_postproc,
        n_turns=N_TURNS,
        game_names_list=GAME_NAMES[GAME_ST:GAME_ED],
        level_ids_list=LEVEL_IDS[LVL_ST:LVL_ED],
        sid_indices=(list(map(lambda r: f"session_{r:04}", range(SID_ST or 0, SID_ED or 1000)))
                     if SID_ST or SID_ED else None),
        prepend_example=ONE_SHOT,
        # remove_if_output_file_exist=False,
        assistant_uses_raw_response=True,
    )
