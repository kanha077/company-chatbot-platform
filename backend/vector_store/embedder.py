from sentence_transformers import SentenceTransformer

# We use bge-small-en-v1.5 as per architecture for local embedding
# This downloads the model to cache on first run
model = SentenceTransformer("BAAI/bge-small-en-v1.5")

def embed_text(text: str) -> list[float]:
    """
    Returns the embedding vector for a single string.
    """
    # .tolist() converts the numpy array to a python list of floats
    return model.encode(text).tolist()

def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Returns embedding vectors for a list of strings.
    """
    return model.encode(texts).tolist()
