import os
import re
from openai import OpenAI
import fitz
import tiktoken  # Ensure this library is installed and supports your models
from PyPDF2 import PdfReader  # For reading PDF files
from dotenv import load_dotenv
load_dotenv()  # loads the variables from .env
# Models
EMBEDDING_MODEL = "text-embedding-3-large"
GPT_MODEL = "gpt-4-0613"

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts and returns the text from a PDF file."""
    reader = PdfReader(pdf_path)
    text = ''
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:  # Check if text was extracted
            text += page_text + ' '
    return text

def num_tokens(text: str, model: str = GPT_MODEL) -> int:
    """Return the number of tokens in a string."""
    encoding = tiktoken.encoding_for_model(model)  # Ensure tiktoken supports your model
    return len(encoding.encode(text))

def query_message(query: str, article_text: str, model: str, token_budget: int) -> str:
    """Return a message for GPT, with the relevant source text."""
    # Trimming or summarizing logic could be added here if needed
    question = f"\n\nGuidelines: {query}"
    message =  f'\n\nArticle text:\n"""\n{article_text}\n"""'
    if num_tokens(message + question, model=model) > token_budget:
        message = "The article is too long to fully include and still ask the question within the token limit. Summarizing the article content:"
    return message + question


def ask(query: str, article_text: str, model: str = GPT_MODEL, token_budget: int = 12000, print_message: bool = False) -> str:
    """Asks the GPT model to list the main topics of an article."""
    prompt = f"{query}\n\nArticle text:\n{article_text}\n\n"

    if num_tokens(prompt, model=model) > token_budget:
        print("using gpt-4 turbo")
        # If the prompt exceeds the token budget, you might need to summarize the article first
        if num_tokens(prompt, model=model) > 32000:
            return None
        model="gpt-4-1106-preview"
    if print_message:
        print("chat prompt:",prompt)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are to extract information from the text following the guidelines with the provided html and return a html div string after analysing the text."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7  # Adjust for creativity
        )

        topics = response.choices[0]# Assuming each topic is on a new line
        return re.sub(r'```htm.*?```', '', topics.message.content, flags=re.DOTALL)

    except Exception as e:
        return f"An error occurred: {str(e)}"

def sanitize_text(text):

    """
    Cleans the article text by removing everything before "Introduction" and everything after "Conclusion",
    and applying prohibited phrases removal.

    :param text: The raw text extracted from the PDF.
    :return: The cleaned article text.
    """
    # Define prohibited phrases based on common patterns observed in the PDFs
    prohibited_phrases = [
        "reproduced with permission of copyright owner further reproduction prohibited without permission",
        "reproduction prohibited without permission",
        # Include more prohibited phrases as observed in the PDFs
    ]

    # Remove everything before "Introduction"
    intro_pattern = re.compile(r".*?Introduction", re.DOTALL)
    text = re.sub(intro_pattern, "Introduction", text)

    # Remove everything after "Conclusion"
    conclusion_pattern = re.compile(r"Conclusion.*", re.DOTALL)
    text = re.sub(conclusion_pattern, "Conclusion", text)

    # Remove or mask prohibited phrases
    for phrase in prohibited_phrases:
        text = text.replace(phrase, '')

    return text


def preprocess_text(text: str) -> str:
    """
    Preprocesses the text for better analysis, like removing extra whitespace, fixing common errors, etc.
    """
    # Example: Replace multiple spaces with a single space
    preprocessed_text = re.sub(' +', ' ', text)

    # Further preprocessing steps can be added here

    return preprocessed_text


def sanitize_text(text: str) -> str:
    """
    Sanitizes text by removing non-ASCII characters and special symbols.
    """
    text = text.encode('ascii', 'ignore').decode('ascii')  # Remove non-ASCII characters
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)  # Remove any special characters
    return text

def preprocess_text(text: str) -> str:
    """
    Preprocesses text by converting to lowercase and removing extra spaces.
    """
    text = text.lower()  # Convert text to lowercase
    text = ' '.join(text.split())  # Remove extra spaces
    return text

def extract_and_clean_pdf_text(pdf_path: str) -> str:
    """
    Extracts text from a PDF file using PyMuPDF (fitz), sanitizes it, and preprocesses it.
    """
    text = ''
    with fitz.open(pdf_path) as doc:
        for page in doc:
            page_text = page.get_text()
            if page_text:
                text += page_text + ' '

    sanitized_text = sanitize_text(text)  # Sanitize the extracted text
    preprocessed_text = preprocess_text(sanitized_text)  # Preprocess the sanitized text

    return preprocessed_text




# Example usage
def chat_response(pdf_path, query):
    article_text = extract_and_clean_pdf_text(pdf_path)
    # Check if the article_text is not empty
    if not article_text.strip():
        return "The article content could not be extracted or is empty. Please check the PDF file."

    # Call the ask function with the extracted article text and the query
    response_text = ask(query, article_text)
    return response_text