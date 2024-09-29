from termcolor import colored
from textgames import GAME_IDS, GAME_NAMES, LEVEL_IDS, LEVELS, new_game, LEVELS_HIDDEN, SINGLE_LINE_GAME_IDS


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

    solved = False
    cur_game = new_game(this_game_name, difficulty_level)
    print(colored("########  Game Start !!  ########", "light_green"))
    print(cur_game.get_prompt())
    while not solved:
        contents = []
        while True:
            try:
                line = str(input("\t" if contents else f"Guess>\t"))
                # automatic break for some games:
                if cur_game_id in SINGLE_LINE_GAME_IDS:
                    contents.append(line)
                    break
                if len(line) == 0:
                    break
            except EOFError:
                break
            contents.append(line)

        user_input = '\n'.join(contents)
        solved, val_msg = cur_game.validate(user_input)
        if val_msg:
            print(val_msg)
        print(f"Attempt #{len(cur_game.attempt_timestamps)}:", "Correct guess" if solved else "Bad guess", end="\n\n")

    print(f"Time to solve: {round(cur_game.attempt_timestamps[-1] - cur_game.start_timestamp, 1)}s")
    print("Thank you for playing!")
            

