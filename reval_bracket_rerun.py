# @title ##### Combine Rerun of the Bracket - All
import os
import json
from tqdm import tqdm
from pathlib import Path

MODEL_OUTPUT_DIR = Path(os.getenv("TG_MODEL_OUTPUT_DIR", "model_outputs"))
fd_new = MODEL_OUTPUT_DIR / "__runs__" / "_redo_bracket"
fd_ori = MODEL_OUTPUT_DIR / "revalidate_anagram_3"
fd_out = MODEL_OUTPUT_DIR / "revalidate_bracket_all_concat"

OUTPUT_FILENAMES = [
    # "results_deepseek-r1-distill-14b.1s.jsonl",    =>  copy from 'revalidate_bracket_all' as it is 1-turn
    # "results_deepseek-r1-distill-14b.zs.jsonl",    =>  copy from 'revalidate_bracket_all' as it is 1-turn

    # _31 & _32
    "results_gemma-2-9b-it.1s.jsonl",
    "results_gemma-2-9b-it.zs.jsonl",
    "results_llama-3.1-8b-instruct.1s.jsonl",
    "results_llama-3.1-8b-instruct.zs.jsonl",
    "results_qwen2-5-7b-instruct.1s.jsonl",
    "results_qwen2-5-7b-instruct.zs.jsonl",

    # _33
    "results_qwen2-5-32b-instruct.1s.jsonl",
    "results_qwen2-5-32b-instruct.zs.jsonl",

    # _36
    "results_qwen2-5-14b-instruct.1s.jsonl",
    "results_qwen2-5-14b-instruct.zs.jsonl",

    # _35
    "results_gemma-2-27b-it.1s.jsonl",
    "results_gemma-2-27b-it.zs.jsonl",

    # _34
    "results_qwen2-5-72b-instruct.1s.jsonl",
    "results_qwen2-5-72b-instruct.zs.jsonl",
    "results_llama-3.1-70b-instruct.1s.jsonl",
    "results_llama-3.1-70b-instruct.zs.jsonl",
    "results_llama-3.3-70b-instruct.1s.jsonl",
    "results_llama-3.3-70b-instruct.zs.jsonl",
]

os.makedirs(fd_out, exist_ok=True)
for fp in tqdm(OUTPUT_FILENAMES):
    with open(fd_out / fp, "w", encoding="utf8") as o:
        with open(fd_ori / fp, "r", encoding="utf8") as i:
            for line in i:
                res = json.loads(line)
                if res['game'].startswith("Bracket Game"):
                    continue
                o.write(line)
        with open((fd_new / fp).with_suffix(".6.jsonl"), "r", encoding="utf8") as i:
            for line in i:
                o.write(line)