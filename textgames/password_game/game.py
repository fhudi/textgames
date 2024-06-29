import random
from enum import Enum
from pathlib import Path
from sympy.parsing.sympy_parser import parse_expr

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
        self.num_char = random.randint(args["min_num_char"], args["max_num_char"])
    
    def validate(self, input):
        return len(input.strip()) == self.num_char
    
    def generate_prompt(self):
        return f"the text has only {self.num_char} characters"
    

# Rule 2
class CountNumUppercaseCharRule(Rule):
    def __init__(self, args):
        self.num_char = random.randint(args["min_num_char"], args["max_num_char"])
    
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
        self.num_char = random.randint(args["min_num_char"], args["max_num_char"])
    
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
        self.num_char = random.randint(args["min_num_char"], args["max_num_char"])

        char_ord = random.randint(0, 25)
        is_upper = random.randint(0, 1)
        if is_upper:
            self.char = chr(ord("A") + char_ord)
        else:
            self.char = chr(ord("a") + char_ord)
    
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
        self.num_char = random.randint(args["min_num_char"], args["max_num_char"])
    
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
        self.num_char = random.randint(args["min_num_char"], args["max_num_char"])
    
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
        self.num_char = random.randint(args["min_num_char"], args["max_num_char"])
    
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
        self.num_char = random.randint(args["min_num_char"], args["max_num_char"])
        self.ROMANS_CHARS = ["I", "V", "X", "L", "C", "D"]
    
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
        self.words = args["words"]
        self.str = self.words[random.randint(0, len(self.words)-1)]
    
    def validate(self, input):
        return self.str in input
    
    def generate_prompt(self):
        return f"the text has '{self.str}' string"
    

# Rule 10
class ConsistCapitalOfRule(Rule):
    def __init__(self, args):
        self.words = args["words"]
        self.str = self.words[random.randint(0, len(self.words)-1)]
        self.country_to_capital_map = args["country_to_capital_map"]
    
    def validate(self, input):
        return self.country_to_capital_map[self.str.lower()].lower() in input.lower()

    def generate_prompt(self):
        return f"the text has the capital city of {self.str}"
    

# Rule 11
class ConsistContinentOfRule(Rule):
    def __init__(self, args):
        self.words = args["words"]
        self.str = self.words[random.randint(0, len(self.words)-1)]
        self.country_to_continent_map = args["country_to_continent_map"]
    
    def validate(self, input):
        return self.country_to_continent_map[self.str.lower()].lower() in input.lower()
    
    def generate_prompt(self):
        return f"the text has the continent of {self.str}"
    

# Rule 12
class ConsistSynonymOfRule(Rule):
    def __init__(self, args):
        self.words = args["words"]
        self.str = self.words[random.randint(0, len(self.words)-1)]
        self.country_to_continent_map = args["word_to_synonym_map"]
    
    def validate(self, input):
        return self.country_to_continent_map[self.str].lower() in input.lower()
    
    def generate_prompt(self):
        return f"the text has the synonym of {self.str}"


# Rule 13
class ConsistAntonymOfRule(Rule):
    def __init__(self, args):
        self.words = args["words"]
        self.str = self.words[random.randint(0, len(self.words)-1)]
        self.country_to_continent_map = args["word_to_antonym_map"]
    
    def validate(self, input):
        return self.country_to_continent_map[self.str].lower() in input.lower()
    
    def generate_prompt(self):
        return f"the text has the antonym of {self.str}"


# Rule 14
class ArithmeticSumAllDigitsRule(Rule):
    def __init__(self, args):
        self.num = random.randint(0, 10)

    def validate(self, input):
        value = 0
        s = input
        for c in s:
            if "0" <= c <= "9":
                value += int(c)
        return self.num == value
    
    def generate_prompt(self):
        return "the text has the sum of all numeral digits"
    

