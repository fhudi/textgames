import os
import torch
import random
import numpy as np
import argparse
import json
import cohere
from openai import OpenAI

from tqdm import tqdm

from collections import Counter

from transformers import LlamaForCausalLM, AutoTokenizer, AutoModelForCausalLM, AutoModelForSeq2SeqLM
import hashlib

from textgames import GAME_NAMES, GAME_IDS, LEVELS, LEVELS_HIDDEN, LEVEL_IDS, new_game

OPENAI_TOKEN = ""
COHERE_TOKEN = ""
HF_TOKEN = ""

def argmax(array):
    """argmax with deterministic pseudorandom tie breaking."""
    max_indices = np.arange(len(array))[array == np.max(array)]
    idx = int(hashlib.sha256(np.asarray(array).tobytes()).hexdigest(),16) % len(max_indices)
    return max_indices[idx]

def logsumexp(x):
    c = x.max()
    return c + np.log(np.sum(np.exp(x - c)))

def normalize(x):
    x = np.array(x)
    return np.exp(x - logsumexp(x))

def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)

def get_commandr_chat_response(gen_model, gen_model_checkpoint, text, seed):
    response = gen_model.chat(
        model="command-r",
        message=text,
        temperature=0,
        max_tokens=64,
        seed=seed,
        p=1
    )
    return response.text


def get_mt0_response(gen_model, tokenizer, gen_model_checkpoint, text, seed):
    input_ids = tokenizer.encode(text, return_tensors="pt").to(gen_model.device)

    outputs = gen_model.generate(
        input_ids,
        max_new_tokens=10,
        do_sample=True,
        temperature=0.2,
        top_p=1
    )

    response = outputs[0]
    return tokenizer.decode(response, skip_special_tokens=True)

def get_gemma_response(gen_model, tokenizer, gen_model_checkpoint, text, seed):
    messages = [
        {"role": "user", "content": text},
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
        max_new_tokens=10,
        eos_token_id=terminators,
        do_sample=True,
        temperature=0.2,
        top_p=1
    )

    response = outputs[0][input_ids.shape[-1]:]
    return tokenizer.decode(response, skip_special_tokens=True)

def get_mistral_instruct_chat_response(gen_model, tokenizer, gen_model_checkpoint, text, seed):
    messages = [
        {"role": "user", "content": text},
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
        max_new_tokens=10,
        eos_token_id=terminators,
        do_sample=True,
        temperature=0.2,
        top_p=1
    )

    response = outputs[0][input_ids.shape[-1]:]
    return tokenizer.decode(response, skip_special_tokens=True)

def get_llama3_instruct_chat_response(gen_model, tokenizer, gen_model_checkpoint, text, seed):
    messages = [
        {"role": "user", "content": text},
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
        max_new_tokens=10,
        eos_token_id=terminators,
        do_sample=True,
        temperature=0.2,
        top_p=1
    )

    response = outputs[0][input_ids.shape[-1]:]
    return tokenizer.decode(response, skip_special_tokens=True)

def get_openai_chat_response(gen_model, gen_model_checkpoint, text, seed):
    messages=[
        {
            "role": "user",
            "content": text
        }
    ]
    response = gen_model.chat.completions.create(
        model=gen_model_checkpoint,
        messages=messages,
        temperature=0,
        max_tokens=64,
        top_p=1,
        seed=seed
    )
    return response.choices[0].message.content

def load_model(gen_model_checkpoint, load_in_8bit=False):
    gen_model = None
    tokenizer = None
    
    if "mistralai/Mistral-7B-Instruct-v0.3" in gen_model_checkpoint or "meta-llama/Meta-Llama-3-8B-Instruct" in gen_model_checkpoint or "google/gemma-1.1-7b-it" in gen_model_checkpoint:
        if load_in_8bit:
            gen_model = AutoModelForCausalLM.from_pretrained(gen_model_checkpoint, token=HF_TOKEN, device_map="auto", load_in_8bit=True)
            tokenizer = AutoTokenizer.from_pretrained(gen_model_checkpoint, token=HF_TOKEN, device_map="auto", load_in_8bit=True)
        else:
            gen_model = AutoModelForCausalLM.from_pretrained(gen_model_checkpoint, token=HF_TOKEN)
            tokenizer = AutoTokenizer.from_pretrained(gen_model_checkpoint, token=HF_TOKEN)
    elif "CohereForAI/aya-101" in gen_model_checkpoint or "bigscience/mt0" in gen_model_checkpoint:
        if load_in_8bit:
            gen_model = AutoModelForSeq2SeqLM.from_pretrained(gen_model_checkpoint, token=HF_TOKEN, device_map="auto", load_in_8bit=True)
            tokenizer = AutoTokenizer.from_pretrained(gen_model_checkpoint, token=HF_TOKEN, device_map="auto", load_in_8bit=True)
        else:
            gen_model = AutoModelForSeq2SeqLM.from_pretrained(gen_model_checkpoint, token=HF_TOKEN)
            tokenizer = AutoTokenizer.from_pretrained(gen_model_checkpoint, token=HF_TOKEN)
    elif "facebook/xglm" in gen_model_checkpoint or "bigscience/bloomz" in gen_model_checkpoint or "aya-23-8B" in args.gen_model_checkpoint:
        if load_in_8bit:
            gen_model = AutoModelForCausalLM.from_pretrained(gen_model_checkpoint, token=HF_TOKEN, device_map="auto", load_in_8bit=True)
            tokenizer = AutoTokenizer.from_pretrained(gen_model_checkpoint, token=HF_TOKEN, device_map="auto", load_in_8bit=True)
        else:
            gen_model = AutoModelForCausalLM.from_pretrained(gen_model_checkpoint, token=HF_TOKEN)
            tokenizer = AutoTokenizer.from_pretrained(gen_model_checkpoint, token=HF_TOKEN)
    elif "gpt-3.5-turbo" in gen_model_checkpoint or "gpt-4" in gen_model_checkpoint:
        gen_model = OpenAI(api_key=OPENAI_TOKEN)
    elif "command-r" in gen_model_checkpoint:
        gen_model = cohere.Client(COHERE_TOKEN)
    
    return gen_model, tokenizer

def generate(num_samples, dir_path):
    print(GAME_NAMES, LEVELS)
    os.system(f"mkdir -p {dir_path}")

    count_duplicate = 0
    for game_name in GAME_NAMES:
        for difficulty_level in filter(lambda level_id: not level_id.startswith("0"), LEVEL_IDS):    # Sample test-caases start with '0'
            prompts_map = {}
            print(game_name, difficulty_level)
            prompts = []
            for i in range(num_samples):
                cur_game = new_game(game_name, difficulty_level)
                prompt = cur_game.get_prompt()
                prompts.append(prompt)
                if prompt in prompts_map:
                    count_duplicate += 1
                prompts_map[prompt] = True
            json_object = json.dumps(prompts, indent=4)
            with open(f"{dir_path}/{game_name}_{difficulty_level}.json", "w") as outfile:
                outfile.write(json_object)
    print(f"duplicates:{count_duplicate}")

generate(1000, "games_data")