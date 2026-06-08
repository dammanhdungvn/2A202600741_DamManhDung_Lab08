"""
Task 5 - Semantic search over the Task 4 local vector store.

The query embedding uses the same model/fallback strategy as Task 4:
sentence-transformers/all-MiniLM-L6-v2 when available, otherwise the 384-dim
hashing embedding fallback. Scores are cosine similarities sorted descending.
"""

from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path

from .task4_chunking_indexing import (
    EMBEDDING_MODEL,
    INDEX_DIR,
    VECTORSTORE_PATH,
    _hashing_embedding,
    run_pipeline,
)


@lru_cache(maxsize=1)
def _load_vector_store() -> tuple[dict, ...]:
    """Load vector store records from JSONL, building it first if needed."""
    if not VECTORSTORE_PATH.exists():
        run_pipeline()

    records: list[dict] = []
    with VECTORSTORE_PATH.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue
            record = json.loads(line)
            if record.get("content") and record.get("embedding"):
                records.append(record)

    return tuple(records)


def _load_manifest() -> dict:
    manifest_path = INDEX_DIR / "index_manifest.json"
    if not manifest_path.exists():
        return {}
    return json.loads(manifest_path.read_text(encoding="utf-8"))


@lru_cache(maxsize=64)
def _embed_query(query: str) -> tuple[float, ...]:
    """Embed a query with the same embedding mode used by Task 4."""
    manifest = _load_manifest()
    embedding_model = manifest.get("embedding_model", "")

    if "hashing_fallback" not in embedding_model:
        try:
            from sentence_transformers import SentenceTransformer

            model = SentenceTransformer(EMBEDDING_MODEL)
            embedding = model.encode(query, normalize_embeddings=True)
            return tuple(float(value) for value in embedding.tolist())
        except Exception:
            pass

    return tuple(_hashing_embedding(query))


def _cosine_similarity(left: tuple[float, ...] | list[float], right: list[float]) -> float:
    if not left or not right:
        return 0.0

    length = min(len(left), len(right))
    dot = sum(float(left[i]) * float(right[i]) for i in range(length))
    left_norm = math.sqrt(sum(float(left[i]) ** 2 for i in range(length)))
    right_norm = math.sqrt(sum(float(right[i]) ** 2 for i in range(length)))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return dot / (left_norm * right_norm)


def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Search semantically using dense vector similarity.

    Args:
        query: Search query.
        top_k: Maximum number of results to return.

    Returns:
        List of {'content': str, 'score': float, 'metadata': dict}, sorted by
        score descending.
    """
    query = (query or "").strip()
    if not query or top_k <= 0:
        return []

    query_embedding = _embed_query(query)
    scored_results: list[dict] = []

    for record in _load_vector_store():
        score = _cosine_similarity(query_embedding, record.get("embedding", []))
        scored_results.append(
            {
                "content": record["content"],
                "score": float(score),
                "metadata": record.get("metadata", {}),
            }
        )

    scored_results.sort(key=lambda item: item["score"], reverse=True)
    return scored_results[:top_k]


if __name__ == "__main__":
    results = semantic_search("hinh phat cho toi tang tru ma tuy", top_k=5)
    for result in results:
        print(f"[{result['score']:.3f}] {result['content'][:100]}...")
