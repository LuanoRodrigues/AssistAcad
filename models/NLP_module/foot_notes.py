import time
from collections import defaultdict

import enchant
from PyDictionary import PyDictionary

dictionary = PyDictionary()
from models.NLP_module.normalise_texts import normalize_text2
from models.NLP_module.normalise_texts import basic_normalization
import fitz  # PyMuPDF
from nltk.corpus import words

english_words = set(words.words())
import spacy

# Load a pre-trained NLP model
nlp = spacy.load("en_core_web_sm")
#TODO get pdfs with html or xml format extracting sup tags along with the text before

import requests

from models.NLP_module.patterns_data import*

def is_english_word(word):
    d = enchant.Dict("en_US")
    valid = d.check(word)
    if not valid:
        time.sleep(1)
    # Check if the word is valid

        """Validate if a word is an English word using dictionaryapi.dev."""
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            return True  # The word is valid
        elif response.status_code == 404:
            return False  # The word is not found
        else:
            # Handle other errors or API issues
            print(f"Error: {response.status_code}")
            return None
    else:
        return valid

def filter_wordnumber_list(full_match,sep):
    stop_list = ['sol3', 'ta17','ta18','apt','ta']  # Define your stop list here
    # Extract the number part
    ref = re.search(r'\d+', full_match).group()
    if sep=='none':
        word =full_match.replace(ref,"")

    else:

        # Extract the word part before the period and quote
        word = full_match.split(sep)[0]
    # Ensure the word is valid, in the English dictionary, not in stop list, and number <= 400
    if  is_english_word(word) and word.lower() not in stop_list and len(word)>1 and int(ref) <= 400:
        return word,ref


def merge_dicts(*dicts):
    merged = defaultdict(list)

    # Loop through each dictionary and each item in the dictionaries
    for d in dicts:
        for item in d:
            merged[item['ref']].append(item['preceeding_text'])

    # Convert defaultdict to regular dict if needed
    merged_dict = {key: value if len(value) > 1 else value[0] for key, value in merged.items()}

    return merged_dict

def extract_paragraphs_from_pdf(pdf_path):
    paragraphs = []
    current_paragraph = " "

    # Open the PDF
    document = fitz.open(pdf_path)

    # Iterate through each page
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        text = page.get_text("text")
        with open("texto.txt", "a", encoding="utf-8") as text_file:
            text_file.write(text+'new paragraph\n')

        # Split the text by lines
        lines = text.split('\n')

        for line in lines:
            stripped_line = line.strip()
            if not stripped_line:
                if current_paragraph:
                    paragraphs.append(current_paragraph.strip())
                    current_paragraph = " "
                continue

            # Append line to the current paragraph
            if current_paragraph:
                current_paragraph += " " + stripped_line
            else:
                current_paragraph = stripped_line

        # Append the last paragraph of the page if exists
        if current_paragraph:
            paragraphs.append(current_paragraph.strip())
            current_paragraph = " "

    return paragraphs


def classify_paragraphs(paragraphs):
    footnotes = []
    body_text = []

    # Define the regex pattern to identify footnotes
    footnote_pattern = re.compile(r'\b\d+\.\s.*')  # Simple example, can be more complex

    # Define stop patterns to identify body text
    stop_patterns = [
        r'\b([a-zA-Z]+)\.\d+\b(?!\.\d|\w)',  # Matches word.number
        r'\b\d{4}\.\d+\b',  # Matches 4-digit number.number
        r'\b\w+\)\d+\b',  # Matches word)number
        r'\b\w+;\d+\b',  # Matches word;number
        r'\b\w+\.\"\d+\b|',  # Matches word.'number
        r'\b\w+\"\d+\b|',  # Matches word'number
        r'\b\w+\.\'\d+\b|',  # Matches word.'"number
        r'\b\w+\.\"\d+\|',  # Matches word.''number
        r'\b\d+\.\"\d+\b|',  # Matches number.'number
        r',\'?\d+\b',  # Matches ,"number or ,'number
        r'\b\w+\,\"\d+\b|',  # Matches word,"number or word,'number
        r'\b[a-zA-Z]+,\d+\b|',  # Matches word,number
        r'\b\d{4}\,\d+\b|',  # Matches 4-digit number,number
        r'\),\d+\b',  # Matches )number
        r'(?<![\w./])\b(?![A-Z]{2}\d+\b)[a-zA-Z]+\d+\b(?![\w./])'  # Matches word+number
    ]

    combined_stop_pattern = re.compile('|'.join(stop_patterns))

    for para in paragraphs:
        para =basic_normalization(para)
        if footnote_pattern.search(para):

            footnotes.append(para)
        elif combined_stop_pattern.search(para):
            body_text.append(para)

    return ' '.join(footnotes), ' '.join(body_text)


