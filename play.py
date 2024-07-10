from textgames.password_game.password_game import PasswordGame
from textgames.sudoku.sudoku import Sudoku
from textgames.bracket_game.bracket_game import BracketGame
from textgames.ordering_text.ordering_text import OrderingTextGame
from textgames.islands.islands import Islands

import random
from termcolor import colored

def print_text_green(string):
    print(colored(string, "light_green"))

def print_text_cyan(string):
    print(colored(string, "cyan"))

def print_text_white(string):
    print(colored(string, "white"))

if __name__ == "__main__":
    GAME_IDS = ["1","2","3","4", "5"]
    GAME_NAMES = ["🔑\tPassword Game", "🧩\tSudoku", "🗳️\tBracket Game", "📈\tOrdering Text", "🏝️\tIslands"]
    LEVEL_IDS = ["1","2","3","0","00"]
    LEVELS = ["🚅\tEasy","🚀\tMedium","🛸\tHard"]

    print_text_green("#" * 20)
    print_text_cyan("    Welcome to")
    print("   🎮 " + colored("Text", "white")+ colored("Games", "yellow"))
    print_text_green("#" * 20)
    print_text_green("Games:")
    for i, game_name in zip(range(len(GAME_NAMES)), GAME_NAMES):
        print_text_green(f"{i+1}. {game_name}")
    print_text_green("#" * 20)

    game_id = None
    difficulty_level = None
    while game_id is None:
        user_input = str(input(f"Choose the game> "))

        if user_input in GAME_IDS:
            game_id = user_input

            print_text_green("#" * 20)
            print_text_green("Difficulty Levels:")
            for i, level in zip(range(len(LEVELS)), LEVELS):
                print_text_green(f"{i+1}. {level}")
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
                    game_id = arr[0]
                    difficulty_level = arr[1]
            else:
                print("The game option is not available.")
                game = None

    print_text_green(f"Game chosen: {GAME_NAMES[int(game_id)-1]} and Difficulty Level: {LEVELS[int(difficulty_level)-1]}")
    if game_id == "1":
        game = PasswordGame()
        if difficulty_level == "1":
            num_rules = 2
        elif difficulty_level == "2":
            num_rules = 4
        elif difficulty_level == "3":
            num_rules = 6
        possible_answer = game.generate_new_game(num_rules=num_rules)
        
        print(f"possible answer: {possible_answer}")
    elif game_id == "2":
        game = Sudoku()
        if difficulty_level == "1":
            setting = random.randint(0,1)
            if setting == 0:
                game.generate_new_game(size=4, characters=["1","2","3","4"], empty_character="_", empty_ratio=0.2)
            elif setting == 1:
                game.generate_new_game(size=4, characters=["A","B","C","D"], empty_character="_", empty_ratio=0.2)
        elif difficulty_level == "2":
            setting = random.randint(0,1)
            if setting == 0:
                game.generate_new_game(size=4, characters=["1","2","3","4"], empty_character="_", empty_ratio=0.4)
            elif setting == 1:
                game.generate_new_game(size=4, characters=["A","B","C","D"], empty_character="_", empty_ratio=0.4)
        elif difficulty_level == "3":
            setting = random.randint(0,1)
            if setting == 0:
                game.generate_new_game(size=9, characters=["1","2","3","4","5","6","7","8","9"], empty_character="_", empty_ratio=0.4)
            elif setting == 1:
                game.generate_new_game(size=9, characters=["A","B","C","D","E","F","G","H","I"], empty_character="_", empty_ratio=0.4)
        
        game.print_sudoku()
    elif game_id == "3":
        game = BracketGame()
        if difficulty_level == "1":
            game.generate_new_game(num_words=3, num_rules=3, depth=2)
        elif difficulty_level == "2":
            game.generate_new_game(num_words=5, num_rules=5, depth=2)
        elif difficulty_level == "3":
            game.generate_new_game(num_words=10, num_rules=7, depth=3)
    elif game_id == "4":
        game = OrderingTextGame()
        match difficulty_level:
            case "0":
                game.generate_new_game(preset_config=1)
            case "00":
                game.generate_new_game(preset_config=2)
            case "1":
                game.generate_new_game(num_rules=(2, 4), uniq_classrules=True, positive_only=False, num_words=(3, 5), word_length=(3, 8), word_dic_only=True)
            case "2":
                game.generate_new_game(num_rules=(4, 8), uniq_classrules=False, positive_only=False, num_words=(5, 10), word_length=(3, 15), word_dic_only=True)
            case "3":
                game.generate_new_game(num_rules=(8, 12), uniq_classrules=False, positive_only=False, num_words=(10, 20), word_length=(6, 15), word_dic_only=False)
            case _:
                game.generate_new_game(preset_config=1)
    elif game_id == "5":
        game = Islands()
        if difficulty_level == "1":
            game.generate_new_game(num_islands=1, island_with_coconut=0)
        elif difficulty_level == "2":
            game.generate_new_game(num_islands=random.randint(1, 3))
        elif difficulty_level == "3":
            game.generate_new_game(num_islands=random.randint(3, 6))

    solved = False
    print(game.get_prompt())
    while not solved:
        contents = []
        while True:
            try:
                line = str(input("\t" if contents else f"Guess>\t"))
                if len(line) == 0:
                    break
            except EOFError:
                break
            contents.append(line)

        user_input = '\n'.join(contents)
        if game.validate(user_input):
            print("Correct guess")
            solved = True
        else:
            print("Bad guess")
    
    print("Thank you for playing!")
            

