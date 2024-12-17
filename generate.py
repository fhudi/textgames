import os
import random
import numpy as np
import torch
import json

from tqdm import tqdm
from pathlib import Path
from textgames import GAME_NAMES, LEVEL_IDS, new_game


def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)


#generate()
if __name__ == '__main__':
    outdir = Path(os.getenv("TEXTGAMES_LOADGAME_DIR", "problemsets"))
    # os.system(f"rm -rfd {outdir}")
    os.makedirs(outdir, exist_ok=False)    # exists_ok is set to False, making sure regeneration.
    set_seed(42)

    # level_ids = LEVEL_IDS
    level_ids = ["1", "3"]
    session_ids = [
        f"session_{sid:04}" for sid in range(os.getenv("TEXTGAMES_GENERATE_N", 100))
    ]

    count_duplicate = 0
    for game_name in GAME_NAMES:
        prompts_map = dict()
        for level_id in level_ids:
            os.environ["TEXTGAMES_NEWGAME_ERRFILE"] = f"{outdir}/{game_name}_{level_id}.err"
            for sid in tqdm(session_ids, desc=f"{game_name}_{level_id}"):
                while True:
                    cur_game = new_game(game_name, level_id)
                    prompt = cur_game._get_prompt()
                    if prompt not in prompts_map:
                        break
                    count_duplicate += 1
                prompts_map[prompt] = sid
            print(f"[{game_name}_{level_id}]  Duplicate #: {count_duplicate:-4}")

            json_object = json.dumps({sid: prompt for prompt, sid in prompts_map.items()}, indent=4)
            with open(outdir / f"{game_name}_{level_id}.json", "w") as outfile:
                outfile.write(json_object)

    print(f"duplicates:{count_duplicate}")
