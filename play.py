from textgames.password_game.password_game import PasswordGame
from textgames.sudoku.sudoku import Sudoku
from textgames.bracket_game.bracket_game import BracketGame

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
            # game.print_sudoku()
            # game.generate_new_game(size=9, characters=["1", "2", "3", "4", "5", "6", "7", "8", "9"],
            #                        empty_character="_", empty_ratio=0.1)
            game.print_sudoku()
        elif user_input == "3":
            game = BracketGame()
            game.generate_new_game(num_words=5, num_rules=3, depth=2)
        else:
            print("The option is not available.")
            game = None

    solved = False
    print(game.get_prompt())
    while not solved:
        # user_input = str(input(f"Guess> "))
        contents = []
        user_input = ""
        count = 0
        while True:
            try:
                if count == 0:
                    line = str(input(f"Guess> \t"))
                    count += 1
                else:
                    line = str(input("\t"))
                if len(line) == 0:
                    break
            except EOFError:
                break
            contents.append(line)
        
        for i in range(len(contents)):
            if i > 0:
                user_input += "\n"
            user_input += contents[i]

        if game.validate(user_input):
            print("Correct guess")
            solved = True
        else:
            print("Bad guess")
    
    print("Thank you for playing!")
            

