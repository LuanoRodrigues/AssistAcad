from collections import defaultdict

import enchant
from pprint import pprint
from NLP_module.normalise_texts import basic_normalization
import fitz  # PyMuPDF
import re
import nltk
from nltk.tokenize import sent_tokenize

import re
import spacy

# Load a pre-trained NLP model
nlp = spacy.load("en_core_web_sm")

from nltk.tokenize import word_tokenize


def extract_preceding_text_with_ref(text, wordnumber_list):
    results = []

    for wordnumber in wordnumber_list:
        # Find all positions of the wordnumber in the text
        start_idx = 0
        while True:
            start_idx = text.find(wordnumber, start_idx)
            if start_idx == -1:
                break

            # Tokenize the text up to the wordnumber position
            tokens = word_tokenize(text[:start_idx])

            # Extract the preceding 7 tokens ensuring wordnumber is the last one
            preceding_text = ' '.join(tokens[-6:]) + ' ' + wordnumber

            # Extract the number part from the wordnumber
            ref = re.search(r'\d+', wordnumber).group()

            # Check if the preceding text contains a file path or unwanted patterns
            if not re.search(r'([a-zA-Z]:\\|//|\\)', preceding_text):  # Adjust regex to capture common path patterns
                if ref.isdigit():
                    # Store the result
                    results.append({
                        'ref': ref,
                        'preceeding_text': preceding_text.strip().replace(ref, "")
                    })

            # Move to the next position
            start_idx += len(wordnumber)

    return results
def filter_wordnumber_list(wordnumber_list):
    # input(wordnumber_list)
    stop_list = ['sol3', 'ta17','ta18']  # Define your stop list here

    def is_english_word(word):
        d = enchant.Dict("en_US")
        # Strip any non-alphabetical characters and check if the word is valid
        word = re.sub(r"[^a-zA-Z]", "", word)
        return word and d.check(word) and len(word) > 1

    valid_wordnumbers = []

    for wordnumber in wordnumber_list:
        # Split the word and the number
        word = re.sub(r'\d+', '', wordnumber)
        number_match = re.search(r'\d+', wordnumber)

        # Continue only if a number is found
        if number_match:
            number = int(number_match.group())

            # Ensure the word is valid, in the English dictionary, not in stop list, and number <= 400
            if is_english_word(word) and word.lower() != 'apt' and wordnumber not in stop_list and number <= 400:
                valid_wordnumbers.append(wordnumber)
    # print(valid_wordnumbers)
    return valid_wordnumbers
from nltk.corpus import words

english_words = set(words.words())

def is_english_word(word):
    return word.lower() in english_words
def extract_words_followed_by_closing_paren_numbers(text):
    # Tokenize the text into sentences
    sentences = sent_tokenize(text)

    matched_texts = []

    # Regex pattern to match words followed by a closing parenthesis and a number
    pattern = re.compile(r'\b\w+\)\d+\b')

    for sentence in sentences:
        # Find all matches in the sentence
        matches = re.findall(pattern, sentence)
        for match in matches:
            # Extract the number part
            ref = re.search(r'\d+', match).group()
            # Extract the word part before the closing parenthesis
            word = match.split(')')[0]
            preceeding_text = sentence.split(match)[0].strip()
            # Store the result
            matched_texts.append({'ref': ref, 'preceeding_text': f"{preceeding_text} {word}"})

    return matched_texts
def extract_words_followed_by_numbers(text):

    # Preprocess the text if needed (e.g., normalization, cleaning)
    text = basic_normalization(text)  # Assuming normalize_text2 is defined elsewhere

    # Tokenize the text into sentences
    sentences = sent_tokenize(text)

    matched_texts = []

    # Regex pattern to match word.number
    pattern_word_number = r'\b[A-Za-z]+\d+\b'

    # Regex pattern to match word.[number]
    pattern_word_bracket_number = r'\b[A-Za-z]+\[\d+\]\b'

    # Combine both patterns using OR (|)
    combined_pattern = re.compile(f'{pattern_word_number}|{pattern_word_bracket_number}')

    # Refined regex pattern to match words immediately followed by a number
    # pattern = re.compile(r'\b\w+\.\d+\b|\b\w +\d +\b')


    # Find all matches in the sentence
    matches = combined_pattern.findall(text)
    for match in matches:
        # input(match)
        # Check to ensure it's not a standalone number
        if not match.isdigit():
            matched_texts.append(match)

    filtered_words = filter_wordnumber_list(matched_texts)
    preceeding_dict =extract_preceding_text_with_ref(text, filtered_words)

    return preceeding_dict
