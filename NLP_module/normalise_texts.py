import re
from datetime import datetime
from random import random
from sklearn.metrics.pairwise import cosine_similarity

import torch
from itertools import tee
import unidecode

import torch



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

def remove_urls_emails(text):
    url_pattern = re.compile(
        r'(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+|'
        r'www\.(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+|'
        r'(?:[a-zA-Z0-9-]+\.[a-zA-Z]{2,})(?:/[^\s]*)?|'
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b)'
    )
    return url_pattern.sub(' ', text)

def remove_bibliographic_references(text):
    # Example pattern to match bibliographic references
    bib_pattern = re.compile(r'\b\w+[,]\s*\d+\s*[\w]*[.]*\b|\b\d{4}[a-zA-Z0-9\s]*[,]*\s*[\w]*[.]*\b|\b\w+\s*[\d]+[,]\s*\d+\s*[.]*\b')
    return bib_pattern.sub('', text)

regex_sub = {
        "numerical_references_inline": "\\b(?:supra note \\d+)",
        "direct_citation_with_page": "\\d+\\.\\s[A-Z].+?,\\s(?:at\\s)?\\d+"}
def apply_regex_substitutions(text, regex_patterns, replacement=""):
    """
    Apply multiple regex substitutions on the provided text.

    Parameters:
    text (str): The input text to be processed.
    regex_patterns (list): A list of regex patterns to apply.
    replacement (str): The replacement text for each match.

    Returns:
    str: The processed text with all substitutions applied.
    """
    for pattern in regex_patterns:
        text = re.sub(pattern, replacement, text)
    return text
    def normalize_title(self,title):
        """ Normalize the title by removing punctuation, converting to lower case, and stripping spaces. """
        return re.sub(r'\W+', ' ', title).lower()

    def parse_date(self,date_str):
        """ Parse the ISO date string to a datetime object. """
        return datetime.fromisoformat(date_str.rstrip('Z'))
def clean_h2_title(html_string):
    """
       Extracts and cleans the text of the first <h2> tag found in the given HTML string.

       Parameters:
       - html_string (str): The HTML string to parse for an <h2> tag.

       Returns:
       - The cleaned text content of the first <h2> tag, with all HTML tags removed. Returns None if no <h2> tag is found.
       """
    # Use regular expression to extract text within <h2> tags
    h2_text = re.search(r'<h2>(.*?)</h2>', html_string)
    if h2_text:
        # If found, return the cleaned text without HTML tags
        return re.sub('<[^<]+?>', '', h2_text.group(1))
    else:
        # If not found, return None or handle the case appropriately
        return None

def split_text_into_chunks(text, chunk_size=3800, avg_token_length=4):
    words = text.split()
    approx_tokens = len(words) * avg_token_length

    # Calculate the approximate number of words per chunk
    words_per_chunk = chunk_size // avg_token_length

    chunks = []
    for i in range(0, len(words), words_per_chunk):
        chunk = ' '.join(words[i:i + words_per_chunk])
        chunks.append(chunk)

    return chunks


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


