import tiktoken
from bs4 import BeautifulSoup
from openai import OpenAI
import re
import fitz  # PyMuPDF
from PyPDF2 import PdfReader  # For reading PDF files
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

tokenizer = tiktoken.get_encoding("cl100k_base")


def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PdfReader(file)
        text_by_pages = []
        for page in reader.pages:
            text_by_pages.append(page.extract_text())
    return text_by_pages

def call_openai_api(client, text, chat_id=None):
    response = client.chat.completions.create(
        model="gpt-4o-mini",

        messages=[
            {"role": "system",     "content": "You are to extract information from the text following the guidelines with the provided HTML and return an HTML <div> string after analyzing the text. If no citation is found, wait for the next chunk of text. The response should not be between ```html and ```, it should be a plain text response with HTML tags."
},
            {"role": "user", "content": text}
        ],
        max_tokens=2048,
        temperature=0.7,
        user=chat_id
    )
    message =response.choices[0].message.content.strip()


    return message, response.id




def process_pdf(pdf_path, prompt, reference=None,page_parsing=5):


    pages_text = extract_text_from_pdf(pdf_path)
    combined_response = ""
    chat_id = None
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    for i in range(0, len(pages_text), page_parsing):
        chunk_text = " ".join(pages_text[i:i+page_parsing])
        text_to_send = f"{prompt}\n\ntext: {chunk_text}"
        tokens = tokenizer.encode(text_to_send)
        text_to_send = tokenizer.decode(tokens)

        response_content, chat_id = call_openai_api(client, text_to_send, chat_id)
        if reference:
            response_content =f"<h1>Page {i+1}</h1>"+response_content
        combined_response += response_content

    return combined_response

