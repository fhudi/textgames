from textgames.password_game.password_game import PasswordGame
from textgames.sudoku.sudoku import Sudoku

if __name__ == "__main__":
    print("#" * 20)
    print("    Welcome to")
    print("   🎮 TextGames")
    print("#" * 20)
    print("Games:")
    print("1. 🔑\tPassword Game")
    print("2. 🧩\tSudoku")
    print("3. 🗳️\tBracket Game")
    print("#" * 20)
    user_input = str(input(f"Choose the game> "))
    if user_input == "1":
        game = PasswordGame()
        possible_answer = game.generate_new_game(num_rules=3)
        solved = False

        print(game.get_prompt())
        print(f"possible answer: {possible_answer}")
        while not solved:
            user_input = str(input(f"Guess> "))
            if game.validate(user_input):
                print("Correct guess")
                solved=True
            else:
                print("Bad guess")
    elif user_input == "2":
        game = Sudoku()
        game.generate_new_game(size=4, characters=["1","2","3","4"], empty_character="_", empty_ratio=0.5)
        game.print_sudoku()

        # game.generate_new_game(size=9, characters=["1","2","3","4","5","6","7","8","9"], empty_character="_", empty_ratio=0.5)
        # game.print_sudoku()
        solved = False

        print(game.get_prompt())
        while not solved:
            user_input = str(input(f"Guess> "))
            if game.validate(user_input):
                print("Correct guess")
                solved=True
            else:
                print("Bad guess")
    
    print("Thank you for playing!")
            

