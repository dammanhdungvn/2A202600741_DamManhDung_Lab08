"""
Task 4 - Chunking and indexing Markdown documents.

Chosen chunking strategy:
    RecursiveCharacterTextSplitter with CHUNK_SIZE=500 and CHUNK_OVERLAP=50.
    This is a conservative default for mixed legal/news Markdown: it preserves
    paragraph boundaries when possible, then falls back to line/word/character
    splitting so very long legal text still respects the size limit.

Chosen embedding model:
    sentence-transformers/all-MiniLM-L6-v2, EMBEDDING_DIM=384.
    It is lightweight and fast for local demos. If sentence-transformers or the
    model weights are unavailable, this file falls back to a deterministic
    hashing embedding with the same 384-dimensional shape, keeping the pipeline
    runnable offline.

Chosen vector store:
    Local JSONL vector store at data/index/vector_store.jsonl.
    Weaviate is a good production choice for hybrid search, but local JSONL is
    dependency-light, reproducible for tests, and can later be loaded into
    Weaviate/Chroma/FAISS without changing the chunk schema.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path

STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
INDEX_DIR = Path(__file__).parent.parent / "data" / "index"
VECTORSTORE_PATH = INDEX_DIR / "vector_store.jsonl"
MANIFEST_PATH = INDEX_DIR / "index_manifest.json"


# Recursive chunking is robust for both legal PDFs converted to text and news
# articles converted from JSON. 500 chars keeps chunks precise enough for
# citation; 50 chars overlap preserves context across article/legal boundaries.
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
CHUNKING_METHOD = "recursive"

# all-MiniLM-L6-v2 is small (384 dim) and quick for classroom/local RAG demos.
# The fallback hashing embedder below intentionally uses the same dimension.
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM = 384

VECTOR_STORE = "local_jsonl"


def load_documents() -> list[dict]:
    """
    Read all Markdown files from data/standardized/.

    Returns:
        List of {'content': str, 'metadata': {'source': str, 'type': str, ...}}
    """
    documents: list[dict] = []
    if not STANDARDIZED_DIR.exists():
        return documents

    for md_file in sorted(STANDARDIZED_DIR.rglob("*.md")):
        if not md_file.is_file() or md_file.name.startswith("."):
            continue

        content = md_file.read_text(encoding="utf-8", errors="replace").strip()
        if not content:
            continue

        relative_path = md_file.relative_to(STANDARDIZED_DIR)
        doc_type = relative_path.parts[0] if len(relative_path.parts) > 1 else "unknown"
        documents.append(
            {
                "content": content,
                "metadata": {
                    "source": md_file.name,
                    "path": str(relative_path).replace("\\", "/"),
                    "type": doc_type,
                    "chars": len(content),
                },
            }
        )

    return documents


def _fallback_split_text(text: str) -> list[str]:
    """Dependency-free splitter used only if langchain_text_splitters is absent."""
    chunks: list[str] = []
    step = CHUNK_SIZE - CHUNK_OVERLAP
    for start in range(0, len(text), step):
        chunk = text[start : start + CHUNK_SIZE].strip()
        if chunk:
            chunks.append(chunk)
    return chunks


def chunk_documents(documents: list[dict]) -> list[dict]:
    """
    Chunk documents using RecursiveCharacterTextSplitter.

    Returns:
        List of {'content': str, 'metadata': dict}
    """
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ". ", "; ", ", ", " ", ""],
        )
        split_text = splitter.split_text
    except ImportError:
        split_text = _fallback_split_text

    chunks: list[dict] = []
    for doc_index, document in enumerate(documents):
        splits = split_text(document["content"])
        for chunk_index, chunk_text in enumerate(splits):
            normalized = chunk_text.strip()
            if not normalized:
                continue
            chunks.append(
                {
                    "content": normalized,
                    "metadata": {
                        **document.get("metadata", {}),
                        "doc_index": doc_index,
                        "chunk_index": chunk_index,
                        "chunk_chars": len(normalized),
                    },
                }
            )

    return chunks


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[\wÀ-ỹ]+", text.lower(), flags=re.UNICODE)


def _hashing_embedding(text: str, dim: int = EMBEDDING_DIM) -> list[float]:
    """
    Deterministic fallback embedding.

    It is not semantic like MiniLM, but it gives stable dense vectors for local
    indexing and keeps the Task 4 artifact usable without network/model access.
    """
    vector = [0.0] * dim
    for token in _tokenize(text):
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        bucket = int.from_bytes(digest[:4], "little") % dim
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[bucket] += sign

    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [round(value / norm, 6) for value in vector]


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """
    Add an 'embedding' key to each chunk.

    Uses sentence-transformers/all-MiniLM-L6-v2 when installed and available;
    otherwise uses a deterministic 384-dim hashing embedding fallback.
    """
    texts = [chunk["content"] for chunk in chunks]
    if not texts:
        return chunks

    try:
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer(EMBEDDING_MODEL)
        embeddings = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
        for chunk, embedding in zip(chunks, embeddings):
            chunk["embedding"] = [float(value) for value in embedding.tolist()]
            chunk["embedding_model"] = EMBEDDING_MODEL
    except Exception:
        for chunk in chunks:
            chunk["embedding"] = _hashing_embedding(chunk["content"])
            chunk["embedding_model"] = f"{EMBEDDING_MODEL}__hashing_fallback"

    return chunks


def index_to_vectorstore(chunks: list[dict]) -> Path:
    """
    Persist chunks and embeddings to a local JSONL vector store.

    Each line is one chunk with content, score-ready embedding, and metadata.
    """
    INDEX_DIR.mkdir(parents=True, exist_ok=True)

    with VECTORSTORE_PATH.open("w", encoding="utf-8") as file:
        for chunk_id, chunk in enumerate(chunks):
            record = {
                "id": f"chunk-{chunk_id:06d}",
                "content": chunk["content"],
                "embedding": chunk.get("embedding", []),
                "metadata": chunk.get("metadata", {}),
                "embedding_model": chunk.get("embedding_model", EMBEDDING_MODEL),
            }
            file.write(json.dumps(record, ensure_ascii=False) + "\n")

    manifest = {
        "vector_store": VECTOR_STORE,
        "path": str(VECTORSTORE_PATH.relative_to(Path(__file__).parent.parent)),
        "document_count": len({c["metadata"].get("path") for c in chunks}),
        "chunk_count": len(chunks),
        "chunking_method": CHUNKING_METHOD,
        "chunk_size": CHUNK_SIZE,
        "chunk_overlap": CHUNK_OVERLAP,
        "embedding_model": chunks[0].get("embedding_model", EMBEDDING_MODEL) if chunks else EMBEDDING_MODEL,
        "embedding_dim": EMBEDDING_DIM,
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return VECTORSTORE_PATH


def run_pipeline() -> Path:
    """Run load -> chunk -> embed -> index."""
    print("=" * 50)
    print("Task 4: Chunking & Indexing")
    print(f"  Chunking: {CHUNKING_METHOD} (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")
    print(f"  Embedding: {EMBEDDING_MODEL} (dim={EMBEDDING_DIM})")
    print(f"  Vector Store: {VECTOR_STORE}")
    print("=" * 50)

    docs = load_documents()
    print(f"Loaded {len(docs)} documents")

    chunks = chunk_documents(docs)
    print(f"Created {len(chunks)} chunks")

    chunks = embed_chunks(chunks)
    print(f"Embedded {len(chunks)} chunks")

    index_path = index_to_vectorstore(chunks)
    print(f"Indexed to: {index_path}")
    return index_path


if __name__ == "__main__":
    run_pipeline()
