import hashlib
import json
from datetime import time
from difflib import SequenceMatcher
from typing import List, Dict, Optional, Union, Tuple
import math
import re
# from NLP_module.normalise_texts import
from collections import defaultdict
import logging

import nltk
import numpy as np
from nltk import ngrams, PorterStemmer
from nltk.corpus import wordnet, stopwords
from tensorboard.compat.tensorflow_stub.tensor_shape import vector

from NLP_module.patterns_data import patterns_number_brackets
# from NLP_module.normalise_texts import
from Vector_Database.embedding_handler import get_embedding,query_with_history
from qdrant_client import QdrantClient
from qdrant_client.grpc import SparseVectorParams, Modifier
from qdrant_client.models import Distance, VectorParams, PointStruct
from qdrant_client.http import models  # Import models from qdrant_client.http
from qdrant_client.http.exceptions import UnexpectedResponse
from sklearn.cluster._hdbscan import hdbscan
from sklearn.decomposition import LatentDirichletAllocation as LDA
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import silhouette_score
from sklearn.metrics.pairwise import cosine_distances
# from Vector_Database.embedding_handler import query_with_history
from qdrant_client.http.models import VectorParams, SparseVectorParams, Distance, Modifier
from Pychat_module.gpt_api import call_openai_api
import uuid
from File_management.exporting_files import export_results
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from yellowbrick.cluster import KElbowVisualizer
from kneed import KneeLocator
import matplotlib.pyplot as plt
# Helper Functions

def extract_phrases(query: str, max_n: int = 3) -> List[str]:
    tokens = [word for word in nltk.word_tokenize(query.lower()) if word.isalnum()]
    phrases = set()
    for n in range(2, max_n + 1):
        for gram in ngrams(tokens, n):
            phrases.add(' '.join(gram))
    return list(phrases)
import spacy


def get_synonyms_dynamic(token: str) -> List[str]:
    """
    Dynamically fetch synonyms for the given token using WordNet.
    """
    synonyms = set()

    for syn in wordnet.synsets(token):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name())  # Get all the lemma names for synonyms

    return list(synonyms)


def normalize_text2(text: str) -> List[str]:
    """
    Normalize the input text by lowercasing, removing non-alphanumeric characters,
    and splitting into tokens. This replaces the previous preprocess function.
    """
    # Convert to lowercase
    normalized_text = text.lower()

    # Remove non-alphanumeric characters (except spaces)
    normalized_text = re.sub(r'[^a-z0-9\s]', '', normalized_text)

    # Split text into tokens (words)
    tokens = normalized_text.split()

    return tokens


# Load spaCy model
nlp = spacy.load('en_core_web_sm')
def calculate_dynamic_weights(overlap: float, proximity: int) -> Dict[str, float]:
    """
    Dynamically calculate weights based on overlap and proximity.
    Overlap is a value between 0 and 1, proximity is the distance between tokens.
    """
    # Base weights for different sections, dynamically scaled by overlap
    section_weight = 1.0 + (overlap * 0.5)  # Scale section weight by overlap
    paragraph_title_weight = 1.0 + (overlap * 0.3)  # Slightly less emphasis on paragraph title
    text_weight = 1.0 + (overlap * 0.2)  # Less weight on main text overlap

    # Apply proximity boost dynamically
    proximity_boost_weight = 0.5 + (1.0 / (proximity + 1))  # Inversely proportional to proximity

    return {
        'section_weight': section_weight,
        'paragraph_title_weight': paragraph_title_weight,
        'text_weight': text_weight,
        'proximity_boost_weight': proximity_boost_weight
    }


def preprocess_text(text: str, phrases: Optional[List[str]] = None) -> List[str]:
    """
    Preprocess text by lowercasing, replacing phrases, removing non-alphabetic characters,
    lemmatizing, and extracting only nouns and adjectives using spaCy.

    :param text: Input text to be processed.
    :param phrases: Optional list of phrases to replace with underscores.
    :return: List of lemmatized tokens (nouns and adjectives only).
    """
    # Lowercase the text
    text = text.lower()
    stopwords_tailored = ['attribution','state','cyber']
    # Replace custom phrases with underscore versions (e.g., "New York" -> "New_York")
    if phrases:
        for phrase in phrases:
            phrase_pattern = re.escape(phrase)
            text = re.sub(r'\b' + phrase_pattern + r'\b', phrase.replace(' ', '_'), text)

    # Remove non-alphabetic characters except underscores
    text = re.sub(r'[^a-zA-Z_\s]', '', text)

    # Process text using spaCy to get nouns and adjectives
    doc = nlp(text)

    # Extract lemmas for nouns, proper nouns, and adjectives, excluding stop words and punctuation
    tokens = [token.lemma_.lower() for token in doc if
              token.pos_ in {"NOUN", "PROPN", "ADJ"} and not token.is_stop and not token.is_punct and token.lemma_.lower() not in stopwords_tailored]

    return tokens

def get_synonyms(word: str) -> set:
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            name = lemma.name().replace('_', ' ').lower()
            if name != word:
                synonyms.add(name)
    return synonyms


# Example text normalization function
def normalize_text(text: str) -> List[str]:
    """
    Normalize the text by converting to lowercase, removing punctuation, and stemming words.
    """
    # Lowercase and remove punctuation
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)

    # Tokenize text
    tokens = text.split()

    # Apply stemming or lemmatization
    ps = PorterStemmer()
    tokens = [ps.stem(token) for token in tokens if token not in stopwords.words('english')]

    return tokens


# Example token overlap function using normalized text
def token_overlap(query_tokens: List[str], text_tokens: List[str]) -> int:
    """
    Calculate the number of matching tokens between query and text after normalization.
    """
    normalized_query = normalize_text(' '.join(query_tokens))
    normalized_text = normalize_text(' '.join(text_tokens))

    # Find the overlap in normalized tokens
    overlap = set(normalized_query).intersection(set(normalized_text))

    return len(overlap)


