import json
import os

import openai
from Vector_Database.qdrant_handler import QdrantHandler

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # Load the variables from .env

# Load query history from a local file, if exists
def load_query_history(file_path='query_history.json'):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return {}
def add_query_to_history(self,query_text, embedding, query_history):
    query_history[query_text] = {
        'embedding': embedding
    }
    save_query_history(query_history)
def query_with_history(query_text):
    # Load the query history from the local file
    query_history = load_query_history()

    # Check if the query already exists in history
    existing_embedding = check_existing_query(query_text=query_text, query_history=query_history)

    if existing_embedding:
        print(f"Using the existing embedding for '{query_text}'")
        return existing_embedding
    else:
        # Generate a new embedding and add it to the history
        print(f"Generating a new embedding for '{query_text}'...")
        new_embedding = get_embedding(query_text)
        add_query_to_history(query_text, new_embedding, query_history)
        return new_embedding

def get_embedding(text):
    """Generate an embedding for the given text using OpenAI's most capable embedding model."""
    response = client.embeddings.create(
        model="text-embedding-3-large",  # Use the most capable model, with 3,072 dimensions
        input=text
    )
    return response.data[0].embedding
def check_existing_query(query_text, query_history):
    if query_text in query_history:
        print(f"The query '{query_text}' already exists in history.")
        user_input = input("Do you want to use the existing query? (yes/no): ").strip().lower()
        if user_input == 'yes':
            return query_history[query_text]['embedding']
    return None
# Save the query history back to the file
def save_query_history(query_history, file_path='query_history.json'):
    with open(file_path, 'w') as f:
        json.dump(query_history, f, indent=4)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class EmbeddingsHandler:
    def __init__(self, qdrant_url="http://localhost:6333"):
        self.qdrant_handler = QdrantHandler(qdrant_url)



    def process_and_append(self, paper_id, section_title, paragraph_title, paragraph_text, paragraph_blockquote):
        """Process embeddings and append data to the collection."""
        # Get embeddings for both title and text
        title_embedding = self.get_embedding(paragraph_title)
        text_embedding = self.get_embedding(paragraph_text)

        # Get the collection name
        collection_name = f"paper_{paper_id}"

        # Append data to the collection
        # Somewhere in your code where you call append_data
        operation_info = self.qdrant_handler.append_data(
            collection_name=collection_name,  # Your collection name
            section_title=section_title,  # Section title
            paragraph_title=paragraph_title,  # Paragraph title
            paragraph_text=paragraph_text,  # Paragraph text
            paragraph_blockquote=paragraph_blockquote,  # Blockquote (if available)
            custom_id=paper_id,  # Your custom ID (e.g., "SV5QMQSM")
            title_embedding=title_embedding,  # Embedding for the title
            text_embedding=text_embedding  # Embedding for the text
        )

        return operation_info

    # Check if a query exists in history and ask user whether to reuse it


    # Add a new query and its embedding to history


    # Main function to handle embedding and query history
