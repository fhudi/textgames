from textgames.crossword_arranger.crossword_arranger import CrosswordArrangerGame
from textgames.password_game.password_game import PasswordGame
from textgames.sudoku.sudoku import Sudoku
from textgames.bracket_game.bracket_game import BracketGame
from textgames.ordering_text.ordering_text import OrderingTextGame
from textgames.islands.islands import Islands
from textgames.string_search.string_search import StringSearch
from textgames.anagram_scribble.anagram_scribble import AnagramScribble

import random
import os

from pandas import read_csv
import json


# [
#  "📰\tCrossword Arranger", "🧩\tText Sudoku", "🏝️\tIslands", "🔑\tPassword Game",
#  "📈\tOrdering Text", "🔤\tAnagram Scribble", "🗳️\tBracket Game", "🔎\tString Search",
#  ]
THE_GAMES = {
    k: v.get_game_name() for k, v in [
        ("1", CrosswordArrangerGame),
        ("2", Sudoku),
        ("3", Islands),
        ("4", PasswordGame),
        ("5", OrderingTextGame),
        ("6", AnagramScribble),
        ("7", BracketGame),
        ("8", StringSearch),
    ]
}
GAME_IDS = list(THE_GAMES.keys())
GAME_NAMES = list(THE_GAMES.values())
SINGLE_LINE_GAME_IDS = list(map(lambda g: GAME_IDS[GAME_NAMES.index(g.get_game_name())],
                                [PasswordGame, BracketGame, StringSearch, AnagramScribble]
                                ))

LEVEL_IDS = ["1", "2", "3", "4", "0", "00"]
LEVELS = ["🚅\tEasy", "🚀\tMedium", "🛸\tHard"]
LEVELS_HIDDEN = ["🌌\tInsane", "🔰\tSample #1", "🔰\tSample #2"]
_show_hidden_level_ = os.getenv("TEXTGAMES_SHOW_HIDDEN_LEVEL", False)
if _show_hidden_level_:
    LEVELS, LEVELS_HIDDEN = LEVELS + LEVELS_HIDDEN, []


def _reload(prompt, game_cls):
    game = game_cls()
    game.load_game(prompt)
    return game


def game_filename(_game_name):
    return _game_name.split('\t', 1)[-1]


def _game_class_from_name(game_name):
    for game_class in [PasswordGame, Sudoku, BracketGame, OrderingTextGame, Islands,
                       StringSearch, CrosswordArrangerGame, AnagramScribble]:
        if game_name == game_class.get_game_name():
            return game_class
    return None


def preload_game(game_name, level_id, user, sid=None):
    game_cls = _game_class_from_name(game_name)
    if not sid:
        email_sid_dict = read_csv(
            f"{os.getenv('TEXTGAMES_OUTPUT_DIR')}/textgames_userauth.tsv", sep='\t'
        ).dropna().set_index("EMAIL").SID.to_dict()
        sid = email_sid_dict.get(user["email"])
    print(f"preload_game('{game_name}', '{level_id}', '{user['email']}') on {sid}")

    with open(f"problemsets/{game_filename(game_name)}_{level_id}.json", "r", encoding="utf8") as f:
        sid_prompt_dict = json.load(f)
    prompt = sid_prompt_dict.get(sid)
    # print("Loaded prompt:", prompt, sep="\n")

    return _reload(prompt, game_cls)


