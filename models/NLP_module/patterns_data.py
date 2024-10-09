import re
patterns_number_brackets = [
    {
        "word_dot_number": {
            "pattern": re.compile(
                r"\b([a-zA-Z]+)\.\[\d+\]\b(?!\.\d|\w)|"  # Matches word.[number] (not followed by another dot-number or word)
                r"\b\d{4}\.\[\d+\]\b"                    # Matches 4-digit number.[number]
            ),
            "sep": "."
        },
        "word_semicolon": {
            "pattern": re.compile(r"\b\w+;\[\d+\]\b"),  # Matches word;[number]
            "sep": ";"
        }
    },
    {
        "word_parenthesis": {
            "pattern": re.compile(
                r"\b\w+\)\[\d+\]\b"                      # Matches word)[number]
            ),
            "sep": ")"
        },
        "word_semicolon": {
            "pattern": re.compile(r"\b\w+;\[\d+\]\b"),  # Matches word;[number]
            "sep": ";"
        }
    },
    {
        "word_quote": {
            "pattern": re.compile(
                r"\b\w+\.\[\"\d+\]\b|"                # Matches word.["number]
                r"\b\w+\"\[\d+\]\b|"                  # Matches word["number]
                r"\b\w+\.\[\'\"\d+\]\b|"              # Matches word.['"number]
                r"\b\w+\.\"\[\d+\]\|"                 # Matches word.["number]
                r"\b\d+\.\[\"\d+\]\b|"                # Matches number.["number]
                r",\[\'?\d+\]\b"                      # Matches ,["number]
            ),
            "sep": "\""
        },
        "word_semicolon": {
            "pattern": re.compile(r"\b\w+;\[\d+\]\b"),  # Matches word;[number]
            "sep": ";"
        }
    },
    {
        "word_comma": {
            "pattern": re.compile(
                r"\b\w+\,\"\[\d+\]\b|"                # Matches word,["number]
                r'\b[a-zA-Z]+,\[\d+\]\b|'             # Matches word,[number]
                r"\b\d{4}\,\[\d+\]\b|"                # Matches 4-digit number,[number]
                r"\),\[\d+\]\b"                       # Matches ),[number]
            ),
            "sep": ","
        },
        "word_semicolon": {
            "pattern": re.compile(r"\b\w+;\[\d+\]\b"),  # Matches word;[number]
            "sep": ";"
        }
    },
    {
        "word_number": {
            "pattern": re.compile(
                r'(?<![\w./])\b(?![A-Z]{2}\d+\b)[a-zA-Z]+\[\d+\]\b(?![\w./])'  # Matches word[number], but not preceded or followed by word, dot, or slash
            ),
            "sep": "none"
        },
        "word_semicolon": {
            "pattern": re.compile(r"\b\w+;\[\d+\]\b"),  # Matches word;[number]
            "sep": ";"
        }
    }
]

patterns_number = [
    {
        "word_dot_number": {
            "pattern": re.compile(
                r"\b([a-zA-Z]+)\.\d+\b(?!\.\d|\w)|"  # Matches word.number (not followed by another dot-number or word)
                r"\b\d{4}\.\d+\b"                    # Matches 4-digit number.number
            ),
            "sep": "."
        },
        "word_semicolon": {
            "pattern": re.compile(r"\b\w+;\d+\b"),  # Matches word;number
            "sep": ";"
        }
    },
    {
        "word_parenthesis": {
            "pattern": re.compile(
                r"\b\w+\)\d+\b"                      # Matches word)number
            ),
            "sep": ")"
        },
        "word_semicolon": {
            "pattern": re.compile(r"\b\w+;\d+\b"),  # Matches word;number
            "sep": ";"
        }
    },
    {
        "word_quote": {
            "pattern": re.compile(
                r"\b\w+\.\"\d+\b|"                # Matches word.'number
                r"\b\w+\"\d+\b|"                  # Matches word'number
                r"\b\w+\.'\"\d+\b|"              # Matches word.'"number
                r"\b\w+\.\"\d+\|"                # Matches word.''number
                r"\b\d+\.\"\d+\b|"                # Matches number.'number
                r",\''?\d+\b"                    # Matches ,"number
            ),
            "sep": "\""
        },
        "word_semicolon": {
            "pattern": re.compile(r"\b\w+;\d+\b"),  # Matches word;number
            "sep": ";"
        }
    },
    {
        "word_comma": {
            "pattern": re.compile(
                r"\b\w+\,\"\d+\b|"                # Matches word,"number
                r'\b[a-zA-Z]+,\d+\b|'             # Matches word,number
                r"\b\d{4}\,\d+\b|"                # Matches 4-digit number,number
                r"\),\d+\b"                       # Matches )number
            ),
            "sep": ","
        },
        "word_semicolon": {
            "pattern": re.compile(r"\b\w+;\d+\b"),  # Matches word;number
            "sep": ";"
        }
    },
    {
        "word_number": {
            "pattern": re.compile(
                r'(?<![\w./])\b(?![A-Z]{2}\d+\b)[a-zA-Z]+\d+\b(?![\w./])'  # Matches word followed by number, but not preceded or followed by word, dot, or slash
            ),
            "sep": "none"
        },
        "word_semicolon": {
            "pattern": re.compile(r"\b\w+;\d+\b"),  # Matches word;number
            "sep": ";"
        }
    }
]


