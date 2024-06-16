import json
import random
from enum import Enum

from textgames.rules import generate_rules

def __main__():
    generate_rules()

# Multi-hop


# Please construct a text string with following criteria and print only the string:

#     the text has only 10 characters
#     the text has 2 special characters, including '!', '@', '#', '$', '%', '^', '&', '*'

# Model

# !aBcde@1F3
# User

# Please modify the generated text by adding this criteria without changing the previous rules:

#     the text has 3 uppercase latin characters.




# Please construct a text string with following criteria and print only the string there is such as a string otherwise print None:

#     the text has only 10 characters
#     the text has 3 uppercase character
#     the text has a number that equals to 2 + 2


# Please construct a text string with following criteria and print only the string there is such as a string otherwise print None:

#     the text has only 10 characters
#     the text has 3 uppercase character
#     the text has a number that equals to five plus two


# Please construct a text string with following criteria and print only the string there is such as a string otherwise print None:

#     the text has only 10 characters
#     the text has 3 uppercase character
#     the text has a single-digit number that equals to five plus five


# Please construct a text string with following criteria and print only the string there is such as a string otherwise print None:

#     the text has only 10 characters
#     the text has 3 uppercase character
#     the text has a multi-digit number that equals to five plus five


# Please construct a text string with following criteria and print only the string there is such as a string otherwise print None:
# - the text has only 10 characters
# - the text has 3 uppercase character
# - the text has a real number that equals to five divide by 2


# too hard:
# Please construct a text string with following criteria and print only the string there is such as a string otherwise print None:
# the text has only 10 characters
# the text has 3 uppercase character
# the text has a rounded real number with three significant figures that equals to five divide by 3