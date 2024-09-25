import ast
import re
from collections import defaultdict
from datetime import datetime
from random import random

from nipype.interfaces.fsl import PRELUDE
from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial.distance import cosine
import numpy as np
import nltk
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from fuzzywuzzy import fuzz
from itertools import tee
import unidecode
from tensorflow.python.framework.test_ops import in_polymorphic_twice
from tqdm import tqdm

# Modified function for trigram matching using GPU
from transformers import BertTokenizer, BertModel
import torch

from Pychat_module.gpt_api import call_openai_api


def normalize_text(text):
    """
    Normalize text by handling ligatures, removing all punctuation, digits, converting to lower case,
    and collapsing multiple spaces.
    """
    # Handle common ligatures and special characters
    replacements = {
        'ﬃ': 'ffi',
        'ﬀ': 'ff',
        'ﬁ': 'fi',
        'ﬂ': 'fl',
        'œ': 'oe',
        'æ': 'ae',
        'Œ': 'OE',
        'Æ': 'AE'
    }
    for k, v in replacements.items():
        text = text.replace(k, v)

    # Remove all non-alphanumeric characters except for spaces (including digits)
    text = re.sub(r'[^\w\s]', '', text)
    # Remove digits
    text = re.sub(r'\d+', '', text)
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text).lower().strip()
    return text

def normalize_text2(text):
  """
  Normalize text by converting to lowercase, removing extra spaces, and standardizing quotation marks.
  """
  text = text.lower()  # Convert to lowercase
  text = re.sub(r"\s+", " ", text)  # Replace multiple spaces with a single space
  text = re.sub(r"[‘’“”\"']", "'", text)  # Normalize quotation marks
  text = text.strip()  # Trim leading and trailing whitespace
  # Handle common ligatures and special characters
  replacements = {
      'ﬃ': 'ffi',
      'ﬀ': 'ff',
      'ﬁ': 'fi',
      'ﬂ': 'fl',
      'œ': 'oe',
      'æ': 'ae',
      'Œ': 'OE',
      'Æ': 'AE'
  }
  for k, v in replacements.items():
      text = text.replace(k, v)
  return text


