#%%
"""
Rules Description
!! only lower_case characters are considered. (assumption for now)

word length:
- example: word less than 5 characters gets 10 points
- possible operands: {\eq, \lt, \gt, \ne}
    - \le and \ge will be randomized for prompt generation
- possible combinations: {\gt\lt, \gt\lt\ne}
- only 1 \ne is considered

neighboring / consecutive chars
- example: every pair of consecutive consonant gets 5 points
- possible concepts: {vowels, consonants}
- possible combinations: vowel after consonant, and vice versa
- possible counting, i.e.: "3 consecutive consonants".

prefix / suffix
- examples:
    - word starts with gen gets extra 100 point
    - word ends with ta gets negative 1000 point
- possibility of combination.

infix
- example: 1 point if there exists exactly 1 `g`
- possible for counting


------------------
Example Prompt #00
------------------

Given a set of rules to calculate point, sort the set of words in increasing order.
When there 2 or more words with same point, sort lexicographically.

rules:
- every pair of consecutive consonant has 5 points
- additional 1 point if there exists exactly 1 'g'
- word less than 5 characters gets extra 10 points
- word starts with 'gen' gets additional 100 points
- word ends with 'ta' gets negative 1000 points

words:
- genta
- winata
- hudi
- alham
- aji
- ruochen

Print only the answer.
"""

#%%
import re
import random
import string
from typing import Tuple, List
from itertools import chain

import numpy as np
from textgames.base_game import BaseGame

#%%
from textgames.assets.word_list import WORDS_LIST, WORDS_BY_LEN


#%%
class Scoring:
    def __init__(self, point: int):
        self.point = point
        self.str_point_patterns = [
            f"{{pattern}} gets {self.point} point{'s' if self.point > 1 else ''}",
            f"add {self.point} point{'s' if self.point > 1 else ''} if {{pattern}}",
        ]

    def calc_score(self, word: str) -> int:
        raise NotImplementedError()

    # def generate_pattern(self):
    #     raise NotImplementedError()

    def generate_prompt(self):
        raise NotImplementedError()

    def text_wrapper_for_point(self, pattern: str, randint: int = 0) -> str:
        return self.str_point_patterns[randint].format(pattern=pattern)

    def text_sampler(self, valid: bool = True, *args, **kwargs) -> str:
        raise NotImplementedError()

    def __eq__(self, other) -> bool:
        return isinstance(other, Scoring) and (repr(self) == repr(other))


#%%
def load_scoring_from_prompt(prompt: str) -> Scoring:
    if match := re.search(r"(.*) gets (-?\d+) points?", prompt):
        point, pattern = int(match.group(2)), match.group(1)
    elif match := re.search(r"add (-?\d+) points? if (.*)", prompt):
        point, pattern = int(match.group(1)), match.group(2)
    else:
        raise AssertionError(f"Failed to parse prompt. prompt: \"{prompt}\"")
    scoring = None
    for scoring_cls in SCORING_CLASSES:
        try:
            scoring = scoring_cls(point=point, pattern_text=pattern)
        except AssertionError:
            pass
    return scoring