# Rule 15
class ArithmeticMathExpressionRule(Rule):
    def __init__(self, args):
        self.operators = ["+", '-', "/", "*"]

        self.max_num_operator = args["max_num_operator"]
        num_operator = random.randint(1, self.max_num_operator)
        expression = ""

        value = None

        while value is None or int(value) != value:
            for i in range(num_operator):
                if i == 0:
                    expression = str(random.randint(0, 9))
                next_num = random.randint(0, 9)
                next_operator = self.operators[random.randint(0,len(self.operators)-1)]
                expression += " " + next_operator + " " + next_num

                if next_operator == "/" and next_num == 0:
                    restart = True

            if restart:
                continue

            value = parse_expr(expression)

        self.expression = expression
        self.num = value

    def validate(self, input):
        return str(self.num) in input
    
    def generate_prompt(self):
        return f"the text has a number that equals to {self.expression}"
    

# Rule 16
class ArithmeticMathWordExpressionRule(Rule):
    def __init__(self, args):
        self.num_to_word = {
            0:"zero", 1:"one", 2:"two", 3:"three", 4:"four", 5:"five",
            6:"six", 7:"seven", 8:"eight", 9:"nine"
        }
        self.operators_words = ["plus", 'minus', "divided by", "multiply by"]
        self.operators = ["+", '-', "/", "*"]

        self.max_num_operator = args["max_num_operator"]
        num_operator = random.randint(1, self.max_num_operator)

        expression = ""
        word_expression = ""
        value = None

        while value is None or int(value) != value:
            restart = False
            for i in range(num_operator):
                if i == 0:
                    num = random.randint(0, 9)
                    word_expression = self.num_to_word[num]
                    expression = str(num)
                    
                next_num = random.randint(0, 9)
                next_num_word = self.num_to_word[next_num]

                next_operator_id = random.randint(0,len(self.operators_words)-1)
                next_operator_word = self.operators_words[next_operator_id]
                next_operator = self.operators[next_operator_id]

                expression += " " + next_operator + " " + str(next_num)
                word_expression += " " + next_operator_word + " " + next_num_word

                if next_operator == "/" and next_num == 0:
                    restart = True
                    
            if restart:
                continue
            
            value = parse_expr(expression)
        self.expression = expression
        self.num = value

    def validate(self, input):
        return str(self.num) in input
    
    def generate_prompt(self):
        return f"the text has a number that equals to {self.expression}"

