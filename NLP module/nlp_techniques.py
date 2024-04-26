from gensim.models import Word2Vec
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Sample text data
texts = [
    "Natural language processing is a field of artificial intelligence that deals with the interaction between computers and humans through natural language.",
    "Machine learning is the scientific study of algorithms and statistical models that computer systems use to perform a specific task without using explicit instructions.",
    "Deep learning is a subset of machine learning in artificial intelligence that has networks capable of learning unsupervised from data that is unstructured or unlabeled.",
    "Computer vision is an interdisciplinary field that deals with how computers can gain high-level understanding from digital images or videos.",
    "Reinforcement learning is an area of machine learning concerned with how software agents ought to take actions in an environment to maximize some notion of cumulative reward."
]


# Define a function to get embeddings for a given text
def get_embedding(text, model):
    words = text.lower().split()  # Split text into words
    embedding = np.zeros((model.vector_size,), dtype=np.float32)  # Initialize embedding vector

    # Aggregate word vectors
    word_count = 0
    for word in words:
        if word in model.wv:
            embedding += model.wv[word]  # Add word vector to the embedding
            word_count += 1

    # Normalize the embedding vector
    if word_count != 0:
        embedding /= word_count

    return embedding


# Train a Word2Vec model on the text data
sentences = [text.lower().split() for text in texts]
model = Word2Vec(sentences, vector_size=100, window=5, min_count=1, workers=4)


# Define a function to calculate cosine similarity between two texts
def cosine_similarity_text(text1, text2, model):
    embedding1 = get_embedding(text1, model)
    embedding2 = get_embedding(text2, model)
    return cosine_similarity([embedding1], [embedding2])[0][0]


# Calculate cosine similarity between all pairs of texts
for i in range(len(texts)):
    for j in range(i + 1, len(texts)):
        similarity = cosine_similarity_text(texts[i], texts[j], model)
        print(f"Similarity between '{texts[i]}' and '{texts[j]}': {similarity}")
