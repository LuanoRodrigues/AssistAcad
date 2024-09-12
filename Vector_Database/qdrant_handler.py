import hashlib
import json
from datetime import time
from typing import List, Dict, Optional
import math
import re
# from NLP_module.normalise_texts import
from collections import defaultdict
import logging
import numpy as np


from NLP_module.normalise_texts import fuzzy_match,get_synonyms,preprocess_text,proximity_boost, normalize_text2,wildcard_match,generate_trigrams,compute_similarity
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
def get_trigram_matches(text,get_cache_embedding, query_vector='', similarity_threshold=0.7, batch=False):


    trigrams = generate_trigrams(text)  # Generate trigrams from the preprocessed text
    matching_trigrams = []

    for trigram in trigrams:
        trigram_embedding = get_cache_embedding(trigram)
        if batch:
            continue  # In batch mode, skip similarity check and continue to next trigram

        # Compute similarity using GPU
        similarity_score = compute_similarity(query_vector, trigram_embedding)

        if similarity_score >= similarity_threshold:  # Check if similarity meets the threshold
            matching_trigrams.append((trigram, similarity_score))  # Save matching trigram and score

    return sorted(matching_trigrams, key=lambda x: x[1], reverse=True)  # Return sorted matching trigrams


def apply_trigram_embedding_boost(text: str, query_vector: list, weight: float,get_cache_embedding:None, similarity_threshold: float,
                                  batch=False) -> float:
    """
    Apply a boost to the score based on trigram matching between the text and the query vector.

    Parameters:
    -----------
    text : str
        The text to search for trigrams in.
    query_vector : list
        The dense vector representation of the query.
    weight : float
        The weight to apply if a trigram match is found.
    similarity_threshold : float
        The threshold for trigram similarity to trigger a boost.

    Returns:
    --------
    float
        The weighted boost to be applied to the score based on trigram matching.
    """
    # Get matching trigrams and their similarity scores
    matching_trigrams = get_trigram_matches(text=text, query_vector=query_vector, similarity_threshold=similarity_threshold, batch=batch,get_cache_embedding=get_cache_embedding)

    if not matching_trigrams:
        return 0  # No matching trigrams

    # Use the best trigram match's similarity score for boosting
    best_match_score = matching_trigrams[0][1]  # Get the highest similarity score
    return weight * best_match_score

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

    def process_and_append(self, metadata,paragraph_count,paper_id, article_title,section_title, paragraph_title, paragraph_text, paragraph_blockquote):
        """Process embeddings and append data to the collection."""

        # Get embeddings for both title and text
        text_embedding = get_embedding(paragraph_text)

        # Get the collection name based on the paper_id
        collection_name = f"paper_{paper_id}"

        # Append data to the collection and get operation info
        operation_info = self.append_data(
            collection_name=collection_name,  # Your collection name
            article_title=article_title,
            section_title=section_title,  # Section title
            paragraph_title=paragraph_title,  # Paragraph title
            paragraph_text=paragraph_text,  # Paragraph text
            paragraph_blockquote=paragraph_blockquote,  # Blockquote (if available)
            custom_id=paper_id,  # Your custom ID (e.g., "SV5QMQSM")
            text_embedding=text_embedding,  # Embedding for the text
            paragraph_count=paragraph_count,
            metadata=metadata
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
        if vector:
            collection_name = f"paper_{collection_name}"

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

    def append_data(self, collection_name,text_embedding,metadata='', paragraph_count='',article_title='',section_title='', paragraph_title='', paragraph_text='', paragraph_blockquote='',
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
                "metadata":metadata
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

    def advanced_search(self, collection_name: str, query: str = None,
                        top_k: Optional[int] = None,
                        filter_conditions: Optional[Dict[str, str]] = None, score_threshold: float = 0.60,
                        with_payload: bool = True, with_vectors: bool = False, hnsw_ef: int = 512, exact: bool = False,
                        keywords: Optional[List[str]] = None) -> Dict[str, List]:
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
        query_vector =  query_with_history(query)
        # if keywords is None:
        #     keywords= query.split()
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
        #----
        # result, next_page_token = self.qdrant_client.scroll(
        #     collection_name=collection_name,
        #
        #     limit=1000  # Limit to one result
        # )
        # print(result)
        # input('Press Enter to continue...')
        #---
        try:
            # Perform the query
            results = self.qdrant_client.query_points(
                collection_name=collection_name,
                query=query_vector,  # Dense vector search for semantic matching
                with_payload=with_payload,
                with_vectors=with_vectors,
                query_filter=query_filter,  # Apply any filters
                search_params=search_params,
                # score_threshold=score_threshold,
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
                query_vector=query_vector,
                payload=payload,
                keywords=keywords,
                section_weight=0.4,
                paragraph_title_weight=0.55,
                text_weight=0.5,
                score_threshold=score_threshold,
                initial_score =score,
                query=query

            )
            # print(result)
            # input('Press Enter to continue...')
            if adjusted_score is None:
                # Skip the result if _rescore_result indicates a NOT keyword match
                continue

            # Append results only if the paragraph passed the "NOT" filter and has been rescored
            processed_results['section_title'].append(payload.get('section_title', "N/A"))
            processed_results['paragraph_title'].append(payload.get('paragraph_title', "N/A"))
            processed_results['paragraph_text'].append(payload.get('paragraph_text', "N/A"))
            processed_results['paragraph_blockquote'].append(payload.get('paragraph_blockquote', "N/A"))
            processed_results['rescore'].append(adjusted_score)
            processed_results['paragraph_id'].append(result.id)
            # new_bigrams = get_trigram_matches(payload.get('paragraph_text', "N/A"))


        # Rescore and sort the results
        self._sort_results(processed_results)
        return processed_results

    def _rescore_result(self, query_vector:list,payload: Dict[str, str], initial_score: float, score_threshold: float,
                        query: str, keywords: Optional[Dict[str, List[str]]] = None,
                        section_weight: float = 0.5, paragraph_title_weight: float = 0.4, text_weight: float = 0.2,
                        proximity_boost_weight: float = 0.3, proximity_threshold: int = 5,
                        similarity_threshold: float = 0.7) -> Optional[float]:
        """
        Rescore the result based on:
        - If keywords are None: use bigram matches between the query and the section/paragraph fields and apply the weights,
          with additional exact keyword matches using lemmatization, stopword removal, fuzzy matching, proximity boosting, and synonym expansion.
        - If keywords are provided: apply the keyword logic (AND, OR, NOT) with the same additional matching techniques.
        """

        # Extract fields from the payload
        section_title = payload.get('section_title', "")
        paragraph_title = payload.get('paragraph_title', "")
        paragraph_text = payload.get('paragraph_text', "")

        # Initialize adjusted score with the initial score
        adjusted_score = initial_score

        # Generate query embedding using OpenAI's embedding model


        # Helper function: Apply fuzzy matching, proximity boosting, and synonym expansion
        def process_text_for_keywords(text, keywords, weight):
            expanded_keywords = set()
            for keyword in keywords:
                expanded_keywords.update(get_synonyms(keyword))
            expanded_keywords.update(keywords)

            # Apply fuzzy matching to the text
            confidence = fuzzy_match(text, expanded_keywords)
            dynamic_weight = weight * confidence  # Scale weight dynamically by fuzzy match confidence
            return dynamic_weight

        # Normalize or adjust the score if necessary (logarithmic normalization)
        def normalize_score(score):
            return math.log(1 + score)

        # Proximity boost logic
        def apply_proximity_boost(text, keywords, base_weight):
            boost = proximity_boost(text, keywords, proximity_threshold)
            return base_weight if boost else 0

        # Bigram matching using embeddings


        # If keywords are None, use the query string for bigram matching, lemmatization, and apply the weights
        if keywords is None:
            # query_bigrams = generate_bigrams(query)  # Generate bigrams
            query_tokens = preprocess_text(query)  # Preprocess query for exact keyword match

            # trigram checking and keyword matches for each field using embedding similarity
            adjusted_score += apply_trigram_embedding_boost(get_cache_embedding=self.get_cache_embedding,text=section_title, query_vector=query_vector, weight=section_weight,similarity_threshold=similarity_threshold)
            adjusted_score += apply_trigram_embedding_boost(get_cache_embedding=self.get_cache_embedding,text=paragraph_title, query_vector=query_vector, weight=section_weight,similarity_threshold=similarity_threshold)
            adjusted_score += apply_trigram_embedding_boost(get_cache_embedding=self.get_cache_embedding,text=paragraph_text,  query_vector=query_vector, weight=section_weight,similarity_threshold=similarity_threshold)

            # Exact keyword matching with fuzzy logic and synonym expansion
            adjusted_score += process_text_for_keywords(section_title, query_tokens, section_weight)
            adjusted_score += process_text_for_keywords(paragraph_title, query_tokens, paragraph_title_weight)
            adjusted_score += process_text_for_keywords(paragraph_text, query_tokens, text_weight)

            # Apply proximity boost for query tokens in paragraph text
            adjusted_score += apply_proximity_boost(paragraph_text, query_tokens, proximity_boost_weight)

        # If keywords are provided, apply keyword logic (AND, OR, NOT) with the same matching techniques
        else:
            expanded_keywords = set()

            # Process OR logic: Match if any keyword in the OR group is found
            if "OR" in keywords:
                for keyword in keywords["OR"]:
                    expanded_keywords.update(get_synonyms(keyword))
                expanded_keywords.update(keywords["OR"])

            # Process AND logic: All keywords in the AND group must be present
            if "AND" in keywords:
                for keyword in keywords["AND"]:
                    expanded_keywords.update(get_synonyms(keyword))
                expanded_keywords.update(keywords["AND"])

            # Handle "NOT" logic: Exclude results if any keyword in the NOT group is found
            if "NOT" in keywords:
                for keyword in keywords["NOT"]:
                    keyword_normalized = normalize_text2(keyword)
                    if (wildcard_match(keyword_normalized, section_title) or
                            wildcard_match(keyword_normalized, paragraph_title) or
                            wildcard_match(keyword_normalized, paragraph_text)):
                        return None  # Exclude result if a NOT keyword is found

            # Apply AND logic
            if "AND" in keywords:
                for keyword in keywords["AND"]:
                    keyword_normalized = normalize_text2(keyword)
                    adjusted_score += process_text_for_keywords(section_title, [keyword_normalized], section_weight)
                    adjusted_score += process_text_for_keywords(paragraph_title, [keyword_normalized],
                                                                paragraph_title_weight)
                    adjusted_score += process_text_for_keywords(paragraph_text, [keyword_normalized], text_weight)

            # Apply OR logic
            if "OR" in keywords:
                for keyword in keywords["OR"]:
                    keyword_normalized = normalize_text2(keyword)
                    if (process_text_for_keywords(section_title, [keyword_normalized], section_weight) or
                            process_text_for_keywords(paragraph_title, [keyword_normalized], paragraph_title_weight) or
                            process_text_for_keywords(paragraph_text, [keyword_normalized], text_weight)):
                        adjusted_score += section_weight + paragraph_title_weight + text_weight
                        break  # Exit once an OR match is found

            # Apply proximity boost for keywords in paragraph text
            adjusted_score += apply_proximity_boost(paragraph_text, expanded_keywords, proximity_boost_weight)

        # Apply normalization to smooth out the score
        adjusted_score = normalize_score(adjusted_score)

        # Apply the threshold after rescoring
        if adjusted_score < score_threshold:
            return None  # Exclude the result if the score is below the threshold

        # Return the adjusted score
        return adjusted_score
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

