import tiktoken
from config import MAX_TOKENS

def split_into_chunks(text, max_tokens=MAX_TOKENS):
    enc = tiktoken.get_encoding("cl100k_base")
    words = text.split('. ')
    chunks, current = [], []

    for sentence in words:
        current.append(sentence)
        tokens = len(enc.encode('. '.join(current)))
        if tokens >= max_tokens:
            chunks.append('. '.join(current[:-1]))
            current = [sentence]
    if current:
        chunks.append('. '.join(current))

    return chunks