#%%
class ConsecutiveScoring(Scoring):
    _regex_pattern = {
        'c': "[bcdfghjklmnpqrstvwxyz]",
        'v': "[aeiou]",
    }

    _seq_to_prompt = {
        "c": "every consonant",
        "v": "every vowel",
        "cc": "every pair of consecutive consonant",
        "vv": "every pair of consecutive vowel",
        "vc": "every consonant right after a vowel",
        "cv": "every vowel right after a consonant",
    }
    _prompt_to_seq = {v: k for k, v in _seq_to_prompt.items()}

    def __init__(self, point=1, seq=None, pattern_text=None, allow_no_match_pattern=False):
        super().__init__(point)

        # Reload from pattern of prompt text
        if pattern_text is not None:
            if pattern_text in self._prompt_to_seq:
                seq = self._prompt_to_seq[pattern_text]
            elif match := re.search(r"every (\d+) consecutive (consonant|vowel)", pattern_text):
                seq = ('v' if match.group(2) == "vowel" else 'c') * int(match.group(1))
            else:
                if not allow_no_match_pattern:
                    raise AssertionError("Failed to load the pattern")
                # else:
                #     print("Pattern text can't be loaded, regenerating the pattern ..")

        # random initialisation
        if seq is None:
            mode = random.randint(1, 6)    # [cv], [cv]{2}, (c{x}|v{x})
            match mode:
                case 1:
                    seq = random.choice(["c", "v"])
                case 2 | 3 | 4 | 5:
                    seq = ["cc", "vv", "vc", "cv"][mode-2]
                case 6:
                    seq = random.choice(["ccc", "vvv"])
        # print("seq", seq)
        assert all(c in self._regex_pattern.keys() for c in seq), \
            f"Please use only the allowed pattern: {self._regex_pattern.keys()}"
        self._seq = seq

        pattern = ""
        n = 1
        for a, b in zip(seq, seq[1:] + '$'):
            if a == b:
                n += 1
                continue
            else:
                cur_pattern = self._regex_pattern.get(a, None)
                if cur_pattern:
                    pattern += cur_pattern
                    pattern += f"{{{n}}}" if (n > 1) else ""
                n = 1
        self._pattern = re.compile(pattern)

        self.prompt = None

    def __repr__(self):
        return f"{self.__class__.__qualname__}(point={self.point}, seq={self._seq})"

    def calc_score(self, word):
        return len(self._pattern.findall(word)) * self.point

    def generate_prompt(self):
        if self.prompt is not None:
            return self.prompt

        prompt = None
        if self._seq in self._seq_to_prompt:
            prompt = self._seq_to_prompt[self._seq]
        elif len(set(self._seq)) == 1 and self._seq[0] in {'c', 'v'}:
            prompt = f"every {len(self._seq)} consecutive {'consonant' if self._seq[0] == 'c' else 'vowel'}s"

        if prompt is None:
            raise NotImplementedError(repr(self))
        else:
            self.prompt = self.text_wrapper_for_point(prompt, randint=0)
        return self.prompt

    def text_sampler(self, valid=True, *args, **kwargs) -> str:
        def randomise(c):
            while True:
                ret = random.choice(string.ascii_lowercase)
                check = re.search(self._regex_pattern[c], ret)
                if (valid and check) or (not valid and not check):
                    return ret
        return ''.join(map(randomise, self._seq))


#%%
class LengthScoring(Scoring):
    def __init__(self, point=1, lt=None, gt=None, eq=None, ne=None, pattern_text=None, allow_no_match_pattern=False):
        super().__init__(point)

        # Reload from pattern of prompt text
        if pattern_text is not None:
            match, prompt = None, None
            if match := re.search(r"word more than (\d+) characters?", pattern_text):
                gt = int(match.group(1))
                prompt = match.group(0)

            if match := re.search(rf"{'word' if prompt is None else f'{prompt} and'} less than (\d+) characters", pattern_text):
                lt = int(match.group(1))
                prompt = match.group(0)

            if match := re.search(rf"{'word' if prompt is None else f'{prompt} but'} not equal to (\d+) characters?", pattern_text):
                ne = int(match.group(1))
                prompt = match.group(0)

            if match := re.search(r"word that has exactly (\d+) characters?", pattern_text):
                eq = int(match.group(1))
                prompt = match.group(0)

            if prompt is None and not allow_no_match_pattern:
                raise AssertionError("Failed to load the pattern")

        # random initialisation
        if gt is None and lt is None and eq is None and ne is None:
            mode = random.randint(1, 10)    # gt; lt; eq(2); ne; gtlt; gt-ne; lt-ne; gtlt-ne; eq-ne;
            if mode in {1, 6, 7, 9}:
                gt = random.randint(2, 8)
            if mode in {2, 6, 8, 9}:
                lt = random.randint((gt or 2) + 3, 12)
            if mode in {3, 4, 10}:
                eq = random.randint(3, 11)
            if mode in {5, 7, 8, 9, 10}:
                _min, _mak = (gt or 1) + 1, (lt or 12) - 1
                assert _min < _mak, f"lhoooo ({_min}, {_mak})"
                ne = random.randint(_min, _mak)
                while eq is not None and (ne == eq):
                    ne = random.randint(_min, _mak)

        self.lt, self.gt = lt or np.inf, gt or 0
        self.ne = ne
        self.eq = eq if (lt is None) and (gt is None) and (ne is None) else None
        assert self.eq is None or self.ne is None, "lhoo"
        assert (self.gt+1 < self.lt) and ((self.gt+1 != self.ne) or (self.gt+2 < self.lt)), \
            f"lhooo ({self.gt} < x < {self.lt}; x == {self.eq}; x <> {self.ne})"
        self.prompt = None

    def __repr__(self):
        return f"{self.__class__.__qualname__}(point={self.point}, lt={self.lt}, gt={self.gt}, eq={self.eq}, ne={self.ne})"

    def calc_score(self, word):
        n = len(word)
        if not (self.gt < n < self.lt):
            return 0
        if self.eq is not None and not (n == self.eq):
            return 0
        if self.ne is not None and not (n != self.ne):
            return 0
        return self.point

    def generate_prompt(self):
        if self.prompt is not None:
            return self.prompt

        prompt = None
        if self.gt > 0:
            prompt = f"word more than {self.gt} character{'s' if self.gt > 1 else ''}"
        if self.lt < np.inf:
            prompt = f"{'word' if prompt is None else f'{prompt} and'} less than {self.lt} characters"
        if self.ne is not None:
            prompt = f"{'word' if prompt is None else f'{prompt} but'} not equal to {self.ne} character{'s' if self.ne > 1 else ''}"
        if prompt is None and self.eq is not None:
            prompt = f"word that has exactly {self.eq} character{'s' if self.eq > 1 else ''}"

        if prompt is None:
            raise NotImplementedError(repr(self))
        else:
            self.prompt = self.text_wrapper_for_point(prompt, randint=0)
        return self.prompt

    def text_sampler(self, valid=True, cur="", *args, **kwargs) -> str:
        if not valid:
            raise NotImplementedError(repr(self))
        target_length = self.eq if self.eq is not None else random.randint(self.gt+1, self.lt-1)
        while self.ne is not None and (target_length == self.ne):
            target_length = random.randint(self.gt+1, self.lt-1)
        return ''.join(random.choices(string.ascii_lowercase, k=target_length))


