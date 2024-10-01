import hashlib
import os
import json
import logging
import pickle
from collections import defaultdict

from fastembed.embedding import TextEmbedding
from fastembed.sparse import SparseTextEmbedding
from fastembed.late_interaction import LateInteractionTextEmbedding



import joblib
import numpy as np
import pandas as pd
from nltk import WordNetLemmatizer, word_tokenize
from qdrant_client import QdrantClient, models
from qdrant_client.grpc import TextIndexParams, TokenizerType
from qdrant_client.http.models import (
    SearchParams,
    Filter,
    Range,
    MatchValue,
    FieldCondition,
    MatchText,
    SparseVector,
)
from typing import List, Optional, Dict, Tuple, Union


from collections import defaultdict, Counter
import numpy as np
from qdrant_client.conversions.common_types import SparseVector, SparseVectorParams, HnswConfigDiff
from sentence_transformers import SentenceTransformer

from Vector_Database.embedding_handler import get_embedding,query_with_history
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from qdrant_client.http import models  # Import models from qdrant_client.http
from qdrant_client.http.exceptions import UnexpectedResponse
from sklearn.cluster._hdbscan import hdbscan
from sklearn.decomposition import LatentDirichletAllocation as LDA
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics import silhouette_score
from sklearn.metrics.pairwise import cosine_distances
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

from Pychat_module.gpt_api import call_openai_api
import uuid
from File_management.exporting_files import export_results
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from yellowbrick.cluster import KElbowVisualizer



import re

from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import spacy
from rank_bm25 import BM25Okapi

# Sentence Transformer for dense embeddings
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

dense_embedding_model = TextEmbedding("sentence-transformers/all-MiniLM-L6-v2")
bm42_embedding_model = SparseTextEmbedding("Qdrant/bm42-all-minilm-l6-v2-attentions")
colbert_embedding_model = LateInteractionTextEmbedding("colbert-ir/colbertv2.0")
# Preprocessing functions (assuming they are defined elsewhere or include them)
def preprocess_text(text: str) -> str:
    """
    Preprocesses the input text for BM25 and dense embeddings.
    """
    # Implement your preprocessing here (e.g., lowercase, remove punctuation, tokenize)
    # For demonstration, we'll just lowercase and remove non-alphanumeric characters
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return text

# Configure logging
logging.basicConfig(level=logging.INFO)
def token_in_text(tokens: set, text_tokens: List[str]) -> bool:
    return any(token in text_tokens for token in tokens)
def normalize_text2(text: str) -> List[str]:
    """
    Normalize the input text by lowercasing, removing non-alphanumeric characters,
    and splitting into tokens.
    """
    normalized_text = text.lower()
    normalized_text = re.sub(r'[^a-z0-9\s]', '', normalized_text)
    tokens = normalized_text.split()
    return tokens


def preprocess_text2(text: str, phrases: Optional[List[str]] = None) -> List[str]:
    nlp = spacy.load("en_core_web_sm")

    """
    Preprocess text by lowercasing, replacing phrases, removing non-alphabetic characters,
    lemmatizing, and extracting only nouns and adjectives using spaCy.
    """
    text = text.lower()
    stopwords_tailored = ['attribution', 'state', 'cyber']

    if phrases:
        for phrase in phrases:
            phrase_pattern = re.escape(phrase)
            text = re.sub(r'\b' + phrase_pattern + r'\b', phrase.replace(' ', '_'), text)

    text = re.sub(r'[^a-zA-Z_\s]', '', text)
    doc = nlp(text)
    tokens = [token.lemma_ for token in doc if
              token.pos_ in {"NOUN", "PROPN", "ADJ"} and not token.is_stop and token.lemma_ not in stopwords_tailored]

    return tokens



def normalize_text(text: str) -> List[str]:
    """
    Normalize the text by converting to lowercase, removing punctuation, and stemming words.
    """
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    tokens = text.split()
    ps = PorterStemmer()
    tokens = [ps.stem(token) for token in tokens if token not in stopwords.words('english')]
    return tokens


def token_overlap(query_tokens: List[str], text_tokens: List[str]) -> int:
    """
    Calculate the number of matching tokens between query and text after normalization.
    """
    normalized_query = normalize_text(' '.join(query_tokens))
    normalized_text = normalize_text(' '.join(text_tokens))
    overlap = set(normalized_query).intersection(set(normalized_text))
    return len(overlap)


