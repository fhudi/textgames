from textgames.password_game.password_game import PasswordGame
from textgames.sudoku.sudoku import Sudoku
from textgames.bracket_game.bracket_game import BracketGame
from textgames.ordering_text.ordering_text import OrderingTextGame

from termcolor import colored, cprint

def print_text_green(string):
    print(colored(string, "light_green"))

def print_text_cyan(string):
    print(colored(string, "cyan"))

if __name__ == "__main__":
    print_text_green("#" * 20)
    print_text_cyan("    Welcome to")
    print_text_cyan("   🎮 TextGames")
    print_text_green("#" * 20)
    print_text_green("Games:")
    print_text_green("1. 🔑\tPassword Game")
    print_text_green("2. 🧩\tSudoku")
    print_text_green("3. 🗳️\tBracket Game")
    print_text_green("4. 📈\tOrdering Text")
    print_text_green("#" * 20)

    game = None
    while game is None:
        user_input = str(input(f"Choose the game> "))
        if user_input == "1":
            game = PasswordGame()
            possible_answer = game.generate_new_game(num_rules=3)
            print(f"possible answer: {possible_answer}")
        elif user_input == "2":
            game = Sudoku()
            game.generate_new_game(size=4, characters=["1","2","3","4"], empty_character="_", empty_ratio=0.2)
            game.print_sudoku()
        elif user_input == "3":
            game = BracketGame()
            game.generate_new_game(num_words=5, num_rules=3, depth=2)
        elif user_input == "4":
            game = OrderingTextGame()
            game.generate_new_game()
        else:
            print("The option is not available.")
            game = None

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
            

