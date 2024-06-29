import random
from pathlib import Path
from textgames.password_game.rules import *
from textgames.game import BaseGame

class PasswordGame(BaseGame):
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

    def __init__(self, rules_args=None):
        self.num_rules = None
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

        with open(str(Path(__file__).absolute()).replace("password_game.py","") + "/kb/word_list.txt") as f:
            for line in f:
                self.WORD_LIST.append(line.replace("\n", ""))

        with open(str(Path(__file__).absolute()).replace("password_game.py","") + "/kb/country_capital_city.tsv") as f:
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

    def generate_new_game(self, num_rules=1):
        self.rules = []
        self.rules_ids = []
        self.num_rules = num_rules

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