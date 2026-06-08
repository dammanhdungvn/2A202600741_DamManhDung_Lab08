"""
Task 9 - Complete retrieval pipeline.

Pipeline:
    1. semantic_search + lexical_search
    2. Reciprocal Rank Fusion (RRF)
    3. Local reranking
    4. Fallback to PageIndex vectorless retrieval when hybrid confidence is low
"""

from __future__ import annotations

from .task5_semantic_search import semantic_search
from .task6_lexical_search import lexical_search
from .task7_reranking import rerank, rerank_rrf
from .task8_pageindex_vectorless import pageindex_search


SCORE_THRESHOLD = 0.3
DEFAULT_TOP_K = 5
RERANK_METHOD = "local_overlap"


def _with_retrieval_source(results: list[dict], source: str) -> list[dict]:
    normalized: list[dict] = []
    for item in results:
        copy = item.copy()
        copy["metadata"] = item.get("metadata", {})
        copy["source"] = source
        normalized.append(copy)
    return normalized


def _fallback(query: str, top_k: int) -> list[dict]:
    fallback_results = pageindex_search(query, top_k=top_k)
    normalized: list[dict] = []
    for item in fallback_results[:top_k]:
        copy = item.copy()
        copy["metadata"] = item.get("metadata", {})
        copy["source"] = "pageindex"
        copy["score"] = float(item.get("score", 0.0))
        normalized.append(copy)
    return normalized


def retrieve(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    score_threshold: float = SCORE_THRESHOLD,
    use_reranking: bool = True,
) -> list[dict]:
    """
    Complete retrieval pipeline with PageIndex fallback.

    1. Run semantic_search + lexical_search.
    2. Merge with RRF.
    3. Rerank merged candidates.
    4. If the best hybrid score is below threshold, fallback to PageIndex.
    5. Return top_k results with source in {'hybrid', 'pageindex'}.
    """
    query = (query or "").strip()
    if not query or top_k <= 0:
        return []

    search_k = max(top_k * 3, 10)
    dense_results = semantic_search(query, top_k=search_k)
    sparse_results = lexical_search(query, top_k=search_k)

    merged = rerank_rrf([dense_results, sparse_results], top_k=search_k)
    merged = _with_retrieval_source(merged, "hybrid")

    if use_reranking and merged:
        final_results = rerank(query, merged, top_k=top_k, method=RERANK_METHOD)
        final_results = _with_retrieval_source(final_results, "hybrid")
    else:
        final_results = merged[:top_k]

    if not final_results:
        return _fallback(query, top_k)

    best_score = float(final_results[0].get("score", 0.0))
    if best_score < score_threshold:
        fallback_results = _fallback(query, top_k)
        if fallback_results:
            return fallback_results

    return final_results[:top_k]


if __name__ == "__main__":
    test_queries = [
        "Hinh phat cho toi tang tru trai phep chat ma tuy",
        "Nghe si nao bi bat vi su dung ma tuy",
        "Luat phong chong ma tuy 2021 quy dinh gi ve cai nghien",
    ]

    for question in test_queries:
        print(f"\nQuery: {question}")
        print("-" * 60)
        for index, result in enumerate(retrieve(question, top_k=3), start=1):
            print(f"{index}. [{result['score']:.3f}] [{result['source']}] {result['content'][:80]}...")
