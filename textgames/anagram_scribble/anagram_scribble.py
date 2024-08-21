import random
from pathlib import Path
from textgames.base_game import BaseGame
import json
import string

class AnagramScribble(BaseGame):
    @staticmethod
    def get_game_name() -> str:
        return "🔤\tAnagram Scribble"

    def __init__(self):
        self.WORD_LIST_BIN = {}
        with open(str(Path(__file__).absolute()).replace("anagram_scribble/anagram_scribble.py","") + "assets/kb/words_by_length.json") as f:
            self.WORD_LIST_BIN = json.load(f)
        self.low_num_chars = None
        self.high_num_chars = None
        self.num_chars = None
        self.allow_repeat = True
        self.all_chars = list(string.ascii_lowercase)
        self.total_chars_num = 10
        self.total_chars = []
        self.answer = ""

    def generate_new_game(self, *args, **kwargs) -> None:
        self.low_num_chars = kwargs['low_num_chars']
        self.high_num_chars = kwargs['high_num_chars']
        self.num_chars = random.randint(self.low_num_chars, self.high_num_chars)
        self.allow_repeat = kwargs['allow_repeat']
        self.answer = random.choice(self.WORD_LIST_BIN[str(self.num_chars)])
        remaining_chars_num = self.total_chars_num - self.num_chars
        available_characters = [char for char in self.all_chars if char not in self.answer]
        self.total_chars = list(self.answer) + random.sample(available_characters, remaining_chars_num)
        random.shuffle(self.total_chars)
        print(self.answer)

    def get_prompt(self) -> str:
        if self.allow_repeat:
            prompt = f"Construct a valid {self.num_chars}-character English word from the following letters:\n{self.total_chars}.\nEach character can be used multiple times. Please write None if there is no valid combination."
        else:
            prompt = f"Construct a valid {self.num_chars}-character English word from the following letters:\n{self.total_chars}\nEach character can only be used once. Please write None if there is no valid combination."
        return prompt
    
    def validate(self, answer: str) -> (bool, str):
        answer = answer.lower()
        if self.answer != "" and answer == "none":
            val_msg = "There is a valid answer."
            print(val_msg)
            return False, val_msg
        if len(answer) != self.num_chars:
            val_msg = f"Your answer must be exactly {self.num_chars} characters long"
            print(val_msg)
            return False, val_msg
        for char in answer:
            if char not in self.total_chars:
                val_msg = "Your answer must only contain the characters provided"
                print(val_msg)
                return False, val_msg
        if not self.allow_repeat and len(set(answer)) != len(answer) and len(self.answer) == len(set(self.answer)):
            val_msg = "Your answer must not contain repeated characters"
            print(val_msg)
            return False, val_msg
        if answer not in self.WORD_LIST_BIN[str(self.num_chars)]:
            val_msg = "Your answer is not a valid English word"
            print(val_msg)
            return False, val_msg

        return True, ""
