import re
import numpy as np
import random
import math
from textgames.base_game import BaseGame
from typing import List
#%%
"""Example Prompt
You are asked to construct a 2D [N] x [N] grid, consisting of water tiles (denoted by ’.’), 
land tiles (denoted by ’#’), and coconut tree tiles (denoted by ’o’). 
Coconut tree tiles are also considered as land tiles. 

A group of connected land tiles in 4 cardinal directions forms an island.

Your 2D grid must follow the following rules:
- There must be exactly [K] islands.
- The size of each island must be at least [Y] tiles.
- There must be exactly [L] islands that have coconut trees on them.
- There must be exactly [C] total coconut trees.

Print only the answer.
"""

"""Rule Constraint
Grid size 5 <= N <= 8

num islands 1 <= K <= 5
island size 1 <= Y < Z <= 10

total coconut trees should fit the minimum total land tiles (to simplify)

Print only the answer
"""

#%%
class Islands(BaseGame):
    @staticmethod
    def get_game_name() -> str:
        return "🏝️\tIslands"

    def __init__(self):
        super().__init__()

    def load_game(self, state_string):
        pattern_N = re.compile(r"construct a 2D (\d+) x \d+ grid")
        pattern_num_islands = re.compile(r"exactly (\d+) islands")
        pattern_island_size_min = re.compile(r"from (\d+) to \d+ tiles")
        pattern_island_size_max = re.compile(r"from \d+ to (\d+) tiles")
        pattern_island_with_coconut = re.compile(r"exactly (\d+) islands that have coconut")
        pattern_total_coconuts = re.compile(r"exactly (\d+) total coconut trees")
        
        def extract_variable(pattern, input_string):
            match = pattern.search(input_string)
            if match:
                return int(match.group(1))
            else:
                return 0

        self.N = extract_variable(pattern_N, state_string)
        self.num_islands = extract_variable(pattern_num_islands, state_string)
        self.island_size_min = extract_variable(pattern_island_size_min, state_string)
        self.island_size_max = extract_variable(pattern_island_size_max, state_string)
        self.island_with_coconut = extract_variable(pattern_island_with_coconut, state_string)
        self.total_coconuts = extract_variable(pattern_total_coconuts, state_string)


    def _generate_new_game(self, N = None, num_islands = None, island_size_min = None, island_size_max = None, island_with_coconut = None, total_coconuts = None):
        if N is None:
            N = random.randint(5, 8)
        if num_islands is None:
            num_islands = random.randint(1, 6)

        if island_size_min is None:
            worst_case = math.floor((N * N // num_islands) * 0.6)

            island_size_min = random.randint(1, worst_case)

        if island_size_max is None:
            island_size_max = random.randint(island_size_min, worst_case)
        
        if island_with_coconut is None:
            island_with_coconut = random.randint(1, num_islands)

        if total_coconuts is None:
            total_coconuts = min(random.randint(island_with_coconut, island_with_coconut * island_size_min), 6)

        self.N = N
        self.num_islands = num_islands
        self.island_size_min = island_size_min
        self.island_size_max = island_size_max
        self.island_with_coconut = island_with_coconut
        self.total_coconuts = total_coconuts

    def _validate(self, answer: str) -> (bool, str):

        # clean up the input, to make it more flexible towards formatting
        answer = answer.split("\n")
        answer = [a.replace(" ", "").lower().strip() for a in answer]

        # check the size
        if len(answer) != self.N or len(answer[0]) != self.N:
            val_msg = f"2D grid is not {self.N} x {self.N}. ({len(answer)} x {len(answer[0])})"
            return False, val_msg

        # check the tiles, ensure they are valid
        for a in answer:
            for c in a:
                if c != 'o' and c != '.' and c != '#':
                    val_msg = f'2D contains invalid character ({c})'
                    return False, val_msg

        islands = []
        # build the islands, denoted as a set of coordinate and tile
        visited = [[False] * self.N for _ in range(self.N)] # for flood-fill

        # helper flood-fill
        def flood_fill(x, y, answer, visited, island_set):

            if x < 0 or y < 0 or x == self.N or y == self.N or answer[x][y] == '.' or visited[x][y]:
                return

            visited[x][y] = True
            island_set.add((x, y, answer[x][y]))

            flood_fill(x + 1, y, answer, visited, island_set)
            flood_fill(x, y + 1, answer, visited, island_set)
            flood_fill(x - 1, y, answer, visited, island_set)
            flood_fill(x, y - 1, answer, visited, island_set)

        for i in range(self.N):
            for j in range(self.N):
                if answer[i][j] != '.' and visited[i][j] == False:
                    island_set = set()
                    flood_fill(i, j, answer, visited, island_set)
                    islands.append(island_set)
        
        # constraint 1: has exactly K islands
        if len(islands) != self.num_islands:
            val_msg = f"There must be exactly {self.num_islands} islands, but you provided {len(islands)} islands"
            return False, val_msg

        # constraint 2: island size
        for island in islands:
            if len(island) < self.island_size_min or len(island) > self.island_size_max:
                val_msg = f"The size of each island must be from {self.island_size_min} to {self.island_size_max} tiles"
                return False, val_msg

        # constraint 3: islands with coconut
        solution_island_with_coconut = 0

        for island in islands:
            has_coconut = any(c == 'o' for _, _, c in island)
            if has_coconut:
                solution_island_with_coconut += 1
        if solution_island_with_coconut != self.island_with_coconut:
            val_msg = f"There must be exactly {self.island_with_coconut} islands that have coconut trees on them"
            return False, val_msg

        # constraint 4: total coconut trees
        solution_total_coconuts = sum(c == 'o' for island in islands for _, _, c in island)

        if solution_total_coconuts != self.total_coconuts:
            val_msg = f"There must be exactly {self.total_coconuts} total coconut trees."
            return False, val_msg

        return True, ""

    def _get_prompt(self):
        if self.island_with_coconut == 0:
            prompt = f"""You are asked to construct a 2D {self.N} x {self.N} grid, consisting of water tiles (denoted by ’.’), 
land tiles (denoted by ’#’). 

A group of connected land tiles in 4 cardinal directions forms an island.

Your 2D grid must follow the following rules:
- There must be exactly {self.num_islands} islands.
- The size of each island must be from {self.island_size_min} to {self.island_size_max} tiles.

Print only the answer.
"""
        else:
            prompt = f"""Example Prompt
You are asked to construct a 2D {self.N} x {self.N} grid, consisting of water tiles (denoted by ’.’), 
land tiles (denoted by ’#’), and coconut tree tiles (denoted by ’o’). 
Coconut tree tiles are also considered as land tiles. 

A group of connected land tiles in 4 cardinal directions forms an island.

Your 2D grid must follow the following rules:
- There must be exactly {self.num_islands} islands.
- The size of each island must be from {self.island_size_min} to {self.island_size_max} tiles.
- There must be exactly {self.island_with_coconut} islands that have coconut trees on them.
- There must be exactly {self.total_coconuts} total coconut trees.

Print only the answer.
"""
        return prompt