patterns_dot_parenthesis = [
    {
        "word_dot_number": {
            "pattern": re.compile(
                r"\b([a-zA-Z]+)\.\((\d+)\)\b(?!\.\d|\w)|"  # Matches word.(number) (not followed by another dot-number or word)
                r"\b\d{4}\.\((\d+)\)\b"                    # Matches 4-digit number.(number)
            ),
            "sep": "."
        },
        "word_semicolon": {
            "pattern": re.compile(r"\b\w+;\((\d+)\)\b"),  # Matches word;(number)
            "sep": ";"
        }
    },
    {
        "word_parenthesis": {
            "pattern": re.compile(
                r"\b\w+\)\((\d+)\)\b"                      # Matches word)(number)
            ),
            "sep": ")"
        },
        "word_semicolon": {
            "pattern": re.compile(r"\b\w+;\((\d+)\)\b"),  # Matches word;(number)
            "sep": ";"
        }
    },
    {
        "word_quote": {
            "pattern": re.compile(
                r"\b\w+\.\(\"(\d+)\)\b|"                # Matches word.("number)
                r"\b\w+\"\((\d+)\)\b|"                  # Matches word"(number)
                r"\b\w+\.\('\"\((\d+)\)\b|"             # Matches word.('"number)
                r"\b\w+\.\"\((\d+)\)\|"                 # Matches word.("number)
                r"\b\d+\.\(\"(\d+)\)\b|"                # Matches number.("number)
                r",\('?\"?\((\d+)\)\b"  # Matches ,("number), ,('number), or ,(number)
            ),
            "sep": "\""
        },
        "word_semicolon": {
            "pattern": re.compile(r"\b\w+;\((\d+)\)\b"),  # Matches word;(number)
            "sep": ";"
        }
    },
    {
        "word_comma": {
            "pattern": re.compile(
                r"\b\w+\,\"\((\d+)\)\b|"                # Matches word,("number)
                r'\b[a-zA-Z]+,\((\d+)\)\b|'             # Matches word,(number)
                r"\b\d{4}\,\((\d+)\)\b|"                # Matches 4-digit number,(number)
                r"\),\((\d+)\)\b"                       # Matches ),(number)
            ),
            "sep": ","
        },
        "word_semicolon": {
            "pattern": re.compile(r"\b\w+;\((\d+)\)\b"),  # Matches word;(number)
            "sep": ";"
        }
    },
    {
        "word_number": {
            "pattern": re.compile(
                r'(?<![\w./])\b(?![A-Z]{2}\d+\b)[a-zA-Z]+\((\d+)\)\b(?![\w./])'  # Matches word(number), but not preceded or followed by word, dot, or slash
            ),
            "sep": "none"
        },
        "word_semicolon": {
            "pattern": re.compile(r"\b\w+;\((\d+)\)\b"),  # Matches word;(number)
            "sep": ";"
        }
    }
]

