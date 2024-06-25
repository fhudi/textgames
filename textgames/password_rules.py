# \item Rule 1 (easy): X number of characters
# \item Rule 2 (easy): X number of uppercase characters
# \item Rule 3 (easy): X number of lowercase characters
# \item Rule 4 (easy): X number of specific characters
# \item Rule 5 (easy): X number of latin alpha
# \item Rule 6 (easy): X number of digits
# \item Rule 7 (easy): X number of special characters (!, @, #, $, %, ^, &, *)
# \item Rule 8 (easy): X number of roman numbers
# \item Rule 9 (easy): must consist a string ""

# requires knowledge
# \item Rule 10 (hard): has the name of capital city of ...
# \item Rule 11 (hard): has the name of continent of ...

# requires reasoning
# \item Rule 12 (hard): sum of all number digits equal to ...


# \item Rule 11 (hard): sum of all roman numbers equal to ...
# \item Rule 12 (hard): the number of capital letters should be less than ...

import random
from sympy.parsing.sympy_parser import parse_expr
from enum import Enum

class RuleType(Enum):
    NONREPEATABLE = 1 # non repeatable
    REPEATABLE = 2 # repeatable with different values

class Rule():
    def __init__(self, args):
        pass

    def generate_rule(self, args):
        pass

    def validate(self, input):
        pass

    def generate_prompt(self):
        pass


# Rule 1
class CountNumCharRule(Rule):
    def __init__(self, args):
        self.num_char = args["num_char"]

    def generate_rule(self, args):
        num_char = random.randint(args["min_num_char"], args["max_num_char"])
        return {"num_char": num_char}
    
    def validate(self, input):
        return len(input.strip()) == self.num_char
    
    def generate_prompt(self):
        return f"the text has only {self.num_char} characters"
    

# Rule 2
class CountNumUppercaseCharRule(Rule):
    def __init__(self, args):
        self.num_char = args["num_char"]

    def generate_rule(self, args):
        num_char = random.randint(args["min_num_char"], args["max_num_char"])
        return {"num_char": num_char}
    
    def validate(self, input):
        count = 0
        for c in input:
            if "A" <= c <= "Z":
                count += 1
        return count == self.num_char
    
    def generate_prompt(self):
        return f"the text has {self.num_char} uppercase characters"


# Rule 3
class CountNumLowercaseCharRule(Rule):
    def __init__(self, args):
        self.num_char = args["num_char"]

    def generate_rule(self, args):
        num_char = random.randint(args["min_num_char"], args["max_num_char"])
        return {"num_char": num_char}
    
    def validate(self, input):
        count = 0
        for c in input:
            if "a" <= c <= "z":
                count += 1
        return count == self.num_char

    def generate_prompt(self):
        return f"the text has {self.num_char} lowercase characters"


# Rule 4
class CountNumSpecificCharRule(Rule):
    def __init__(self, args):
        self.char = args["char"]
        self.num_char = args["num_char"]

    def generate_rule(self, args):
        char_ord = random.randint(0, 25)
        is_upper = random.randint(0, 1)
        if is_upper:
            char = chr(ord("A") + char_ord)
        else:
            char = chr(ord("a") + char_ord)
        num_char = random.randint(args["min_num_char"], args["max_num_char"])
        return {"num_char": num_char, "char": char}
    
    def validate(self, input):
        counts = 0
        for c in input:
            if c == self.char:
                counts += 1
        return counts == self.num_char
    
    def generate_prompt(self):
        return f"the text has {self.num_char} '{self.char}' character"


# Rule 5
class CountNumLatinAlphaRule(Rule):
    def __init__(self, args):
        self.num_char = args["num_char"]

    def generate_rule(self, args):
        num_char = random.randint(args["min_num_char"], args["max_num_char"])
        return {"num_char": num_char}
    
    def validate(self, input):
        counts = 0
        for c in input:
            if "a" <= c <= "z" or "A" <= c <= "Z":
                counts += 1
        return counts == self.num_char
    
    def generate_prompt(self):
        return f"the text has {self.num_char} latin character"


# Rule 6
class CountNumDigitRule(Rule):
    def __init__(self, args):
        self.num_char = args["num_char"]

    def generate_rule(self, args):
        num_char = random.randint(args["min_num_char"], args["max_num_char"])
        return {"num_char": num_char}
    
    def validate(self, input):
        counts = 0
        for c in input:
            if "0" <= c <= "9":
                counts += 1
        return counts == self.num_char
    
    def generate_prompt(self):
        return f"the text has {self.num_char} number digits"


# Rule 7
class CountNumSpecialCharRule(Rule):
    def __init__(self, args):
        self.num_char = args["num_char"]

    def generate_rule(self, args):
        num_char = random.randint(args["min_num_char"], args["max_num_char"])
        return {"num_char": num_char}
    
    def validate(self, input):
        counts = 0
        for c in input:
            if c in ["!", "@", "#", "$", "%", "^", "&", "*"]:
                counts += 1
        return counts == self.num_char
    
    def generate_prompt(self):
        return f"the text has {self.num_char} special characters, including '!', '@', '#', '$', '%', '^', '&', '*'"


# Rule 8
class CountNumRomansDigitRule(Rule):
    def __init__(self, args):
        self.num_char = args["num_char"]
        self.ROMANS_CHARS = ["I", "V", "X", "L", "C", "D"]

    def generate_rule(self, args):
        num_char = random.randint(args["min_num_char"], args["max_num_char"])
        return {"num_char": num_char}
    
    def validate(self, input):
        counts = {}
        for roman_char in self.ROMANS_CHARS:
            counts[roman_char] = 0
        for c in input:
            if c in counts:
                counts[c] += 1
        
        num_roman_char = 0
        for roman_char in self.ROMANS_CHARS:
            num_roman_char += counts[roman_char]
        return num_roman_char == self.num_char
    
    def generate_prompt(self):
        return f"the text has {self.num_char} number of roman digits"