def apply_proximity_boost(text: str, query_tokens: List[str], threshold: int) -> bool:
    """
    Determine if a proximity boost should be applied by checking the closeness of query tokens in the text.
    """
    normalized_text = normalize_text(text)
    for token in query_tokens:
        if token in normalized_text:
            return True
    return False


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


# Preprocessing function
def preprocess_text(text: str) -> str:
    """
    Preprocesses the input text.
    """
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    return text

class QdrantHandler:
    # Initialize models

    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",

        corpus_path: str = r"C:\Users\luano\Downloads\AcAssitant\Files\Models corpus\bm25_corpus.pkl",

    ):
        self.qdrant_client = QdrantClient(url=qdrant_url)
        self.dense_embedding_model = TextEmbedding("sentence-transformers/all-MiniLM-L6-v2")
        self.bm42_embedding_model = SparseTextEmbedding("Qdrant/bm42-all-minilm-l6-v2-attentions")



    def fit_bm25(self, corpus: List[List[str]]):
        """
        Fit the BM25 model on the provided corpus and save it.

        Args:
            corpus (List[List[str]]): A list of tokenized documents to fit the model.
        """
        print("Fitting BM25 model on the corpus...")
        self.bm25_corpus = corpus
        self.bm25 = BM25Okapi(self.bm25_corpus)
        # Save the corpus for future use
        with open(self.corpus_path, 'wb') as f:
            pickle.dump(self.bm25_corpus, f)
        # Build vocabulary
        self.vocab = {term: idx for idx, term in enumerate(self.bm25.idf.keys())}
        print(f"BM25 model fitted and corpus saved to {self.corpus_path}.")

    def create_collection(self, collection_name: str) -> bool:
        from qdrant_client import QdrantClient, models

        try:
            self.qdrant_client.get_collection(collection_name)
            print(f"Collection '{collection_name}' already exists.")
            return False
        except Exception:
            print(f"Collection '{collection_name}' not found. Creating a new collection.")

        try:
            self.qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config={
                    "text_dense": models.VectorParams(
                        size=3072,  # Size of the dense embedding
                        distance=models.Distance.COSINE
                    ),
                    "colbert": models.VectorParams(
                        size=128,  # Size of ColBERT embeddings (adjust as needed)
                        distance=models.Distance.COSINE,
                        multivector_config=models.MultiVectorConfig(
                            comparator=models.MultiVectorComparator.MAX_SIM
                        )
                    ),
                },
                sparse_vectors_config={
                    "bm42": models.SparseVectorParams(
                        modifier=models.Modifier.IDF,
                        index=models.SparseIndexParams(
                            # Any additional index params if needed
                            on_disk=False
                        )
                    )
                },
                on_disk_payload=False
            )
            print(f"Collection '{collection_name}' created successfully.")
            return True
        except Exception as create_error:
            print(f"Error creating collection '{collection_name}': {create_error}")
            return False

    def append_data(
            self,
            collection_name: str,
            metadata: str = '',
            keywords: str = '',
            keyword_categories: str ='',
            paragraph_count: str = '',
            article_title: str = '',
            section_title: str = '',
            paragraph_title: str = '',
            paragraph_text: str = '',
            paragraph_blockquote: str = '',
            custom_id: str = ''
    ) -> Optional[Dict]:
        """
        Insert dense, sparse (BM42), and ColBERT embeddings along with paragraph metadata into the collection.
        """
        from qdrant_client import models

        # Validate collection existence
        try:
            self.qdrant_client.get_collection(collection_name)
        except Exception:
            print(f"Collection '{collection_name}' does not exist. Please create it first.")
            return None

        # Create a unique ID based on the paragraph title
        hash_object = hashlib.sha256(paragraph_title.encode('utf-8'))
        paragraph_id = int(hash_object.hexdigest(), 16) % (10 ** 8)

        # Structure the payload, storing custom ID and other metadata
        payload = {
            "article_title": article_title,
            "section_title": section_title,
            "paragraph_title": paragraph_title,
            "paragraph_text": paragraph_text,
            "paragraph_blockquote": paragraph_blockquote,
            "custom_id": custom_id,
            "paragraph_count": paragraph_count,
            "metadata": metadata,
            "keywords":keywords,
            "keyword_categories":keyword_categories
        }

        # Preprocess paragraph text
        preprocessed_paragraph_text = preprocess_text(paragraph_text)

        # Generate Dense Embedding
        dense_embedding =get_embedding(preprocessed_paragraph_text)
        # dense_embedding = list(dense_embedding_model.embed([preprocessed_paragraph_text]))[0].tolist()

        # Generate BM42 Sparse Embedding
        bm42_embedding = list(bm42_embedding_model.embed([preprocessed_paragraph_text]))[0]
        bm42_sparse_vector = models.SparseVector(
            indices=bm42_embedding.indices.tolist(),
            values=bm42_embedding.values.tolist()
        )

        # Generate ColBERT Embeddings
        colbert_embeddings = list(colbert_embedding_model.embed([preprocessed_paragraph_text]))[0]
        colbert_embeddings_list = [embedding.tolist() for embedding in colbert_embeddings]

        # Prepare the vector dictionary
        vector = {
            "text_dense": dense_embedding,
            "bm42": bm42_sparse_vector,  # Use SparseVector directly
            "colbert": colbert_embeddings_list
        }

        # Insert data into Qdrant with all vectors
        try:
            operation_info = self.qdrant_client.upsert(
                collection_name=collection_name,
                points=[
                    models.PointStruct(
                        id=paragraph_id,
                        vector=vector,  # Use 'vector' instead of 'vectors'
                        payload=payload
                    )
                ]
            )
            print(
                f"Inserted data for paragraph '{paragraph_title}' under section '{section_title}' with custom ID '{custom_id}'.")
            return operation_info
        except Exception as e:
            print(f"Failed to insert data: {e}")
            return None

    def hybrid_search(
            self,
            collection_name: str,
            query: str,
            top_k: int = 10,
            with_payload: bool = True,
            keywords: Optional[Dict[str, List[str]]] = None,
            update: bool = False
    ) -> Dict[str, List]:
        """
        Perform a hybrid search in Qdrant using BM42 sparse embeddings and dense embeddings.

        Args:
            collection_name (str): Name of the Qdrant collection.
            query (str): The search query.
            top_k (int): Number of top results to return.
            with_payload (bool): Whether to return payload with results.
            keywords (Optional[Dict[str, List[str]]]): Keywords for filtering.
            update (bool): Whether to update the cache.

        Returns:
            Dict[str, List]: A dictionary containing the search results.
        """
        # Cache file path
        cache_file_path = rf"C:\Users\luano\Downloads\AcAssitant\Files\Cache\search_cache\search_results_{collection_name}.json"

        # Check if the cache file exists
        if os.path.exists(cache_file_path) and not update:
            with open(cache_file_path, 'r') as cache_file:
                cache = json.load(cache_file)
                if query in cache:
                    logging.info(f"Returning cached result for query: {query}")
                    return cache[query]

        # Parse the query into a filter and search terms
        try:
            filter, search_terms = self.parse_query(query)
        except Exception as e:
            logging.error(f"Error parsing query: {e}")
            return {}

        # Generate embeddings for the search terms
        dense_embedding = get_embedding(search_terms)
        bm42_embedding = list(self.bm42_embedding_model.embed([search_terms]))[0]
        bm42_sparse_vector = models.SparseVector(
            indices=bm42_embedding.indices.tolist(),
            values=bm42_embedding.values.tolist()
        )

        try:
            # Perform dense vector search
            results_dense = self.qdrant_client.search(
                collection_name=collection_name,
                query_vector=models.NamedVector(
                    name="text_dense",
                    vector=dense_embedding
                ),
                query_filter=filter,
                limit=top_k * 2,
                with_payload=with_payload
            )

            # Perform sparse vector search
            results_sparse = self.qdrant_client.search(
                collection_name=collection_name,
                query_vector=models.NamedSparseVector(
                    name="bm42",
                    vector=bm42_sparse_vector
                ),
                query_filter=filter,
                limit=top_k * 2,
                with_payload=with_payload
            )

            # Combine results using RRF
            combined_results = self.reciprocal_rank_fusion([results_dense, results_sparse], top_k)

            # Process the combined results
            processed_results = defaultdict(list)
            for result in combined_results:
                payload = result.payload
                score = result.score

                # Adjust score based on keywords if necessary
                include_result = True
                if keywords:
                    include_result = self._apply_keyword_filter(
                        keywords, payload
                    )
                if not include_result:
                    continue

                processed_results['section_title'].append(payload.get('section_title', "N/A"))
                processed_results['paragraph_title'].append(payload.get('paragraph_title', "N/A"))
                processed_results['paragraph_text'].append(payload.get('paragraph_text', "N/A"))
                processed_results['paragraph_blockquote'].append(payload.get('paragraph_blockquote', "N/A"))
                processed_results['metadata'].append(payload.get('metadata', "N/A"))
                processed_results['keywords'].append(payload.get('keywords', []))
                processed_results['score'].append(score)
                processed_results['paragraph_id'].append(result.id)

            if not processed_results:
                logging.info("No results after processing.")
                return {}

            # Cache the processed results
            cache = {}
            if os.path.exists(cache_file_path):
                with open(cache_file_path, 'r') as cache_file:
                    cache = json.load(cache_file)

            cache[query] = processed_results  # Store the result in the cache
            with open(cache_file_path, 'w') as cache_file:
                json.dump(cache, cache_file)

            return processed_results

        except Exception as e:
            logging.error(f"Error during hybrid search in collection {collection_name}: {e}")
            return {}

    def parse_query(self, query: str):
        """
        Parses the query string and returns a Qdrant filter and search terms.

        Args:
            query (str): The query string.

        Returns:
            Tuple[models.Filter, str]: A tuple containing the Qdrant filter and the search terms.
        """
        import re
        from qdrant_client.http import models

        # Patterns
        field_pattern = re.compile(r'(\w+):(".*?"|\S+)')
        phrase_pattern = re.compile(r'"(.*?)"')
        boolean_operators = {'AND', 'OR', 'NOT'}

        # Initialize filter conditions
        must_conditions = []
        should_conditions = []
        must_not_conditions = []

        # Extract field-specific searches
        remaining_query = query
        field_matches = field_pattern.findall(query)
        for field_name, value in field_matches:
            # Remove from remaining query
            remaining_query = remaining_query.replace(f'{field_name}:{value}', '')

            # Remove quotes if present
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]

            # Use MatchText for text matching
            condition = models.FieldCondition(
                key=field_name,
                match=models.MatchText(text=value)
            )

            must_conditions.append(condition)

        # Now handle the remaining query for terms and boolean logic
        tokens = remaining_query.strip().split()
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token.upper() in boolean_operators:
                operator = token.upper()
                i += 1
                if i >= len(tokens):
                    break
                next_token = tokens[i]

                # Determine which conditions list to use
                if operator == 'NOT':
                    conditions_list = must_not_conditions
                elif operator == 'OR':
                    conditions_list = should_conditions
                else:
                    conditions_list = must_conditions

                # Handle phrases or terms
                if next_token.startswith('"'):
                    phrase_match = phrase_pattern.match(' '.join(tokens[i:]))
                    if phrase_match:
                        phrase = phrase_match.group(1)
                        i += len(phrase.split())  # Advance index
                        condition = models.FieldCondition(
                            key="paragraph_text",
                            match=models.MatchText(text=phrase)
                        )
                    else:
                        phrase = next_token.strip('"')
                        condition = models.FieldCondition(
                            key="paragraph_text",
                            match=models.MatchText(text=phrase)
                        )
                else:
                    # Regular term
                    condition = models.FieldCondition(
                        key="paragraph_text",
                        match=models.MatchText(text=next_token)
                    )

                conditions_list.append(condition)
            else:
                # Handle as a term in must conditions
                if token.startswith('"'):
                    # Exact phrase
                    phrase_match = phrase_pattern.match(' '.join(tokens[i:]))
                    if phrase_match:
                        phrase = phrase_match.group(1)
                        i += len(phrase.split())  # Advance index
                        condition = models.FieldCondition(
                            key="paragraph_text",
                            match=models.MatchText(text=phrase)
                        )
                    else:
                        phrase = token.strip('"')
                        condition = models.FieldCondition(
                            key="paragraph_text",
                            match=models.MatchText(text=phrase)
                        )
                else:
                    # Regular term
                    condition = models.FieldCondition(
                        key="paragraph_text",
                        match=models.MatchText(text=token)
                    )
                must_conditions.append(condition)
            i += 1

        # Build the filter
        filter_conditions = []
        if must_conditions:
            filter_conditions.append(models.Filter(must=must_conditions))
        if should_conditions:
            filter_conditions.append(models.Filter(should=should_conditions))
        if must_not_conditions:
            filter_conditions.append(models.Filter(must_not=must_not_conditions))

        if len(filter_conditions) == 1:
            combined_filter = filter_conditions[0]
        else:
            # Combine filters
            combined_filter = models.Filter(
                must=filter_conditions  # Combine using must
            )

        # For the embeddings, we can use the terms extracted from the query without operators
        search_terms = ' '.join(token for token in tokens if token.upper() not in boolean_operators)

        return combined_filter, search_terms

    def reciprocal_rank_fusion(self, results_list, top_k):
        """
        Combine multiple result lists using Reciprocal Rank Fusion (RRF).
        results_list: List of lists of results.
        Returns combined results sorted by RRF score.
        """
        # Assign a fixed k value for RRF
        k = 60
        # Dictionary to store cumulative scores
        scores = {}
        # Map of result IDs to result objects
        result_map = {}
        for results in results_list:
            for rank, result in enumerate(results):
                # Compute RRF score
                rrf_score = 1.0 / (k + rank)
                if result.id in scores:
                    scores[result.id] += rrf_score
                else:
                    scores[result.id] = rrf_score
                    result_map[result.id] = result  # Store the result object

        # Assign combined scores to result objects
        for id, score in scores.items():
            result_map[id].score = score

        # Sort results by combined score
        combined_results = sorted(result_map.values(), key=lambda x: x.score, reverse=True)
        # Return top_k results
        return combined_results[:top_k]


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

    def get_all_collections_payloads_and_save_csv(self, output_file: str = 'qdrant_all_collections_cleaned.csv'):
        """
        Fetches all collections from Qdrant, retrieves payloads, preprocesses the text,
        and saves the cleaned data into a CSV file.

        Args:
            output_file (str): The path of the CSV file to save the cleaned payloads.
                               Default is 'qdrant_all_collections_cleaned.csv'.
        """

        # Initialize an empty list to store payloads from all collections
        all_payloads = []


        # Get all collection names from the Qdrant instance
        collections_response = self.qdrant_client.get_collections()
        collections = collections_response.collections

        for collection in collections:
            collection_name = collection.name
            print(f"Fetching data from collection: {collection_name}")

            try:
                # Retrieve all points with vectors from the collection using scroll (no need for IDs)
                scroll_results, next_page_token = self.qdrant_client.scroll(
                    collection_name=collection_name,
                    with_payload=True,
                    with_vectors=False,  # You can set to True if vectors are required
                    limit=1000  # Adjust the limit as needed
                )
            except Exception as e:
                print(f"Error in collection {collection_name}: {e}")
                continue

            # Process the scroll results
            while scroll_results:
                for scroll_result in scroll_results:
                    payload = scroll_result.payload

                    # Check if required fields exist in the payload before processing
                    paragraph_text = payload.get('paragraph_text', "")
                    paragraph_title = payload.get('paragraph_title', "")
                    section_title = payload.get('section_title', "")
                    keywords = payload.get('keywords',"")

                    # Clean and preprocess relevant fields in the payload, joining tokens into strings
                    new_payload = {
                        'paragraph_title_cleaned': preprocess_text(paragraph_title),
                        'paragraph_text_cleaned': preprocess_text(paragraph_text),
                        'section_title_cleaned': preprocess_text(section_title),
                        # 'keywords_cleaned': preprocess_text(" ".join(convert_to_obsidian_tags(keywords)))
                    }

                    # Append the cleaned payload to the global list
                    all_payloads.append(new_payload)
                    print(type(new_payload))

                    # print(new_payload)
                # If there is a next page token, fetch more points
                if next_page_token:
                    scroll_results, next_page_token = self.qdrant_client.scroll(
                        collection_name=collection_name,
                        with_payload=True,
                        with_vectors=False,
                        limit=1000,
                        page_token=next_page_token
                    )
                else:
                    break

        # Convert the list of all payloads into a DataFrame
        df = pd.DataFrame(all_payloads)

        # Save the DataFrame to a CSV file
        df.to_csv(output_file, index=False)

        print(f"Data from all collections has been successfully saved to {output_file}")



