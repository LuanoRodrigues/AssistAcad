import hashlib
import json
import os
from uuid import uuid4

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # Load the variables from .env
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
# Load query history from a local file, if exists
def load_query_history(file_path='query_history.json'):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}
def add_query_to_history(query_text, embedding, query_history):
    query_history[query_text] = {
        'embedding': embedding
    }
    save_query_history(query_history)
def query_with_history(query_text,batch=False,cache_location='query_history.json'):
    # Load the query history from the local file
    query_history = load_query_history(file_path=cache_location)

    # Check if the query already exists in history
    existing_embedding = check_existing_query(query_text=query_text, query_history=query_history)

    if existing_embedding:
        print(f"Using the existing embedding for '{query_text}'")
        return existing_embedding
    else:
        if batch:
            prepare_batch_requests(text_to_send=query_text)
        else:
            # Generate a new embedding and add it to the history
            print(f"Generating a new embedding for '{query_text}'...")
            new_embedding = get_embedding(query_text)
            add_query_to_history(query_text, new_embedding, query_history)
            return new_embedding
def append_to_jsonl_file(request, file_path=r"C:\Users\luano\Downloads\AcAssitant\Files\Batching_files\batch_input.jsonl"):
    with open(file_path, "a") as f:

        f.write(json.dumps(request) + "\n")

def prepare_batch_requests(text_to_send, model="text-embedding-3-large"):
    unique_id = uuid4()
    hash_object = hashlib.sha256()

    # Create a unique hash for the request
    hash_object.update(text_to_send.encode('utf-8'))
    paragraph_hash = hash_object.hexdigest()[:8]

    # Construct the JSON request
    results = {
        "custom_id": f"{unique_id}-{paragraph_hash}",
        "method": "POST",
        "url": "/v1/embeddings",
        "body": {
            "model": model,
            "input": text_to_send,
            "response_format": "json",
            "max_tokens": 2048
        }
    }
    append_to_jsonl_file(results)
    return results
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
    else:
        return None


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



