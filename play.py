import json
import random
from enum import Enum

from textgames.password_game.game import PasswordGame

# def __main__():
print("#" * 20)
print("     TextGames")
print("#" * 20)
print("Game options:")
print("1. Password Games")
print("#" * 20)
print(">")
user_input = str(input())
if user_input == "1":
    while True:
        game = PasswordGame(num_rules=5)
        game.generate_rule()

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

