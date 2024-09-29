import re
import numpy as np
import random
import math
import string
from textgames.base_game import BaseGame
from collections import defaultdict


class StringSearch(BaseGame):

    @staticmethod
    def get_game_name() -> str:
        return "🔎\tString Search"

    extra_artificial_constraints = []

    def __init__(self):
        super().__init__()
        self.extra_artificial_constraints = []
        self.exclude_states = ['answer', 'difficulty']

    def _load_game(self, state_string):
        pattern_input_string = re.compile(r'You are given the following string:\n([a-zA-Z]+)')
        pattern_contains = re.compile(r'Contains ([a-z](?:, [a-z])*)(?: and ([a-z]))?')
        pattern_not_contain = re.compile(r'not contain ([a-z](?:, [a-z])*)(?: and ([a-z]))?')
        pattern_answer_length = re.compile(r'substring of exactly (\d+) characters long that')

        def get_letter_constraint(pattern, input):
            match = pattern.search(input)

            #print(match.group(1))

            letters = match.group(1).replace(", ", "")
            if match.group(2):
                letters = letters + match.group(2)
            
            return list(letters)

        self.input_text = pattern_input_string.search(state_string).group(1)
        self.contains_chars = get_letter_constraint(pattern_contains, state_string)
        self.not_contain_chars =  get_letter_constraint(pattern_not_contain, state_string)

        self.answer_len = int(pattern_answer_length.search(state_string).group(1))

        self.is_palindrome_answer = "forms a palindrome" in state_string

        potential_extra_constraints = [
            " - has 2 consecutive consonants\n",
            " - does not have 2 consecutive consonants\n",
            " - has 2 consecutive vowels\n",
            " - does not have 2 consecutive vowels\n",
            " - has more vowels than consonants\n",
            " - has less vowels than consonants\n",
            " - has the same amount of vowels and consonants\n"]

        for c in potential_extra_constraints:
            if c in state_string:
                self.extra_artificial_constraints.append(c)

        self.extra_artificial_constraints.sort()


    def _validate(self, answer: str) -> (bool, str):
        answer = answer.strip().lower()
        if self.answer_len != len(answer):
            val_msg = f"{answer} is not {self.answer_len} characters long."
            return False, val_msg

        if answer not in self.input_text:
            val_msg = f"{answer} does not exist in {self.input_text}."
            return False, val_msg

        s = answer
        if " - has 2 consecutive consonants\n" in self.extra_artificial_constraints:
            if not (any(s[i].lower() not in 'aeiou' and s[i+1].lower() not in 'aeiou' for i in range(len(s)-1))):
                val_msg = f"{answer} does not have 2 consecutive consonants"
                return False, val_msg

        if " - does not have 2 consecutive consonants\n" in self.extra_artificial_constraints:
            if (any(s[i].lower() not in 'aeiou' and s[i+1].lower() not in 'aeiou' for i in range(len(s)-1))):
                val_msg = f"{answer} has 2 consecutive consonants"
                return False, val_msg

        if " - has 2 consecutive vowels\n" in self.extra_artificial_constraints:
            if not(any(s[i].lower() in 'aeiou' and s[i+1].lower() in 'aeiou' for i in range(len(s)-1))):
                val_msg = f"{answer} does not have 2 consecutive vowels"
                return False, val_msg

        if " - does not have 2 consecutive vowels\n" in self.extra_artificial_constraints:
            if (any(s[i].lower() in 'aeiou' and s[i+1].lower() in 'aeiou' for i in range(len(s)-1))):
                val_msg = f"{answer} has 2 consecutive vowels"
                return False, val_msg

        if " - has more vowels than consonants\n" in self.extra_artificial_constraints:
            if not(sum(1 for char in s.lower() if char in 'aeiou') > sum(1 for char in s.lower() if char.isalpha() and char not in 'aeiou')):
                val_msg = f"{answer} has less or equal vowels than consonants"
                return False, val_msg

        if " - has less vowels than consonants\n" in self.extra_artificial_constraints:
            if not(sum(1 for char in s.lower() if char in 'aeiou') < sum(1 for char in s.lower() if char.isalpha() and char not in 'aeiou')):
                val_msg = f"{answer} has more or equal vowels than consonants"
                return False, val_msg

        if " - has the same amount of vowels and consonants\n" in self.extra_artificial_constraints:
            if not(sum(1 for char in s.lower() if char in 'aeiou') == sum(1 for char in s.lower() if char.isalpha() and char not in 'aeiou')):
                val_msg = f"{answer} does not have the same amount of vowels and consonants"
                return False, val_msg

        for c in self.contains_chars:
            if c not in answer:
                val_msg = f"{c} does not appear in {answer}."
                return False, val_msg

        for c in self.not_contain_chars:
            if c in answer:
                val_msg = f"{c} exists in {answer}."
                return False, val_msg

        if self.is_palindrome_answer and answer != answer[::-1]:
            val_msg = f"{answer} is not a palindrome."
            return False, val_msg

        return True, ""



    def replace_substring_with_validity_update(self, original_string, new_substring, valid):
        """
        Randomly replaces a substring of the same length as 'new_substring' in 'original_string', considering
        a 'valid' list that indicates which positions can be modified. Updates the 'valid' list to mark
        replaced positions as invalid.

        Parameters:
        original_string (str): The string to modify.
        new_substring (str): The substring to replace with, dictating the length of the chunk to be replaced.
        valid (list[bool]): List indicating if each position in the original string can be modified.

        Returns:
        tuple: A tuple containing the modified string and the updated 'valid' list.
        """
        n = len(new_substring)
        if len(original_string) != len(valid):
            raise ValueError("Length of 'valid' list must match the length of 'original_string'")

        # Find all possible starting indices where a replacement of length n can be made
        possible_starts = []
        for start_index in range(len(original_string) - n + 1):
            if all(valid[start_index:start_index + n]):
                possible_starts.append(start_index)

        if not possible_starts:
            return original_string, valid  # No valid replacement possible, return original string and unchanged valid list

        # Select a random valid starting index
        start_index = random.choice(possible_starts)

        # Construct the new string with the replacement
        modified_string = original_string[:start_index] + new_substring + original_string[start_index + n:]

        # Update the valid list
        updated_valid = valid[:]
        for i in range(start_index, start_index + n):
            updated_valid[i] = False

        return modified_string, updated_valid


    # Helper: create incorrect answer that's quite similar to the correct answer!
    def create_incorrect_answer(self):
        fake_answer = []

        neutral_char = set(string.ascii_lowercase) - set(self.contains_chars) - set(self.not_contain_chars)
        neutral_char = list(neutral_char)

        random.shuffle(self.contains_chars)

        for c in self.contains_chars:
            fake_answer.append(c)
        if len(self.contains_chars) > 1 and random.randint(1, 10) % 2 == 1:
            fake_answer[0] = random.choice(neutral_char)
        else:
            fake_answer = [random.choice(self.not_contain_chars)] + fake_answer

        while len(fake_answer) < self.answer_len:
            fake_answer.append(random.choice(neutral_char))

        if self.is_palindrome_answer:
            fake_answer = fake_answer[:(self.answer_len + 1)// 2]
            random.shuffle(fake_answer)
            fake_answer = fake_answer[:self.answer_len// 2] + fake_answer[::-1]
        else:
            fake_answer = fake_answer[:self.answer_len]
            random.shuffle(fake_answer)

        return "".join(fake_answer)

    def _generate_new_game(self, difficulty=3):
        dictionary = []

        self.difficulty = difficulty
        
        with open("textgames/assets/kb/word_list.txt", 'r') as file:
            for line in file:
                line = line.strip()
                if len(line) <= 8:
                    dictionary.append(line)

        # generate the input text. To make it (kinda) readable, we use a combination of random strings
        self.input_text = "".join([random.choice(dictionary) for _ in range(10)])

        # randomly get the answer from a subset of the input text
        if difficulty == 1:
            self.answer_len = random.randint(3, 3)
            self.input_text = self.input_text[:15]
        elif difficulty == 2:
            self.answer_len = random.randint(4, 5)
            self.input_text = self.input_text[:30]
        else:
            self.answer_len = random.randint(5, 7)
            self.input_text = self.input_text[:60]
            
        answer_start = random.randint(0, len(self.input_text) - self.answer_len)
        self.answer = self.input_text[answer_start: answer_start + self.answer_len]

        if difficulty == 3 and random.randint(1, 100) % 2 == 1:
            self.is_palindrome_answer = True
        else:
            self.is_palindrome_answer = False

        # make sure the answer is palindrome
        if (self.is_palindrome_answer):
            make_palindrome = lambda s: s[:(len(s) + 1) // 2] + s[:len(s) // 2][::-1]
            self.answer = make_palindrome(self.answer)
            self.input_text = self.input_text[: answer_start] + self.answer + self.input_text[answer_start + self.answer_len:]

        # find random character as a constraint, for both appearing and not appearing one
        char_in_answers = list(set(self.answer))

        self.contains_chars = random.sample(char_in_answers, random.randint(1, min(difficulty, len(char_in_answers))))

        not_contain_chars_options = list(set(self.input_text) - set(self.answer))
        self.not_contain_chars = random.sample(not_contain_chars_options, random.randint(1, min(1 + difficulty, len(not_contain_chars_options))))

        # set a flag to set which part of the string is editable (Valid = true)
        # initially, all string is editable except for the answer, to ensure that the answer is still there 
        valid = [True] * len(self.input_text)
        valid = valid[:answer_start] + [False] * self.answer_len + valid[answer_start + self.answer_len:]
        # we will randomly insert fake answer on the text. But we only 
        for _ in range(1 + difficulty):
            self.input_text, valid = self.replace_substring_with_validity_update(self.input_text, self.create_incorrect_answer(), valid)

        # If difficulty is 3, we will remove 'accidental' answer that's not in the original location
        if difficulty == 3:
            for i in range(len(self.input_text) - self.answer_len):
                # original answer, can't change and no need to check
                if i >= answer_start and i < answer_start + self.answer_len:
                    continue
                is_valid, _ = self._validate(self.input_text[i: i + self.answer_len])
                if is_valid:
                    # print("Accident", self.input_text[i: i + self.answer_len])
                    self.input_text = self.input_text[:i] + random.choice(self.not_contain_chars) + self.input_text[i + 1:]

            # create artificial constraints
            self._generate_artificial_constraints()

    def _generate_artificial_constraints(self):
        # artificial constriants: constraint that does not change anything since it's been there already anyway
        artificial_constraints = []
        s = self.answer
        if any(s[i].lower() not in 'aeiou' and s[i+1].lower() not in 'aeiou' for i in range(len(s)-1)):
            artificial_constraints.append(" - has 2 consecutive consonants\n")
        else:
            artificial_constraints.append(" - does not have 2 consecutive consonants\n")
        if any(s[i].lower() in 'aeiou' and s[i+1].lower() in 'aeiou' for i in range(len(s)-1)):
            artificial_constraints.append(" - has 2 consecutive vowels\n")
        else:
            artificial_constraints.append(" - does not have 2 consecutive vowels\n")
        if sum(1 for char in s.lower() if char in 'aeiou') > sum(1 for char in s.lower() if char.isalpha() and char not in 'aeiou'):
            artificial_constraints.append(" - has more vowels than consonants\n")
        if sum(1 for char in s.lower() if char in 'aeiou') < sum(1 for char in s.lower() if char.isalpha() and char not in 'aeiou'):
            artificial_constraints.append(" - has less vowels than consonants\n")
        if sum(1 for char in s.lower() if char in 'aeiou') == sum(1 for char in s.lower() if char.isalpha() and char not in 'aeiou'):
            artificial_constraints.append(" - has the same amount of vowels and consonants\n")
        
        if self.is_palindrome_answer:
            self.extra_artificial_constraints = random.sample(artificial_constraints, random.randint(1, 2))
        else:
            self.extra_artificial_constraints = random.sample(artificial_constraints, 1)

        self.extra_artificial_constraints.sort()

    def _get_prompt(self):
        def print_chars(X):
            return ", ".join(X[:-1]) + " and " + X[-1] if len(X) > 1 else X[0]

        extra_constraints = ""
        # len(self.input_text) > 50 is to indirectly check the difficulty == 3
        if len(self.input_text) > 50 and self.is_palindrome_answer:
            extra_constraints = " - forms a palindrome\n"
        extra_constraints = extra_constraints + ''.join(self.extra_artificial_constraints)

        prompt = f"""You are given the following string:
{self.input_text}

Find a substring of exactly {self.answer_len} characters long that:
 - Contains {print_chars(self.contains_chars)}
 - Does not contain {print_chars(self.not_contain_chars)}
{extra_constraints}
Print only the answer.
"""
        return prompt