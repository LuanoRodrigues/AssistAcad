import json
import os

from Vector_Database.qdrant_handler import QdrantHandler

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # Load the variables from .env
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
# Load query history from a local file, if exists
def load_query_history(file_path='query_history.json'):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return {}
def add_query_to_history(query_text, embedding, query_history):
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
    """
        Check if a query already exists in the query history.
        If it exists, return the corresponding embedding.
        Otherwise, prompt the user to select from previous queries.

        Args:
            query_text (str): The query text to check in the history.
            query_history (dict): A dictionary containing previous queries and their embeddings.

        Returns:
            embedding (list): The embedding of the existing query or None if not selected.
        """

    # Check if the query exists in the query history
    if query_text in query_history:
        return query_history[query_text]['embedding']

    # If not, prompt the user to select from existing queries
    print("The query does not exist. Here's the history of previous queries:\n")

    history = {index + 1: key for index, key in enumerate(query_history.keys())}

    # Display the query history with numbers
    for index, query in history.items():
        print(f"{index}: {query}")

    try:
        # Prompt user to select from history or skip
        user_input = input("Pick a number to use an existing query (n=0 to skip): ").strip()

        # If the user chooses to skip
        if int(user_input) == 0:
            return None

        # Get the query text based on user selection
        query_text = history[int(user_input)]
        return query_history[query_text]['embedding']

    except (ValueError, KeyError) as e:
        print(f"Invalid input: {e}")
        return None
# Save the query history back to the file
def save_query_history(query_history, file_path='query_history.json'):
    with open(file_path, 'w') as f:
        json.dump(query_history, f, indent=4)


class EmbeddingsHandler:
    def __init__(self, qdrant_url="http://localhost:6333"):
        self.qdrant_handler = QdrantHandler(qdrant_url)

    def process_and_append(self, paragraph_count,paper_id, article_title,section_title, paragraph_title, paragraph_text, paragraph_blockquote):
        """Process embeddings and append data to the collection."""

        # Get embeddings for both title and text
        text_embedding = get_embedding(paragraph_text)

        # Get the collection name based on the paper_id
        collection_name = f"paper_{paper_id}"

        # Append data to the collection and get operation info
        operation_info = self.qdrant_handler.append_data(
            collection_name=collection_name,  # Your collection name
            article_title=article_title,
            section_title=section_title,  # Section title
            paragraph_title=paragraph_title,  # Paragraph title
            paragraph_text=paragraph_text,  # Paragraph text
            paragraph_blockquote=paragraph_blockquote,  # Blockquote (if available)
            custom_id=paper_id+paragraph_count,  # Your custom ID (e.g., "SV5QMQSM")
            text_embedding=text_embedding,  # Embedding for the text
            paragraph_count=paragraph_count
        )

        # Check if the operation was successful
        if operation_info.status == "completed":
            print(
                f"Data successfully appended to the collection '{collection_name}' for paragraph '{paragraph_text}'.")
            return True
        else:
            print(f"Failed to append data to collection '{collection_name}'. Status: {operation_info.status}")
        return operation_info