def basic_normalization(text, lowercase=False):
    """
    Normalize text by:
    - Converting to lowercase (optional)
    - Removing extra spaces
    - Standardizing quotation marks and apostrophes
    - Handling special characters and ligatures
    - Correcting hyphenated word splits across lines
    - Merging lines within sentences
    """
    # Replace special characters and ligatures
    replacements = {
        'ﬃ': 'ffi', 'ﬀ': 'ff', 'ﬁ': 'fi', 'ﬂ': 'fl',
        'œ': 'oe', 'æ': 'ae', 'Œ': 'OE', 'Æ': 'AE',
        '©': '(c)', '®': '(r)', '™': '(tm)', '℠': '(sm)',
        '…': '...', '–': '-', '—': '-', '−': '-',  # Dashes and hyphens
        '¼': '1/4', '½': '1/2', '¾': '3/4',
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    # url_pattern = re.compile(
    #     r'\[?http[s]?://(?:[a-zA-Z0-9$-_@.&+!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F])|[\w.-])+\]?'
    #     r'|\[?www\.(?:[a-zA-Z0-9$-_@.&+!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F])|[\w.-])+\]?'
    #     r'|\[?(?:[a-zA-Z0-9-]+\.[a-zA-Z]{2,})(?:/[^\s]*)?\]?'
    #     r'|\[?\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b\]?'
    # )
    # text = re.sub(url_pattern, '', text)
    # text = re.sub(r"\d+\.\s(?:[^.]+\.\s*){1,3}(?=\d+\.\s|\Z)", " ", text)

    # Normalize spaces and quotation marks
    # text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[‘’´`]", "'", text)  # Normalize apostrophes
    text = re.sub(r'[“”«»„]', '"', text)  # Normalize quotation marks

    # Handle accented characters and Unicode
    text = unidecode.unidecode(text)


    # Expand common contractions
    contractions = {"don't": "do not", "we're": "we are", "can't": "cannot"}
    for contraction, expansion in contractions.items():
        text = re.sub(r'\b' + contraction + r'\b', expansion, text)





    # # Correct hyphenated line breaks
    # text = re.sub(r'\b(\w+)-\s*(\w+)\b', r'\1\2', text)
    # text = re.sub(r'(?<=\w)-\n(?=\w)', '', text)
    # text = re.sub(r'(?<!\.)\n(?!\s*\n)', ' ', text)

    # Normalize split numbers across lines
    pattern = re.compile(r'(\.\s*["\'])\s*(\d+)\n\s*(\d+)')
    text = pattern.sub(r'\1\2\3', text)

    return text


def clean_hyphenated_words(text):
    # Regex pattern to match words with more than two hyphens followed by any characters
    pattern = re.compile(r'\b[\w]+(?:-[\w]+){2,}\b')

    # Replace the matched patterns with an empty string
    cleaned_text = re.sub(pattern, ' ', text)

    # Remove any trailing whitespace that might result from the replacement
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()

    return cleaned_text



def remove_bibliographic_references(text):
    # Example pattern to match bibliographic references
    bib_pattern = re.compile(r'\b\w+[,]\s*\d+\s*[\w]*[.]*\b|\b\d{4}[a-zA-Z0-9\s]*[,]*\s*[\w]*[.]*\b|\b\w+\s*[\d]+[,]\s*\d+\s*[.]*\b')
    return bib_pattern.sub('', text)

regex_sub = {
        "numerical_references_inline": "\\b(?:supra note \\d+)",
        "direct_citation_with_page": "\\d+\\.\\s[A-Z].+?,\\s(?:at\\s)?\\d+"}


def get_last_four_tokens(input_string):
    # Tokenize the string using regex to keep words and punctuation together
    tokens = re.findall(r'\S+', input_string)

    # Return the last four tokens
    return " ".join(tokens[-4:])
def replace_substring_and_check(input_string, old_substring):
    # Escape the old substring to safely use it in a regex pattern
    escaped_old_substring = re.escape(old_substring)

    # Define a regex pattern to find the old substring with optional surrounding whitespace or punctuation
    flexible_pattern = rf'(?<!\w)[\s.,;!?-]*{escaped_old_substring}[\s.,;!?-]*(?!\w)'

    # Define the new substring with an added space at the end (if needed)
    new_substring = f"{old_substring} "

    # Perform the replacement
    result, count = re.subn(flexible_pattern, new_substring, input_string, flags=re.IGNORECASE)

    success = count > 0

    return result, success


# Define the function to replace key words with one of the elements from the list of synonyms randomly
def replace_with_synonyms(text):
    synonyms = {
        "complexities": ["difficulties", "complications", "challenges", "details"],
        "sophisticated": ["refined", "elegant", "advanced", "subtle"],
        "multifaceted": ["versatile", "diverse", "varied", "complex"],
        "complicated": ["complex", "difficult", "confusing", "involved"],
        "intricate": ["detailed", "complicated", "complex", "elaborate"],
        "nuanced": ["subtle", "refined", "detailed", "fine"],
        "comprehensive": ["complete", "thorough", "inclusive", "all-encompassing"],
        "dynamic": ["changing", "energetic", "active", "vibrant"],
        "advanced": ["modern", "progressive", "sophisticated", "leading"],
        "challenging": ["difficult", "demanding", "tough", "testing"],
        "revolutionary": ["groundbreaking", "radical", "innovative", "transformative"],
        "cutting-edge": ["advanced", "modern", "innovative", "leading"],
        "pioneering": ["leading", "trailblazing", "innovative", "first-of-its-kind"],
        "meticulous": ["careful", "precise", "thorough", "detailed"],
        "thorough": ["complete", "comprehensive", "detailed", "meticulous"],
        "explore": ["investigate", "examine", "analyze", "study"],
        "remarkable": ["notable", "extraordinary", "impressive", "noteworthy"],
        "vital": ["essential", "crucial", "important", "necessary"],
        "moreover": ["furthermore", "also", "in addition", "besides"],
        "navigate": ["steer", "traverse", "maneuver", "find one's way"]
    }
    # Split text into words
    words = text.split()

    # Loop through the words in the text
    for i, word in enumerate(words):
        # Check if the word is in the synonym dictionary (case insensitive)
        for key in synonyms:
            if word.lower() == key.lower():
                # Replace the word with a random synonym
                words[i] = random.choice(synonyms[key])
                break

    # Join the words back into a string
    return ' '.join(words)


# Helper function to calculate the proximity between keyword matches in the text
def wildcard_match(keyword: str, text: str) -> bool:
    # Convert the wildcard to a regex pattern, replacing "*" with ".*"
    pattern = re.escape(keyword).replace(r'\*', '.*')
    regex = re.compile(rf'\b{pattern}\b', re.IGNORECASE)
    return bool(regex.search(text))


def process_themes(themes, more_subsection_get, collection_name, type_collection):
    """
    Iterate through the original theme structure and append new subsections fetched from more_subsection_get
    to the subsections key of each heading in the new_theme structure.
    """
    # Initialize a new theme to hold the processed structure

    # Iterate through each theme in the list of themes
    for theme in themes:
        theme_title = theme['theme']  # Get the title of the theme

        # Iterate through each heading under this theme (h1 level)
        for heading in theme['outline']:
            print('processing the heading:',heading)
            # Process the subheadings of this heading and fetch additional subsections (more_subs)
            new_subheadings = process_subheadings(heading, more_subsection_get, collection_name, type_collection, theme_title)


        #     subs.append(new_subheadings)
        #     # Append the processed heading (with new subsections) to the new theme structure
        # new_theme[theme_title].append({
        #     'title': h1_title,
        #     'level': heading['level'],
        #     'subheadings':subs ,  # Directly assign fetched subheadings (with more_subs)
        #     'paragraph_title': heading.get('paragraph_title', []),
        #     'paragraph_text': heading.get('paragraph_text', []),
        #     'paragraph_blockquote': heading.get('paragraph_blockquote', [])
        # })

    return themes


def process_subheadings(subheading, more_subsection_get, collection_name, type_collection, parent_title):
    """
    Helper function that fetches subheadings using more_subsection_get and appends them to the original structure.
    """
    # Create the query for fetching more subsections
    query = {'title': subheading['title'], 'level': subheading['level'], 'parent': parent_title}
    # Fetch more subsections using the query
    more_subs = more_subsection_get(query=query,
                                    type_collection=type_collection,
                                    collection_name=collection_name,
                                    filter_conditions=None,
                                    with_payload=True,
                                    with_vectors=False,
                                    score_threshold=0.60,
                                    ai=True
                                    )

    if more_subs:

        # Include all necessary fields like title, level, paragraph_title, paragraph_text, blockquote
        subheading['subheadings']=more_subs

        return subheading

def update_response_with_paragraph_data(response, aggregated_paragraph_data):
    # Extract the lists of paragraph information from the dictionary
    paragraph_ids = [str(pid).strip() for pid in aggregated_paragraph_data.get('paragraph_id', [])]
    paragraph_titles = aggregated_paragraph_data.get('paragraph_title', [])
    paragraph_texts = aggregated_paragraph_data.get('paragraph_text', [])
    paragraph_blockquotes = aggregated_paragraph_data.get('paragraph_blockquote', [])
    section_titles = aggregated_paragraph_data.get('section_title', [])
    section_metadata = aggregated_paragraph_data.get('metadata', [])

    # Create a dictionary for quick lookup of paragraph data by id
    paragraph_data_dict = {}
    for i in range(len(paragraph_ids)):
        paragraph_data_dict[paragraph_ids[i]] = {
            'paragraph_title': paragraph_titles[i] if i < len(paragraph_titles) else 'N/A',
            'paragraph_text': paragraph_texts[i] if i < len(paragraph_texts) else 'N/A',
            'paragraph_blockquote': paragraph_blockquotes[i] if i < len(paragraph_blockquotes) else 'N/A',
            'section_title': section_titles[i] if i < len(section_titles) else 'N/A',
            'metadata': section_metadata[i] if i < len(section_metadata) else 'N/A'
        }

    # Function to process a single section recursively
    def process_section(section):
        updated_section = {
            'title': section.get('title', 'N/A'),
            'level': section.get('level', 'N/A'),
            'paragraph_title': [],  # List of all paragraph titles
            'paragraph_text': [],  # List of all paragraph texts
            'section_title': [],  # List of section titles
            'paragraph_id': [],  # List of paragraph ids
            'paragraph_blockquote': [],  # List of blockquotes
            'metadata': []  # List of metadata
        }

        # Replace paragraph_ids with actual paragraph data if available
        for paragraph_id in section.get('paragraph_ids', []):
            if paragraph_id in paragraph_data_dict:
                paragraph_info = paragraph_data_dict[paragraph_id]
                updated_section['paragraph_title'].append(paragraph_info.get('paragraph_title', 'N/A'))
                updated_section['paragraph_text'].append(paragraph_info.get('paragraph_text', 'N/A'))
                updated_section['section_title'].append(paragraph_info.get('section_title', 'N/A'))
                updated_section['paragraph_id'].append(paragraph_id)
                updated_section['paragraph_blockquote'].append(paragraph_info.get('paragraph_blockquote', 'N/A'))
                updated_section['metadata'].append(paragraph_info.get('metadata', 'N/A'))

        # Process subheadings recursively and add them to subsections
        updated_section['subheadings'] = []

        for subsection in section.get('subheadings', []):
            # print('subsection:', subsection)
            updated_section['subheadings'].append(process_section(subsection))

        return updated_section


    # Process the entire response recursively
    return [process_section(section) for section in [response]]



lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))





def clean_and_normalize(text):
    # Convert text to lowercase
    text = text.lower()

    # Remove non-alphanumeric characters (punctuation, symbols, etc.)
    text = re.sub(r'[^a-z0-9\s]', '', text)

    # Tokenize text
    words = nltk.word_tokenize(text)

    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    words = [word for word in words if word not in stop_words]

    # Return cleaned words
    return ' '.join(words)
