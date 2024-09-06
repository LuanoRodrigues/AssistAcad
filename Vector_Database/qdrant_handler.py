from collections import defaultdict

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from qdrant_client.http import models  # Import models from qdrant_client.http
from qdrant_client.http.exceptions import UnexpectedResponse

import uuid
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
            # Create collection if it doesn't exist
            self.qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
            )
            print(f"Collection '{collection_name}' created.")
            return True  # Collection was newly created

    def append_data(self, collection_name, section_title, paragraph_title, paragraph_text, paragraph_blockquote,
                    custom_id, title_embedding, text_embedding):
        """Insert embeddings for paragraph title, text, and blockquote into the collection."""

        # Use UUID or hash as point ID (this will be the actual point ID)
        paragraph_id = str(uuid.uuid4())  # Generate a UUID

        # Structure the payload, storing custom ID and title embedding
        payload = {
            "section_title": section_title,
            "paragraph_title": paragraph_title,
            "paragraph_text": paragraph_text,
            "paragraph_blockquote": paragraph_blockquote,  # Include blockquote information
            "custom_id": custom_id,  # Store 'SV5QMQSM' as part of the metadata
            "title_embedding": title_embedding  # Store the title embedding in the payload
        }

        # Insert data into Qdrant with UUID point ID and custom ID in payload
        operation_info = self.qdrant_client.upsert(
            collection_name=collection_name,
            points=[
                PointStruct(
                    id=paragraph_id,  # Use UUID as point ID
                    vector=text_embedding,  # Use paragraph text embedding for vector storage
                    payload=payload  # Store metadata, including custom ID and title embedding
                )
            ]
        )

        print(
            f"Inserted data for paragraph '{paragraph_title}' under section '{section_title}' with custom ID '{custom_id}'.")
        return operation_info


    def get_section_embeddings(self, paper_id, section_title):
        """Retrieve all embeddings for paragraphs under a specific section."""
        collection_name = f"paper_{paper_id}"

        # Query all points in the collection that match the section title
        results = self.qdrant_client.scroll(
            collection_name=collection_name,
            scroll_filter=models.Filter(
                must=[models.FieldCondition(
                    key="section_title",
                    match=models.MatchValue(value=section_title)
                )]
            )
        )

        embeddings = []
        for point in results:
            embeddings.append({
                "paragraph_title": point.payload["paragraph_title"],
                "paragraph_text": point.payload["paragraph_text"],
                "paragraph_blockquote": point.payload["paragraph_blockquote"],
                "paragraph_text_embedding": point.vector
            })

        return embeddings

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

    def advanced_search(self, collection_name, query_vector=None, top_k=None, filter_conditions=None,
                        score_threshold=2, with_payload=True, with_vectors=False, hnsw_ef=256, exact=False):
        """
            Perform an advanced search in the Qdrant collection and return the text fields associated with the embedding.

            This function retrieves the results based on the `title_embedding` and `text_embedding`, but returns the corresponding
            'paragraph_title', 'paragraph_text', and their 'section_title'.
            """
        # Define optional filtering if provided
        query_filter = None
        if filter_conditions:
            must_conditions = [models.FieldCondition(
                key=key,
                match=models.MatchValue(value=value)
            ) for key, value in filter_conditions.items()]
            query_filter = models.Filter(must=must_conditions)

        # Define search parameters for HNSW ANN search
        search_params = models.SearchParams(
            hnsw_ef=hnsw_ef,
            exact=exact
        )

        # Perform the query using `query_points` API
        results = self.qdrant_client.query_points(

            collection_name=collection_name,
            query=query_vector,  # The vector to search against
            query_filter=query_filter,  # Optional filters for non-embedding fields
            limit=top_k,  # Optionally limit number of results
            with_payload=with_payload,  # Include payload data
            with_vectors=with_vectors,  # Don't include vectors in the result
            score_threshold=score_threshold,  # Filter results based on the score threshold
            search_params=search_params  # Additional search parameters (HNSW config)
        ).points
        print(results)

        # Initialize list to store processed results
        processed_results =  {
                            'section_title': [],
                            'paragraph_title': [],
                            'paragraph_text': []
}

        # Process each result: collect paragraph title, text, and section title
        for result in results:
            payload = result.payload

            title_embedding = payload.get('title_embedding', None)
            text_embedding = payload.get('text_embedding', None)

            # If there's a match on embeddings, retrieve the associated text and section
            if title_embedding or text_embedding:
                result_data = {
                    'section_title': payload.get('section_title', "N/A"),  # Get section title
                    'paragraph_title': payload.get('paragraph_title', "N/A"),  # Get paragraph title
                    'paragraph_text': payload.get('paragraph_text', "N/A"),  # Get paragraph text
                }
                processed_results['section_title'].append(result_data['section_title'])
                processed_results['paragraph_title'].append(result_data['paragraph_title'])
                processed_results['paragraph_text'].append(result_data['paragraph_text'])

        input(processed_results)
        return processed_results
    def qdrant_collections(self,col_name):
        collection = [collection.name for collection in self.qdrant_client.get_collections().collections if collection.name.split("_")[-1]==col_name]
        return collection
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