#%%
class AffixScoring(Scoring):
    def __init__(self, point=1, prefix=None, suffix=None, pattern_text=None, allow_no_match_pattern=False):
        super().__init__(point)

        # Reload from pattern of prompt text
        if pattern_text is not None:
            if match := re.search(r"word starts with ([a-z]+) and ends with ([a-z]+)", pattern_text):
                prefix, suffix = match.group(1), match.group(2)
            elif match := re.search(r"word starts with ([a-z]+)", pattern_text):
                prefix = match.group(1)
            elif match := re.search(r"word ends with ([a-z]+)", pattern_text):
                suffix = match.group(1)
            else:
                if not allow_no_match_pattern:
                    raise AssertionError("Failed to load the pattern")

        # random initialisation
        if prefix is None and suffix is None:
            mode = random.randint(1, 3)  # prefix_only, suffix_only, both
            if mode % 2 == 1:
                word_len = random.randint(1, 3)
                while len(prefix := random.choice(WORDS_LIST)) < word_len:
                    pass
                prefix = prefix[:word_len]
            if mode // 2 == 1:
                word_len = random.randint(1, 3)
                while len(suffix := random.choice(WORDS_LIST)) < word_len:
                    pass
                suffix = suffix[:word_len]

        self.prefix_txt, self.suffix_txt = prefix, suffix
        self.prefix = None if prefix is None else re.compile(f"^{prefix}")
        self.suffix = None if suffix is None else re.compile(f"{suffix}$")
        self.prompt = None

    def __repr__(self):
        return f"{self.__class__.__qualname__}(point={self.point}, prefix={self.prefix_txt}, suffix={self.suffix_txt})"

    def calc_score(self, word):
        if self.prefix is not None and self.prefix.search(word) is None:
            return 0
        if self.suffix is not None and self.suffix.search(word) is None:
            return 0
        return self.point

    def generate_prompt(self):
        if self.prompt is not None:
            return self.prompt

        prompt = None
        if self.prefix is not None and self.suffix is None:
            prompt = f"word starts with {self.prefix_txt}"
        elif self.prefix is None and self.suffix is not None:
            prompt = f"word ends with {self.suffix_txt}"
        else:
            prompt = f"word starts with {self.prefix_txt} and ends with {self.suffix_txt}"

        if prompt is None:
            raise NotImplementedError(repr(self))
        else:
            self.prompt = self.text_wrapper_for_point(prompt, randint=0)
        return self.prompt

    def text_sampler(self, valid=True, cur="", *args, **kwargs) -> str:
        if not valid:
            raise NotImplementedError(repr(self))
        return (self.prefix_txt or "") + cur + (self.suffix_txt or "")