def filter__word_number_dot(matched_texts):
    # Additional filtering before returning results


    filtered_texts = []
    for item in matched_texts:
        text = item['preceeding_text']

        # Exclude text if it is less than one full sentence
        if not re.search(r'[.!?]', text):
            continue


        filtered_texts.append(item)

    return filtered_texts
def extract_words_followed_by_dots_numbers(text):
    sentences = sent_tokenize(text)
    # print(text[:10000])
    matched_texts = []

    # Loop through numbers from 1 to 150
    for n in range(1, 350):
        # Refined regex pattern to avoid common citations and phrases

        pattern_number = rf'\b(\w+\s{n})\b(?!\s*(Figure|Version|Volume|Nr|on))|([^.?!]*?[.?!]\s*{n})(?=\s|$)'


        pattern_number = re.compile(r'\b\w+\.\[\d+\]\b')

        for sentence in sentences:
            match = re.search(pattern_number, sentence)
            if match:
                # input(match.group())
                matched_text = match.group(0).strip().replace(str(n), '').replace(str(n - 1), '')
                # Filter out unwanted matches more specifically
                if "Figure" not in matched_text and "Volume" not in matched_text and "Version" not in matched_text:
                    matched_texts.append({'ref': n, 'preceeding_text': matched_text})
    return filter__word_number_dot(matched_texts)