def add_paragraphs_to_structure(structure, search_paragraphs_by_query, collection_name):
    """
    Function to add paragraphs to each heading (h1, h2, h3) in the structure.
    :param structure: The dictionary representing the list of themes, headings, and subheadings.
    :param search_paragraphs_by_query: The function used to query for paragraphs.
    :param collection_name: The name of the collection being queried.
    """

    def process_heading(heading):
        """
        Helper function to process paragraphs for a given heading or subheading.
        :param heading: A dictionary representing the current heading or subheading.
        """
        title = heading.get('title', '')
        print(f"Processing title: {title}")

        try:
            # Get paragraphs based on the title using the search function
            paragraph_list = search_paragraphs_by_query(
                collection_name=collection_name,
                query=title,
                filter_conditions=None,
                with_payload=True,
                with_vectors=False,
                score_threshold=0.60
            )
        except Exception as e:
            print(f"Error retrieving paragraphs for '{title}': {e}")
            paragraph_list = None

        # Check if paragraphs is a dict and properly extract data
        if isinstance(paragraph_list, dict) and paragraph_list:
            topic_sentences = paragraph_list.get('paragraph_title', [])
            paragraphs = paragraph_list.get('paragraph_text', [])
            blockquotes = paragraph_list.get('paragraph_blockquote', [])
            paragraph_ids = paragraph_list.get('paragraph_id', [])

            # Add paragraphs to the heading
            heading['paragraphs'] = []

            for i in range(len(paragraphs)):
                paragraph_data = {
                    'topic sentence': topic_sentences[i] if i < len(topic_sentences) else 'No topic sentence',
                    'paragraph': paragraphs[i] if i < len(paragraphs) else 'No paragraph text',
                    'paragraph_id': paragraph_ids[i] if i < len(paragraph_ids) else 'No ID',
                    'blockquote': blockquotes[i] if i < len(blockquotes) else False
                }
                heading['paragraphs'].append(paragraph_data)

            print(f"Added {len(paragraphs)} paragraphs to '{title}'")
        else:
            print(f"No paragraphs found for '{title}'")

    # Process headings and subheadings for each theme
    for theme in structure.get('themes', []):
        for heading in theme.get('headings', []):
            # Process the heading (h1 level)
            process_heading(heading)

            # Process subheadings (h2, h3 levels) if they exist
            for subheading in heading.get('subheadings', []):
                process_heading(subheading)


import nltk
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from fuzzywuzzy import fuzz



lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))


# Preprocessing text: Lemmatization and stopword removal
def preprocess_text(text):
    tokens = text.split()
    tokens = [lemmatizer.lemmatize(token) for token in tokens if token.lower() not in stop_words]
    return tokens


# Generate bigrams from preprocessed text
def generate_bigrams(text):
    tokens = preprocess_text(text)
    return [' '.join(bigram) for bigram in zip(tokens, tokens[1:])]


# Expand keywords with synonyms using WordNet
def get_synonyms(word):
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name())
    return synonyms


# Apply FuzzyWuzzy for partial matching
def fuzzy_match(text, keywords, threshold=95):
    return any(fuzz.partial_ratio(text, keyword) > threshold for keyword in keywords)


# Proximity-based boosting
def proximity_boost(paragraph_text, keywords, threshold=5):
    tokens = paragraph_text.split()
    positions = {k: [i for i, token in enumerate(tokens) if token == k] for k in keywords}

    for keyword1, pos1 in positions.items():
        for keyword2, pos2 in positions.items():
            if keyword1 != keyword2:
                for p1 in pos1:
                    for p2 in pos2:
                        if abs(p1 - p2) <= threshold:
                            return 1  # Boost score if keywords are close
    return 0

# Function to generate bigrams from text
def generate_bigrams(text):
    tokens = text.split()  # Split the text into words
    it1, it2 = tee(tokens)
    next(it2, None)
    return [' '.join(bigram) for bigram in zip(it1, it2)]

# Function to get BERT embeddings for a given text (bigram)
# Function to generate bigrams from text

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
# Preprocess text to remove stopwords
def preprocess_text_remove_stopwords(text):
    tokens = text.split()
    return ' '.join([word.lower() for word in tokens if word.lower() not in stop_words])
# Function to generate bigrams from text (with stopword removal)

def generate_trigrams(text):
    preprocessed_text = clean_and_normalize(text)  # Remove stopwords and normalize the text
    tokens = preprocessed_text.split()  # Split the text into words
    it1, it2, it3 = tee(tokens, 3)  # Create three iterators for trigrams
    next(it2, None)  # Move second iterator one step ahead
    next(it3, None)  # Move third iterator two steps ahead
    next(it3, None)

    return [' '.join(trigram) for trigram in zip(it1, it2, it3)]  # Join tokens into trigrams


# Function to compute cosine similarity using GPU
def compute_similarity(query_vector, trigram_vector):
    # Convert to PyTorch tensors and move to GPU
    query_tensor = torch.tensor(query_vector).cuda()
    trigram_tensor = torch.tensor(trigram_vector).cuda()

    # Compute cosine similarity
    cosine_sim = torch.nn.functional.cosine_similarity(query_tensor, trigram_tensor, dim=0)
    return cosine_sim.item()

# Modified function for trigram matching using GPU