class PasswordGame():
    RULES = {
        "count_num_char": [CountNumCharRule, RuleType.NONREPEATABLE],
        "count_num_upper_char": [CountNumUppercaseCharRule, RuleType.NONREPEATABLE],
        "count_num_lower_char": [CountNumLowercaseCharRule, RuleType.NONREPEATABLE],
        "count_num_specific_char": [CountNumSpecificCharRule, RuleType.REPEATABLE],
        "count_num_latin_alpha": [CountNumLatinAlphaRule, RuleType.NONREPEATABLE],
        "count_num_digit": [CountNumDigitRule, RuleType.NONREPEATABLE],
        "count_num_special_char": [CountNumSpecialCharRule, RuleType.NONREPEATABLE],
        "count_num_romans_digit": [CountNumRomansDigitRule, RuleType.NONREPEATABLE],
        "consist_str": [ConsistStrRule, RuleType.REPEATABLE],
        "consist_capital_of": [ConsistCapitalOfRule, RuleType.REPEATABLE],
        "consist_continent_of": [ConsistContinentOfRule, RuleType.REPEATABLE],
        # "consist_synonym_of": [ConsistSynonymOfRule, RuleType.REPEATABLE],
        # "consist_antonym_of": [ConsistAntonymOfRule, RuleType.REPEATABLE],
        "arithmetic_sum_all_digits": [ArithmeticSumAllDigitsRule, RuleType.NONREPEATABLE],
        "arithmetic_consist_math_expression": [ArithmeticMathExpressionRule, RuleType.REPEATABLE],
        "arithmetic_consist_math_expression": [ArithmeticMathWordExpressionRule, RuleType.REPEATABLE],
    }

    def __init__(self, num_rules=1, rules_args=None):
        self.num_rules = num_rules
        self.rules_ids = []
        self.rules = []

        self.WORD_LIST = []
        self.COUNTRY_LIST = []
        # SYNONYM_WORD_LIST = []
        # ANTONYM_WORD_LIST = []

        self.COUNTRY_TO_CAPITAL_MAP = {}
        self.COUNTRY_TO_CONTINENT_MAP = {}
        # WORD_TO_SYNONYM_MAP = {}
        # WORD_TO_ANTONYM_MAP = {}

        with open(str(Path(__file__).absolute()).replace("game.py","") + "/kb/word_list.txt") as f:
            for line in f:
                self.WORD_LIST.append(line.replace("\n", ""))

        with open(str(Path(__file__).absolute()).replace("game.py","") + "/kb/country_capital_city.tsv") as f:
            count = 0
            for line in f:
                count += 1
                if count == 1:
                    continue
                country, capital_city, continent = line.replace("\n", "").split("\t")
                if len(continent.split(" ")) > 1:
                    continue
                if len(capital_city.split(" ")) > 1:
                    continue
                self.COUNTRY_TO_CAPITAL_MAP[country.lower()] = capital_city.lower()
                self.COUNTRY_TO_CONTINENT_MAP[country.lower()] = continent.lower()
                self.COUNTRY_LIST.append(country)

        # print(COUNTRY_TO_CAPITAL_MAP)
        # print(COUNTRY_TO_CONTINENT_MAP)

        if rules_args is not None:
            self.rules_args = rules_args
        else:
            self.rules_args = {
                "count_num_char": {
                    "min_num_char": 10, "max_num_char": 20
                },
                "count_num_upper_char": {
                    "min_num_char": 2, "max_num_char": 5
                },
                "count_num_lower_char": {
                    "min_num_char": 2, "max_num_char": 5
                },
                "count_num_specific_char": {
                    "min_num_char": 2, "max_num_char": 5
                },
                "count_num_latin_alpha": {
                    "min_num_char": 5, "max_num_char": 10
                },
                "count_num_digit": {
                    "min_num_char": 2, "max_num_char": 5
                },
                "count_num_special_char": {
                    "min_num_char": 2, "max_num_char": 5
                },
                "count_num_romans_digit": {
                    "min_num_char": 2, "max_num_char": 5
                },
                "consist_str": {
                    "words": self.WORD_LIST   
                },
                "consist_capital_of": {
                    "words": self.COUNTRY_LIST,
                    "country_to_capital_map": self.COUNTRY_TO_CAPITAL_MAP
                },
                "consist_continent_of": {
                    "words": self.COUNTRY_LIST,
                    "country_to_continent_map": self.COUNTRY_TO_CONTINENT_MAP
                },
                # "consist_synonym_of": {
                #     "words": SYNONYM_WORD_LIST,
                #     "word_to_synonym_map": WORD_TO_SYNONYM_MAP
                # },
                # "consist_antonym_of": {
                #     "words": ANTONYM_WORD_LIST,
                #     "word_to_antonym_map": WORD_TO_ANTONYM_MAP
                # },
                "arithmetic_sum_all_digits": {},
                "arithmetic_consist_math_expression": {
                    "max_num_operator": 5
                },
                "arithmetic_consist_math_expression": {
                    "max_num_operator": 5
                }
            }

        self.rule_id_list = [key for key in PasswordGame.RULES]

    def validate(self):
        pass

    def generate_rule(self):
        self.rules = []
        self.rules_ids = []

        # rule = ConsistCapitalOfRule({"words": self.COUNTRY_LIST, "country_to_capital_map": self.COUNTRY_TO_CAPITAL_MAP})
        # rule.str = "indonesia"
        # print(">>>>>", rule.validate("jakarta"))

        while len(self.rules_ids) < self.num_rules:
            rule_num_id = random.randint(0, len(self.rule_id_list)-1)
            rule_id = self.rule_id_list[rule_num_id]
            if rule_id in self.rules_ids:
                if PasswordGame.RULES[rule_id][1] == RuleType.REPEATABLE:
                    self.rules_ids.append(rule_id)
                    self.rules.append(PasswordGame.RULES[rule_id][0](self.rules_args[rule_id]))
            else:
                self.rules_ids.append(rule_id)
                self.rules.append(PasswordGame.RULES[rule_id][0](self.rules_args[rule_id]))

    def get_prompt(self):
        prompt = "Please construct a text string with the following criteria and print only the string if there is such a string otherwise print None:\n"
        for rule in self.rules:
            prompt += "- " + rule.generate_prompt() + "\n"
        return prompt
    
    def validate(self, input):
        res = True
        for rule in self.rules:
            if not rule.validate(input):
                print(input, " is not satisfying this rule:", rule.generate_prompt())
                res = False
        return res