#%%
class InfixScoring(Scoring):
    def __init__(self, point=1, infix=None, n=None, pattern_text=None, allow_no_match_pattern=False):
        super().__init__(point)

        # Reload from pattern of prompt text
        if pattern_text is not None:
            if match := re.search(r"there exists '([a-z]+)' in the word", pattern_text):
                infix, n = match.group(1), None
            elif match := re.search(r"there exists exactly (\d+) '([a-z]+)' in the word", pattern_text):
                infix, n = match.group(2), int(match.group(1))
            else:
                if not allow_no_match_pattern:
                    raise AssertionError("Failed to load the pattern")

        # random initialisation
        if infix is None:
            mode = random.randint(1, 2)    # with or without n
            word_length = random.choices([1, 2, 3], weights=[4, 5, 1])[0]
            while len(infix := random.choice(WORDS_LIST)) < word_length:
                pass
            split_idx = random.randint(0, len(infix) - word_length)
            infix = infix[split_idx:split_idx + word_length]
            n = random.randint(1, 2) if (mode == 1) else None

        self.infix = infix
        self.pattern = re.compile(infix)
        self.n = n
        self.prompt = None

    def __repr__(self):
        return f"{self.__class__.__qualname__}(point={self.point}, infix={self.infix}, n={self.n})"

    def calc_score(self, word):
        if self.n is None:
            return 0 if self.pattern.search(word) is None else self.point
        else:
            return (len(self.pattern.findall(word)) == self.n) * self.point

    def generate_prompt(self):
        if self.prompt is not None:
            return self.prompt

        assert self.infix is not None, "owowo"
        if self.n is None:
            prompt = f"there exists '{self.infix}' in the word"
        else:
            prompt = f"there exists exactly {self.n} '{self.infix}' in the word"

        if prompt is None:
            raise NotImplementedError(repr(self))
        else:
            self.prompt = self.text_wrapper_for_point(prompt, randint=1)
        return self.prompt

    def text_sampler(self, valid=True, cur="", *args, **kwargs) -> str:
        if not valid:
            raise NotImplementedError(repr(self))
        if len(cur) <= 0:
            return self.infix
        else:
            split_idx = random.randint(0, len(cur))    # got chance become prefix or suffix
            return cur[:split_idx] + self.infix + cur[split_idx:]


#%%
def _game_preset_config(preset_config: int) -> Tuple[List[Scoring], List[str]]:
    match preset_config:
        case 1:
            return [
                InfixScoring(point=1, infix="g", n=1),
                LengthScoring(point=10, lt=5),
            ], [
                "aji", "genta", "ruochen", "hudi",
            ]
        case 2:
            return [
                ConsecutiveScoring(point=5, seq="cc"),
                ConsecutiveScoring(point=3, seq="vv"),
                InfixScoring(point=1, infix="g", n=1),
                LengthScoring(point=10, lt=5),
                AffixScoring(point=100, prefix="gen"),
                AffixScoring(point=-1000, suffix="ta"),
            ], [
                "genta", "winata", "hudi", "alham", "aji", "ruochen",
            ]
        case _:
            return [], []


#%%
SCORING_CLASSES = [ConsecutiveScoring, LengthScoring, AffixScoring, InfixScoring]


