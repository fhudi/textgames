from textgames.password_game.password_game import PasswordGame
from textgames.sudoku.sudoku import Sudoku
from textgames.bracket_game.bracket_game import BracketGame
from textgames.ordering_text.ordering_text import OrderingTextGame

if __name__ == "__main__":
    print("#" * 20)
    print("    Welcome to")
    print("   🎮 TextGames")
    print("#" * 20)
    print("Games:")
    print("1. 🔑\tPassword Game")
    print("2. 🧩\tSudoku")
    print("3. 🗳️\tBracket Game")
    print("4. 📈\tOrdering Text")
    print("#" * 20)

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
                line = str(input("" if contents else f"Guess>\n"))
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
            

