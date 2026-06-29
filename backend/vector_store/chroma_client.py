import chromadb
from chromadb.config import Settings
from config import CHROMA_PERSIST_DIR
from vector_store.embedder import embed_texts, embed_text
import uuid

# Initialize Chroma client
client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)

def get_bot_collection(bot_id: str):
    return client.get_or_create_collection(
        name=f"bot_{bot_id}",
        metadata={"hnsw:space": "cosine"}
    )

def add_chunks(chunks: list[str], source_id: str, bot_id: str):
    """
    Embed and store a list of text chunks for a specific bot.
    """
    if not chunks:
        return
        
    embeddings = embed_texts(chunks)
    ids = [f"{source_id}_{uuid.uuid4().hex[:8]}" for _ in chunks]
    metadatas = [{"source_id": source_id, "chunk_index": i} for i in range(len(chunks))]
    
    collection = get_bot_collection(bot_id)
    collection.add(
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas,
        ids=ids
    )

def retrieve_context(query: str, top_k: int = 3, bot_id: str = "") -> tuple[str, list, float]:
    """
    Search for top_k most similar chunks to the query for a specific bot.
    """
    if not bot_id:
        return "", [], 0.0
        
    query_embedding = embed_text(query)
    collection = get_bot_collection(bot_id)
    
    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
    except Exception:
        # Collection might be empty
        return "", [], 0.0
    
    out = []
    if results['documents'] and len(results['documents']) > 0 and len(results['documents'][0]) > 0:
        docs = results['documents'][0]
        distances = results['distances'][0] if 'distances' in results and results['distances'] else []
        metas = results['metadatas'][0] if 'metadatas' in results and results['metadatas'] else []
        
        for i in range(len(docs)):
            score = 1.0 - distances[i] if distances else 0.0
            out.append({
                "text": docs[i],
                "score": score,
                "metadata": metas[i] if i < len(metas) else {}
            })
            
        context_text = "\n\n".join([doc["text"] for doc in out])
        avg_confidence = sum([doc["score"] for doc in out]) / len(out)
        return context_text, out, avg_confidence
        
    return "", [], 0.0

def clear_all(bot_id: str):
    """
    Deletes all items in a specific bot's collection.
    """
    try:
        client.delete_collection(f"bot_{bot_id}")
    except Exception:
        pass
