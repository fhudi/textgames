import numpy as np

from pathlib import Path
_FP_WORDS_ = Path(__file__).parent / "kb" / "word_list.txt"

WORDS_LIST = []
WORDS_BY_LEN = {}
with open(_FP_WORDS_) as f:
    for line in map(lambda _: _.strip(), f):
        if 1 <= len(line) <= 20:
            WORDS_LIST.append(line)
            WORDS_BY_LEN.setdefault(len(line), []).append(line)


class Node:
    def __init__(self, word=None, depth=0, parent=None, capacity=np.inf):
        self.word = word
        self.depth = depth
        self.parent = parent
        self.capacity = capacity
        self.children = {}


class PrefixTrie:
    def __init__(self, word_set=None):
        self.root = Node()
        if word_set is not None:
            for word in word_set:
                self.insert(word)

    def insert(self, word):
        node = self.root
        for depth, letter in enumerate(word, 1):
            node = node.children.setdefault(letter, Node(depth=depth, parent=node, capacity=0))
            node.capacity += 1
        node.word = word    # the full word is saved only in the leaves