def extract_words_followed_by_quotes_numbers(text):
    # Preprocess the text if needed (e.g., normalization, cleaning)
    text = basic_normalization(text)  # Assuming basic_normalization is defined elsewhere
    print(text[10000:50000])
    matched_texts = []


    # Individual regex components for regular numbers
    pattern_word_dot_quote_number = r"\b\w+\.\'\d+\b"  # Matches patterns like word.'number
    pattern_word_quote_number = r"\b\w+'\d+\b"  # Matches patterns like word'number
    pattern_word_dot_doublequote_number = r"\b\w+\.'\"\d+\b"  # Matches patterns like word.'"number
    pattern_word_dot_doublequote_number_strict = r"\b\w+\.'\'\d+\b"  # Matches patterns like word.''number
    pattern_number_dot_quote_number = r"\b\d+\.\'\d+\b"  # Matches patterns like number.'number
    pattern_comma_doublequote_number = r",\''?\d+\b"  # Matches patterns like ,"number
    pattern_paren_comma_number = r"\),\d+\b"  # Matches patterns like ),number
    pattern_word_semicolon_number = r"\b\w+;\d+\b"  # Matches patterns like word;number

    # Individual regex components for bracketed numbers
    pattern_bracket_word_dot_quote_number_brackets = r"\b(\w+)\.\'\[(\d+)\]"  # Matches patterns like word].[number]
    pattern_word_dot_quote_bracket_number = r"\w+\.\'\[\d+\]\b"  # Matches patterns like word.'[number]
    pattern_word_quote_bracket_number = r"\b\w+'\[\d+\]\b"  # Matches patterns like word'[number]
    pattern_word_dot_doublequote_bracket_number = r"\b\w+\.'\"\[\d+\]\b"  # Matches patterns like word.'"[number]
    pattern_word_dot_doublequote_bracket_number_strict = r"\b\w+\.'\'\[\d+\]\b"  # Matches patterns like word.''[number]
    pattern_number_dot_quote_bracket_number = r"\b\d+\.\'\[\d+\]\b"  # Matches patterns like number.'[number]
    pattern_comma_doublequote_bracket_number = r",\''?\[\d+\]\b"  # Matches patterns like ,"[number]
    pattern_paren_comma_bracket_number = r"\),\[\d+\]\b"  # Matches patterns like ),[number]
    pattern_paren_dot_bracket_number = r"\).\[\d+\]\b"  # Matches patterns like ).[number]
    pattern_word_semicolon_bracket_number = r"\b\w+;\[\d+\]\b"  # Matches patterns like word;[number]

    # Individual regex components for parenthesized numbers
    pattern_bracket_word_dot_quote_number_parens = r"\b(\w+)\.\'\((\d+)\)"  # Matches patterns like word.('[number])
    pattern_word_dot_quote_paren_number = r"\w+\.\'\(\d+\)\b"  # Matches patterns like word.'(number)
    pattern_word_quote_paren_number = r"\b\w+'\(\d+\)\b"  # Matches patterns like word'(number)
    pattern_word_dot_doublequote_paren_number = r"\b\w+\.'\"\(\d+\)\b"  # Matches patterns like word.'"[(number)]
    pattern_word_dot_doublequote_paren_number_strict = r"\b\w+\.'\'\(\d+\)\b"  # Matches patterns like word.''(number)
    pattern_number_dot_quote_paren_number = r"\b\d+\.\'\(\d+\)\b"  # Matches patterns like number.'(number)
    pattern_comma_doublequote_paren_number = r",\''?\(\d+\)\b"  # Matches patterns like ,"(number)
    pattern_paren_comma_paren_number = r"\),\(\d+\)\b"  # Matches patterns like ),(number)
    pattern_paren_dot_paren_number = r"\)\.\(\d+\)\b"  # Matches patterns like ).(number)

    # Combined regex pattern using the individual components
    pattern = re.compile(
        f"{pattern_bracket_word_dot_quote_number_brackets}|"
        f"{pattern_word_dot_quote_bracket_number}|"
        f"{pattern_word_quote_bracket_number}|"
        f"{pattern_word_dot_doublequote_bracket_number}|"
        f"{pattern_word_dot_doublequote_bracket_number_strict}|"
        f"{pattern_number_dot_quote_bracket_number}|"
        f"{pattern_comma_doublequote_bracket_number}|"
        f"{pattern_paren_comma_bracket_number}|"
        f"{pattern_paren_dot_bracket_number}|"
        f"{pattern_bracket_word_dot_quote_number_parens}|"
        f"{pattern_word_dot_quote_paren_number}|"
        f"{pattern_word_quote_paren_number}|"
        f"{pattern_word_dot_doublequote_paren_number}|"
        f"{pattern_word_dot_doublequote_paren_number_strict}|"
        f"{pattern_number_dot_quote_paren_number}|"
        f"{pattern_comma_doublequote_paren_number}|"
        f"{pattern_paren_comma_paren_number}|"
        f"{pattern_paren_dot_paren_number}"
        f"{pattern_bracket_word_dot_quote_number_brackets}|"
        f"{pattern_paren_dot_bracket_number}|"
        f"{pattern_word_dot_quote_number}|"
        f"{pattern_word_quote_number}|"
        f"{pattern_word_dot_doublequote_number}|"
        f"{pattern_word_dot_doublequote_number_strict}|"
        f"{pattern_number_dot_quote_number}|"
        f"{pattern_comma_doublequote_number}|"
        f"{pattern_paren_comma_number}|"
        f"{pattern_word_semicolon_number}|"
        f"{pattern_word_dot_quote_bracket_number}|"
        f"{pattern_word_quote_bracket_number}|"
        f"{pattern_word_dot_doublequote_bracket_number}|"
        f"{pattern_word_dot_doublequote_bracket_number_strict}|"
        f"{pattern_number_dot_quote_bracket_number}|"
        f"{pattern_comma_doublequote_bracket_number}|"
        f"{pattern_paren_comma_bracket_number}|"
        f"{pattern_word_semicolon_bracket_number}"
    )

    # Find all matches in the entire text
    matches = pattern.finditer(text)

    for match in matches:
        # Extract the full match
        full_match = match.group(0)
        # print("match")
        # input(full_match)
        # Extract the number part (with or without brackets)
        ref = re.search(r'\d+', full_match).group()

        # Extract the word part before the period and quote
        if "." in full_match:
            word = full_match.split(".")[0]
        else:
            word = full_match.split("'")[0]

        # Extract the preceding text (up to a reasonable limit, e.g., 50 characters)
        start_idx = max(0, match.start() - 50)
        preceeding_text = text[start_idx:match.start()].strip()

        if int(ref) <= 400:
            # Store the result
            matched_texts.append({'ref': ref, 'preceeding_text': f"{preceeding_text} {word}".strip()})

    return matched_texts
def extract_words_followed_by_comma_numbers(text):
    # Tokenize the text into sentences
    sentences = sent_tokenize(text)
    print(text[:100000])
    matched_texts = []

    # Define the pattern to match word,123 and word,[39]
    pattern_word_comma_digits = r'\b[a-zA-Z]+,\d+\b'  # Matches word,123
    pattern_word_comma_bracket_number = r'\b\w+\,\[\d+\]'  # Matches word,[39]
    pattern_word_comma_number = r'\b\w+\)\[\d+\]'  # Matches word).[39]



    # Combine the two patterns into a single pattern
    combined_pattern = re.compile(f"{pattern_word_comma_digits}|{pattern_word_comma_bracket_number}|{pattern_word_comma_number}")

    for sentence in sentences:
        # Find all matches in the sentence
        matches = re.findall(combined_pattern, sentence)
        for match in matches:
            # Extract the number part

            ref = re.search(r'\d+', match).group()
            # Extract the word part before the comma
            word = match.split(',')[0]
            preceeding_text = sentence.split(match)[0].strip()
            # print("comma")
            # input(match)
            # Store the result
            matched_texts.append({'ref': ref, 'preceeding_text': f"{preceeding_text} {word}"})

    return matched_texts


