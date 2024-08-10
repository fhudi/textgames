import random
from pathlib import Path
from textgames.base_game import BaseGame

class BracketGame(BaseGame):
    def __init__(self):
        self.WORD_LIST = []

        with open(str(Path(__file__).absolute()).replace("bracket_game/bracket_game.py","") + "assets/kb/word_list.txt") as f:
            for line in f:
                self.WORD_LIST.append(line.replace("\n", ""))

        self.BRACKETS = [["block", "[", "]"], ["curly", "{", "}"], ["round", "(", ")"], ["angle", "<", ">"]]
        self.rules = []
        self.words = []
        self.string = ""
        self.depth = None

    def validate(self, answer: str) -> (bool, str):
        for rule in self.rules:
            arr = answer.split(rule[0])
            
            if rule[1][1] not in arr[0] or rule[1][2] not in arr[1]:
                val_msg = f"{rule[0]} is not between the correct bracket, {rule[1][1]} not in {arr[0]} and {rule[1][2]} not in {arr[1]}"
                print(val_msg)
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
                    print(val_msg)
                    return False, val_msg
        
        if count == self.depth:
            return True, ""
        else:       
            val_msg = f"The depth of the bracket is {count}. The expected depth is {self.depth}"
            print(val_msg)
            return False, val_msg

    def generate_new_game(self, *args, **kwargs) -> None:
        num_words = kwargs["num_words"]
        num_rules = kwargs["num_rules"]
        self.depth = kwargs["depth"]

        assert num_words >= num_rules

        self.rules = []
        self.words = []
        self.string = ""
        for _ in range(num_words):
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
    
    def get_prompt(self) -> str:
        prompt = f"You are given a text {self.string} Your job is to put some valid parenthesis brackets in the text such that:\n"
        for rule in self.rules:
            prompt += f"- \"{rule[0]}\" is inside a {rule[1][0]} bracket\n"
        prompt += f"The bracket depth must be {self.depth} and print only the answer\n"
        return prompt
