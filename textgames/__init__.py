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

THE_GAMES = {
    "1": CrosswordArrangerGame.get_game_name(),
    "2": Sudoku.get_game_name(),
    "3": Islands.get_game_name(),
    "4": PasswordGame.get_game_name(),
    "5": OrderingTextGame.get_game_name(),
    "6": AnagramScribble.get_game_name(),
    "7": BracketGame.get_game_name(),
    "8": StringSearch.get_game_name(),
}
GAME_IDS = list(THE_GAMES.keys())
GAME_NAMES = list(THE_GAMES.values())
# ["🔑\tPassword Game", "🧩\tText Sudoku", "🗳️\tBracket Game", "📈\tOrdering Text",
#  "🏝️\tIslands", "🔎\tString Search", "📰\tCrossword Arranger", "🔤\tAnagram Scribble",]
SINGLE_LINE_GAME_IDS = list(map(lambda g: GAME_IDS[GAME_NAMES.index(g.get_game_name())],
                                [PasswordGame, BracketGame, StringSearch, AnagramScribble]
                                ))

LEVEL_IDS = ["1", "2", "3", "4", "0", "00"]
LEVELS = ["🚅\tEasy", "🚀\tMedium", "🛸\tHard"]
LEVELS_HIDDEN = ["🌌\tInsane", "🔰\tSample #1", "🔰\tSample #2"]
_show_hidden_level_ = os.getenv("TEXTGAMES_SHOW_HIDDEN_LEVEL", False)
if _show_hidden_level_:
    LEVELS, LEVELS_HIDDEN = LEVELS + LEVELS_HIDDEN, []


def new_game(game_name, level):
    not_available_game_level = NotImplementedError(
        f"The difficulty level is not available for this game: {game_name} - {level}"
    )

    if game_name == PasswordGame.get_game_name():
        game = PasswordGame()
        if level == "1":
            num_rules = 2
        elif level == "2":
            num_rules = 4
        elif level == "3":
            num_rules = 6
        else:
            raise not_available_game_level
        game.generate_new_game(num_rules=num_rules)
        print(f"possible answer: {game.possible_ans}")

    elif game_name == Sudoku.get_game_name():
        game = Sudoku()
        if level == "1":
            setting = random.randint(0,1)
            if setting == 0:
                game.generate_new_game(size=4, characters=["1","2","3","4"], empty_character="_", empty_ratio=0.25)
            elif setting == 1:
                game.generate_new_game(size=4, characters=["A","B","C","D"], empty_character="_", empty_ratio=0.25)
        elif level == "2":
            setting = random.randint(0,1)
            if setting == 0:
                game.generate_new_game(size=4, characters=["1","2","3","4"], empty_character="_", empty_ratio=0.5)
            elif setting == 1:
                game.generate_new_game(size=4, characters=["A","B","C","D"], empty_character="_", empty_ratio=0.5)
        elif level == "3":
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
        if level == "1":
            game.generate_new_game(num_words=3, num_rules=3, depth=2, multi_word=False)
        elif level == "2":
            game.generate_new_game(num_words=5, num_rules=5, depth=2, multi_word=False)
        elif level == "3":
            game.generate_new_game(num_words=10, num_rules=7, depth=3, multi_word=True)
        else:
            raise not_available_game_level

    elif game_name == OrderingTextGame.get_game_name():
        game = OrderingTextGame()
        if level == "0":
            game.generate_new_game(preset_config=1)
        elif level == "00":
            game.generate_new_game(preset_config=2)
        elif level == "1":
            game.generate_new_game(num_rules=(2, 2), uniq_classrules=True, positive_only=False,
                                   num_words=(3, 3), word_length=(3, 8), word_dic_only=True)
        elif level == "2":
            game.generate_new_game(num_rules=(2, 4), uniq_classrules=True, positive_only=False,
                                   num_words=(4, 6), word_length=(3, 8), word_dic_only=True)
        elif level == "3":
            game.generate_new_game(num_rules=(4, 8), uniq_classrules=False, positive_only=False,
                                   num_words=(5, 10), word_length=(3, 15), word_dic_only=True)
        elif level == "4":
            game.generate_new_game(num_rules=(8, 12), uniq_classrules=False, positive_only=False,
                                   num_words=(10, 20), word_length=(6, 15), word_dic_only=False)
        else:
            game.generate_new_game(preset_config=1)

    elif game_name == Islands.get_game_name():
        game = Islands()
        if level == "1":
            game.generate_new_game(num_islands=1, island_with_coconut=0)
        elif level == "2":
            game.generate_new_game(num_islands=random.randint(1, 3))
        elif level == "3":
            game.generate_new_game(num_islands=random.randint(3, 6))
        else:
            raise not_available_game_level

        prompt = game.get_prompt()
        check_game = Islands()
        check_game.load_game(prompt)
        print(vars(game))
        print(vars(check_game))

        exlude_state = ['start_timestamp', 'chat_log', 'attempt_timestamps', 'is_solved']
        original_game_state = {k: v for k, v in vars(game).items() if k not in exlude_state}
        loaded_game_state = {k: v for k, v in vars(check_game).items() if k not in exlude_state}
        assert original_game_state == loaded_game_state, "Game loader fails to load the correct game state"


    elif game_name == StringSearch.get_game_name():
        game = StringSearch()
        game.generate_new_game(difficulty=int(level))

    elif game_name == CrosswordArrangerGame.get_game_name():
        game = CrosswordArrangerGame()
        if level == "0":
            game.generate_new_game(preset_config=1)
        elif level == "1":
            game.generate_new_game(board_size=3, noise_ratio=.25, no_ans_prob=.0, no_duplicate=True,)
        elif level == "2":
            game.generate_new_game(board_size=4, noise_ratio=.5, no_ans_prob=.0, no_duplicate=True,)
        elif level == "3":
            game.generate_new_game(board_size=5, noise_ratio=.5, no_ans_prob=.0, no_duplicate=True,)
        elif level == "4":
            game.generate_new_game(board_size=6, noise_ratio=.5, no_ans_prob=.0, no_duplicate=True,)
        else:
            raise not_available_game_level
        print(f"Possible Answer: {game.possible_ans}\n")

    elif game_name == AnagramScribble.get_game_name():
        game = AnagramScribble()
        if level == "1":
            game.generate_new_game(low_num_chars=3, high_num_chars=5, allow_repeat=True)
        elif level == "2":
            game.generate_new_game(low_num_chars=6, high_num_chars=7, allow_repeat=True)
        elif level == "3":
            game.generate_new_game(low_num_chars=8, high_num_chars=10, allow_repeat=False)
        else:
            raise not_available_game_level
        print(f"Possible Answer: {game.possible_ans}\n")

    else:
        raise not_available_game_level

    return game

