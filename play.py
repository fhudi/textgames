from textgames.crossword_arranger.crossword_arranger import CrosswordArrangerGame
from textgames.password_game.password_game import PasswordGame
from textgames.sudoku.sudoku import Sudoku
from textgames.bracket_game.bracket_game import BracketGame
from textgames.ordering_text.ordering_text import OrderingTextGame
from textgames.islands.islands import Islands
from textgames.string_search.string_search import StringSearch
from textgames.anagram_scribble.anagram_scribble import AnagramScribble
import random
from termcolor import colored

import os

_show_hidden_level_ = os.getenv("TEXTGAMES_SHOW_HIDDEN_LEVEL", False)

GAME_IDS = ["1", "2", "3", "4", "5", "6", "7", "8"]
GAME_NAMES = ["🔑\tPassword Game", "🧩\tSudoku", "🗳️\tBracket Game", "📈\tOrdering Text", "🏝️\tIslands",
              "🔎\tString Search", "📰\tCrossword Arranger", "🔤\tAnagram Scribble"]
LEVEL_IDS = ["1", "2", "3", "4", "0", "00"]
LEVELS = ["🚅\tEasy", "🚀\tMedium", "🛸\tHard"]
LEVELS_HIDDEN = ["🌌\tInsane", "🔰\tSample #1", "🔰\tSample #2"]
if _show_hidden_level_:
    LEVELS, LEVELS_HIDDEN = LEVELS + LEVELS_HIDDEN, []


def new_game(game_id, level):
    not_available_game_level = NotImplementedError(
        f"The difficulty level is not available for this game: {game_id} - {level}"
    )

    if game_id == "1":
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

    elif game_id == "2":
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

    elif game_id == "3":
        game = BracketGame()
        if level == "1":
            game.generate_new_game(num_words=3, num_rules=3, depth=2, multi_word=False)
        elif level == "2":
            game.generate_new_game(num_words=5, num_rules=5, depth=2, multi_word=False)
        elif level == "3":
            game.generate_new_game(num_words=10, num_rules=7, depth=3, multi_word=True)
        else:
            raise not_available_game_level

    elif game_id == "4":
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


    elif game_id == "5":
        game = Islands()
        if level == "1":
            game.generate_new_game(num_islands=1, island_with_coconut=0)
        elif level == "2":
            game.generate_new_game(num_islands=random.randint(1, 3))
        elif level == "3":
            game.generate_new_game(num_islands=random.randint(3, 6))
        else:
            raise not_available_game_level

    elif game_id == "6":
        game = StringSearch()
        game.generate_new_game(difficulty=int(level))

    elif game_id == "7":
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

    elif game_id == "8":
        game = AnagramScribble()
        if level == "1":
            game.generate_new_game(low_num_chars=3, high_num_chars=5, allow_repeat=True)
        elif level == "2":
            game.generate_new_game(low_num_chars=6, high_num_chars=7, allow_repeat=True)
        elif level == "3":
            game.generate_new_game(low_num_chars=8, high_num_chars=10, allow_repeat=False)
        else:
            raise not_available_game_level

    else:
        raise not_available_game_level

    return game


def print_text_green(string):
    print(colored(string, "light_green"))

def print_text_cyan(string):
    print(colored(string, "cyan"))

def print_text_white(string):
    print(colored(string, "white"))


if __name__ == "__main__":
    print_text_green("#" * 20)
    print_text_cyan("    Welcome to")
    print("   🎮 " + colored("Text", "white")+ colored("Games", "yellow"))
    print_text_green("#" * 20)
    print_text_green("Games:")
    for i, game_name in zip(range(len(GAME_NAMES)), GAME_NAMES):
        print_text_green(f"{i+1}. {game_name}")
    print_text_green("#" * 20)

    cur_game_id = None
    difficulty_level = None
    while cur_game_id is None:
        user_input = str(input(f"Choose the game> "))

        if user_input in GAME_IDS:
            cur_game_id = user_input

            print_text_green("#" * 20)
            print_text_green("Difficulty Levels:")
            for i, l in zip(LEVEL_IDS, LEVELS):
                print_text_green(f"{i}. {l}")
            print_text_green("#" * 20)

            while difficulty_level is None:
                user_input = str(input(f"Choose the difficulty level> "))
                if user_input in LEVEL_IDS:
                    difficulty_level = user_input
                else:
                    print("The difficulty level option is not available.")
        else:
            arr = user_input.split("-")
            if len(arr) == 2 and isinstance(arr[0], str) and isinstance(arr[1], str):
                if arr[0] in GAME_IDS and arr[1] in LEVEL_IDS:
                    cur_game_id = arr[0]
                    difficulty_level = arr[1]
            else:
                print("The game option is not available.")
                cur_game = None

    this_game_name = GAME_NAMES[GAME_IDS.index(cur_game_id)]
    this_difficulty_level = (LEVELS + LEVELS_HIDDEN)[LEVEL_IDS.index(difficulty_level)].replace("\t", " ")
    print_text_green(f"Game chosen: {this_game_name} and Difficulty Level: {this_difficulty_level}")

    cur_game = new_game(cur_game_id, difficulty_level)
    solved = False
    print(cur_game.get_prompt())
    while not solved:
        contents = []
        while True:
            try:
                line = str(input("\t" if contents else f"Guess>\t"))
                # automatic break for some games:
                if cur_game_id in ["1", "3", "6"]:
                    contents.append(line)
                    break
                if len(line) == 0:
                    break
            except EOFError:
                break
            contents.append(line)

        user_input = '\n'.join(contents)
        solved, val_msg = cur_game.validate(user_input)
        if solved:
            print("Correct guess")
        else:
            print("Bad guess")
    
    print("Thank you for playing!")
            

