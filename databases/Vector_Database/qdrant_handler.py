import hashlib
import os
import json
import logging

from fastembed.embedding import TextEmbedding
from fastembed.sparse import SparseTextEmbedding
from fastembed.late_interaction import LateInteractionTextEmbedding


import nltk

from qdrant_client import models
from typing import List, Optional, Dict, Tuple

import numpy as np
from pyparsing import (
    Word, alphanums, QuotedString, Forward, oneOf, infixNotation,
    opAssoc, ParserElement, ParseException, delimitedList, Suppress
)
from qdrant_client.http import models

ParserElement.enablePackrat()
from models.NLP_module.nlp_techniques import lists_have_common_words
from databases.Vector_Database.embedding_handler import get_embedding
from qdrant_client import QdrantClient
from qdrant_client.http import models  # Import models from qdrant_client.http
from qdrant_client.http.exceptions import UnexpectedResponse
from sklearn.cluster._hdbscan import hdbscan
from sklearn.decomposition import LatentDirichletAllocation as LDA
from sklearn.cluster import AgglomerativeClustering
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import silhouette_score
from sklearn.metrics.pairwise import cosine_distances

from models.Pychat_module.gpt_api import call_openai_api
import uuid
from File_management.exporting_files import export_results
from sklearn.cluster import KMeans
from yellowbrick.cluster import KElbowVisualizer

from spacy.lang.en.stop_words import STOP_WORDS

import re

from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import spacy

# Sentence Transformer for dense embeddings
from sklearn.metrics.pairwise import cosine_similarity

dense_embedding_model = TextEmbedding("sentence-transformers/all-MiniLM-L6-v2")
bm42_embedding_model = SparseTextEmbedding("Qdrant/bm42-all-minilm-l6-v2-attentions")
colbert_embedding_model = LateInteractionTextEmbedding("colbert-ir/colbertv2.0")

nltk.download('punkt', quiet=True)
import torch
print(torch.cuda.is_available())  # Should return True if CUDA is properly set up
print(torch.cuda.get_device_name(0))  # Should print the name of your GPU

# import torch
#
# # Check if GPU is available
# if torch.cuda.is_available():
#     print(f"GPU is available: {torch.cuda.get_device_name(0)}")
# else:
#     print("GPU is not available. Using CPU.")

def parse_query(query_str):
    from pyparsing import (
        Word, alphanums, QuotedString, Forward, oneOf, infixNotation,
        opAssoc, Suppress, ParserElement, ParseException
    )
    import re

    # Enable packrat parsing for performance
    ParserElement.enablePackrat()

    # Precompile regex patterns to detect field-based conditions and logical operators
    field_pattern = re.compile(r'\w+:\s*(".*?"|\S+)')
    operator_pattern = re.compile(r'\b(AND|OR|NOT)\b')  # Removed re.IGNORECASE

    # Check if the query contains fields or operators
    if field_pattern.search(query_str) or operator_pattern.search(query_str):
        # Proceed with parsing the structured query
        # Define the grammar for parsing field-based and logical operator queries
        field_name = Word(alphanums + "_")
        comparison_op = oneOf(":")
        value = QuotedString('"') | Word(alphanums + "_-")
        field_condition = field_name + comparison_op + value

        # Define a condition (field-specific or general term)
        condition = (
            field_condition.setParseAction(lambda t: ('field', t[0], t[2]))
            | value.setParseAction(lambda t: ('term', t[0]))
        )

        # Define logical operators (case-sensitive)
        AND = oneOf("AND &&")
        OR = oneOf("OR ||")
        NOT = oneOf("NOT !")

        # Define the expression, including parenthesis handling
        expr = Forward()
        atom = condition | (Suppress('(') + expr + Suppress(')'))
        expr <<= infixNotation(
            atom,
            [
                (NOT, 1, opAssoc.RIGHT),
                (AND, 2, opAssoc.LEFT),
                (OR, 2, opAssoc.LEFT),
            ],
        )

        try:
            # Parse the structured query
            parsed_expr = expr.parseString(query_str, parseAll=True)[0]
            # Convert parsed_expr into a Qdrant Filter
            qdrant_filter = build_filter(parsed_expr)
            return qdrant_filter
        except ParseException as pe:
            print(f"Error parsing query: {pe}")
            return None
    else:
        # If no fields or operators are detected, treat as a full-text query
        return None