def find_missing_refs(ref_list):
    # Convert the ref keys to a sorted list of integers
    ref_list = sorted(int(ref) for ref in ref_list)
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
            'missing_ref': sorted(missing_refs),
            'elements':len(missing_refs)
        }

        return result
    except IndexError:
        print("IndexError")
        print("this is the reference list")
        print(ref_list)


def extract_preceeding_refs(text,pattern,sep="."):
    stop_words = ['sol3', 'ta17','ta18','apt','ta']
    # print(text[10000:])
    matched_texts = []

    matches = pattern.finditer(text)
    word,ref=['','']
    for match in matches:
        if match:

            # input(match)
            # input(match.group())
            # Extract the full match
            full_match = match.group(0)
            # print(sep)
            print(full_match)
            # valid_word =filter_wordnumber_list(full_match,sep=sep)
            if sep=="none":
                ref = re.search(r'\d+',full_match).group(0)
                word=full_match.replace(ref,"")
            else:
                word,ref = full_match.split(sep)
                ref = re.search(r'\d+',ref).group(0)

            start_idx = max(0, match.start() - 50)
            preceeding_text = text[start_idx:match.start()].strip()
            # input(f'word:{word}\nref:{ref}')
            # print(preceeding_text)
            # input({'ref': ref, 'preceeding_text': f"{preceeding_text} {word}".strip()})
            if word.lower() not in stop_words and int(ref) <= 400 and len(word)>1:
                matched_texts.append({'ref': ref, 'preceeding_text': f"{preceeding_text} {word}".strip()})
    return matched_texts
def extract_text_with_numbers_from_pdf(pdf_path):
    paragraphs = extract_paragraphs_from_pdf(pdf_path)

    footnotes, text = classify_paragraphs(paragraphs)

    with open("text.txt", "w",encoding="utf-8") as text_file:
        text_file.write(text)

    try:
        preceeding =getting_preeceedings(text,pattern_placeholder=patterns_number)
    except:

        try:
            preceeding =getting_preeceedings(text,pattern_placeholder=patterns_number_brackets)
        except:
            pass
        try:
            preceeding =getting_preeceedings(text,pattern_placeholder=patterns_dot_parenthesis)
        except:
            pass

    return preceeding
    # getting_preeceedings(text,"word_quote")
    # getting_preeceedings(text,"word_number")

    # getting_preeceedings(text,"word_comma",)
    # getting_preeceedings(text,"word_parenthesis")

    return
missing: [30, 311, 187, 319, 323, 324, 199, 200, 201, 202, 203, 204, 205, 78, 206, 207, 83, 212, 213, 214, 91, 232, 233, 106]

# def missing_preceeding_refs(pattern=r"\d+"):

def getting_preeceedings(text, pattern_placeholder,title=None):

    if title:
        patterns_dict_flat = {
            key: value
            for item in pattern_placeholder
            for key, value in item.items()
        }
        print("pattern: ", title)

        pattern, sep = patterns_dict_flat.get(title).values()
        data = extract_preceeding_refs(text, pattern=pattern, sep=sep)
        printing(data)
        return data
    references = []
    indexes = []
    for item in pattern_placeholder:
        for key, value in item.items():
            print('processing key:', key)
            pattern = value["pattern"]
            sep = value["sep"]
            data = extract_preceeding_refs(text, pattern=pattern, sep=sep)
            printing(data)
            references.append(data)
            indexes.extend([int(key['ref']) for key in data])
            # input('______' * 20)
            # print("\n")
    preceeding_dict = merge_dicts(*references)
    missing_refs = find_missing_refs(indexes)

    return missing_refs, preceeding_dict
def printing(x):
    print(x)
    print(len(x))
    print(sorted([int(k['ref']) for k in x]))
    print('len(x)', len(x))


def find_flexible_pattern_positions(text, sections):
  """
  Find the positions of section titles in the text using a highly flexible regex pattern.
  """
  positions = {}
  for section in sections:
    # Normalize the section title for better matching
    normalized_section = normalize_text2(section)

    # Escape the section title to handle special regex characters
    escaped_section = re.escape(normalized_section)

    # Create a more flexible pattern allowing for variations like spaces, punctuation, or line breaks
    flexible_pattern = rf'(?<!\w)[\s.,;!?-]*{escaped_section}[\s.,;!?-]*(?!\w)'

    # Search for the section using the flexible pattern
    match = re.search(flexible_pattern, text, re.IGNORECASE)

    if match:
      positions[section] = match.start()
    else:
      positions[section] = -1  # If the section is not found, return -1

  return positions