# Rule 9
class ConsistStrRule(Rule):
    def __init__(self, args):
        self.str = args["str"]
        self.words = args["words"]

    def generate_rule(self, args):
        # randomly create value
        value = self.words[random.randint(0, len(self.words)-1)]
        return {"str": value}
    
    def validate(self, input):
        return self.str in input
    
    def generate_prompt(self):
        return f"the text has {self.str} string"
    

# Rule 10
class ConsistCapitalOfRule(Rule):
    def __init__(self, args):
        self.str = args["str"]
        self.words = args["words"]
        self.country_to_capital_map = args["country_to_capital_map"]

    def generate_rule(self, args):
        # randomly create value
        value = self.words[random.randint(0, len(self.words)-1)]
        return {"str": value}
    
    def validate(self, input):
        return self.country_to_capital_map[self.str].lower() in input.lower()

    def generate_prompt(self):
        return f"the text has the capital city of {self.str}"
    

# Rule 11
class ConsistContinentOfRule(Rule):
    def __init__(self, args):
        self.str = args["str"]
        self.words = args["words"]
        self.country_to_continent_map = args["country_to_continent_map"]

    def generate_rule(self, args):
        # randomly create value
        value = self.words[random.randint(0, len(self.words)-1)]
        return {"str": value}
    
    def validate(self, input):
        return self.country_to_continent_map[self.str].lower() in input.lower()
    
    def generate_prompt(self):
        return f"the text has the continent of {self.str}"
    

# Rule 12
class ConsistSynonymOfRule(Rule):
    def __init__(self, args):
        self.str = args["str"]
        self.words = args["words"]
        self.country_to_continent_map = args["word_to_synonym_map"]

    def generate_rule(self, args):
        # randomly create value
        value = self.words[random.randint(0, len(self.words)-1)]
        return {"str": value}
    
    def validate(self, input):
        return self.country_to_continent_map[self.str].lower() in input.lower()
    
    def generate_prompt(self):
        return f"the text has the synonym of {self.str}"


# Rule 13
class ConsistAntonymOfRule(Rule):
    def __init__(self, args):
        self.str = args["str"]
        self.words = args["words"]
        self.country_to_continent_map = args["word_to_antonym_map"]

    def generate_rule(self, args):
        # randomly create value
        value = self.words[random.randint(0, len(self.words)-1)]
        return {"str": value}
    
    def validate(self, input):
        return self.country_to_continent_map[self.str].lower() in input.lower()
    
    def generate_prompt(self):
        return f"the text has the antonym of {self.str}"


# Rule 14
class ArithmeticSumAllDigitsRule(Rule):
    def __init__(self, args):
        self.num = args["num"]

    def generate_rule(self, args):
        # randomly create value
        value = random.randint(0, 10)
        return {"value": value}

    def validate(self, args):
        value = 0
        s = args["str"]
        for c in s:
            if "0" <= c <= "9":
                value += int(c)
        return self.num == value
    

# Rule 15
class ArithmeticConsistExpressionRule(Rule):
    def __init__(self, args):
        self.num = args["num"]
        self.num_operator = args["num_operator"]

    def generate_rule(self, args):
        # randomly create value
        operators = ["+", '-', "/", "*"]
        num_operator = random.randint(1, self.num_operator)
        operation = ""
        for i in range(num_operator):
            if i == 0:
                operation = str(random.randint(0, 9))
            next_num = random.randint(0, 9)
            operation += " " + operators[random.randint(0,3)] + " " + next_num
        
        value = parse_expr(operation)
        return {"value": value, "operation": operation}

    def validate(self, args):
        return str(self.num) in args["str"]


COUNT_RULES = {
    "count_num_char": [CountNumCharRule, RuleType.NONREPEATABLE],
    "count_num_upper_char": [CountNumUppercaseCharRule, RuleType.NONREPEATABLE],
    "count_num_lower_char": [CountNumLowercaseCharRule, RuleType.NONREPEATABLE],
    "count_num_specific_char": [CountNumSpecificCharRule, RuleType.REPEATABLE],
    "count_num_latin_alpha": [CountNumLatinAlphaRule, RuleType.NONREPEATABLE],
    "count_num_digit": [CountNumDigitRule, RuleType.NONREPEATABLE],
    "count_num_special_char": [CountNumSpecialCharRule, RuleType.NONREPEATABLE],
    "count_num_romans_digit": [CountNumRomansDigitRule, RuleType.NONREPEATABLE],
}

STRING_RULES = {
    "consist_str": [ConsistStrRule, RuleType.REPEATABLE],
}

KNOWLEDGE_RULES = {
    "consist_capital_of": [ConsistCapitalOfRule, RuleType.REPEATABLE],
    "consist_continent_of": [ConsistContinentOfRule, RuleType.REPEATABLE],
    "consist_synonym_of": [ConsistSynonymOfRule, RuleType.REPEATABLE],
    "consist_antonym_of": [ConsistAntonymOfRule, RuleType.REPEATABLE],
}

ARITHMETIC_RULES = {
    "arithmetic_sum_all_digits": [ArithmeticSumAllDigitsRule, RuleType.NONREPEATABLE],
    "arithmetic_consist_expression": [ArithmeticConsistExpressionRule, RuleType.REPEATABLE],
    # complicated rule, 2^2, some other formula
}

def generate_rules():
    pass