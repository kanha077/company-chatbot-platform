from transformers import AutoTokenizer

# Using a lightweight tokenizer just for chunking limits, e.g. bert-base-uncased
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

def chunk_text(text: str, chunk_size=400, overlap=50) -> list[str]:
    """
    Splits text into overlapping token chunks.
    Overlap ensures context is not lost at chunk boundaries.
    """
    tokens = tokenizer.encode(text, add_special_tokens=False)
    chunks = []
    start = 0
    while start < len(tokens):
        end = start + chunk_size
        chunk_tokens = tokens[start:end]
        chunk = tokenizer.decode(chunk_tokens)
        chunks.append(chunk)
        start += (chunk_size - overlap)
    return chunks
