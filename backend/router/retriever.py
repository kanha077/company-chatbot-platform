from vector_store.chroma_client import search_chunks
from config import RELEVANCE_THRESHOLD

def retrieve_context(query: str, top_k: int = 3) -> tuple[str, list[str], float]:
    """
    Retrieves relevant context for the given query.
    Returns:
        - aggregated_context (str)
        - list_of_chunk_ids (list)
        - max_confidence (float)
    """
    results = search_chunks(query, top_k=top_k)
    
    if not results:
        return "", [], 0.0
        
    max_score = max(r["score"] for r in results)
    
    if max_score < RELEVANCE_THRESHOLD:
        # Not relevant enough
        return "", [], max_score
        
    context_text = "\n\n".join([r["text"] for r in results])
    source_chunks = [r.get("metadata", {}).get("source_id", "unknown") for r in results]
    
    return context_text, source_chunks, max_score
