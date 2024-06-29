import random
import math
from textgames.base_game import BaseGame

class Sudoku(BaseGame):
    def __init__(self):
        pass

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

    def validate(self, input):
        mat = [[self.empty_character for i in range(self.size)] for j in range(self.size)]

        arr = input.split(" ")
        for i in range(len(arr)):
            for j in range(len(arr[i])):
                if arr[i][j] not in self.char_to_id:
                    print("Found unrecognized character(s)")
                    return False
                
                mat[i][j] = self.char_to_id[arr[i][j]]
                if arr[i][j] != self.mat[i][j] and self.mat[i][j] != self.empty_character:
                    print("One or more characters are replaced")
                    return False
        return self.is_valid_sudoku(mat)

    def generate_new_game(self, *args, **kwargs) -> None:
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
            for j in range(self.size):
                print(self.mat[i][j], end=" ")
            print()

    def get_prompt(self):
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