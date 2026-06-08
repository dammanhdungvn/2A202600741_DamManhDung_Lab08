"""
Task 6 - Lexical search with BM25.

BM25 scores exact keyword matches using term frequency, inverse document
frequency, and document-length normalization. This module indexes the same
chunks produced by Task 4 so semantic and lexical retrieval can be fused later.
"""

from __future__ import annotations

import json
import re
from functools import lru_cache

from rank_bm25 import BM25Okapi

from .task4_chunking_indexing import VECTORSTORE_PATH, run_pipeline


def tokenize(text: str) -> list[str]:
    """
    Tokenize Vietnamese/English text with a lightweight Unicode regex.

    This keeps Vietnamese letters and digits while removing punctuation.
    """
    return re.findall(r"[\wÀ-ỹ]+", (text or "").lower(), flags=re.UNICODE)


@lru_cache(maxsize=1)
def load_corpus() -> tuple[dict, ...]:
    """Load chunk corpus from Task 4 vector_store.jsonl."""
    if not VECTORSTORE_PATH.exists():
        run_pipeline()

    corpus: list[dict] = []
    with VECTORSTORE_PATH.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue
            record = json.loads(line)
            content = record.get("content", "")
            if content:
                corpus.append(
                    {
                        "content": content,
                        "metadata": record.get("metadata", {}),
                    }
                )
    return tuple(corpus)


def build_bm25_index(corpus: list[dict] | tuple[dict, ...]) -> BM25Okapi:
    """
    Build a BM25 index from corpus chunks.

    Args:
        corpus: List of {'content': str, 'metadata': dict}
    """
    tokenized_corpus = [tokenize(doc["content"]) for doc in corpus]
    return BM25Okapi(tokenized_corpus)


@lru_cache(maxsize=1)
def _bm25_index() -> BM25Okapi:
    return build_bm25_index(load_corpus())


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Search chunks by lexical BM25 score.

    Args:
        query: Search query.
        top_k: Maximum number of results.

    Returns:
        List of {'content': str, 'score': float, 'metadata': dict}, sorted by
        score descending.
    """
    query_tokens = tokenize(query)
    if not query_tokens or top_k <= 0:
        return []

    corpus = load_corpus()
    if not corpus:
        return []

    scores = _bm25_index().get_scores(query_tokens)
    ranked_indices = sorted(range(len(scores)), key=lambda index: float(scores[index]), reverse=True)

    results: list[dict] = []
    for index in ranked_indices:
        score = float(scores[index])
        if score <= 0:
            continue
        doc = corpus[index]
        results.append(
            {
                "content": doc["content"],
                "score": score,
                "metadata": doc.get("metadata", {}),
            }
        )
        if len(results) >= top_k:
            break

    return results


if __name__ == "__main__":
    results = lexical_search("Dieu 248 tang tru trai phep chat ma tuy", top_k=5)
    for result in results:
        print(f"[{result['score']:.3f}] {result['content'][:100]}...")
