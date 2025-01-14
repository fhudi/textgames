import numpy as np
from pathlib import Path

_FP_WORDS_ = {
    "dwyl": Path(__file__).parent / "kb" / "word_list.txt",
    "oxford5k_opal": Path(__file__).parent / "word_list" / "word_list.oxford5k_opal.lower.txt",
    "nltk_words": Path(__file__).parent / "word_list" / "word_list.nltk_words.lower.txt",
}
WORDS_LISTS = {}


def get_word_list(corpus=None):
    corpus = corpus or {"dwyl"}
    word_list = set()
    for c in corpus:
        with open(_FP_WORDS_[c], 'r') as f:
            for line in f:
                word_list.add(line.strip().lower())
    return sorted(word_list)


def get_word_list_by_length(corpus=None, min_length=0, max_length=20):
    corpus = corpus or {"dwyl"}
    word_list = get_word_list(corpus=corpus)
    word_list_by_length = {}
    for word in filter(lambda w: (min_length <= len(w) <= max_length), word_list):
        word_list_by_length.setdefault(len(word), []).append(word)
    return word_list_by_length


WORDS_LIST = get_word_list({"dwyl"})
WORDS_BY_LEN = get_word_list_by_length({"dwyl"})


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

