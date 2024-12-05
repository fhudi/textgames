import random
import math
import re
from textgames.base_game import BaseGame
#%%
"""Example Prompt
Please solve the 9x9 sudoku with 1,2,3,4,5,6,7,8,9 as the values and fill _ with the possible value. Follow the sudoku rule.
74_13__8_ __189_247 968247_1_ 1235_9_68 5_6_1__3_ 489_2____ 8_496217_ __7351__4 _1__8__96
Print only the answer.
"""

#%%
class Sudoku(BaseGame):
    @staticmethod
    def get_game_name() -> str:
        return "🧩\tText Sudoku"

    def __init__(self):
        super().__init__()
        self.exclude_states = ["possible_ans", "rules", "num_rules", "WORD_LIST", "MULTI_WORD_LIST", "multi_word",]

    def is_valid_sudoku(self, mat):
        rows = [set() for _ in range(self.size)]
        cols = [set() for _ in range(self.size)]
        subgrids = [set() for _ in range(self.size)]
    
        for i in range(self.size):
            for j in range(self.size):
                num = mat[i][j]
                if num == 0:
                    continue
    
                subgrid_index = (i // self.srn) * self.srn + j // self.srn
    
                if num in rows[i] or num in cols[j] or num in subgrids[subgrid_index]:
                    return False
    
                rows[i].add(num)
                cols[j].add(num)
                subgrids[subgrid_index].add(num)
    
        return True

    def _validate(self, input) -> (bool, str):
        mat = [[self.empty_character for i in range(self.size)] for j in range(self.size)]

        arr = input.split()
        for i in range(len(arr)):
            for j in range(len(arr[i])):
                if arr[i][j] not in self.char_to_id:
                    val_msg = "Found unrecognized character(s)"
                    return False, val_msg
                
                mat[i][j] = self.char_to_id[arr[i][j]]
                if arr[i][j] != self.mat[i][j] and self.mat[i][j] != self.empty_character:
                    val_msg = "One or more characters are replaced"
                    return False, val_msg
        return self.is_valid_sudoku(mat), ""

    def _generate_new_game(self, *args, **kwargs) -> None:
        size=kwargs["size"]
        characters=kwargs["characters"]
        empty_character=kwargs["empty_character"]
        empty_ratio=kwargs["empty_ratio"]

        assert size == len(characters)
        
        self.size = size
        self.srn = int(math.sqrt(self.size))

        valid_puzzle = False
        while not valid_puzzle:
            self.mat = [[0 for _ in range(self.size)] for _ in range(self.size)]
            self.characters = characters
            self.empty_character = empty_character
            self.num_empty_block = int(size * size * empty_ratio)

            self.char_to_id = {}
            for c_id in range(len(self.characters)):
                self.char_to_id[self.characters[c_id]] = c_id

            # fill the diagonal of small square (srn x srn) matrices
            self.fill_diagonal()
            self.fill_remaining(0, self.srn)
            self.replace_digits()

            valid_puzzle = True
            for i in range(self.size):
                for j in range(self.size):
                    if self.mat[i][j] == 0:
                        valid_puzzle = False

            self.remove_digits()
    
    def unused_in_row(self, i, num):
        for j in range(self.size):
            if self.mat[i][j] == num:
                return False
        return True
    
    def unused_in_col(self, j, num):
        for i in range(self.size):
            if self.mat[i][j] == num:
                return False
        return True
    
    def check_if_safe(self, i, j, num):
        return (self.unused_in_row(i, num) and self.unused_in_col(j, num) and self.unused_in_box(i - i % self.srn, j - j % self.srn, num))

    def random_generator(self, num):
        return math.floor(random.random() * num + 1)

    def unused_in_box(self, row_start, col_start, num):
        for i in range(self.srn):
            for j in range(self.srn):
                if self.mat[row_start + i][col_start + j] == num:
                    return False
        return True

    def fill_box(self, row, col):
        num = 0
        for i in range(self.srn):
            for j in range(self.srn):
                while True:
                    num = self.random_generator(self.size)
                    if self.unused_in_box(row, col, num):
                        break
                self.mat[row + i][col + j] = num

    def fill_diagonal(self):
        for i in range(0, self.size, self.srn):
            self.fill_box(i, i)

    def fill_remaining(self, i, j):
        # Check if we have reached the end of the matrix
        if i == self.size - 1 and j == self.size:
            return True
    
        # Move to the next row if we have reached the end of the current row
        if j == self.size:
            i += 1
            j = 0
    
        # Skip cells that are already filled
        if self.mat[i][j] != 0:
            return self.fill_remaining(i, j + 1)
    
        # Try filling the current cell with a valid value
        for num in range(1, self.size + 1):
            if self.check_if_safe(i, j, num):
                self.mat[i][j] = num
                if self.fill_remaining(i, j + 1):
                    return True
                self.mat[i][j] = 0
        
        # No valid value was found, so backtrack
        return False

    def remove_digits(self):
        for i in range(self.size):
            for j in range(self.size):
                if self.mat[i][j] == 0:
                    self.mat[i][j] = self.empty_character

        count = self.num_empty_block

        while (count != 0):
            i = self.random_generator(self.size) - 1
            j = self.random_generator(self.size) - 1
            if (self.mat[i][j] != self.empty_character):
                count -= 1
                self.mat[i][j] = self.empty_character

    def replace_digits(self):
        for i in range(len(self.mat)):
            for j in range(len(self.mat[i])):
                if self.mat[i][j] != 0:
                    self.mat[i][j] = self.characters[self.mat[i][j]-1]

    def print_sudoku(self):
        for i in range(self.size):
            string = ""
            for j in range(self.size):
                string += self.mat[i][j]
            print(string)

    def _get_prompt(self):
        characters = ",".join(c for c in self.characters)
        prompt = f"Please solve the {self.size}x{self.size} sudoku with {characters} as the values and fill {self.empty_character} with the possible value and only print the answer. Follow the sudoku rule.\n"
        sudoku = ""
        for i in range(len(self.mat)):
            if i > 0:
                sudoku += " "
            sudoku_row = ""
            for j in range(len(self.mat[i])):
               sudoku_row += self.mat[i][j]
            sudoku += sudoku_row
        prompt += sudoku
        return prompt
    
    def _load_game(self, state_string):
        pattern_size = re.compile(r"Please solve the (\d+)x\d+ sudoku")
        pattern_characters = re.compile(r"with ([0-9A-Z,]+) as")
        self.empty_character = "_"
        
        def extract_variable(pattern, input_string, mode):
            match = pattern.search(input_string)
            if match:
                if mode == "number":
                    return int(match.group(1))
                else:
                    return match.group(1)
            else:
                return 0

        self.size = extract_variable(pattern_size, state_string, "number")
        self.characters = extract_variable(pattern_characters, state_string, "string").split(",")
        content = state_string.split("rule.\n")[1].split("Print only")[0].split(" ")
        self.mat = []
        self.srn = int(math.sqrt(self.size))
        self.num_empty_block = 0

        for row in content:
            self.mat.append(list(row))
            for cc in list(row):
                if cc == "_":
                    self.num_empty_block += 1

        self.char_to_id = {}
        for c_id in range(len(self.characters)):
            self.char_to_id[self.characters[c_id]] = c_id
        