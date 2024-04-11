import os
import pickle
import re
import time

import openai
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


# Constants
PICKLE_FILE_PATH = 'file_thread_mapping.pickle'
ASSISTANT_ID = 'asst_NcixO2BWUT7ExDHt5IoZQQTw'  # Fixed Assistant ID
def load_file_thread_mapping():
    """Loads the mapping from a pickle file."""
    if os.path.exists(PICKLE_FILE_PATH):
        with open(PICKLE_FILE_PATH, 'rb') as f:
            return pickle.load(f)
    return {}

def save_file_thread_mapping(mapping):
    """Saves the mapping to a pickle file."""
    with open(PICKLE_FILE_PATH, 'wb') as f:
        pickle.dump(mapping, f)

def upload_file(client, file_path):
    """Uploads a file using the provided client and returns the file ID."""
    with open(file_path, 'rb') as f:
        response = client.files.create(file=f, purpose='assistants')
    print("File uploaded successfully.")
    return response.id

def create_thread(client, file_id):
    """Creates a thread with the uploaded file attached and returns the thread ID."""
    thread = client.beta.threads.create(
        messages=[{"role": "user",
                   "content": "Analyze the content of the attached file. output: only in html string div format",
                   "file_ids": [file_id]}]
    )
    print("Thread created successfully.")
    return thread.id
def clear_and_create_new_thread(client, file_id, mapping, pdf_path):
    """Clears the existing thread by creating a new one and updates the mapping."""
    new_thread_id = create_thread(client, file_id)
    mapping[pdf_path] = {'file_id': file_id, 'thread_id': new_thread_id}
    save_file_thread_mapping(mapping)
    print("Existing thread cleared and new thread created.")
    return new_thread_id

def send_messages_to_thread( thread_id, assistant_id, prompts_dict):
    """Sends messages to the thread based on the provided dictionary of prompts."""
    for section, prompt in prompts_dict.items():
        print(f"Asking about {section}: {prompt}")
        response = client.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id, messages=[{"role": "user", "content": prompt}])
        # Assuming you want to print the response from the assistant
        print("Response:", response.choices[0].message.content)
def add_message_and_get_response(client, thread_id, assistant_id, prompt):
    # Add the message to the thread
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=prompt
    )
    print(f"Message added: {prompt}")

    # Create a run to process the thread messages
    run_response = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
        model="gpt-4-turbo-preview",
        tools=[{"type": "retrieval"}]
    )
    print("Run created.")

    # Polling to wait for the run to complete
    run_id = run_response.id
    run_status = run_response.status
    while run_status not in ["completed", "failed"]:
        print("Waiting for run to complete...")
        time.sleep(2)  # Wait for 2 seconds before checking again
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run_id
        )
        run_status = run.status

    if run_status == "completed":
        # List messages in the thread to find the response
        thread_messages = client.beta.threads.messages.list(thread_id=thread_id)

        # Debug: Print all messages in reverse order
        for message in reversed(thread_messages.data):
            print(f"Debug: Message ID: {message.id}, Role: {message.role}")

        # Assuming the last message from the assistant is the response
        for message in reversed(thread_messages.data):
            if message.role == "assistant":

                response_message = message.content[0].text.value
                print(f"Response: {response_message}")
                return response_message

    print("Run failed or no response received.")
    return None


def api_send(pdf_path, prompt, clear_thread=True):
    mapping = load_file_thread_mapping()

    # Check if the thread exists for the PDF
    if pdf_path in mapping:
        print("PDF path exists in the mapping.")
        if clear_thread:
            # Clear the existing thread by creating a new one
            print("Clearing existing thread.")
            file_id = mapping[pdf_path]['file_id']  # Reuse the existing file ID
            thread_id = create_thread(client, file_id)  # Create a new thread
            mapping[pdf_path] = {'file_id': file_id, 'thread_id': thread_id}  # Update mapping
            save_file_thread_mapping(mapping)  # Save the updated mapping
        else:
            print("Using existing file and thread.")
            thread_id = mapping[pdf_path]['thread_id']
    else:
        # If the PDF path doesn't exist in the mapping, upload the file and create a new thread
        file_id = upload_file(client, pdf_path)
        thread_id = create_thread(client, file_id)
        mapping[pdf_path] = {'file_id': file_id, 'thread_id': thread_id}  # Update mapping
        save_file_thread_mapping(mapping)  # Save the updated mapping

    response = add_message_and_get_response(client, thread_id, 'asst_NcixO2BWUT7ExDHt5IoZQQTw', prompt)
    return response

