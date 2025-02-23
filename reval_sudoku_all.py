import os
import json
from tqdm import tqdm
from textgames import GAME_NAMES, game_filename, _game_class_from_name
from pathlib import Path

GAME_NAME = GAME_NAMES[1]
PROBLEMSET_DIR = Path(os.getenv("TG_PROBLEMSET_DIR", "problemsets"))
MODEL_OUTPUT_DIR = Path(os.getenv("TG_MODEL_OUTPUT_DIR", "model_outputs"))
OUTPUT_FILENAMES = [
    # "results_gemma-2-9b-it.1s.jsonl",
    # "results_gemma-2-9b-it.zs.jsonl",
    # "results_gemma-2-27b-it.1s.jsonl",
    # "results_gemma-2-27b-it.zs.jsonl",
    #
    # "results_llama-3.1-8b-instruct.1s.jsonl",
    # "results_llama-3.1-8b-instruct.zs.jsonl",
    # "results_llama-3.1-70b-instruct.1s.jsonl",
    # "results_llama-3.1-70b-instruct.zs.jsonl",
    # "results_llama-3.3-70b-instruct.1s.jsonl",
    # "results_llama-3.3-70b-instruct.zs.jsonl",
    #
    # "results_qwen2-5-7b-instruct.1s.jsonl",
    # "results_qwen2-5-7b-instruct.zs.jsonl",
    # "results_qwen2-5-14b-instruct.1s.jsonl",
    # "results_qwen2-5-14b-instruct.zs.jsonl",
    # "results_qwen2-5-32b-instruct.1s.jsonl",
    # "results_qwen2-5-32b-instruct.zs.jsonl",
    # "results_qwen2-5-72b-instruct.1s.jsonl",
    # "results_qwen2-5-72b-instruct.zs.jsonl",
    #
    # "results_deepseek-r1-distill-14b.1s.jsonl",
    # "results_deepseek-r1-distill-14b.zs.jsonl",
    # # "results_deepseek-r1-distill-14b.rerun.1s.jsonl",
    #
    # "results_chatgpt-4o-mini.1s.jsonl",
    # "results_chatgpt-4o-mini.zs.jsonl",
    # "results_chatgpt-o3-mini.zs.jsonl",
    #
    # # "results_qwen2-5-7b-instruct_sp.1s.jsonl",
    # # "results_qwen2-5-7b-instruct_sp.zs.jsonl",

    "results_deepseek-r1-distill-8b.1s.jsonl",
    "results_deepseek-r1-distill-8b.zs.jsonl",
]


def revalidate_bracket(fp, reval_dir="revalidate_sudoku_all",
                       source_dirs=("revalidate_crosswords_all",)):
    os.makedirs(MODEL_OUTPUT_DIR/reval_dir, exist_ok=True)
    count_pos, count_neg = 0, 0
    source_dir = "."
    for source_dir in source_dirs:
        if (MODEL_OUTPUT_DIR / source_dir / fp).exists():
            break
    with (open(MODEL_OUTPUT_DIR / source_dir / fp, "r", encoding="utf8") as i,
          open(MODEL_OUTPUT_DIR / reval_dir / fp, "w", encoding="utf8") as o,
          tqdm(total=3000, desc=fp) as pbar,
          ):
        for line in i:
            res = json.loads(line)
            if (res['game'].startswith(f"{game_filename(GAME_NAME)}")):
                sid_prompt_dict = sid_prompt_dicts[res['game'].rsplit("_", 1)[-1]]
                if (res['turn'] == 1):
                    cur_sid = res["session"]
                    prompt = sid_prompt_dict[cur_sid]
                    cur_game = game_cls()
                    cur_game.load_game(prompt)
                    pbar.update(1)
                elif solved == True:
                    continue
                else:
                    assert cur_sid == res["session"]
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
    def load(k):
        with open(f"{PROBLEMSET_DIR}/{game_filename(GAME_NAME)}_{k}.json", "r", encoding="utf8") as f:
            sid_prompt_dict = json.load(f)
        return sid_prompt_dict
    sid_prompt_dicts = {k: load(k) for k in map(str, range(1, 4))}
    game_cls = _game_class_from_name(GAME_NAME)
    for fp in OUTPUT_FILENAMES:
        print(revalidate_bracket(fp))