def new_game(game_name, level_id):
    not_available_game_level = NotImplementedError(
        f"The difficulty level is not available for this game: {game_name} - {level_id}"
    )

    if game_name == PasswordGame.get_game_name():
        game = PasswordGame()
        if level_id == "1":
            num_rules = 2
        elif level_id == "2":
            num_rules = 4
        elif level_id == "3":
            num_rules = 6
        else:
            raise not_available_game_level
        game.generate_new_game(num_rules=num_rules)
        if os.getenv("TEXTGAMES_NEWGAME_VERBOSE", False):
            print(f"possible answer: {game.possible_ans}")

    elif game_name == Sudoku.get_game_name():
        game = Sudoku()
        if level_id == "1":
            setting = random.randint(0,1)
            if setting == 0:
                game.generate_new_game(size=4, characters=["1","2","3","4"], empty_character="_", empty_ratio=0.25)
            elif setting == 1:
                game.generate_new_game(size=4, characters=["A","B","C","D"], empty_character="_", empty_ratio=0.25)
        elif level_id == "2":
            setting = random.randint(0,1)
            if setting == 0:
                game.generate_new_game(size=4, characters=["1","2","3","4"], empty_character="_", empty_ratio=0.5)
            elif setting == 1:
                game.generate_new_game(size=4, characters=["A","B","C","D"], empty_character="_", empty_ratio=0.5)
        elif level_id == "3":
            setting = random.randint(0,1)
            if setting == 0:
                game.generate_new_game(size=9, characters=["1","2","3","4","5","6","7","8","9"], empty_character="_", empty_ratio=0.4)
            elif setting == 1:
                game.generate_new_game(size=9, characters=["A","B","C","D","E","F","G","H","I"], empty_character="_", empty_ratio=0.4)
        else:
            raise not_available_game_level
        game.print_sudoku()

    elif game_name == BracketGame.get_game_name():
        game = BracketGame()
        if level_id == "1":
            game.generate_new_game(num_words=3, num_rules=3, depth=2, multi_word=False)
        elif level_id == "2":
            game.generate_new_game(num_words=5, num_rules=5, depth=2, multi_word=False)
        elif level_id == "3":
            game.generate_new_game(num_words=10, num_rules=7, depth=3, multi_word=True)
        else:
            raise not_available_game_level

    elif game_name == OrderingTextGame.get_game_name():
        game = OrderingTextGame()
        if level_id == "0":
            game.generate_new_game(preset_config=1)
        elif level_id == "00":
            game.generate_new_game(preset_config=2)
        elif level_id == "1":
            game.generate_new_game(num_rules=(2, 2), uniq_classrules=True, positive_only=False,
                                   num_words=(3, 3), word_length=(3, 8), word_dic_only=True)
        elif level_id == "2":
            game.generate_new_game(num_rules=(2, 4), uniq_classrules=True, positive_only=False,
                                   num_words=(4, 6), word_length=(3, 8), word_dic_only=True)
        elif level_id == "3":
            game.generate_new_game(num_rules=(4, 8), uniq_classrules=False, positive_only=False,
                                   num_words=(5, 10), word_length=(3, 15), word_dic_only=True)
        elif level_id == "4":
            game.generate_new_game(num_rules=(8, 12), uniq_classrules=False, positive_only=False,
                                   num_words=(10, 20), word_length=(6, 15), word_dic_only=False)
        else:
            game.generate_new_game(preset_config=1)

    elif game_name == Islands.get_game_name():
        game = Islands()
        if level_id == "1":
            game.generate_new_game(num_islands=1, island_with_coconut=0)
        elif level_id == "2":
            game.generate_new_game(num_islands=random.randint(1, 3))
        elif level_id == "3":
            game.generate_new_game(num_islands=random.randint(3, 6))
        else:
            raise not_available_game_level
        assert game.is_game_reloadable(), \
            "Game loader fails to load the correct game state"

    elif game_name == StringSearch.get_game_name():
        game = StringSearch()
        game.generate_new_game(difficulty=int(level_id))
        if os.getenv("TEXTGAMES_NEWGAME_VERBOSE", False):
            print(f"possible answer: {game.answer}")
        assert game.is_game_reloadable(), \
            "Game loader fails to load the correct game state"

    elif game_name == CrosswordArrangerGame.get_game_name():
        game = CrosswordArrangerGame()
        if level_id == "0":
            game.generate_new_game(preset_config=1)
        elif level_id == "1":
            game.generate_new_game(board_size=3, noise_ratio=.25, no_ans_prob=.0, no_duplicate=True,)
        elif level_id == "2":
            game.generate_new_game(board_size=4, noise_ratio=.5, no_ans_prob=.0, no_duplicate=True,)
        elif level_id == "3":
            game.generate_new_game(board_size=5, noise_ratio=.5, no_ans_prob=.0, no_duplicate=True,)
        elif level_id == "4":
            game.generate_new_game(board_size=6, noise_ratio=.5, no_ans_prob=.0, no_duplicate=True,)
        else:
            raise not_available_game_level
        if os.getenv("TEXTGAMES_NEWGAME_VERBOSE", False):
            print(f"Possible Answer: {game.possible_ans}")

    elif game_name == AnagramScribble.get_game_name():
        game = AnagramScribble()
        if level_id == "1":
            game.generate_new_game(low_num_chars=3, high_num_chars=5, allow_repeat=True)
        elif level_id == "2":
            game.generate_new_game(low_num_chars=6, high_num_chars=7, allow_repeat=True)
        elif level_id == "3":
            game.generate_new_game(low_num_chars=8, high_num_chars=10, allow_repeat=False)
        else:
            raise not_available_game_level
        if os.getenv("TEXTGAMES_NEWGAME_VERBOSE", False):
            print(f"Possible Answer: {game.possible_ans}")

    else:
        raise not_available_game_level

    if game.is_game_reloadable():
        if os.getenv("TEXTGAMES_NEWGAME_VERBOSE", False):
            print("reloading the game ..")
        game = _reload(game.get_prompt(), game.__class__)    # Let's use the reloaded state
    else:
        _out_str_ =(
            "!! game is NOT reloaded.. !!\n"
            + f"[{game_name}_{level_id}]\n"
            + game.get_prompt()
        )
        outpath = os.getenv("TEXTGAMES_NEWGAME_ERRFILE", "")
        if outpath:
            with open(outpath, "a") as f:
                f.write(_out_str_)
        else:
            print(_out_str_)

    return game