def extract_words_followed_by_bracketed_numbers(text):
    # Debug print to check the initial part of the text
    # print(text[:1000])
    matched_texts = []

    # Define the pattern to match word.[number] and word[number]
    pattern_bracket_dot_number = r'(\b\w+)\.\[(\d+)\]'  # Captures word.[number]
    pattern_word_bracket_number = r'(\b\w+)\[(\d+)\]'  # Captures word[number]

    # Combine the two patterns into a single pattern
    combined_pattern = re.compile(f"{pattern_bracket_dot_number}|{pattern_word_bracket_number}")


    matches = combined_pattern.finditer(text)

    for match in matches:
        # Debug output to see the match and groups


        # Check if the group exists and extract the number part (without brackets)
        if match.lastindex and match.lastindex >= 1:
            ref = match.group(0).split('[')[1].replace(']','')
            # print(ref)
            # input(match.group(0))
        else:

            ref = None

        # Get the preceding text before the match
        preceding_text = text[:match.start()].strip()

        # Split preceding text into tokens and get the last 7
        preceding_words = preceding_text.split()[-6:]

        # Join the last 7 words back into a string
        preceding_text = ' '.join(preceding_words)+" "+match.group(0).split('[')[0]

        matched_texts.append({'ref': ref, 'preceeding_text': preceding_text})

    return matched_texts


def merge_dicts(*dicts):
    merged = defaultdict(list)

    # Loop through each dictionary and each item in the dictionaries
    for d in dicts:
        for item in d:
            merged[item['ref']].append(item['preceeding_text'])

    # Convert defaultdict to regular dict if needed
    merged_dict = {key: value if len(value) > 1 else value[0] for key, value in merged.items()}

    return merged_dict


def find_missing_refs(ref_dict):
    # Convert the ref keys to a sorted list of integers
    ref_list = sorted(int(ref) for ref in ref_dict.keys())
    try:
        # Determine the range from the first to the last ref
        start = 1
        end = ref_list[-1]
        full_range = set(range(start, end + 1))

        # Find the missing refs by subtracting the actual refs from the full range
        missing_refs = list(full_range - set(ref_list))

        # Create the result dictionary
        result = {
            'range': f"{start}-{end}",
            'missing_ref': sorted(missing_refs)
        }

        return result
    except IndexError:
        print("IndexError")
        print("this is the reference list")
        print(ref_list)
def extract_text_with_numbers_from_pdf(pdf_path):
    # Open the PDF file
    doc = fitz.open(pdf_path)
    # Initialize an empty string to store the extracted text
    text = ""

    # Extract text from all pages in the PDF
    for page_num in range(len(doc)):
        page = doc[page_num]
        text += page.get_text()


    # Preprocess the text
    text = basic_normalization(text)


    # word_quote_numbers = extract_words_followed_by_quotes_numbers(text)
    # #
    # print(word_quote_numbers)
    # print(len(word_quote_numbers))
    # print([k['ref'] for k in word_quote_numbers])

    # closing_paren_numbers = extract_words_followed_by_closing_paren_numbers(text)
    # pprint(closing_paren_numbers)

    # words_comma =extract_words_followed_by_comma_numbers(text)
    # pprint(words_comma)
    # #
    # words_numbers = extract_words_followed_by_numbers(text)
    # pprint(words_numbers)
    # print('63' in [k['ref'] for k in words_numbers])
    # print([k['ref'] for k in words_numbers])
    #
    # words_dots_number= extract_words_followed_by_dots_numbers(text)

    # words_dots =extract_words_followed_by_bracketed_numbers(text)
    # print(words_dots)



    word_quote_numbers = extract_words_followed_by_quotes_numbers(text)

    closing_paren_numbers = extract_words_followed_by_closing_paren_numbers(text)

    words_comma =extract_words_followed_by_comma_numbers(text)

    words_numbers = extract_words_followed_by_numbers(text)

    words_dots_number= extract_words_followed_by_dots_numbers(text)

    words_dots_brackets =extract_words_followed_by_bracketed_numbers(text)

    preceeding_dict =merge_dicts(word_quote_numbers,
                                 closing_paren_numbers,
                                 words_comma,
                                 words_numbers,
                                 words_dots_number,
                                 words_dots_brackets

                                 )

    missing_refs = find_missing_refs(preceeding_dict)
    return missing_refs, preceeding_dict



