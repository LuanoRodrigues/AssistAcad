import PyPDF2
import tiktoken
import docx
from bs4 import BeautifulSoup
from openai import OpenAI
import re
import time
from docx import Document
import fitz  # PyMuPDF
from PyPDF2 import PdfReader  # For reading PDF files
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

tokenizer = tiktoken.get_encoding("cl100k_base")


import json




def prepare_batch_requests(text_to_send, index, id, tag):
    return {
        "custom_id": f"{id}-{tag}-part-{index}",
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are to extract information from the text following the guidelines with the provided HTML and return an HTML <div> string after analyzing the text. If no citation is found, wait for the next chunk of text. The response should not be between ```html and ```, it should be a plain text response with HTML tags."},
                {"role": "user", "content": text_to_send}
            ],
            "max_tokens": 2048
        }
    }

def call_openai_api(client, text):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are to extract information from the text following the guidelines with the provided HTML and return an HTML <div> string after analyzing the text. If no citation is found, wait for the next chunk of text. The response should not be between ```html and ```, it should be a plain text response with HTML tags."},
            {"role": "user", "content": text}
        ],
        max_tokens=2048,
        temperature=0.7
    )

    message = response.choices[0].message.content.strip()
    return message, response.id

def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text_by_pages = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)  # Load each page
        text = page.get_text("text")  # Extract text from the page
        if text.strip():  # Only add non-empty text
            text_by_pages.append(text)

    return text_by_pages
# Extract text from PDF



def write_batch_requests_to_file(batch_requests, file_name=r"C:\Users\luano\Downloads\AcAssitant\Batching_files\batchinput.jsonl"):
    with open(file_name, "a+", encoding="utf-8") as f:
        for request in batch_requests:
            f.write(json.dumps(request) + "\n")
    return file_name

def upload_batch_file(file_name):
    """
    Upload a JSONL file to OpenAI.

    Args:
    - file_name (str): The name of the JSONL file to upload.

    Returns:
    - str: The ID of the uploaded batch input file.
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Upload the batch input file
    with open(file_name, "rb") as f:
        batch_input_file = client.files.create(file=f, purpose="batch")
    batch_input_file_id = batch_input_file.id
    print(f"[DEBUG] Batch input file {file_name} uploaded successfully. File ID: {batch_input_file_id}")

    return batch_input_file_id

def create_batch(batch_input_file_id):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Create the batch
    batch = client.batches.create(
        input_file_id=batch_input_file_id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={"description": "Batch processing for statements_citations"}
    )
    return batch.id

def check_save_batch_status(batch_id):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    while True:
        status = client.batches.retrieve(batch_id)
        print(f"[DEBUG] Checking status of batch ID {batch_id}: {status.status}")
        if status =="completed":
            retrieve_batch_results(batch_id)
            break
        if status.status in ['failed', 'expired']:
            break
        time.sleep(60)  # Check status every minute
    save_batch_object(r"C:\Users\luano\Downloads\AcAssitant\Batching_files", status)
    return status.status

def retrieve_batch_results(batch_id):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    status = client.batches.retrieve(batch_id)
    if status.status == 'completed':
        output_file_id = status.output_file_id
        file_response = client.files.content(output_file_id)
        results = [json.loads(line) for line in file_response.text.splitlines()]
        print("[DEBUG] Batch processing completed successfully.")
        return results
    else:
        print("[DEBUG] Batch processing failed or expired.")
        return None
def process_batch_output(output_file_path):
    """
    Processes the batch output file to extract data into a list of dictionaries.

    Args:
    - output_file_path (str): Path to the batch output JSONL file.

    Returns:
    - list: A list of dictionaries, each containing data from one line of the output file.
    """
    results = []
    with open(output_file_path, 'r') as file:
        for line in file:
            data = json.loads(line)
            results.append(data)
    return results


def save_batch_object(directory, batch_object):
        # Ensure the directory exists
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Define the file path
        file_path = os.path.join(directory, 'batch_objects.json')

        # Load existing batch objects if the file exists
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                batch_objects = json.load(file)
        else:
            batch_objects = []

        # Append the new batch object
        batch_objects.append(batch_object)

        # Save the batch objects back to the file
        with open(file_path, 'w') as file:
            json.dump(batch_objects, file, indent=4)

def get_batch_ids(directory=r"C:\Users\luano\Downloads\AcAssitant\Batching_files"):
    # Define the file path
    file_path = os.path.join(directory, 'batch_objects.json')

    # Load and return the last batch object if the file exists
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            batch_objects = json.load(file)
            if batch_objects:
                return batch_objects[-1]
    return None
def read_or_download_batch_output(batch_id, directory=r"C:\Users\luano\Downloads\AcAssitant\Batching_files"):
    """
    Checks for the existence of an output.jsonl file, reads it if present, or downloads it if the batch is completed.

    Args:
    - file_name (str): The base file name of the batch job.
    - directory (str): Directory where batch files are stored.

    Returns:
    - str: Path to the batch output file.
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    output_file_path = os.path.join(directory, f"{batch_id}_output.jsonl")

    if not os.path.exists(output_file_path):
        # Retrieve the batch status
        batch_object = client.batches.retrieve(batch_id)

        if batch_object.status == 'completed':
            output_file_id = batch_object.output_file_id
            file_response = client.files.retrieve_content(output_file_id)
            # Write the binary content to a file
            with open(output_file_path, 'w', encoding='utf-8') as output_file:
                output_file.write(file_response)
            print(f"[INFO] Downloaded batch output to {output_file_path}")
        else:
            print(f"[INFO] Batch {batch_id} status is {batch_object.status}. Output not ready.")
            return None

    return output_file_path




