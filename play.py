from textgames.password_game.password_game import PasswordGame
from textgames.sudoku.sudoku import Sudoku

if __name__ == "__main__":
    print("#" * 20)
    print("    Welcome to")
    print("   🎮 TextGames")
    print("#" * 20)
    print("Game options:")
    print("1. 🔑 Password Games")
    print("2. 🧩 Sudoku [under construction]")
    print("#" * 20)
    user_input = str(input(f"Game option> "))
    if user_input == "1":
        while True:
            game = PasswordGame()
            game.generate_new_game(num_rules=5)

            solved = False

            while not solved:
                print(game.get_prompt())
                user_input = str(input(f"Guess> "))
                if game.validate(user_input):
                    print("Correct guess")
                    solved=True
                else:
                    print("Bad guess")

