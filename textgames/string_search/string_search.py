import re
import numpy as np
import random
import math
import string
from textgames.base_game import BaseGame
from collections import defaultdict

class StringSearch(BaseGame):
    def __init__(self):
        pass

    def validate(self, answer: str) -> bool:
        answer = answer.strip().lower()
        if len(self.answer) != len(answer):
            print(f"{answer} is not {len(self.answer)} characters long.")
            return False

        if answer not in self.input_text:
            print(f"{answer} does not exist in {self.input_text}.")
            return False

        for c in self.contains_chars:
            if c not in answer:
                print(f"{c} does not appear in {answer}.")
                return False

        for c in self.not_contain_chars:
            if c in answer:
                print(f"{c} exists in {answer}.")
                return False

        if self.is_palindrome_answer and answer != answer[::-1]:
            print(f"{answer} is not a palindrome.")
            return False


        return True



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

        while len(fake_answer) < len(self.answer):
            fake_answer.append(random.choice(neutral_char))

        if self.is_palindrome_answer:
            fake_answer = fake_answer[:(len(self.answer) + 1)// 2]
            random.shuffle(fake_answer)
            fake_answer = fake_answer[:len(self.answer)// 2] + fake_answer[::-1]
        else:
            fake_answer = fake_answer[:len(self.answer)]
            random.shuffle(fake_answer)

        return "".join(fake_answer)

    def generate_new_game(self, difficulty=3):
        self.dictionary_by_len = [[] for _ in range(9)]
        self.dictionary = []
        
        with open("textgames/assets/kb/word_list.txt", 'r') as file:
            for line in file:
                line = line.strip()
                if len(line) <= 8:
                    self.dictionary_by_len[len(line)].append(line)
                    self.dictionary.append(line)

        # generate the input text. To make it (kinda) readable, we use a combination of random strings
        self.input_text = "".join([random.choice(self.dictionary) for _ in range(10)])

        # randomly get the answer from a subset of the input text
        if difficulty == 1:
            answer_len = random.randint(3, 3)
            self.input_text = self.input_text[:10]
        elif difficulty == 2:
            answer_len = random.randint(4, 4)
            self.input_text = self.input_text[:20]
        else:
            answer_len = random.randint(5, 6)
            self.input_text = self.input_text[:35]
            
        answer_start = random.randint(0, len(self.input_text) - answer_len)
        self.answer = self.input_text[answer_start: answer_start + answer_len]

        if difficulty == 3 and random.randint(1, 100) % 2 == 1:
            self.is_palindrome_answer = True
        else:
            self.is_palindrome_answer = False

        if (self.is_palindrome_answer):
            make_palindrome = lambda s: s[:(len(s) + 1) // 2] + s[:len(s) // 2][::-1]
            self.answer = make_palindrome(self.answer)
            self.input_text = self.input_text[: answer_start] + self.answer + self.input_text[answer_start + answer_len:]

        # find random character as a constraint, for both appearing and not appearing one
        char_in_answers = list(set(self.answer))

        self.contains_chars = random.sample(char_in_answers, random.randint(1, min(difficulty, len(char_in_answers))))

        not_contain_chars_options = list(set(self.input_text) - set(self.answer))
        self.not_contain_chars = random.sample(not_contain_chars_options, random.randint(1, min(1 + difficulty, len(not_contain_chars_options))))

        
        valid = [True] * len(self.input_text)
        valid = valid[:answer_start] + [False] * len(self.answer) + valid[answer_start + answer_len:]

        for _ in range(difficulty):
            self.input_text, valid = self.replace_substring_with_validity_update(self.input_text, self.create_incorrect_answer(), valid)


    def get_prompt(self):
        def print_chars(X):
            return ", ".join(X[:-1]) + " and " + X[-1] if len(X) > 1 else X[0]

        if self.is_palindrome_answer:
            extra_constraints = " - forms a palindrome\n"
        else:
            extra_constraints = ""

        
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
        
        if extra_constraints == "":
            extra_constraints = extra_constraints + ''.join(random.sample(artificial_constraints, random.randint(1, 2)))
        else:
            extra_constraints = extra_constraints + ''.join(random.sample(artificial_constraints, 1))

        prompt = f"""You are given the following string:
{self.input_text}

Find a substring of exactly {len(self.answer)} characters long that:
 - Contains {print_chars(self.contains_chars)}
 - Does not contain {print_chars(self.not_contain_chars)}
{extra_constraints}
Print only the answer.
"""
        return prompt