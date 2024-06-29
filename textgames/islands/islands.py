import re
import numpy as np
import random
import math
from textgames.base_game import BaseGame

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


    def __init__(self):
        pass

    def generate_new_game(self, N = None, num_islands = None, island_size_min = None, island_size_max = None, island_with_coconut = None, total_coconuts = None):
        if N is None:
            N = random.randint(5, 8)
        if num_islands is None:
            num_islands = random.randint(1, 5)

        if island_size_min is None:
            worst_case = math.floor((N * N // num_islands) * 0.6)

            island_size_min = random.randint(1, worst_case)

        if island_size_max is None:
            island_size_max = random.randint(island_size_min, worst_case)
        
        if island_with_coconut is None:
            island_with_coconut = random.randint(1, num_islands)

        if total_coconuts is None:
            total_coconuts = min(random.randint(1, island_with_coconut * island_size_min), 5)

        self.N = N
        self.num_islands = num_islands
        self.island_size_min = island_size_min
        self.island_size_max = island_size_max
        self.island_with_coconut = island_with_coconut
        self.total_coconuts = total_coconuts

    def get_prompt(self):
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