def build_filter(filter_terms):
    from qdrant_client.http import models

    def build_conditions(field_terms):
        conditions = []
        for field, terms in field_terms.items():
            for term in terms:
                conditions.append(
                    models.FieldCondition(
                        key=field,
                        match=models.MatchText(text=term)

                    )
                )
        return conditions

    must_conditions = []
    should_conditions = []
    must_not_conditions = []

    for operator, field_terms in filter_terms.items():
        if operator.lower() == 'and':
            must_conditions.extend(build_conditions(field_terms))
        elif operator.lower() == 'or':
            should_conditions.extend(build_conditions(field_terms))
        elif operator.lower() == 'not':
            must_not_conditions.extend(build_conditions(field_terms))
        else:
            raise ValueError(f"Invalid operator in filter_terms: {operator}")

    qdrant_filter = models.Filter(
        must=must_conditions if must_conditions else None,
        should=should_conditions if should_conditions else None,
        must_not=must_not_conditions if must_not_conditions else None
    )

    return qdrant_filter

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

nlp = spacy.load("en_core_web_md")


def generate_bigrams(tokens: List[str]) -> List[tuple]:
    """
    Generate bigrams from a list of tokens.

    Args:
        tokens (List[str]): A list of preprocessed tokens.

    Returns:
        List[tuple]: A list of bigrams (tuples of consecutive token pairs).
    """
    return list(nltk.bigrams(tokens))


def match_query_with_keywords(query: str, keywords: List[str]) -> float:
    """
            Compare the query with the keyword list by preprocessing and generating bigrams.

            Args:
                query (str): The search query.
                keywords (List[str]): A list of keyword phrases to compare against.

            Returns:
                float: A weight (boost) score based on keyword matches.
            """
    # Preprocess the query
    preprocessed_query = preprocess_text2(query)
    query_bigrams = generate_bigrams(preprocessed_query)

    # Initialize boost score
    boost_score = 0.0

    # Iterate through the list of keywords
    for keyword in keywords:
        # Preprocess each keyword and generate bigrams
        preprocessed_keyword = preprocess_text2(keyword)
        keyword_bigrams = generate_bigrams(preprocessed_keyword)

        # Bigram match
        if set(query_bigrams).intersection(set(keyword_bigrams)):
            boost_score = 1.0  # Set boost to 1.0 if bigram matches
            return boost_score  # Bigram match takes precedence

        # Exact token match
        if set(preprocessed_query).intersection(set(preprocessed_keyword)):
            boost_score = max(boost_score, 0.5)  # Set boost to 0.5 if any word matches

    return boost_score

def convert_to_obsidian_tags(keywords_dict):
    tags = []

    # Loop through the categories (topics, entities, academic_features)
    for category, words in keywords_dict['keywords'].items():
        for word in words:
            # Convert each keyword into a tag with a hash (#) and replace spaces with underscores
            tags.append(word)

    return tags
