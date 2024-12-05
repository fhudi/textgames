import random
import re
from pathlib import Path
from textgames.password_game.rules import *
from textgames.base_game import BaseGame

"""
Please write a text string without any space by following a set of given rules. Please write only the answer and follow the following criteria:
- the text has 0 uppercase characters
- the text has 0 lowercase characters

Print only the answer.
"""

class PasswordGame(BaseGame):
    @staticmethod
    def get_game_name() -> str:
        return "🔑\tPassword Game"

    RULES = {
        "count_num_char": [CountNumCharRule, RuleType.NONREPEATABLE, 1],
        "count_num_upper_char": [CountNumUppercaseCharRule, RuleType.NONREPEATABLE, 3],
        "count_num_lower_char": [CountNumLowercaseCharRule, RuleType.NONREPEATABLE, 3],
        "count_num_specific_char": [CountNumSpecificCharRule, RuleType.REPEATABLE, 2],
        "count_num_english_alpha": [CountNumEnglishAlphaRule, RuleType.NONREPEATABLE, 4],
        "count_num_digit": [CountNumDigitRule, RuleType.NONREPEATABLE, 4],
        "count_num_special_char": [CountNumSpecialCharRule, RuleType.NONREPEATABLE, 4],
        "count_num_romans_digit": [CountNumRomansDigitRule, RuleType.NONREPEATABLE, 4],
        "consist_str": [ConsistStrRule, RuleType.REPEATABLE, 5],
        "consist_capital_of": [ConsistCapitalOfRule, RuleType.REPEATABLE, 5],
        "consist_continent_of": [ConsistContinentOfRule, RuleType.REPEATABLE, 5],
        # "consist_synonym_of": [ConsistSynonymOfRule, RuleType.REPEATABLE, 5],
        # "consist_antonym_of": [ConsistAntonymOfRule, RuleType.REPEATABLE, 5],
        # "arithmetic_sum_all_digits": [ArithmeticSumAllDigitsRule, RuleType.NONREPEATABLE, 2],
        "arithmetic_consist_math_expression": [ArithmeticMathExpressionRule, RuleType.REPEATABLE, 5],
        "arithmetic_consist_math_word_expression": [ArithmeticMathWordExpressionRule, RuleType.REPEATABLE, 5],
    }

    RULES_IDS = [
        rule for rule in RULES
    ]

    def __init__(self):
        super().__init__()
        self.exclude_states = ["possible_ans", "rules", "num_rules", "WORD_LIST", "MULTI_WORD_LIST", "multi_word",]

        self.num_rules = None
        self.rules_ids = []
        self.rules = []
        self.possible_ans = None

        self.WORD_LIST = []
        self.COUNTRY_LIST = []
        # SYNONYM_WORD_LIST = []
        # ANTONYM_WORD_LIST = []

        self.COUNTRY_TO_CAPITAL_MAP = {}
        self.COUNTRY_TO_CONTINENT_MAP = {}
        # WORD_TO_SYNONYM_MAP = {}
        # WORD_TO_ANTONYM_MAP = {}

        with open(str(Path(__file__).absolute()).replace("password_game/password_game.py","") + "/assets/kb/word_list.txt") as f:
            for line in f:
                self.WORD_LIST.append(line.replace("\n", ""))

        with open(str(Path(__file__).absolute()).replace("password_game/password_game.py","") + "/assets/kb/country_capital_city.tsv") as f:
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
                if continent == "":
                    continue
                if capital_city == "":
                    continue
                self.COUNTRY_TO_CAPITAL_MAP[country.lower()] = capital_city.lower()
                self.COUNTRY_TO_CONTINENT_MAP[country.lower()] = continent.lower()
                self.COUNTRY_LIST.append(country)

        # print(COUNTRY_TO_CAPITAL_MAP)
        # print(COUNTRY_TO_CONTINENT_MAP)

        self.rules_args = {
            "count_num_char": {},
            "count_num_upper_char": {},
            "count_num_lower_char": {
                "min_extra_num_char": 1, "max_extra_num_char": 5
            },
            "count_num_specific_char": {},
            "count_num_english_alpha": {
                "min_extra_num_char": 1, "max_extra_num_char": 5
            },
            "count_num_digit": {
                "min_extra_num_char": 1, "max_extra_num_char": 5
            },
            "count_num_special_char": {
                "min_extra_num_char": 1, "max_extra_num_char": 5
            },
            "count_num_romans_digit": {
                "min_extra_num_char": 1, "max_extra_num_char": 5
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
            # "arithmetic_sum_all_digits": {},
            "arithmetic_consist_math_expression": {
                "max_num_operator": 5
            },
            "arithmetic_consist_math_word_expression": {
                "max_num_operator": 5
            }
        }

        self.rule_id_list = [key for key in PasswordGame.RULES]

    def _generate_new_game(self, *args, **kwargs) -> None:
        self.rules = []
        self.rules_ids = []
        self.num_rules = kwargs["num_rules"]

        # rule = ConsistCapitalOfRule({"words": self.COUNTRY_LIST, "country_to_capital_map": self.COUNTRY_TO_CAPITAL_MAP})
        # rule.str = "indonesia"
        # print(">>>>>", rule.validate("jakarta"))

        while len(self.rules_ids) < self.num_rules:
            rule_num_id = random.randint(0, len(self.rule_id_list)-1)
            rule_id = self.rule_id_list[rule_num_id]
            if rule_id in self.rules_ids:
                if PasswordGame.RULES[rule_id][1] == RuleType.REPEATABLE:
                    self.rules_ids.append(rule_id)
                    self.rules.append([PasswordGame.RULES[rule_id][0], PasswordGame.RULES[rule_id][2], rule_id])
            else:
                self.rules_ids.append(rule_id)
                self.rules.append([PasswordGame.RULES[rule_id][0], PasswordGame.RULES[rule_id][2], rule_id])
        
        self.rules.sort(key=lambda l: l[1], reverse=True)
        self.rules = [rule[0](self.rules_args[rule[2]]) for rule in self.rules]

        output = ""
        for rule in self.rules:
            output = rule.generate_rule(output)
        self.possible_ans = output

    def _get_prompt(self) -> str:
        prompt = "Please write a text string without any space by following a set of given rules. Please write only the answer and follow the following criteria:\n"
        for rule in self.rules:
            prompt += "- " + rule.generate_prompt() + "\n"
        return prompt
    
    def _validate(self, answer: str) -> (bool, str):
        res = True
        val_msgs = []
        for rule in self.rules:
            if not rule.validate(answer):
                val_msgs.append(' '.join([answer, " is not satisfying this rule:", rule.generate_prompt()]))
                res = False
        return res, "\n".join(val_msgs)
    
    def _load_game(self, state_string):
        patterns = [re.compile(r"the text has only ([0-9]+) characters"), re.compile(r"the text has ([0-9]+) uppercase characters"), re.compile(r"the text has ([0-9]+) lowercase characters"), re.compile(r"the text has ([0-9]+ '[a-zA-Z]+') character"), re.compile(r"the text has ([0-9]+) english character"), re.compile(r"the text has ([0-9]+) number digits"), re.compile(r"the text has ([0-9]+) special characters"), re.compile(r"the text has ([0-9]+) roman digits"), re.compile(r"the text has \"([0-9a-zA-Z!@#$%^&*]+)\" string"), re.compile(r"the text has the capital city of ([0-9a-zA-Z!@#$%^&*]+)"), re.compile(r"the text has the continent of ([0-9a-zA-Z!@#$%^&*]+)"), re.compile(r"the text has a number that equals to ([0-9a-zA-Z!@#$%^&*+-x/ ]+)"), re.compile(r"the text has a number that equals to ([a-zA-Z ]+)")]
        
        def extract_variable(pattern, input_string, mode):
            match = pattern.search(input_string)
            if match:
                if mode == "number":
                    return int(match.group(1))
                else:
                    return match.group(1)
            else:
                return None
            
        self.rules = []
        self.rules_ids = []
        self.num_rules = 0
        
        rule_args = []
        string = state_string.split("Please write a text string without any space by following a set of given rules. Please write only the answer and follow the following criteria:")[1]
        string = string.split("Print only the answer.")[0].replace("\n\n","").split("\n")

        rule_chosen = {}

        for s in range(len(string)):
            contents = [extract_variable(patterns[i], string[s], mode="string") for i in range(len(patterns))]

            for rule_num_id in range(len(contents)):
                rule_id = self.rule_id_list[rule_num_id]
                content = contents[rule_num_id]
                if content is not None:
                    rule_chosen[rule_num_id] = True
                    rule_args.append(content)
                    self.rules_ids.append(rule_id)

                    rule_key = PasswordGame.RULES_IDS[rule_num_id]
                    self.rules.append([PasswordGame.RULES[rule_key][0], PasswordGame.RULES[rule_key][2], rule_id, content, rule_num_id])

        self.rule_id_list = [key for key in PasswordGame.RULES]

        self.rules.sort(key=lambda l: l[1], reverse=True)
        new_rules = []
        for rule_id in range(len(self.rules)):
            rule = self.rules[rule_id].copy()
            content = rule[3]
            rule_obj = rule[0](self.rules_args[rule[2]])
            if rule[4] == 3:
                params = content.split(" '")
                rule_obj.num_char = int(params[0])
                rule_obj.char = params[1].split("'")[0].strip()
            elif rule[4] <= 7:
                rule_obj.num_char = int(content)
            elif 8 <= rule[4] <= 10:
                rule_obj.str = str(content)
            else:
                value = parse_expr(content)
                rule_obj.expression = content
                rule_obj.num = value
            new_rules.append(rule_obj)

        self.rules = [rule for rule in new_rules]
