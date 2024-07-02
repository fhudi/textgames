from textgames.password_game.password_game import PasswordGame
from textgames.sudoku.sudoku import Sudoku
from textgames.bracket_game.bracket_game import BracketGame
from textgames.ordering_text.ordering_text import OrderingTextGame

import random
from termcolor import colored, cprint

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
    print_text_green("1. 🔑\tPassword Game")
    print_text_green("2. 🧩\tSudoku")
    print_text_green("3. 🗳️\tBracket Game")
    print_text_green("4. 📈\tOrdering Text")
    print_text_green("#" * 20)

    game_id = None
    difficulty_level = None
    while game_id is None:
        user_input = str(input(f"Choose the game> "))

        if user_input in ["1", "2", "3", "4"]:
            game_id = user_input

            print_text_green("#" * 20)
            print_text_green("Difficulty Levels:")
            print_text_green("1. 🚅\tEasy")
            print_text_green("2. 🚀\tMedium")
            print_text_green("3. 🛸\tHard")
            print_text_green("#" * 20)

            while difficulty_level is None:
                user_input = str(input(f"Choose the difficulty level> "))
                if user_input in ["1", "2", "3"]:
                    difficulty_level = user_input
                else:
                    print("The difficulty level option is not available.")
        else:
            print("The game option is not available.")
            game = None

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
        game.generate_new_game()

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
            

