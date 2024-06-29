from textgames.password_game.password_game import PasswordGame
from textgames.sudoku.sudoku import Sudoku

if __name__ == "__main__":
    print("#" * 20)
    print("    Welcome to")
    print("   🎮 TextGames")
    print("#" * 20)
    print("Game options:")
    print("1. 🔑 Password Games")
    print("#" * 20)
    print(">")
    user_input = str(input())
    if user_input == "1":
        while True:
            game = PasswordGame(num_rules=5)
            game.generate_new_game()

            solved = False

            while not solved:
                print(game.get_prompt())
                print("guess>")
                user_input = str(input())
                if game.validate(user_input):
                    print("correct guess")
                    solved=True
                else:
                    print("bad guess")

