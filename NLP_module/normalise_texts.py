import re
from datetime import datetime

import unidecode
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