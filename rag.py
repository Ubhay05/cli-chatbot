import os
import pickle
from config import NOTES_DIR, VECTOR_STORE

os.makedirs(NOTES_DIR, exist_ok=True)
os.makedirs(VECTOR_STORE, exist_ok=True)

STORE_FILE = os.path.join(VECTOR_STORE, "index.pkl") # pickle file way to store emdeddings in disk

def _chunk_text(text, chunk_size=500, overlap=50):# overlap to ensure no missing of imp parts
    words  = text.split()
    chunks = []
    i      = 0
    while i < len(words):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks

def _embed_texts(texts):#imp why this works ? concept behind tf-idf ? 
    """
    We use a simple TF-IDF(term freq,inverse document freq) style similarity
    """
    from collections import Counter
    import math

    def tokenize(text):
        return text.lower().split()

    def tfidf_vector(text, vocab):
        tokens = tokenize(text)
        tf     = Counter(tokens)
        vec    = [tf.get(w, 0) / (len(tokens) + 1) for w in vocab]
        return vec

    # Build vocabulary from all texts ( likee set in c++ )
    all_tokens = []
    for t in texts:
        all_tokens.extend(tokenize(t))
    vocab = list(set(all_tokens))

    return [tfidf_vector(t, vocab) for t in texts], vocab

def _cosine_similarity(a, b):#dot product to find similarity
    dot    = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x ** 2 for x in a) ** 0.5
    norm_b = sum(x ** 2 for x in b) ** 0.5
    return dot / (norm_a * norm_b + 1e-10)

def index_notes(): #mixing chunks from all files then taking vectorisation of all
    notes_files = [f for f in os.listdir(NOTES_DIR) if f.endswith(".txt")]

    if not notes_files:
        print(f"  No .txt files found in {NOTES_DIR}/")
        print("  Add your notes as .txt files and run 'index' again.")
        return False

    all_chunks  = []
    all_sources = []

    for fname in notes_files:
        path = os.path.join(NOTES_DIR, fname)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        chunks = _chunk_text(text)
        all_chunks.extend(chunks)
        all_sources.extend([fname] * len(chunks))
        print(f"  Indexed: {fname} ({len(chunks)} chunks)")

    print(f"  Building TF-IDF vectors for {len(all_chunks)} chunks...")
    embeddings, vocab = _embed_texts(all_chunks)

    store = {
        "chunks":     all_chunks,
        "sources":    all_sources,
        "embeddings": embeddings,
        "vocab":      vocab
    }
    with open(STORE_FILE, "wb") as f:
        pickle.dump(store, f)

    print(f" Saved vector store → {STORE_FILE}")
    return True

def retrieve(query, top_k=3):
    if not os.path.exists(STORE_FILE):
        return []

    with open(STORE_FILE, "rb") as f:
        store = pickle.load(f)

    vocab = store["vocab"]

    # Vectorize query using same vocab
    from collections import Counter
    tokens = query.lower().split()
    tf     = Counter(tokens)
    query_vec = [tf.get(w, 0) / (len(tokens) + 1) for w in vocab]

    scored = []
    for i, emb in enumerate(store["embeddings"]):
        score = _cosine_similarity(query_vec, emb)
        scored.append((score, store["chunks"][i], store["sources"][i]))

    scored.sort(reverse=True, key=lambda x: x[0])
    return scored[:top_k]

def build_rag_context(query):
    results = retrieve(query)
    if not results:
        return None

    context = "Relevant notes:\n\n"
    for score, chunk, source in results:
        context += f"[From {source}]:\n{chunk}\n\n"
    return context

def rag_available():
    return os.path.exists(STORE_FILE)