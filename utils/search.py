import faiss, json, numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.read_index("embeddings/faiss_index.bin")

with open("embeddings/metadata.json") as f:
    metadata = json.load(f)

def search_faiss(query, top_k=5):
    vector = model.encode([query], convert_to_numpy=True)
    D, I = index.search(np.array(vector).astype("float32"), top_k)
    return [metadata[str(i)] for i in I[0] if str(i) in metadata]