def process_pdf(file_path, prompt, reference=None, page_parsing=1, batch=False, id="", tag="tag",store_only=False,collection=""):

    pages_text = extract_text_from_pdf(file_path.replace("docx", "pdf"))


    combined_response = ""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    batch_requests = []

    for i in range(0, len(pages_text), page_parsing):

        chunk_text = " ".join(pages_text[i:i + page_parsing])
        text_to_send = f"{prompt}\n\ntext: {chunk_text}"

        if batch or store_only:
            batch_request = prepare_batch_requests(text_to_send=text_to_send,index= i // page_parsing, id=id, tag=tag)
            batch_requests.append(batch_request)
        else:
            response_content, chat_id = call_openai_api(client, text_to_send)
            if reference:
                response_content = response_content.replace("</blockquote>",
                                                            f"{reference.replace(')', f' p.{i + 1})')}</blockquote>")
            combined_response += response_content

    if store_only:
        file_name = rf"C:\Users\luano\Downloads\AcAssitant\Batching_files\{collection}batch.jsonl"
        write_batch_requests_to_file(batch_requests, file_name)
        print(f"[DEBUG] Stored batch requests locally in {file_name}")
        return None  # Return None as we are storing only

    return combined_response if not batch else batch_requests
def normalize_text(text):
    return re.sub(r'\s+', ' ', text).lower().strip()

def escape_special_characters(section):
    section = re.escape(section).replace(r'\ ', r'\s+')
    return section

def extract_sections(file_path, sections):
    # Initialize the text variable
    text = ''

    # Check the file extension and read the file accordingly
    if file_path.endswith('.pdf'):
        # Read the PDF
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in range(len(reader.pages)):
                text += reader.pages[page].extract_text()
    elif file_path.endswith('.docx'):
        # Read the DOCX
        doc = docx.Document(file_path)
        for paragraph in doc.paragraphs:
            text += paragraph.text + '\n'
    else:
        raise ValueError("Unsupported file type. Only PDF and DOCX files are supported.")

    # Normalize the text
    text = normalize_text(text)

    # Normalize the section names
    sections = [normalize_text(section) for section in sections]

    # Initialize the dictionary to store sections and their text
    section_texts = {section: None for section in sections}

    # Generate the regex pattern for splitting text into sections
    split_pattern = '|'.join([escape_special_characters(section) for section in sections])
    split_pattern = f"({split_pattern})"

    # Split the text into sections
    parts = re.split(split_pattern, text)

    # Assign the body text to the corresponding sections
    for i in range(1, len(parts), 2):
        section_name = parts[i].strip()
        body_text = parts[i + 1].strip() if (i + 1) < len(parts) else ''
        section_texts[section_name] = body_text

    # Print sections that failed to get a body text
    for section, body_text in section_texts.items():
        if not body_text:
            print(f"Section '{section}' failed to get a body text.")

    return section_texts
def process_document_sections(file_path, sections):
    section_texts = extract_sections(file_path, sections)
    chat_id = None
    combined_response = ""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    for section, body_text in section_texts.items():
        if body_text:
            html_section = f"<h2>{section}</h2>"
            html_body_text = f"<p>{body_text}</p>"
            text_to_send = html_section + html_body_text
            prompt = f"Read the provided PDF carefully, paragraph by paragraph, and perform an in-depth section analysis of the section: '{section}' in the attached PDF document. Carefully count each paragraph. For each key finding/idea, reference the specific paragraph numbers (e.g., 'Paragraph 1,' 'Paragraphs 2,3') accompanied by the respective paragraph(s) with direct quotes enclosed by strong tags to illustrate or support the key. Follow this structure: ```html <h3>Paragraph 1 - [key finding in one short sentence]</h3> <blockquote>'<strong>[first paragraph and statement enclosed by strong tags in the form of a full sentence. The paragraph should be exactly as it is in the text, strictly unmodified. Before using it, check for a full match between the sentence and the text]</strong>'</blockquote> <h3>Paragraphs 2,3 - [Next key finding or idea in one short sentence]</h3> <blockquote>'<strong>[second paragraph and statement enclosed by strong tags in the form of a full sentence. The paragraph should be exactly as it is in the text, strictly unmodified. Before using it, check for a full match between the sentence and the text]</strong>'</blockquote> <blockquote>'<strong>[Direct quote from paragraph 3]</strong>'</blockquote> [Continue this structure for additional paragraphs or groups of paragraphs, correlating each with its key findings or ideas until the end of the section]``` This methodical approach ensures a structured and precise examination of the section: '{section}', organized by the specific paragraphs and their associated key findings or ideas, all supported by direct quotations from the document for a comprehensive and insightful analysis until the end of the provided section. Take your time, and review the final output for accuracy and consistency in HTML formatting and citation-context alignment. note1: Output format: HTML in a code block."
            text_to_send =f"{prompt}\n\ntext: {body_text}"
            response_content, chat_id = call_openai_api(client, text_to_send, chat_id)
            combined_response += html_section +response_content
    return combined_response