#%%
class OrderingTextGame(BaseGame):
    @staticmethod
    def get_game_name() -> str:
        return "📈\tOrdering Text"

    def __init__(self, rules=None, words=None):
        super().__init__()
        self.rules = rules or set()
        self.words = words or set()
        self.points = dict()
        self.answer = None

    def calc_point(self, word):
        ret = 0
        for rule in self.rules:
            ret += rule.calc_score(word)
        return ret

    def get_point(self, word):
        if word not in self.points:
            self.points[word] = self.calc_point(word)
        return self.points[word]

    def recalculate_all(self):
        self.points, self.answer = dict(), None
        for word in self.words:
            self.points[word] = self.calc_point(word)
        self.answer = sorted(self.words, key=lambda x: (-self.points[x], x))

    def get_answer(self):
        if self.answer is None:
            self.recalculate_all()
        return self.answer    # sorted(self.words, key=lambda word: (self.get_point(word), word))

    def _validate(self, answer: str) -> (bool, str):
        answer = answer.lower().replace(' ', '\n')
        if answer != "\n".join(self.get_answer()):
            for i, (a, b) in enumerate(zip(answer.split(), self.get_answer()), 1):
                if a != b:
                    val_msg = f"{a} is not supposed to be at index {i}."
                    return False, val_msg
        else:
            return True, ""

    def _generate_new_game(self, *args, **kwargs) -> None:
        if "preset_config" in kwargs:
            self.rules, self.words = _game_preset_config(kwargs["preset_config"])

        elif "rules" in kwargs or "words" in kwargs:
            _rules, _words = _game_preset_config(1)
            self.rules = kwargs.get("rules", _rules)
            self.words = kwargs.get("words", _words)

        else:
            num_rules = random.randint(*kwargs["num_rules"])
            # print("num_rules", num_rules)
            scoring_list = random.choices(SCORING_CLASSES, k=num_rules)\
                if not kwargs["uniq_classrules"] else\
                random.sample(SCORING_CLASSES, k=num_rules)
            # print("scoring_list", scoring_list)
            _rules = [
                scoring(point=(random.randrange(5, 101, 5) *
                               random.choice([1] if kwargs["positive_only"] else [-1, 1])))
                for scoring in scoring_list
            ]
            # print("rules", _rules)
            self.rules = _rules

            _words = []
            num_words = random.randint(*kwargs["num_words"])
            for i in range(num_words):
                if kwargs["word_dic_only"] or (i < 2) or random.randint(0, 1):
                    word_length = random.randint(*kwargs["word_length"])
                    _word = random.choice(WORDS_BY_LEN[word_length])
                    j, mak_j = 0, 2000
                    while (i < 2) and (j < mak_j) and (self.calc_point(_word) == 0):
                        word_length = random.randint(*kwargs["word_length"])
                        _word = random.choice(WORDS_BY_LEN[word_length])
                        j += 1
                    if j >= mak_j:
                        print("can't find matching word")
                    _words.append(_word)
                else:
                    word_length = random.randint(*kwargs["word_length"])
                    _words.append(''.join(random.choices(string.ascii_lowercase, k=word_length)))
            self.words = _words

        self.recalculate_all()

    def _load_game(self, state_string) -> None:
        pat_rules = re.compile(r"Rules:\n((- [^\n]+\n)+)\n")
        rules_str = pat_rules.search(state_string).group(1).strip()
        self.rules = list(map(lambda t: load_scoring_from_prompt(t.strip("- ")), rules_str.split('\n')))
        pat_words = re.compile(r"Words:\n((- [^\n]+\n)+)\n")
        words_str = pat_words.search(state_string).group(1).strip()
        self.words = list(map(lambda t: t.strip("- "), words_str.split('\n')))
        self.recalculate_all()

    def _get_prompt(self) -> str:
        prompt = (
            "Given a set of rules to calculate point, sort the set of words in decreasing order.\n"
            "When there 2 or more words with same point, sort lexicographically.\n"
        )

        prompt += "\nRules:\n"
        for rule in self.rules:
            prompt += f"- {rule.generate_prompt()}\n"

        prompt += "\nWords:\n"
        for word in self.words:
            prompt += f"- {word}\n"

        prompt += "\nPrint only the answer."
        return prompt


#%%


#%%
if __name__ == '__main__':
    thegame = OrderingTextGame()

    # - every pair of consecutive consonant has 5 points
    # - every pair of consecutive vowels has 3 points
    # - additional 1 point if there exists exactly 1 'g'
    # - word less than 5 characters gets extra 10 points
    # - word starts with 'gen' gets additional 100 points
    # - word ends with 'ta' gets negative 1000 points
    tc_rules, tc_words = _game_preset_config(2)
    thegame.generate_new_game(rules=tc_rules, words=tc_words)

    print(thegame.get_prompt())

    def calc_point(word, verbose=False):
        cnt = 0

        cur = len(re.findall(f'[^aeiou][^aeiou]', word)) * 5
        cnt += cur
        if verbose:
            print(cnt)

        cur = len(re.findall(f'[aeiou][aeiou]', word)) * 3
        cnt += cur
        if verbose:
            print(cnt)

        cur = (len(re.findall(r'g', word)) == 1) * 1
        cnt += cur
        if verbose:
            print(cur, cnt)

        cur = (len(word) < 5) * 10
        cnt += cur
        if verbose:
            print(cur, cnt)

        cur = (re.search(r'^gen', word) is not None) * 100
        cnt += cur
        if verbose:
            print(cur, cnt)

        cur = (re.search(r'ta$', word) is not None) * -1000
        cnt += cur
        if verbose:
            print(cur, cnt)

        if verbose:
            print(word, cnt)
        return cnt

    ans = sorted(thegame.words, key=lambda w: (-calc_point(w), w))
    assert thegame.get_answer() == ans, f"found: {thegame.get_answer()},  expected: {ans}."
    # print(thegame.validate("\n".join(ans)))
    print("All tests passed")
    print(" > answer:", ans)
    print(" > points:", list(map(lambda x: (thegame.get_point(x), x), ans)))


#%%



#%%


#%%


#%%