def apply_proximity_boost(text: str, query_tokens: List[str], threshold: int) -> bool:
    """
    Determine if a proximity boost should be applied by checking the closeness of query tokens in the text.
    """
    normalized_text = normalize_text(text)
    for token in query_tokens:
        if token in normalized_text:
            # Check if the distance between tokens is within the threshold
            return True
    return False


def token_in_text(tokens: set, text_tokens: List[str]) -> bool:
    return any(token in text_tokens for token in tokens)

def normalize_score(score: float) -> float:
    return math.log1p(score)

def get_headings_for_clusters(clusters):
    aggregated_results = []
    # print(replace_ids_with_content(structure=result_text, clusters=clusters[0]))
    # input('')
    blockquote= []
    # Loop over the clusters dictionary
    for cluster_key, cluster_value in clusters.items():
        # Construct the data for this cluster
        data = {item["id"]: item["content"] for item in cluster_value}  # Full tuple content for replacement

        # Format the data for the API prompt
        data_str = "\n".join([f"id = {key}: topic_sentence = {value[0].strip()}" for key, value in data.items()])

        # Call the API (replace this with actual API call)
        result_text = call_openai_api(function='get_headings', data=data_str, id='')


        # Parse the API result text to a dictionary if it's in JSON format
        if isinstance(result_text, str):
            try:
                result_text = json.loads(result_text)  # Convert to a dictionary
            except json.JSONDecodeError as e:
                print(f"Failed to decode API response: {e}")
                continue
        # Replace ids with paragraph content (both tuple elements)
        updated_structure = replace_ids_with_content(result_text, cluster_value)
        # Append parsed result to the aggregated results
        aggregated_results.append(updated_structure)

    # Use the overarching theme extracted from the first cluster
    return aggregated_results

def write_and_export_sections(clusters, filename=r"C:\Users\luano\Downloads\AcAssitant\Files\Thematic_Review",export_to=['doc', 'html']):

    # with open('final_structural.txt','r',encoding='utf-8') as f:
    #     sections = eval(f.read())
    # print(type(sections))
    # export_results(filename=str(filename), structure=sections,export_to= export_to)
    # input()
    # input(replace_ids_with_content(structure=to_be_replaced,clusters=clusters_to_test[0]))
    data=get_headings_for_clusters(clusters=clusters)
    data_wrote = []
    for data_item in data:
        theme = data_item.get('overarching_theme', 'No Theme')


        # Iterate through the structure and call the OpenAI API
        for idx, heading in enumerate(data_item.get('structure', [])):

            # Ensure heading has the 'heading' key before processing
            if 'heading' in heading:
                # Generate context for the current heading
                context = get_context(data_item, heading)

                # Concatenate context and data for the API request
                data_to_send = concatenate_context_and_data(heading, context)

                # Call the OpenAI API with the provided function and data
                result = call_openai_api(data=data_to_send, id=f'heading-{idx}', function='thematic_review')
                data_wrote.append(result)

            else:
                print(f"Skipping entry at index {idx} as it doesn't have a 'heading' key.")

    # Prepare the final structure for export
    final_structure = {
        'overarching_theme': theme,
        'structure': data_wrote
    }

    # Ensure that final structure is correct for export
    print('Final structure:', final_structure)
    # with open('final_structural.txt','w') as f:
    #     f.write(f)
    # Adjust the filename to be unique for each theme (optional)
    unique_filename = f"{filename}_{theme.replace(' ', '_')}"

    # Call the export_results function to handle the export
    export_results(structure=final_structure, filename=unique_filename, export_to=export_to)

def replace_ids_with_content(structure, clusters,feature='content'):
    # Extract the overarching theme from the first entry in the structure
    overarching_theme = structure["structure"][0]["title"] if structure["structure"] and structure["structure"][0]["heading"] == 'h1' else "Unknown Theme"
    # Iterate over the structure and replace paragraph_ids with corresponding content (both parts of the tuple)
    # Create a dictionary to map IDs to their tuple content (both topic sentence and full content)
    id_to_content = {item['id']: item[feature] for item in clusters}
    # Iterate over the structure and replace paragraph_ids with corresponding content
    for entry in structure["structure"]:

        if 'paragraph_ids' in entry:
            # Initialize new lists to hold topic sentences and paragraphs
            topic_sentences = []
            paragraphs = []

            # Replace each paragraph_id with its corresponding topic sentence and paragraph content
            for par_id in entry["paragraph_ids"]:

                if par_id in id_to_content.keys():

                    topic_sentence, paragraph_content = id_to_content[par_id]
                    topic_sentences.append(topic_sentence)  # Add the topic sentence
                    paragraphs.append(paragraph_content)  # Add the full paragraph

                else:
                    topic_sentences.append(f"Topic sentence for {par_id} not found")
                    paragraphs.append(f"Full content for {par_id} not found")
            # Add topic sentences and paragraphs back into the structure
            entry["topic_sentence"] = topic_sentences # Join sentences into a single string
            entry["paragraph_ids"] = paragraphs
    # Add the overarching theme to the structure
    structure["overarching_theme"] = overarching_theme

    return structure


def get_context(data, current_heading):
    """
    This function generates the context for the current heading based on its level, up to h5.
    """
    context = ""
    # Tracks the parent headings
    parent_context = []

    # Loop through the structure to build the context
    for heading in data['structure']:
        # Check if it's an h1 heading (Overarching theme and h1)
        if heading['heading'] == 'h1':
            parent_context.append(f"Main Heading (h1): {heading['title']}")

        # Add context for h2, h3, h4, and h5
        if heading == current_heading:
            if current_heading['heading'] == 'h2':
                parent_context.append(f"Subheading (h2): {current_heading['title']}")
            elif current_heading['heading'] == 'h3':
                parent_context.append(f"Sub-subheading (h3): {current_heading['title']}")
            elif current_heading['heading'] == 'h4':
                parent_context.append(f"Sub-sub-subheading (h4): {current_heading['title']}")
            elif current_heading['heading'] == 'h5':
                parent_context.append(f"Sub-sub-sub-subheading (h5): {current_heading['title']}")
            break

    # Combine overarching theme and parent headings to create full context
    context = f"Overarching theme: {data['overarching_theme']}\n" + "\n".join(parent_context)

    return context




