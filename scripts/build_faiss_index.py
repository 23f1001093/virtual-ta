import os, json, faiss
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
texts, metadata, idx = [], {}, 0

for filename, source in [("course_notes.json", "course"), ("discourse_posts.json", "discourse")]:
    path = f"data/{filename}"
    if not os.path.exists(path): continue
    with open(path) as f: data = json.load(f)
    for entry in data:
        section = entry.get("section", entry.get("title", ""))
        for line in entry.get("points", []) + [p["content"] for p in entry.get("posts", []) if "content" in p]:
            if not line.strip(): continue
            full = f"{section}: {line}"
            texts.append(full)
            metadata[str(idx)] = {"text": full, "url": entry.get("url"), "title": section}
            idx += 1

vectors = model.encode(texts, convert_to_numpy=True)
index = faiss.IndexFlatL2(vectors.shape[1])
index.add(vectors)
os.makedirs("embeddings", exist_ok=True)
faiss.write_index(index, "embeddings/faiss_index.bin")
with open("embeddings/metadata.json", "w") as f:
    json.dump(metadata, f, indent=2)
print("✅ FAISS index built.")
