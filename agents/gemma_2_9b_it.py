#%%
import os
import re

#%%
from transformers import AutoTokenizer, AutoModelForCausalLM
from textgames import THE_GAMES, GAME_NAMES
from agents import run_with_agent


#%%
def gemma_postproc(response_txt, game_name, difficulty_level):
    if game_name in [THE_GAMES[i] for i in ["1", "7"]]:  # crossword
        pat = re.compile(r'^```\n([^`]*)\n```')
        match = pat.search(response_txt)
        return match.group(1).strip().replace(" ", "") if match else response_txt

    elif game_name == THE_GAMES["6"]:  # anagram
        pat = re.compile(r'\*\*\"?([^\"*]*)\"?\*\*')
        match = pat.search(response_txt)
        return match.group(1) if match else response_txt

    return response_txt or ""


#%%
def get_gemma_response(texts, game_name, difficulty_level, turn):
    # global gen_model, tokenizer
    messages = [
        {"role": ("model" if i % 2 else "user"), "content": texts}
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
st, ed = os.getenv("TG_GAME_ST", None), os.getenv("TG_GAME_ED", None)
st, ed = ((None if x is None else int(x)) for x in (st, ed))

#%%
fp_out = f"model_outputs/results_gemma-2-9b-it{'' if st is None else f'.{st}'}.jsonl"
gen_model_checkpoint = "google/gemma-2-9b-it"
quantize = True
kwargs = {
    "device_map": "auto",
} if quantize else {}


#%%
if __name__ == "__main__":
    gen_model = AutoModelForCausalLM.from_pretrained(gen_model_checkpoint, **kwargs)
    tokenizer = AutoTokenizer.from_pretrained(gen_model_checkpoint, **kwargs)
    run_with_agent(fp_out, get_gemma_response, gemma_postproc, game_names_list=GAME_NAMES[st:ed])
