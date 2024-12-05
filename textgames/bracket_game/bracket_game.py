import random
import re
from pathlib import Path
from textgames.base_game import BaseGame
#%%
"""Example Prompt
You are given a text archigasterbalersnitrosylsulfuric Your job is to put some valid parenthesis brackets in the text such that:
- \"archigaster\" is inside a curly bracket
- \"balers\" is inside a curly bracket
- \"nitrosylsulfuric\" is inside a angle bracket
The bracket depth must be 2.
Print only the answer.
"""


#%%
def sort_game_states(game):
    game_states = {k: v for k, v in vars(game).items() if k not in game.exclude_states}
    for k in game_states.keys():
        if isinstance(game_states[k], list):
            try:
                game_states[k].sort()
            except:
                print("ignore the sort")


#%%
class BracketGame(BaseGame):
    @staticmethod
    def get_game_name() -> str:
        return "🗳️\tBracket Game"

    def __init__(self):
        super().__init__()
        self.exclude_states = ["possible_ans", "rules", "num_rules", "WORD_LIST", "MULTI_WORD_LIST", "multi_word",]

        self.WORD_LIST = []
        self.MULTI_WORD_LIST = []

        with open(str(Path(__file__).absolute()).replace("bracket_game/bracket_game.py","") + "assets/kb/word_list.txt") as f:
            for line in f:
                self.WORD_LIST.append(line.replace("\n", ""))

        self.BRACKETS = [["block", "[", "]"], ["curly", "{", "}"], ["round", "(", ")"], ["angle", "<", ">"]]
        self.rules = []
        self.words = []
        self.string = ""
        self.depth = None
        self.multi_word = False
        self.create_multiple_words()

    def create_multiple_words(self):
        for i in range(1000):
            num1 = random.randint(0, len(self.WORD_LIST)-1)
            num2 = random.randint(0, len(self.WORD_LIST)-1)
            if num1 != num2:
                self.MULTI_WORD_LIST.append(self.WORD_LIST[num1] + self.WORD_LIST[num2])

    def _validate(self, answer: str) -> (bool, str):
        for rule in self.rules:
            arr = answer.split(rule[0])
            
            if rule[1][1] not in arr[0] or rule[1][2] not in arr[1]:
                val_msg = f"{rule[0]} is not between the correct bracket, {rule[1][1]} not in {arr[0]} and {rule[1][2]} not in {arr[1]}"
                return False, val_msg
            
        filter_answer = answer
        for i in range(0, 26):
            cc = chr(ord("a") + i)
            filter_answer = filter_answer.replace(cc,"")

            cc = chr(ord("A") + i)
            filter_answer = filter_answer.replace(cc,"")
        
        open_bracket_list = ["[", "{", "(", "<"]
        close_bracket_map = {
            "[":"]", "{":"}", "(":")", "<":">"
        }

        # check max depth
        count = 0
        st = []

        for i in range(len(filter_answer)):
            if (filter_answer[i] in open_bracket_list):
                st.append(filter_answer[i]) # pushing the bracket in the stack
            else:
                if len(st) > 0 and (filter_answer[i] == close_bracket_map[st[-1]]):
                    if (count < len(st)):
                        count = len(st)
                    st.pop()
                else:
                    val_msg = "There is a closing bracket without an open bracket"
                    return False, val_msg
        
        if count == self.depth:
            return True, ""
        else:       
            val_msg = f"The depth of the bracket is {count}. The expected depth is {self.depth}"
            return False, val_msg

    def _generate_new_game(self, *args, **kwargs) -> None:
        num_words = kwargs["num_words"]
        num_rules = kwargs["num_rules"]
        self.depth = kwargs["depth"]
        self.multi_word = kwargs["multi_word"]

        assert num_words >= num_rules

        self.rules = []
        self.words = []
        self.string = ""

        for _ in range(num_words):
            if self.multi_word:
                toggle_multi_word = random.randint(0, 1)
                if toggle_multi_word == 1:
                    word = self.MULTI_WORD_LIST[random.randint(0, len(self.MULTI_WORD_LIST)-1)]
                else:
                    word = self.WORD_LIST[random.randint(0, len(self.WORD_LIST)-1)]
            else:
                word = self.WORD_LIST[random.randint(0, len(self.WORD_LIST)-1)]
                while word in self.words:
                    word = self.WORD_LIST[random.randint(0, len(self.WORD_LIST)-1)]
            self.string += word
            self.words.append(word)

        self.chosen_words = []
        for _ in range(num_rules):
            cur_word = self.words[random.randint(0, len(self.words)-1)]
            while cur_word in self.chosen_words:
                cur_word = self.words[random.randint(0, len(self.words)-1)]
            self.chosen_words.append(cur_word)
            
            bracket = self.BRACKETS[random.randint(0, len(self.BRACKETS)-1)]
            self.rules.append([cur_word, bracket])

        sort_game_states(self)

    def _get_prompt(self) -> str:
        prompt = f"You are given a text {self.string} Your job is to put some valid parenthesis brackets in the text such that:\n"
        for rule in self.rules:
            prompt += f"- \"{rule[0]}\" is inside a {rule[1][0]} bracket\n"
        prompt += f"The bracket depth must be {self.depth} and print only the answer\n"
        return prompt

    def _load_game(self, state_string):
        pattern_str = re.compile(r"text ([a-zA-Z0-9]+) Your")
        pattern_str_rule = re.compile(r"- \"([a-zA-Z]+)\" is")
        pattern_depth = re.compile(r"must be ([0-9]+).")
        
        def extract_variable(pattern, input_string, mode):
            match = pattern.search(input_string)
            if match:
                if mode == "number":
                    return int(match.group(1))
                else:
                    return match.group(1)
            else:
                return 0
            
        content = state_string.split("the text such that:")[1].split("\nThe bracket depth must be")[0].split("\n")

        self.words = []
        self.rules = []
        self.chosen_words = []

        self.string = extract_variable(pattern_str, state_string, "string")
        for row in content[1:]:
            word = extract_variable(pattern_str_rule, row, "string")

            bracket = row.split("inside a")[1].split("bracket")[0].strip()
            self.words.append(word)
            bracket_obj = None
            for obj in self.BRACKETS:
                if obj[0] == bracket:
                    bracket_obj = obj
                    break
            self.chosen_words.append(word)
            self.rules.append([word, bracket_obj])

        self.depth = extract_variable(pattern_depth, state_string, "number")

        with open(str(Path(__file__).absolute()).replace("bracket_game/bracket_game.py","") + "assets/kb/word_list.txt") as f:
            for line in f:
                self.WORD_LIST.append(line.replace("\n", ""))

        self.create_multiple_words()        

        sort_game_states(self)
