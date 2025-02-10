import os
import json
from tqdm import tqdm
from textgames import GAME_NAMES, game_filename, _game_class_from_name
from pathlib import Path

GAME_NAME = GAME_NAMES[5]
PROBLEMSET_DIR = Path(os.getenv("TG_PROBLEMSET_DIR", "problemsets"))
MODEL_OUTPUT_DIR = Path(os.getenv("TG_MODEL_OUTPUT_DIR", "model_outputs"))
OUTPUT_FILENAMES = [
    # "results_gemma-2-9b-it.1s.jsonl",
    # "results_gemma-2-9b-it.zs.jsonl",
    # "results_gemma-2-27b-it.1s.jsonl",
    # "results_gemma-2-27b-it.zs.jsonl",
    # "results_llama-3.1-8b-instruct.1s.jsonl",
    # "results_llama-3.1-8b-instruct.zs.jsonl",
    # "results_qwen2-5-7b-instruct.1s.jsonl",
    # "results_qwen2-5-7b-instruct.zs.jsonl",
    # "results_qwen2-5-7b-instruct_sp.1s.jsonl",
    # "results_qwen2-5-7b-instruct_sp.zs.jsonl",
    # "results_qwen2-5-14b-instruct.1s.jsonl",
    # "results_qwen2-5-14b-instruct.zs.jsonl",
    # "results_qwen2-5-32b-instruct.1s.jsonl",
    # "results_qwen2-5-32b-instruct.zs.jsonl",
    # "results_qwen2-5-72b-instruct.1s.jsonl",
    # "results_qwen2-5-72b-instruct.zs.jsonl",
    # "results_deepseek-r1-distill-14b.1s.jsonl",
    # "results_deepseek-r1-distill-14b.zs.jsonl",
    # "results_llama-3.1-70b-instruct.1s.jsonl",
    # "results_llama-3.3-70b-instruct.1s.jsonl",

    # TODO:
    "results_llama-3.1-70b-instruct.zs.jsonl",
    "results_llama-3.3-70b-instruct.zs.jsonl",
]


def revalidate_anagram_3(fp, reval_dir="revalidate_anagram_3"):
    os.makedirs(MODEL_OUTPUT_DIR/reval_dir, exist_ok=True)
    count_pos, count_neg = 0, 0
    with (open(MODEL_OUTPUT_DIR/fp, "r", encoding="utf8") as i,
          open(MODEL_OUTPUT_DIR/reval_dir/fp, "w", encoding="utf8") as o,
          tqdm(total=1000, desc=fp) as pbar,
          ):
        for line in i:
            res = json.loads(line)
            if (res['game'] == f"{game_filename(GAME_NAME)}_3"):
                if (res['turn'] == 1):
                    prompt = sid_prompt_dict[res["session"]]
                    cur_game = game_cls()
                    cur_game.load_game(prompt)
                    pbar.update(1)
                elif solved == True:
                    continue
                solved, _ = cur_game.validate(res["response"])
                if solved and not res["solved"]:
                    count_pos += 1
                elif not solved and res["solved"]:
                    count_neg += 1
                res["solved"] = solved
            o.write(json.dumps(res))
            o.write("\n")
    return count_pos, count_neg


if __name__ == "__main__":
    game_cls = _game_class_from_name(GAME_NAME)
    with open(f"{PROBLEMSET_DIR}/{game_filename(GAME_NAME)}_3.json", "r", encoding="utf8") as f:
        sid_prompt_dict = json.load(f)
    for fp in OUTPUT_FILENAMES:
        print(revalidate_anagram_3(fp))
