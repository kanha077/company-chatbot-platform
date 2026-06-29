import chromadb
from chromadb.config import Settings
from config import CHROMA_PERSIST_DIR
from vector_store.embedder import embed_texts, embed_text
import uuid

# Initialize Chroma client
client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)

# Get or create the main collection
collection = client.get_or_create_collection(
    name="company_knowledge",
    metadata={"hnsw:space": "cosine"}
)

def add_chunks(chunks: list[str], source_id: str):
    """
    Embed and store a list of text chunks.
    """
    if not chunks:
        return
        
    embeddings = embed_texts(chunks)
    ids = [f"{source_id}_{uuid.uuid4().hex[:8]}" for _ in chunks]
    metadatas = [{"source_id": source_id, "chunk_index": i} for i in range(len(chunks))]
    
    collection.add(
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas,
        ids=ids
    )

def search_chunks(query: str, top_k: int = 3) -> list[dict]:
    """
    Search for top_k most similar chunks to the query.
    """
    query_embedding = embed_text(query)
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    
    out = []
    if results['documents'] and len(results['documents']) > 0:
        docs = results['documents'][0]
        distances = results['distances'][0] if 'distances' in results and results['distances'] else []
        metas = results['metadatas'][0] if 'metadatas' in results and results['metadatas'] else []
        
        for i in range(len(docs)):
            score = 1.0 - distances[i] if distances else 0.0 # Convert distance to similarity score
            out.append({
                "text": docs[i],
                "score": score,
                "metadata": metas[i] if i < len(metas) else {}
            })
    return out

def clear_all():
    """
    Deletes all items in the collection.
    """
    global collection
    client.delete_collection("company_knowledge")
    collection = client.get_or_create_collection(
        name="company_knowledge",
        metadata={"hnsw:space": "cosine"}
    )
