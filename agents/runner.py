#%%
import os
import json

from textgames import GAME_NAMES, LEVEL_IDS, game_filename, _game_class_from_name

from tqdm import tqdm
from itertools import product
from pathlib import Path
from typing import Union, Callable


def response_postprocess(response_txt, game_name, difficulty_level):
    return response_txt or ""


def run_with_agent(fp_out: Union[str, Path],
                   get_response: Callable,
                   get_postprocess: Callable = response_postprocess,
                   n_turns=3,
                   game_names_list=GAME_NAMES,
                   level_ids_list=LEVEL_IDS[:3],
                   sid_indices=None,  # sid_index_range=range(0, 1000),
                   remove_if_output_file_exist=True,
                   prepend_example=False,
                   ) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(fp_out)), exist_ok=True)
    print(fp_out)
    if remove_if_output_file_exist:
        with open(fp_out, "wb"):
            pass

    for game_name, difficulty_level in product(game_names_list, level_ids_list):
        game_str = f"{game_filename(game_name)}_{difficulty_level}"
        game_cls = _game_class_from_name(game_name)
        with open(f"problemsets/{game_str}.json", "r", encoding="utf8") as f:
            sid_prompt_dict = json.load(f)
        if sid_indices is not None:
            sid_prompt_dict = {k: sid_prompt_dict[k] for k in sid_indices}

        correct_cnt, exception_cnt = 0, 0
        for sid, prompt in tqdm(sid_prompt_dict.items(), desc=game_str, total=len(sid_prompt_dict)):
            cur_game = game_cls()
            cur_game.load_game(prompt)
            if prepend_example:
                texts = [*cur_game.example(), f"Correct guess. Now let's try another example.\n{cur_game.get_prompt()}"]
            else:
                texts = [cur_game.get_prompt()]
            for turn in range(1, n_turns + 1):
                response_raw, response, e = None, None, None
                solved, val_msg = False, None
                try:
                    response_raw = get_response(texts, game_name, difficulty_level, turn)
                    texts.append(response_raw)
                    response = get_postprocess(response_raw, game_name, difficulty_level)
                    solved, val_msg = cur_game.validate(response)
                    texts.append(
                        f"Bad guess (Wrong Answer).\n{val_msg}\nPlease try again and print the answer only."
                        if not solved else "Correct guess."
                    )
                except Exception as _e:
                    e = _e
                with open(fp_out, "a", encoding="utf8") as o:
                    json.dump({
                        "game": game_str,
                        "session": sid,
                        "turn": turn,
                        "response": response,
                        "solved": solved,
                        "val_msg": val_msg,
                        "response_raw": response_raw,
                        "error": repr(e) if e else e,
                    }, o, ensure_ascii=False)
                    o.write("\n")
                if solved:
                    correct_cnt += 1
                if e:
                    exception_cnt += 1
                if solved or e:
                    break

        print(f"{game_filename(game_name)}_-_{difficulty_level}")
        print(f"    > Correct: {correct_cnt:>6,}  ({correct_cnt / len(sid_prompt_dict):.2%})")
        print(f"    > Error  : {exception_cnt:>6,}  ({exception_cnt / len(sid_prompt_dict):.2%})")