def process_keywords(keywords_dict, authors_list):
    tags = []

    # Loop through the categories (topics, entities, academic_features)
    for category, words in keywords_dict['keywords'].items():
        for word in words:
            # If category is "entities", check for common words with authors_list
            if category == "entities":
                if not lists_have_common_words([word], authors_list):
                    # Append only if a common word is found
                    tags.append(word.lower())
            else:
                # For other categories (topics, academic_features), just append the tag
                tags.append(word.lower())
    return tags


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
    """
    Preprocess text by lowercasing, replacing phrases, removing non-alphabetic characters,
    lemmatizing, and extracting specific parts of speech (nouns, proper nouns, adjectives, verbs).

    Args:
        text (str): The input text to be preprocessed.
        phrases (Optional[List[str]]): A list of phrases to replace in the text.

    Returns:
        List[str]: A list of preprocessed tokens (lemmatized and filtered).
    """
    # Convert text to lowercase
    text = text.lower()

    # Combine default stopwords with domain-specific stopwords
    stopwords_tailored = STOP_WORDS.union({'attribution', 'state', 'cyber', 'is', 'the', 'what'})

    # Replace phrases with underscore-separated versions, handling spaces and punctuation
    if phrases:
        for phrase in phrases:
            phrase_pattern = rf'\b{re.escape(phrase)}\b'  # More flexible phrase matching
            text = re.sub(phrase_pattern, phrase.replace(' ', '_'), text)

    # Remove non-alphabetic characters (except underscores for phrases)
    text = re.sub(r'[^a-zA-Z_\s]', '', text)

    # Process the text with spaCy NLP pipeline
    doc = nlp(text)

    # Lemmatize tokens and extract nouns, proper nouns, adjectives, and verbs
    tokens = [
        token.lemma_ for token in doc
        if token.pos_ in {"NOUN", "PROPN", "ADJ", "VERB"}  # Include verbs for action relevance
           and not token.is_stop
           and token.lemma_ not in stopwords_tailored  # Remove tailored stopwords
    ]

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



    def create_collection(self, collection_name: str) -> bool:
        from qdrant_client import models

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
            query: str = '',
            filter_terms: Optional[Dict[str, Dict[str, List[str]]]] = None,
            score_threshold: float = 0.5,
            top_k: Optional[int] = None,
            dense_weight: float = 1.0,
            sparse_weight: float = 3.0,
            keyword_weight: float = 1.0,
            with_payload: bool = True,
            update_results_cache: bool = True
    ) -> Dict[str, List]:
        """
        Perform a hybrid search in Qdrant using BM42 sparse embeddings and dense embeddings,
        with additional weighting for exact keyword and bigram matches.

        Args:
            collection_name (str): Name of the Qdrant collection.
            query (str): The search query.
            score_threshold (float): Minimum similarity score threshold.
            top_k (Optional[int]): Number of top results to return, or None to return all results.
            dense_weight (float): Weight to apply to dense vector scores.
            sparse_weight (float): Weight to apply to sparse vector scores.
            keyword_weight (float): Multiplier for the boost score based on keyword matches.
            with_payload (bool): Whether to return payload with results.
            filter_terms (Optional[Dict[str, Dict[str, List[str]]]]): Keywords for filtering.
            update_results_cache (bool): Whether to update the search results cache.

        Returns:
            Dict[str, List]: A dictionary containing the search results.
        """
        import os
        import json
        import hashlib
        import logging

        # Define cache file paths
        embeddings_cache_file_path = r"/Files/Cache/embeddings_cache.json"
        results_cache_file_path = rf"C:\Users\luano\Downloads\AcAssitant\Files\Cache\search_cache\search_results_{collection_name}.json"

        # Ensure the cache directories exist
        os.makedirs(os.path.dirname(embeddings_cache_file_path), exist_ok=True)
        os.makedirs(os.path.dirname(results_cache_file_path), exist_ok=True)

        # Load embeddings cache with error handling
        try:
            with open(embeddings_cache_file_path, 'r') as cache_file:
                embeddings_cache = json.load(cache_file)
        except (json.JSONDecodeError, IOError) as e:
            logging.warning(f"Error loading embeddings cache: {e}. Initializing empty cache.")
            embeddings_cache = {}

        # Load results cache with error handling
        try:
            with open(results_cache_file_path, 'r') as cache_file:
                results_cache = json.load(cache_file)
        except (json.JSONDecodeError, IOError) as e:
            logging.warning(f"Error loading results cache: {e}. Initializing empty cache.")
            results_cache = {}

        # Create a unique query hash for caching based on both query and filter_terms
        combined_query = f"{query}|{json.dumps(filter_terms, sort_keys=True)}"
        query_hash = hashlib.sha256(combined_query.encode('utf-8')).hexdigest()

        # Check if search results exist in the cache and return if not updating the cache
        if combined_query in results_cache and not update_results_cache:
            logging.info(f"Returning cached results for combined query: {combined_query}")
            return results_cache[combined_query]

        # Initialize qdrant_filter
        qdrant_filter = None

        # Build filter from filter_terms
        if filter_terms:
            try:
                filter_terms_filter = build_filter(filter_terms)
                qdrant_filter = filter_terms_filter
                logging.debug(f"Constructed Qdrant Filter from filter_terms: {qdrant_filter}")
            except ValueError as ve:
                logging.error(f"Error in filter_terms: {ve}")
                return {}

        # Build filter from query
        if query:
            parsed_query_filter = parse_query(query)
            if parsed_query_filter is None:
                # This means it's a full-text query, not a structured query, handle as vector query
                logging.info(f"Handling query as full-text: {query}")
                # No changes to qdrant_filter, full-text handled by vectors
            else:
                # Combine filters if both filter_terms and query filters exist
                if qdrant_filter:
                    qdrant_filter = models.Filter(
                        must=[
                            qdrant_filter,
                            parsed_query_filter
                        ]
                    )
                else:
                    qdrant_filter = parsed_query_filter
                logging.debug(f"Combined Qdrant Filter with Query: {qdrant_filter}")

        # Proceed with embedding generation if query is present
        if query:
            # Check if embeddings exist in the cache
            if query_hash in embeddings_cache:
                logging.info(f"Loading embeddings from cache for query: {query}")
                dense_embedding = embeddings_cache[query_hash]['dense']
                bm42_sparse_vector_data = embeddings_cache[query_hash]['sparse']

                # Convert the cached sparse vector data back into a SparseVector object
                bm42_sparse_vector = models.SparseVector(
                    indices=bm42_sparse_vector_data['indices'],
                    values=bm42_sparse_vector_data['values']
                )
            else:
                logging.info(f"Generating embeddings for query: {query}")
                # Generate embeddings for the search terms
                dense_embedding = get_embedding(query)  # Define this function as per your embedding model
                bm42_embedding = list(self.bm42_embedding_model.embed([query]))[0]  # Adjust as needed
                bm42_sparse_vector = models.SparseVector(
                    indices=bm42_embedding.indices.tolist(),
                    values=bm42_embedding.values.tolist()
                )

                # Cache the embeddings in a JSON serializable format (lists for indices and values)
                embeddings_cache[query_hash] = {
                    'dense': dense_embedding,
                    'sparse': {
                        'indices': bm42_sparse_vector.indices,  # Serialize indices as a list
                        'values': bm42_sparse_vector.values  # Serialize values as a list
                    }
                }
                with open(embeddings_cache_file_path, 'w') as cache_file:
                    json.dump(embeddings_cache, cache_file)

        # Perform searches based on the presence of query and filters
        if query:
            logging.info("Performing hybrid search with vectors and filters.")
            # Perform dense vector search
            results_dense = self.qdrant_client.search(
                collection_name=collection_name,
                query_vector=models.NamedVector(
                    name="text_dense",
                    vector=dense_embedding
                ),
                query_filter=qdrant_filter,
                with_payload=with_payload,
                limit=1000  # Set a high limit to retrieve all potential results
            )
            logging.info(f"Results from dense search: {len(results_dense)}")

            # Perform sparse vector search
            results_sparse = self.qdrant_client.search(
                collection_name=collection_name,
                query_vector=models.NamedSparseVector(
                    name="bm42",
                    vector=bm42_sparse_vector
                ),
                query_filter=qdrant_filter,
                with_payload=with_payload,
                limit=1000  # Set a high limit to retrieve all potential results
            )
            logging.info(f"Results from sparse search: {len(results_sparse)}")

            # Combine results using RRF
            combined_results = self.reciprocal_rank_fusion(
                [results_dense, results_sparse],
                top_k=top_k,
                dense_weight=dense_weight,
                sparse_weight=sparse_weight
            )

            # Apply extra weight based on keyword matching
            for result in combined_results:
                payload_keywords = result.payload.get('keywords', [])
                if not payload_keywords:
                    continue  # Skip if no keywords in payload

                # Get the boost score based on matching
                boost_score = match_query_with_keywords(query, payload_keywords)

                if boost_score > 0:
                    original_score = result.score
                    # Add boost_score to the result score, cap at 1.0
                    result.score = int(result.score + boost_score * keyword_weight)
                    logging.info(f"Result ID: {result.id} matched keywords. Original Score: {original_score}, "
                                 f"Boosted Score: {result.score}")

            # Apply the score threshold to the combined results
            filtered_results = [result for result in combined_results if result.score >= score_threshold]
            logging.info(f"Results after applying score threshold ({score_threshold}): {len(filtered_results)}")
        else:
            logging.info("Performing keyword-only search.")
            # Perform search based solely on filters without vector search
            search_results = self.qdrant_client.scroll(
                collection_name=collection_name,
                scroll_filter=qdrant_filter,
                with_payload=with_payload,
                limit=1000
            )
            filtered_results = search_results
            logging.info(f"Results from keyword-only search: {len(filtered_results)}")

        if not filtered_results:
            logging.info("No results after processing.")
            return {}

        # Serialize results for caching and return
        serialized_results = {
            "paragraph_id": [result.id for result in filtered_results],
            "section_title": [result.payload.get('section_title', "N/A") for result in filtered_results],
            "paragraph_title": [result.payload.get('paragraph_title', "N/A") for result in filtered_results],
            "paragraph_text": [result.payload.get('paragraph_text', "N/A") for result in filtered_results],
            "paragraph_blockquote": [result.payload.get('paragraph_blockquote', "N/A") for result in
                                     filtered_results],
            "metadata": [result.payload.get('metadata', "N/A") for result in filtered_results],
            "keywords": [result.payload.get('keywords', []) for result in filtered_results],
            "score": [result.score for result in filtered_results]
        }

        # Cache the processed results using combined_query as the key
        results_cache[combined_query] = serialized_results
        with open(results_cache_file_path, 'w') as cache_file:
            json.dump(results_cache, cache_file)

        return serialized_results

    def reciprocal_rank_fusion(self, results_list: List[List[models.ScoredPoint]], top_k: Optional[int] = None,
                               dense_weight: float = 1.0,
                               sparse_weight: float = 1.0) -> List[models.ScoredPoint]:
        """
        Combine multiple result lists using Reciprocal Rank Fusion (RRF) with adjustable weights.

        Args:
            results_list (List[List[models.ScoredPoint]]): List of result lists (dense and sparse).
            top_k (Optional[int]): If provided, limit the results to top_k.
            dense_weight (float): Weight to apply to the dense vector scores.
            sparse_weight (float): Weight to apply to the sparse vector scores.

        Returns:
            List[models.ScoredPoint]: Combined and sorted results by weighted RRF score.
        """
        k = 1  # Set k=1 to keep scores between 0 and 1
        scores = {}
        result_map = {}

        for idx, results in enumerate(results_list):
            weight = dense_weight if idx == 0 else sparse_weight

            for rank, result in enumerate(results):
                rrf_score = weight * (1.0 / (k + rank))
                if result.id in scores:
                    scores[result.id] += rrf_score
                else:
                    scores[result.id] = rrf_score
                    result_map[result.id] = result  # Store the result object

        # Assign combined scores to result objects
        for id, score in scores.items():
            result_map[id].score = round(score, 3)  # Round to three decimal places

        # Sort results by combined score
        combined_results = sorted(result_map.values(), key=lambda x: x.score, reverse=True)
        logging.info(f"Combined results after RRF: {len(combined_results)}")
        for result in combined_results:
            logging.info(f"Result ID: {result.id}, Score: {result.score}")

        # Apply top_k if provided
        if top_k:
            combined_results = combined_results[:top_k]

        return combined_results



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
    def set_payload(self):
        with open(r"C:\Users\luano\Downloads\AcAssitant\Files\Cache\replacing_keywords.json","r") as f:
            data= json.load(f)
        for i in data:

            print(self.qdrant_client.set_payload(
        **i
            ))

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

    def get_all_collections_payloads_and_save_csv(self, output_file: str = r'C:\Users\luano\Downloads\AcAssitant\Files\Cache',save=False):
        """
        Fetches all collections from Qdrant, retrieves payloads, preprocesses the text,
        and saves the cleaned data into a CSV file.

        Args:
            output_file (str): The path of the CSV file to save the cleaned payloads.
                               Default is 'qdrant_all_collections_cleaned.csv'.
        """

        # Initialize an empty list to store payloads from all collections
        all_payloads = []

        network_list= []
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

                    # # Check if required fields exist in the payload before processing
                    # paragraph_text = payload.get('paragraph_text', "")
                    # paragraph_title = payload.get('paragraph_title', "")
                    # section_title = payload.get('section_title', "")
                    authors=[i.lower() for i in payload.get('metadata',"")["authors"].split(", ")]
                    cleaned= process_keywords(authors_list=authors,keywords_dict=payload.get('keyword_categories',""))
                    all_payloads.extend(cleaned)
                    new_payload = {payload['metadata']["citation_key"]+"_"+str(scroll_result.id): cleaned}
                    replacing={"collection_name":collection_name,"points":[scroll_result.id], "payload":{"keywords":cleaned}}
                    network_list.append(replacing)
                    print(payload["keywords"])
                    # print([i["keywords"] for i in payload.get('keyword_categories',"") ])
                    # Clean and preprocess relevant fields in the payload, joining tokens into strings
                    # new_payload = {
                    #     # 'paragraph_title_cleaned': preprocess_text(paragraph_title),
                    #     # 'paragraph_text_cleaned': preprocess_text(paragraph_text),
                    #     # 'section_title_cleaned': preprocess_text(section_title),
                    #     # 'keywords_cleaned': preprocess_text(" ".join(convert_to_obsidian_tags(keywords)))
                    # }

                    # Append the cleaned payload to the global list
                    # all_payloads.append(new_payload)
                    # print(type(new_payload))

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
        # with open(os.path.join(output_file, "replacing_keywords.json"), 'w', encoding="utf-8") as f_output:
        #     f_output.write(json.dumps(network_list, indent=4))
        if save:
            with open(os.path.join(output_file,"keywords.txt"), 'w', encoding="utf-8") as f_output:
                f_output.write(str(all_payloads) )
            with open(os.path.join(output_file, "keywords_nextwork.txt"), 'w', encoding="utf-8") as f_output:
                f_output.write(str(network_list))
            print(f"Data from all collections has been successfully saved to {output_file}")



