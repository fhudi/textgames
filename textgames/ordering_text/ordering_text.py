#%%
"""Example Prompt
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

Print only the answer.
"""

#%%
import re
import numpy as np

#%%

"""Rules Description
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
"""


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

    def point_wrapper(self, pattern: str, randint: int = 0) -> str:
        return self.str_point_patterns[randint].format(pattern=pattern)


#%%
class ConsecutiveScoring(Scoring):
    regex_pattern = {
        'c': "[^aeiou]",
        'v': "[aeiou]",
    }

    def __init__(self, point=1, seq="cc"):
        super().__init__(point)
        pattern = ""
        n = 1
        for a, b in zip(seq, seq[1:] + '$'):
            if a == b:
                n += 1
                continue
            else:
                cur_pattern = self.regex_pattern.get(a, None)
                if cur_pattern:
                    pattern += cur_pattern
                    pattern += f"{{{n}}}" if (n > 1) else ""
                n = 1
        self._pattern = re.compile(pattern)
        self._seq = seq
        self.prompt = None

    def calc_score(self, word):
        return len(self._pattern.findall(word)) * self.point

    def generate_prompt(self):
        if self.prompt is not None:
            return self.prompt

        prompt = None
        if len(self._seq) == 1 and self._seq[0] in {'c', 'v'}:
            prompt = f"every {'consonant' if self._seq == 'c' else 'vowel'}"
        elif self._seq == "cc":
            prompt = f"every pair of consecutive consonant"
        elif self._seq == "vv":
            prompt = f"every pair of consecutive vowel"
        elif self._seq == "vc":
            prompt = f"every consonant right after a vowel"
        elif self._seq == "cv":
            prompt = f"every vowel right after a consonant"
        elif len(set(self._seq)) == 1 and self._seq[0] in {'c', 'v'}:
            prompt = f"every {len(self._seq)} consecutive {'consonant' if self._seq == 'c' else 'vowel'}s"

        if prompt is None:
            raise NotImplementedError(f"[{self.__class__}] Not implemented for pattern: '{self._seq}'")
        else:
            self.prompt = self.point_wrapper(prompt, randint=0)
        return self.prompt


#%%
class LengthScoring(Scoring):
    def __init__(self, point=1, lt=None, gt=None, eq=None, ne=None):
        super().__init__(point)
        self.point = point
        self.lt, self.gt = lt or np.inf, gt or -np.inf
        self.eq = eq if (lt is None) and (gt is None) else None
        self.ne = ne
        self.prompt = None

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
        if self.lt < np.inf and not (self.gt > -np.inf) and self.ne is None:
            prompt = f"word less than {self.lt} characters"

        # print(self.lt, self.gt, self.eq, self.ne)
        # print(self.lt < np.inf, self.gt > -np.inf)

        if prompt is None:
            raise NotImplementedError(f"[{self.__class__}] Not implemented for current condition ()")
        else:
            self.prompt = self.point_wrapper(prompt, randint=0)
        return self.prompt


#%%
class AffixScoring(Scoring):
    def __init__(self, point=1, prefix=None, suffix=None):
        super().__init__(point)
        self.point = point
        self.prefix_txt, self.suffix_txt = prefix, suffix
        self.prefix = None if prefix is None else re.compile(f"^{prefix}")
        self.suffix = None if suffix is None else re.compile(f"{suffix}$")
        self.prompt = None

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

        if prompt is None:
            raise NotImplementedError(f"[{self.__class__}] Not implemented for current condition ({repr(self)})")
        else:
            self.prompt = self.point_wrapper(prompt, randint=0)
        return self.prompt


#%%
# - every pair of consecutive consonant has 5 points
# - additional 1 point if there exists exactly 1 'g'
# - word less than 5 characters gets extra 10 points
# - word starts with 'gen' gets additional 100 points
# - word ends with 'ta' gets negative 1000 points


#%%
class InfixScoring(Scoring):
    def __init__(self, point=1, infix=None, n=None):
        super().__init__(point)
        self.point = point
        self.infix = infix
        self.pattern = re.compile(infix)
        self.n = n
        self.prompt = None

    def calc_score(self, word):
        if self.n is None:
            return 0 if self.pattern.search(word) is None else self.point
        else:
            return (len(self.pattern.findall(word)) == self.n) * self.point

    def generate_prompt(self):
        if self.prompt is not None:
            return self.prompt

        prompt = None
        assert self.infix is not None, "owowo"
        if self.n is None:
            prompt = f"there exists '{self.infix}' in the word"
        else:
            prompt = f"there exists exactly {self.n} '{self.infix}' in the word"

        if prompt is None:
            raise NotImplementedError(f"[{self.__class__}] Not implemented for current condition ({repr(self)})")
        else:
            self.prompt = self.point_wrapper(prompt, randint=1)
        return self.prompt



#%%
class TheGame:
    def __init__(self, rules=None, words=None):
        self.rules = rules or set()
        self.words = words or set()
        self.points = dict()

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
        for word in self.words:
            self.points[word] = self.calc_point(word)

    def get_answer(self):
        return sorted(self.words, key=lambda word: (self.get_point(word), word))


#%%
class RuleSetGenerator:
    def __init__(self):
        raise NotImplementedError()


#%%


#%%
if __name__ == '__main__':
    words = ["genta", "winata", "hudi", "alham", "aji"]

    thegame = TheGame(
        rules={
            ConsecutiveScoring(point=5, seq="cc"),
            InfixScoring(point=1, infix="g", n=1),
            LengthScoring(point=10, lt=5),
            AffixScoring(point=100, prefix="gen"),
            AffixScoring(point=-1000, suffix="ta"),
        },
        words=set(words),
    )

    print("Rule Prompt List:")
    for rule in thegame.rules:
        print(f" - {rule.generate_prompt()}")
    print("==========")

    def calc_point(word, verbose=False):
        cnt = 0

        cur = len(re.findall(f'[^aeiou][^aeiou]', word)) * 5
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

    assert thegame.get_answer() == sorted(words, key=lambda w: (calc_point(w), w))
    print("All tests passed")

#%%


#%%


#%%