def concatenate_context_and_data(heading, context):
    """
    This function concatenates the context with the heading's data for the final request.
    """
    # Combine context with the heading's data to create the full input for the API
    combined_data = {
        "context": context,
        "title": heading['title'],
        "topic_sentence_and_paragraph": f'topic sentenced:{heading.get('topic_sentence', [])}, references:{heading.get('paragraph_ids', [])}',
    }

    return combined_data

class QdrantHandler:
    def __init__(self, qdrant_url="http://localhost:6333"):
        self.qdrant_client = QdrantClient(url=qdrant_url)

    def process_and_append(self, metadata,paragraph_count,collection_name, article_title,section_title, keywords, paragraph_title, paragraph_text, paragraph_blockquote):
        """Process embeddings and append data to the collection."""

        # Get embeddings for both title and text
        text_embedding = get_embedding(paragraph_title)

        # Append data to the collection and get operation info
        operation_info = self.append_data(
            collection_name=collection_name,  # Your collection name
            article_title=article_title,
            section_title=section_title,  # Section title
            paragraph_title=paragraph_title,  # Paragraph title
            paragraph_text=paragraph_text,  # Paragraph text
            paragraph_blockquote=paragraph_blockquote,  # Blockquote (if available)
            text_embedding=text_embedding,  # Embedding for the text
            paragraph_count=paragraph_count,
            metadata=metadata,
            keywords=keywords,
        )

        # Check if the operation was successful
        if operation_info.status == "completed":
            print(
                f"Data successfully appended to the collection '{collection_name}' for paragraph '{paragraph_text}'.")
            return True
        else:
            print(f"Failed to append data to collection '{collection_name}'. Status: {operation_info.status}")
        return operation_info

    def create_collection(self, collection_name, vector_size=3072,vector=True):
        """Create a collection in Qdrant based on a given paper ID if it does not exist."""


        # Check if the collection already exists
        try:
            self.qdrant_client.get_collection(collection_name)
            print(f"Collection '{collection_name}' already exists.")

            return False  # Collection already exists
        except Exception as e:
            print(f"Collection '{collection_name}' not found. Creating new collection.")
            if vector:
                sparse_vectors = {
                    "paragraph_text": models.SparseVectorParams(
                        modifier="idf"  # Use IDF for sparse vector search
                    ),
                    "paragraph_title": models.SparseVectorParams(
                        modifier="idf"  # Use IDF for sparse vector search
                    ),
                    "section_title": models.SparseVectorParams(
                        modifier="idf"  # Use IDF for sparse vector search
                    )
                }

                # HNSW configuration for high-accuracy vector search
                hnsw_config = models.HnswConfigDiff(
                    ef_construct=512,
                    m=64
                )

                # Create the collection with vectors and sparse indexing
                self.qdrant_client.create_collection(

                    collection_name=collection_name,
                    vectors_config=models.VectorParams(size=3072, distance=models.Distance.COSINE),

                    sparse_vectors_config=sparse_vectors,  # Correctly use sparse_vectors
                    hnsw_config=hnsw_config,
                    on_disk_payload=False  # Store payload data on disk to save RAM
                )

                # Create full-text indexes on paragraph_text, paragraph_title, and section_title
                text_fields = ["paragraph_text", "paragraph_title", "section_title"]
                for field in text_fields:
                    self.qdrant_client.create_payload_index(
                        collection_name=collection_name,
                        field_name=field,
                        field_schema=models.TextIndexParams(
                            type="text",
                            tokenizer=models.TokenizerType.WORD,
                            min_token_len=2,
                            max_token_len=15,
                            lowercase=True
                        )
                    )

                print(f"Collection '{collection_name}' created successfully with vector and full-text search.")
                return True  # Collection was newly created
            if not vector:
                # Create the collection with vectors and sparse indexing
                self.qdrant_client.create_collection(

                    collection_name=collection_name,
                    vectors_config=models.VectorParams(size=3072, distance=models.Distance.COSINE),
                    on_disk_payload=False  # Store payload data on disk to save RAM
                )

    def append_data(self, collection_name,text_embedding,metadata='', keywords='',paragraph_count='',article_title='',section_title='', paragraph_title='', paragraph_text='', paragraph_blockquote='',
                    custom_id='',vector=True):
        """
        Insert embeddings for paragraph title and paragraph text into the collection with proper handling for both vectors.
        """
        if vector:
            hash_object = hashlib.sha256(paragraph_title.encode('utf-8'))
            # Convert the hash to an integer
            paragraph_id = int(hash_object.hexdigest(), 16) % (10 ** 8)  # Limiting to 8 digits




            # Structure the payload, storing custom ID and other metadata
            payload = {
                "article_title":article_title,
                "section_title": section_title,
                "paragraph_title": paragraph_title,
                "paragraph_text": paragraph_text,
                "paragraph_blockquote": paragraph_blockquote,  # Include blockquote information
                "custom_id": custom_id,  # Store the custom ID in the payload
                "paragraph_count":paragraph_count,
                "metadata":metadata,
                "keywords":keywords
            }

            # Insert data into Qdrant with both title and text embeddings
            operation_info = self.qdrant_client.upsert(
                collection_name=collection_name,
                points=[
                    PointStruct(
                        id=paragraph_id,  # Use UUID as point ID
                        vector=text_embedding,  # Insert the text embedding for the paragraph text
                        payload=payload  # Store metadata, including custom ID
                    )
                ]
            )
        if not vector:
            hash_object = hashlib.sha256(collection_name.encode('utf-8'))
            # Convert the hash to an integer
            paragraph_id = int(hash_object.hexdigest(), 16) % (10 ** 8)  # Limiting to 8 digits
            # Insert data into Qdrant with both title and text embeddings
            operation_info = self.qdrant_client.upsert(
                collection_name=collection_name,
                points=[
                    PointStruct(
                        id=paragraph_id,  # Use UUID as point ID
                        vector=text_embedding,  # Insert the text embedding for the paragraph text

                    )
                ]
            )
        print(
            f"Inserted data for paragraph '{paragraph_title}' under section '{section_title}' with custom ID '{custom_id}'.")
        return operation_info

    def cluster_paragraphs(self, collection_names="", n_clusters=None, max_clusters=10,method=''):
        """
        Perform clustering on paragraph vectors from multiple collections in Qdrant and group paragraphs based on their vector similarity.
        If a valid number of clusters is provided, use that number for clustering.
        Otherwise, automatically detect the optimal number of clusters using the Elbow Method.

        Parameters:
            collection_names (list): A list of Qdrant collection names where paragraphs are stored.
            n_clusters (int, optional): The number of clusters to use. If None, the optimal number of clusters will be calculated.
            max_clusters (int): The maximum number of clusters to test for the optimal k. Default is 10.

        Returns:
            clustered_paragraphs (dict): A dictionary where each key is a cluster label and each value is a list of paragraph texts.
        """

        paragraph_vectors = []
        paragraph_data = []  # List to store both the title and text as a tuple

        # Step 1: Fetch vectors and corresponding paragraph texts from each collection
        for collection_name in collection_names:
            try:
                # Retrieve all points with vectors from the collection using scroll (no need for IDs)
                scroll_results = self.qdrant_client.scroll(
                    collection_name=collection_name,
                    with_payload=True,
                    with_vectors=True,  # Retrieve vectors
                    limit=1000  # Adjust the limit as needed
                )[0]
            except Exception as e:
                print('error: ', e)
                continue
            # print(len(scroll_results))
            # input('above')
            for scroll_result in scroll_results:
                vector = scroll_result.vector  # Assuming "text_embedding" is the vector field
                text = scroll_result.payload['paragraph_text']  # Extract paragraph text from payload
                title = scroll_result.payload['paragraph_title']  # Extract paragraph title from payload
                blockquote = scroll_result.payload['paragraph_blockquote']  # Extract paragraph text from payload
                # print(blockquote)
                if vector and text and title:

                    paragraph_id = str(uuid.uuid4()).split('-')[0]
                    paragraph_vectors.append(vector)
                    paragraph_data.append({'id':paragraph_id,'content':(title, text),'content_html':(title, blockquote)})  # Store tuple (title, text)

            # Step 2: Apply clustering based on the selected method
        if method == "hdbscan":
            print("Using HDBSCAN with cosine similarity.")
            cosine_distance_matrix = cosine_distances(paragraph_vectors)

            clusterer = hdbscan.HDBSCAN(
                metric='precomputed',  # Use precomputed cosine distance matrix
                min_cluster_size=5,  # Allow smaller clusters (tune this as needed)
                min_samples=3,  # Adjust for noise tolerance
                cluster_selection_epsilon=0.1,  # Helps separate clusters more finely
                allow_single_cluster=False  # Prevents collapsing everything into a single cluster
            )

            # Fit the HDBSCAN model on the precomputed cosine distance matrix
            cluster_labels = clusterer.fit_predict(cosine_distance_matrix)

        elif method == "agglomerative":
            print("Using Agglomerative Clustering with cosine similarity.")
            cosine_distance_matrix = cosine_distances(paragraph_vectors)
            clusterer = AgglomerativeClustering(n_clusters=n_clusters, linkage='average')
            cluster_labels = clusterer.fit_predict(cosine_distance_matrix)

        elif method == "lda":
            print("Using Latent Dirichlet Allocation (LDA).")
            vectorizer = CountVectorizer(max_features=5000)  # Adjust max_features as needed
            doc_term_matrix = vectorizer.fit_transform(
                [data['content'][1] for data in paragraph_data])  # Use paragraph texts

            # Apply LDA to the document-term matrix
            lda_model = LDA(n_components=n_clusters, random_state=42)
            lda_fit = lda_model.fit_transform(doc_term_matrix)

            # Assign each paragraph to the most likely topic
            cluster_labels = np.argmax(lda_fit, axis=1)

        else:  # Default to K-Means
            if n_clusters is None:
                cluster_labels =self.cluster_K_means(vectors=paragraph_vectors,n_clusters=n_clusters)

            # Step 3: Group paragraphs based on their cluster labels
        clustered_paragraphs = {i: [] for i in range(max(0, max(cluster_labels) + 1))}
        for label, paragraph_info in zip(cluster_labels, paragraph_data):
            if label >= 0:  # Handle noise if using HDBSCAN
                clustered_paragraphs[label].append(paragraph_info)


        return clustered_paragraphs

    def cluster_K_means(self, vectors, n_clusters=None, max_clusters=10):
        """
        Perform KMeans clustering on paragraph vectors and return the cluster labels.

        Parameters:
            vectors (list): A list of paragraph vectors.
            n_clusters (int, optional): The number of clusters to use. If None, the optimal number of clusters will be calculated.
            max_clusters (int): The maximum number of clusters to test for the optimal k. Default is 10.

        Returns:
            cluster_labels (ndarray): Cluster labels for each paragraph.
        """
        vectors = np.array(vectors)  # Ensure vectors is a NumPy array
        num_vectors = len(vectors)
        max_clusters = min(max_clusters, num_vectors)  # Ensure we don't exceed the number of samples

        if n_clusters is None or n_clusters < 2:
            print("Calculating the optimal number of clusters using K-Means with the Elbow method.")
            kmeans = KMeans()

            # Using KElbowVisualizer to determine the optimal number of clusters
            visualizer = KElbowVisualizer(kmeans, k=(2, max_clusters), metric='distortion', timings=False)
            visualizer.fit(vectors)

            n_clusters = visualizer.elbow_value_

            # If no elbow point is detected, switch to silhouette score
            if n_clusters is None:
                print("No elbow point detected, calculating optimal clusters using Silhouette Score.")
                silhouette_scores = []
                for k in range(2, max_clusters + 1):
                    kmeans = KMeans(n_clusters=k, random_state=42)
                    cluster_labels = kmeans.fit_predict(vectors)
                    score = silhouette_score(vectors, cluster_labels)
                    silhouette_scores.append(score)

                # Get the number of clusters with the highest silhouette score
                n_clusters = np.argmax(silhouette_scores) + 2  # +2 because range starts from 2
                print(f"Optimal number of clusters using Silhouette Score: {n_clusters}")

        print(f"Using {n_clusters} clusters for K-means clustering.")

        # Perform K-means clustering with the chosen number of clusters
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(vectors)

        return cluster_labels
    def classify_paragraphs(self, collection_name, section_titles):
        """
        Classify paragraphs into the respective section titles based on similarity between paragraph embeddings
        and section title embeddings.

        Parameters:
            collection_name (str): The name of the Qdrant collection containing the paragraphs.
            section_titles (list): A list of section titles to classify paragraphs into.

        Returns:
            classified_paragraphs (dict): A dictionary where keys are section titles and values are lists of classified paragraphs.
        """

        # Step 1: Fetch all paragraph vectors and text from Qdrant
        all_points = self.qdrant_client.scroll(
            collection_name=collection_name,
            limit=1000,  # Fetch in batches if necessary
            with_payload=True,
            with_vectors=True  # Retrieve vectors and payloads
        ).points

        # Extract paragraph vectors and corresponding paragraph texts
        paragraph_vectors = []
        paragraph_texts = []

        for point in all_points:
            vector = point.vector.get("text_embedding")  # Assuming "text_embedding" is the vector field
            text = point.payload.get("paragraph_text")  # Extract paragraph text from payload

            if vector and text:
                paragraph_vectors.append(vector)
                paragraph_texts.append(text)

        # Step 2: Create embeddings for the section titles
        section_embeddings = [self.embed_section_title(title) for title in
                              section_titles]  # Assume you have a function to embed section titles

        # Step 3: Initialize a dictionary to store classified paragraphs
        classified_paragraphs = {section_title: [] for section_title in section_titles}

        # Step 4: Classify each paragraph by comparing its vector to the section title embeddings
        for paragraph_vector, paragraph_text in zip(paragraph_vectors, paragraph_texts):
            # Compute the cosine similarity between paragraph vector and all section title vectors
            similarities = cosine_similarity([paragraph_vector], section_embeddings)[0]

            # Find the index of the section title with the highest similarity score
            best_section_idx = similarities.argmax()

            # Assign the paragraph to the most similar section title
            best_section_title = section_titles[best_section_idx]
            classified_paragraphs[best_section_title].append(paragraph_text)

        return classified_paragraphs

    def check_valid_embeddings(self):

        try:
            # Get all collections
            all_collections = self.qdrant_client.get_collections().collections

            # Check if there are any collections
            if not all_collections:
                return "No collections found in the database."

            # Retrieve the first collection name
            for collection in all_collections:
                for a in collection.dict():

                    print(a)

                collection_info = self.qdrant_client.get_collection(collection_name=collection.name)
                # self.qdrant_client.delete_collection(collection_name=collection.name)
                print(collection_info)
                # return collection_info
        except Exception as e:
            return f"Error retrieving collections: {str(e)}"

    def advanced_search(
            self,
            collection_name: str,
            query: str = None,
            top_k: Optional[int] = None,
            filter_conditions: Optional[Dict[str, str]] = None,
            score_threshold: float = 0.70,
            with_payload: bool = True,
            with_vectors: bool = True,
            hnsw_ef: int = 512,
            exact: bool = False,
            keywords: Optional[Dict[str, List[str]]] = None,  # Changed to Dict
            section_weight: float = 0.5,  # Added as parameters
            paragraph_title_weight: float = 0.4,
            text_weight: float = 0.1
    ) -> Dict[str, List]:
        """
        Perform an advanced search in the Qdrant collection using hybrid search methods
    with sparse embeddings and dense vectors, applying rescoring mechanisms.

    Keyword Filtering:
    ------------------
    The search allows sophisticated filtering based on keywords. These keywords can be provided
    as a list and used for rescoring results based on their presence in the section title, paragraph title,
    and paragraph text. The following options are available for keyword filtering:

    1. **Keyword List**: Provide a list of keywords that will be used to rescore results if found in the
       section title, paragraph title, or text.
       Example:
       ```python
       keywords = ["machine learning", "artificial intelligence", "deep learning"]
       ```

    2. **Logical Operators for Keywords**:
       - You can implement logical operators (AND/OR) using multiple keyword lists or dictionaries.
       - **AND**: Rescore if *all* keywords in a group are found in the text.
       - **OR**: Rescore if *any* keyword from a group is found.

       Example:
       ```python
       keywords = {
           "AND": ["machine learning", "neural networks"],  # All keywords must be found
           "OR": ["deep learning", "AI"]  # Any keyword can be found for a boost
       }
       ```

    3. **Keyword Weighting**:
       - You can assign different weights to specific keywords to emphasize their importance in the rescoring.
       - Higher weights will result in a greater score boost when the keyword is found in the text.
       - These weights can also be field-specific (e.g., higher weights if found in the section title).

       Example:
       ```python
       keywords = {
           "neural networks": 0.3,
           "machine learning": 0.2,
           "deep learning": 0.5
       }
       ```

    4. **Field-Specific Keyword Scoring**:
       - Keywords can be matched in different fields with custom weights applied based on where the keyword
         is found:
           - **section_weight**: The weight applied when a keyword is found in the section title.
           - **paragraph_title_weight**: The weight applied when a keyword is found in the paragraph title.
           - **text_weight**: The weight applied when a keyword is found in the paragraph text.

       Example:
       ```python
       section_weight = 0.5  # Boost more for matches in section titles
       paragraph_title_weight = 0.4  # Medium boost for matches in paragraph titles
       text_weight = 0.2  # Lower boost for matches in the main text
       ```

    5. **Proximity Search** (if implemented):
       - Proximity-based rescoring can be added to give higher relevance to results where keywords appear
         closer together in the text. This can be useful in cases where keyword proximity increases relevance.

       Example (not implemented in this version):
       ```python
       proximity_threshold = 10  # Rescore if keywords appear within 10 words of each other
       ```

    Parameters:
    -----------
    collection_name : str
        The name of the Qdrant collection to search in.

    query_vector : Optional[List[float]], optional
        The dense vector used for semantic search. Default is None.

    top_k : Optional[int], optional
        The maximum number of results to return. Default is None.

    filter_conditions : Optional[Dict[str, str]], optional
        Additional filter conditions for the search, such as exact match or range filters.

    score_threshold : float, optional
        The minimum similarity score for results. Default is 0.60.

    with_payload : bool, optional
        Whether to return the payload along with search results. Default is True.

    with_vectors : bool, optional
        Whether to return vectors with search results. Default is False.

    hnsw_ef : int, optional
        Parameter for controlling the efficiency of the HNSW algorithm. Default is 512.

    exact : bool, optional
        Whether to perform exact search rather than approximate search. Default is False.

    keywords : Optional[List[str]], optional
        A list or dictionary of keywords to use for rescoring the search results.
        Keywords can be provided with optional weights or grouped with logical operators (AND/OR).
        Default is None.

    section_weight : float, optional
        Weight applied to score boosts when keywords are found in the section title. Default is 0.5.

    paragraph_title_weight : float, optional
        Weight applied to score boosts when keywords are found in the paragraph title. Default is 0.4.

    text_weight : float, optional
        Weight applied to score boosts when keywords are found in the paragraph text. Default is 0.2.

    Returns:
    --------
    Dict[str, List]
        A dictionary containing the processed search results, including section titles, paragraph titles,
        paragraph text, blockquotes, and rescored values.
        """

        query_vector = query_with_history(' '.join(preprocess_text(query)))

        # Split the query into keywords if not provided
        if keywords is None:
            query_keywords = query.split()
            keywords = {'OR': query_keywords}  # Default to OR logic for broader results

        # Initialize the processed_results variable as a defaultdict
        processed_results = defaultdict(list)

        # Define optional filtering if provided
        query_filter = None
        if filter_conditions:
            must_conditions = []
            for key, value in filter_conditions.items():
                if isinstance(value, dict) and "range" in value:
                    must_conditions.append(models.RangeCondition(
                        key=key,
                        range=models.Range(
                            gte=value["range"].get("gte"),
                            lte=value["range"].get("lte")
                        )
                    ))
                else:
                    must_conditions.append(models.FieldCondition(
                        key=key,
                        match=models.MatchValue(value=value)
                    ))
            query_filter = models.Filter(must=must_conditions)

        # Define search parameters for HNSW ANN search
        search_params = models.SearchParams(
            hnsw_ef=hnsw_ef,
            exact=exact
        )

        try:
            # Perform the query
            results = self.qdrant_client.query_points(
                collection_name=collection_name,
                query=query_vector,  # Dense vector search for semantic matching
                with_payload=with_payload,
                with_vectors=with_vectors,
                query_filter=query_filter,  # Apply any filters
                search_params=search_params,
                # score_threshold=score_threshold,  # Uncomment if needed
            ).points

        except Exception as e:
            logging.error(f"Error during query to collection {collection_name}: {e}")
            return processed_results  # Return empty results on failure

        if not results:
            logging.info(f"No results found for collection: {collection_name}")
            return processed_results

        # Process results and apply rescoring
        for result in results:

            payload = result.payload
            score = result.score  # Qdrant similarity score

            # Call _rescore_result and check if it returns None (i.e., a NOT keyword was found)
            adjusted_score = self._rescore_result(
                payload=payload,
                keywords=keywords,
                section_weight=section_weight,  # Use dynamic weights
                paragraph_title_weight=paragraph_title_weight,
                text_weight=text_weight,
                score_threshold=score_threshold,
                initial_score=score,
                query=query
            )

            print('score:', score)
            print('adjusted_score:', adjusted_score)
            print(payload.get('paragraph_title', "N/A"))
            # print('____'*10)
            if adjusted_score is None:
                # Skip the result if _rescore_result indicates a NOT keyword match
                continue

            # Append results only if the paragraph passed the "NOT" filter and has been rescored
            processed_results['section_title'].append(payload.get('section_title', "N/A"))
            processed_results['paragraph_title'].append(payload.get('paragraph_title', "N/A"))
            processed_results['paragraph_text'].append(payload.get('paragraph_text', "N/A"))
            processed_results['paragraph_blockquote'].append(payload.get('paragraph_blockquote', "N/A"))
            processed_results['metadata'].append(payload.get('metadata', "N/A"))

            processed_results['rescore'].append(adjusted_score)
            processed_results['paragraph_id'].append(result.id)

        # Rescore and sort the results
        self._sort_results(processed_results)
        return processed_results


    def _rescore_result(
            self,
            payload: Dict[str, str],
            initial_score: float,
            score_threshold: float,
            query: str,
            keywords: Optional[Dict[str, List[str]]] = None,
            section_weight: float = 1.0,
            paragraph_title_weight: float = 1.0,
            text_weight: float = 1.0,
            proximity_boost_weight: float = 0.03,  # 0.33 for proximity boost
            fuzzy_boost_weight: float = 0.06,  # 0.33 for fuzzy match
            proximity_threshold: int = 3,
            min_similarity: float = 0.7,
    ) -> Optional[float]:
        """
        Adjust scoring logic to incorporate keyword, proximity, and fuzzy match boosts.
        All text is normalized before applying boosts, and different boosts are applied
        based on whether matches occur in the section title, paragraph title, or paragraph text.
        """

        # Preprocess and normalize fields
        section_tokens = normalize_text(payload.get('section_title', ""))
        paragraph_title_tokens = normalize_text(payload.get('paragraph_title', ""))
        paragraph_text_tokens = normalize_text(payload.get('paragraph_text', ""))
        query_tokens = normalize_text(query)

        # Compute token overlap
        section_overlap = token_overlap(query_tokens, section_tokens)
        paragraph_title_overlap = token_overlap(query_tokens, paragraph_title_tokens)
        paragraph_text_overlap = token_overlap(query_tokens, paragraph_text_tokens)
        # Apply keyword logic and get combined weight
        # Apply keyword logic and get combined weight
        include_result, keyword_weight = self._apply_keyword_logic(
            keywords, query_tokens, section_tokens, paragraph_title_tokens, paragraph_text_tokens,
            section_weight, paragraph_title_weight, text_weight  # Passing the weights here
        )

        # Initialize adjusted score with the initial score
        adjusted_score = initial_score
        adjusted_score += keyword_weight  # This now includes the field-specific weight + keyword weight

        # Calculate match counts
        section_match_count = len(set(query_tokens).intersection(section_tokens))
        paragraph_title_match_count = len(set(query_tokens).intersection(paragraph_title_tokens))
        paragraph_text_match_count = len(set(query_tokens).intersection(paragraph_text_tokens))

        # If any keyword is found in section or paragraph title, apply a 0.5 boost
        if section_match_count > 0 or paragraph_title_match_count > 0:
            adjusted_score += 0.5  # High relevance boost for titles

        # Apply boosts for paragraph text dynamically based on match count
        if paragraph_text_match_count > 0:
            paragraph_text_boost = text_weight * (0.01 * paragraph_text_match_count)
            adjusted_score += paragraph_text_boost

        # Apply proximity boost if proximity is detected
        if apply_proximity_boost(payload.get('paragraph_text', ""), query_tokens, proximity_threshold):
            adjusted_score += proximity_boost_weight  # Proximity boost

        # Apply fuzzy match boost (assuming overlap gives some measure of fuzziness)
        total_overlap = section_overlap + paragraph_title_overlap + paragraph_text_overlap
        if total_overlap > 0:
            fuzzy_boost = fuzzy_boost_weight * (total_overlap / len(query_tokens))
            adjusted_score += fuzzy_boost

        # Ensure score is within bounds
        adjusted_score = min(1.0, max(0.0, adjusted_score))

        # Log the adjusted score for debugging
        logging.debug(f"Adjusted score for document {payload.get('paragraph_id', 'N/A')}: {adjusted_score}")

        # Apply the score threshold and return
        return adjusted_score if adjusted_score >= score_threshold else None

    def _apply_keyword_logic(
            self,
            keywords: Dict[str, Union[List[str], Dict[str, float]]],  # Supports both list of keywords and weighted dict
            phrases: List[str],
            section_tokens: List[str],
            paragraph_title_tokens: List[str],
            paragraph_text_tokens: List[str],
            section_weight: float,
            paragraph_title_weight: float,
            text_weight: float
    ) -> Tuple[bool, float]:
        """
        Apply keyword logic based on the provided keywords dictionary.
        Supports "NOT", "AND", and "OR" logical operators, and calculates combined weights.

        Returns a tuple:
        - Boolean indicating whether the result should be included
        - Float value representing the combined weight (if applicable).
        """
        combined_weight = 0.0

        # Process "NOT" keywords first
        if "NOT" in keywords:
            not_tokens = set()
            for keyword in keywords["NOT"]:
                not_tokens.update(normalize_text2(keyword))
            if (
                    token_in_text(not_tokens, section_tokens) or
                    token_in_text(not_tokens, paragraph_title_tokens) or
                    token_in_text(not_tokens, paragraph_text_tokens)
            ):
                return False, 0.0  # Exclude this result if a "NOT" keyword is found

        # Process "OR" logic (inclusive matching)
        if "OR" in keywords:
            or_tokens = set()
            for keyword in keywords["OR"]:
                or_tokens.update(normalize_text2(keyword))
                if token_in_text(or_tokens, section_tokens):
                    combined_weight += keywords.get(keyword, 1.0) * 1 # Apply field-specific weight
                elif token_in_text(or_tokens, paragraph_title_tokens):
                    combined_weight += keywords.get(keyword, 1.0) * 1
                elif token_in_text(or_tokens, paragraph_text_tokens):
                    combined_weight += keywords.get(keyword, 1.0) * 1
            if combined_weight > 0:
                return True, combined_weight  # Include if any "OR" keyword is found and weight is calculated

        # Process "AND" logic (strict matching)
        if "AND" in keywords:
            and_tokens = set()
            match_count = 0
            for keyword in keywords["AND"]:
                and_tokens.update(normalize_text2(keyword))
                if token_in_text(and_tokens, section_tokens):
                    combined_weight += keywords.get(keyword, 1.0) * section_weight
                    match_count += 1
                elif token_in_text(and_tokens, paragraph_title_tokens):
                    combined_weight += keywords.get(keyword, 1.0) * paragraph_title_weight
                    match_count += 1
                elif token_in_text(and_tokens, paragraph_text_tokens):
                    combined_weight += keywords.get(keyword, 1.0) * text_weight
                    match_count += 1
            if match_count == len(keywords["AND"]):  # Only include if all "AND" keywords match
                return True, combined_weight

        return True, combined_weight  # Default to include the result and return accumulated weight

    def _sort_results(self, processed_results: defaultdict) -> None:
        """
        Sort the processed results based on the adjusted score in descending order.
        """
        sorted_results = sorted(zip(
            processed_results['section_title'],
            processed_results['paragraph_title'],
            processed_results['paragraph_text'],
            processed_results['paragraph_blockquote'],
            processed_results['rescore'],
            processed_results['pragraph_id']
        ), key=lambda x: x[-1], reverse=True)

        if sorted_results:
            (processed_results['section_title'],
             processed_results['paragraph_title'],
             processed_results['paragraph_text'],
             processed_results['paragraph_blockquote'],
             processed_results['rescore'],
             processed_results['pragraph_id']
             ) = zip(*sorted_results)

    def qdrant_collections(self,col_name):
        collection = [collection.name for collection in self.qdrant_client.get_collections().collections if collection.name.split("_")[-1]==col_name]
        return collection
    def clear_and_set_payload(self, collection_name, new_payload, point_id):
        try:
            # Clear the current payload for the given point ID using the correct points_selector
            self.qdrant_client.clear_payload(
                collection_name=collection_name,
                points_selector=models.PointIdsList(points=[int(point_id)])  # Ensure point_id is an integer
            )
            print(f"Payload cleared for point ID {point_id}.")
            vector= get_embedding(new_payload['paragraph_title'])
            # Set the new payload for the given point ID without modifying the vector
            self.qdrant_client.set_payload(
                collection_name=collection_name,
                payload=new_payload,
                points=[int(point_id)],  # Ensure point_id is an integer
                vector=vector,
            )
            print(f"New payload set for point ID {point_id}: {new_payload}")

            # Fetch and print the updated payload and vector for verification
            updated_point = self.qdrant_client.retrieve(
                collection_name=collection_name,
                ids=[int(point_id)]
            )[0]

            print(f"Final payload for point ID {point_id}: {updated_point.payload}")
            print(f"Vector for point ID {point_id} updated: {updated_point.vector}")

        except Exception as e:
            print(f"Error during clear and set payload to collection {collection_name}\nid:{point_id}\nerr: {e}")
            print(e)
    def update_collection_config(self,collection_name):
        # Initialize Qdrant client
        client = QdrantClient(url="http://localhost:6333")

        # Update the collection's vector configuration
        client.update_collection(
            collection_name=collection_name,
            vectors={
                "dense_vector": models.VectorParams(
                    size=3072,  # Size for text-embedding-3-large
                    distance=models.Distance.COSINE  # Cosine similarity for dense vectors
                )
            },
            sparse_vectors={
                "text": models.SparseVectorParams(
                    modifier="idf"  # The correct way to specify IDF in sparse vectors
                )
            }
        )

        print(f"Updated collection '{collection_name}' successfully.")

        print(f"Collection '{collection_name}' updated successfully.")
    def find_collection_by_custom_id(self, custom_id):
        """
        Find the collection name associated with a given custom_id (paper ID).
        """
        try:
            # List all available collections
            collections = self.qdrant_client.get_collections().collections
            # Iterate over collections to find the one corresponding to the custom_id
            for collection in collections:
                collection_name = collection.name

                # Assuming `custom_id` is stored as payload in points of this collection
                result, next_page_token = self.qdrant_client.scroll(
                    collection_name=collection_name,
                    scroll_filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key="custom_id",
                                match=models.MatchValue(value=custom_id)
                            )
                        ]
                    ),
                    limit=1  # Limit to one result
                )

                # Check if any points are found
                if result:
                    return collection_name

            # If no collection with the custom_id found
            return None

        except UnexpectedResponse as e:
            print(f"Error occurred: {e}")
            return None

    def replace_custom_id_with_embedding(self,input_batch_path, embedding_batch_path, output_file_path):
        handler = QdrantHandler()
        # handler.qdrant_client.delete_collection(
        #     collection_name='elements present two')
        # Dictionary to store the embeddings by custom_id
        custom_id_to_embedding = {}

        # Read the embedding batch file and create a mapping of custom_id to embeddings
        with open(embedding_batch_path, 'r') as f_embed:
            for line in f_embed:
                entry = json.loads(line)
                try:
                    embedding_data = entry['response']['body']['data'][0]['embedding']
                    custom_id = entry.get('custom_id', '')
                    if custom_id:
                        custom_id_to_embedding[custom_id] = embedding_data
                except KeyError:
                    # Skip entries without the necessary structure
                    continue

        # Prepare the output with embeddings replacing custom_ids
        output_data = []

        # Read the input batch file
        with open(input_batch_path, 'r') as f_input:
            for line in f_input:
                entry = json.loads(line)

                input_value = entry['body'].get('input', '')
                custom_id = entry.get('custom_id', '')

                # Replace the custom_id with the corresponding embedding if available
                if custom_id in custom_id_to_embedding:

                    handler.qdrant_client.delete_collection(
                        collection_name=input_value)
                    handler.create_collection(collection_name=input_value,vector=False)

                    handler.append_data(collection_name=input_value,vector=False,text_embedding=custom_id_to_embedding[custom_id]

                                               )
                    output_data.append({
                        input_value: custom_id_to_embedding[custom_id]
                    })
                else:
                    # If no embedding found, append the input without changes
                    output_data.append(entry)

        # Write the output to the specified output file
        with open(output_file_path, 'w') as f_output:
            for entry in output_data:
                f_output.write(json.dumps(entry, indent=4, separators=(',', ': ')) + '\n')

    def get_cache_embedding(self,trigram_text):
        collection_name = trigram_text

        try:
            # Check if the collection already exists
            self.qdrant_client.get_collection(collection_name=collection_name)
            print(f"Collection '{collection_name}' already exists.")

            # Retrieve points with vectors from the collection
            scroll_results = self.qdrant_client.scroll(
                collection_name=collection_name,
                with_payload=False,
                with_vectors=True,  # Retrieve vectors
                limit=1  # Only fetch 1 result
            )[0][0]

            # Return the vector if found
            return scroll_results.vector

        except Exception as e:
            # If collection or vector not found, create a new embedding

            # Create a new collection (if needed) and embedding
            self.create_collection(
                collection_name=collection_name,
                vector_size=3072,  # Size of the vector to be stored
                vector=False,

            )

            # Get the new embedding for the trigram text
            vector = get_embedding(trigram_text)

            # Insert the new vector into the collection
            self.append_data(
                collection_name=collection_name,
                vector=False,  # Assuming vector is stored in the text_embedding
                text_embedding=vector
            )

            # Return the newly created vector
            return vector


    def delete_all_collections(self):
        # Initialize the Qdrant client


        # Fetch all collections
        collections = [collection.name for collection in self.qdrant_client.get_collections().collections ]

        # Loop through and delete each collection
        for collection_name in collections:


            print(f"Deleting collection: {collection_name}")
            self.qdrant_client.delete_collection(collection_name=collection_name)

        print("All collections have been deleted.")


