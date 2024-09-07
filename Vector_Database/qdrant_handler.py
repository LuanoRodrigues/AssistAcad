import hashlib
from typing import List, Dict, Optional
import re
from collections import defaultdict
import logging
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.grpc import SparseVectorParams, Modifier
from qdrant_client.models import Distance, VectorParams, PointStruct
from qdrant_client.http import models  # Import models from qdrant_client.http
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.http.models import VectorParams, SparseVectorParams, Distance, Modifier

import uuid

from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from yellowbrick.cluster import KElbowVisualizer
from kneed import KneeLocator
import matplotlib.pyplot as plt


class QdrantHandler:
    def __init__(self, qdrant_url="http://localhost:6333"):
        self.qdrant_client = QdrantClient(url=qdrant_url)

    def create_collection(self, paper_id, vector_size=3072):
        """Create a collection in Qdrant based on a given paper ID if it does not exist."""
        collection_name = f"paper_{paper_id}"

        # Check if the collection already exists
        try:
            self.qdrant_client.get_collection(collection_name)
            print(f"Collection '{collection_name}' already exists.")

            return False  # Collection already exists
        except Exception as e:
            print(f"Collection '{collection_name}' not found. Creating new collection.")

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

    def append_data(self, collection_name, paragraph_count,article_title,section_title, paragraph_title, paragraph_text, paragraph_blockquote,
                    custom_id,text_embedding):
        """
        Insert embeddings for paragraph title and paragraph text into the collection with proper handling for both vectors.
        """

        # Use UUID or hash as point ID (this will be the actual point ID)
        paragraph_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, custom_id))

        # Structure the payload, storing custom ID and other metadata
        payload = {
            "article_title":article_title,
            "section_title": section_title,
            "paragraph_title": paragraph_title,
            "paragraph_text": paragraph_text,
            "paragraph_blockquote": paragraph_blockquote,  # Include blockquote information
            "custom_id": custom_id,  # Store the custom ID in the payload
            "paragraph_count":paragraph_count
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

        print(
            f"Inserted data for paragraph '{paragraph_title}' under section '{section_title}' with custom ID '{custom_id}'.")
        return operation_info

    def cluster_paragraphs(self, collection_names, max_clusters=10):
        """
           Perform clustering on paragraph vectors from multiple collections in Qdrant and group paragraphs based on their vector similarity.
           Automatically detect the optimal number of clusters using the Elbow Method.

           Parameters:
               collection_names (list): A list of Qdrant collection names where paragraphs are stored.
               max_clusters (int): The maximum number of clusters to test for the optimal k. Default is 10.

           Returns:
               clustered_paragraphs (dict): A dictionary where each key is a cluster label and each value is a list of paragraph texts.
           """

        paragraph_vectors = []
        paragraph_data = []  # List to store both the title and text as a tuple

        # Step 1: Fetch vectors and corresponding paragraph texts from each collection
        for collection_name in collection_names:
            # Retrieve all points with vectors from the collection using scroll (no need for IDs)
            scroll_result = self.qdrant_client.scroll(
                collection_name=collection_name,
                with_payload=True,
                with_vectors=True,  # Retrieve vectors
                limit=1  # Adjust the limit as needed
            )[0][0]

            # input(scroll_result.vector )
            vector = scroll_result.vector  # Assuming "text_embedding" is the vector field
            text = scroll_result.payload['paragraph_text']  # Extract paragraph text from payload
            title = scroll_result.payload['paragraph_title']  # Extract paragraph text from payload

            if vector and text and title:
                paragraph_vectors.append(vector)
                paragraph_data.append((title, text))  # Store tuple (title, text)

                # Step 2: Convert the paragraph_vectors list to a NumPy array
            paragraph_vectors = np.array(paragraph_vectors)

            # Step 3: Adjust max_clusters to ensure it does not exceed the number of samples
            num_paragraphs = len(paragraph_vectors)
            max_clusters = min(max_clusters, num_paragraphs)

            # Step 4: Find the optimal number of clusters (k) using the Elbow method and KneeLocator
            kmeans = KMeans()
            visualizer = KElbowVisualizer(kmeans, k=(2, max_clusters), timings=False)

            # Fit the data to the visualizer to calculate the optimal k
            visualizer.fit(paragraph_vectors)
            visualizer.show()  # This will display the elbow graph

            # Automatically detect the elbow point programmatically
            inertia = visualizer.k_scores_  # Get the inertia values from the visualizer
            kneedle = KneeLocator(range(2, max_clusters + 1), inertia, curve="convex", direction="decreasing")
            optimal_k = kneedle.elbow

            print(f"Optimal number of clusters: {optimal_k}")

            # Step 5: Perform K-means clustering with the optimal number of clusters
            kmeans = KMeans(n_clusters=optimal_k, random_state=42)
            cluster_labels = kmeans.fit_predict(paragraph_vectors)

            # Step 6: Group paragraphs based on their cluster labels
            clustered_paragraphs = {i: [] for i in range(optimal_k)}
            for label, paragraph_info in zip(cluster_labels, paragraph_data):
                clustered_paragraphs[label].append(paragraph_info)  # Append the tuple (title, text)

            return clustered_paragraphs

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

    def advanced_search(self, collection_name: str, query_vector: Optional[List[float]] = None,
                        top_k: Optional[int] = None,
                        filter_conditions: Optional[Dict[str, str]] = None, score_threshold: float = 0.40,
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
                score_threshold=score_threshold,
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
                initial_score=score,
                keywords=keywords,
                section_weight=0.3,
                paragraph_title_weight=0.2,
                text_weight=0.1
            )
            if adjusted_score is None:
                # Skip the result if _rescore_result indicates a NOT keyword match
                continue

            # Append results only if the paragraph passed the "NOT" filter and has been rescored
            processed_results['section_title'].append(payload.get('section_title', "N/A"))
            processed_results['paragraph_title'].append(payload.get('paragraph_title', "N/A"))
            processed_results['paragraph_text'].append(payload.get('paragraph_text', "N/A"))
            processed_results['paragraph_blockquote'].append(payload.get('paragraph_blockquote', "N/A"))
            processed_results['rescore'].append(adjusted_score)

        # Rescore and sort the results
        self._sort_results(processed_results)
        return processed_results

    def _rescore_result(self, payload: Dict[str, str], initial_score: float, keywords: Optional[Dict[str, List[str]]],
                        section_weight: float = 0.5, paragraph_title_weight: float = 0.4, text_weight: float = 0.2) -> \
    Optional[float]:
        """
        Rescore the result based on the presence of keywords in the section title, paragraph title, and text,
        supporting AND/OR/NOT logic for keyword matching. Returns None if a NOT keyword is found.
        """
        section_title = payload.get('section_title', "")
        paragraph_title = payload.get('paragraph_title', "")
        paragraph_text = payload.get('paragraph_text', "")
        if keywords is not None:
            # Handle "NOT" logic - exclude results if any keyword in the NOT group is found
            if "NOT" in keywords:
                for keyword in keywords["NOT"]:
                    if keyword.lower() in section_title.lower() or \
                            keyword.lower() in paragraph_title.lower() or \
                            keyword.lower() in paragraph_text.lower():
                        # Return None to indicate exclusion if a NOT keyword is found
                        return None

            adjusted_score = initial_score

            # Handle "AND" logic - all keywords in the AND group must appear
            if "AND" in keywords:
                all_keywords_found = all(
                    keyword.lower() in section_title.lower() or
                    keyword.lower() in paragraph_title.lower() or
                    keyword.lower() in paragraph_text.lower()
                    for keyword in keywords["AND"]
                )
                if all_keywords_found:
                    adjusted_score += section_weight  # Adjust based on how you want to boost AND logic

            # Handle "OR" logic - any keyword in the OR group can appear
            if "OR" in keywords:
                any_keyword_found = any(
                    keyword.lower() in section_title.lower() or
                    keyword.lower() in paragraph_title.lower() or
                    keyword.lower() in paragraph_text.lower()
                    for keyword in keywords["OR"]
                )
                if any_keyword_found:
                    adjusted_score += paragraph_title_weight  # Adjust based on OR logic

            return adjusted_score
        else:
            return initial_score

    def _sort_results(self, processed_results: defaultdict) -> None:
        """
        Sort the processed results based on the adjusted score in descending order.
        """
        sorted_results = sorted(zip(
            processed_results['section_title'],
            processed_results['paragraph_title'],
            processed_results['paragraph_text'],
            processed_results['paragraph_blockquote'],
            processed_results['rescore']
        ), key=lambda x: x[-1], reverse=True)

        if sorted_results:
            (processed_results['section_title'],
             processed_results['paragraph_title'],
             processed_results['paragraph_text'],
             processed_results['paragraph_blockquote'],
             processed_results['rescore']) = zip(*sorted_results)

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
