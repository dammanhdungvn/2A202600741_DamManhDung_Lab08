"""
Task 7 - Reranking module.

Chosen approach: local reranking plus RRF/MMR helpers.

The default rerank() is an offline relevance reranker: it combines the original
retrieval score with query/document token overlap. This gives deterministic
rescoring without an API key. rerank_rrf() is also implemented for Task 9 hybrid
fusion, and rerank_mmr() is available when candidates include embeddings.
"""

from __future__ import annotations

import math
import re
from collections import Counter


def tokenize(text: str) -> list[str]:
    """Lightweight Unicode tokenizer for Vietnamese and English text."""
    return re.findall(r"[\wÀ-ỹ]+", (text or "").lower(), flags=re.UNICODE)


def _cosine(left: list[float], right: list[float]) -> float:
    if not left or not right:
        return 0.0
    length = min(len(left), len(right))
    dot = sum(float(left[i]) * float(right[i]) for i in range(length))
    left_norm = math.sqrt(sum(float(left[i]) ** 2 for i in range(length)))
    right_norm = math.sqrt(sum(float(right[i]) ** 2 for i in range(length)))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return dot / (left_norm * right_norm)


def _normalize_scores(candidates: list[dict]) -> list[float]:
    scores = [float(item.get("score", 0.0)) for item in candidates]
    if not scores:
        return []
    min_score = min(scores)
    max_score = max(scores)
    if max_score == min_score:
        return [1.0 if max_score > 0 else 0.0 for _ in scores]
    return [(score - min_score) / (max_score - min_score) for score in scores]


def _overlap_score(query: str, document: str) -> float:
    query_terms = Counter(tokenize(query))
    document_terms = Counter(tokenize(document))
    if not query_terms or not document_terms:
        return 0.0

    matched_weight = 0
    total_weight = sum(query_terms.values())
    for term, query_count in query_terms.items():
        matched_weight += min(query_count, document_terms.get(term, 0))

    recall = matched_weight / total_weight if total_weight else 0.0
    unique_overlap = len(set(query_terms).intersection(document_terms)) / len(set(query_terms))
    return 0.7 * recall + 0.3 * unique_overlap


def rerank_cross_encoder(query: str, candidates: list[dict], top_k: int = 5) -> list[dict]:
    """
    Offline cross-encoder-style fallback reranker.

    A real cross-encoder jointly encodes (query, document). For this local
    assignment, we approximate that behavior deterministically by combining
    normalized retrieval score and lexical overlap with the query.
    """
    if top_k <= 0 or not candidates:
        return []

    normalized_scores = _normalize_scores(candidates)
    reranked: list[dict] = []
    for candidate, normalized_score in zip(candidates, normalized_scores):
        overlap = _overlap_score(query, candidate.get("content", ""))
        rerank_score = 0.65 * overlap + 0.35 * normalized_score
        item = candidate.copy()
        item["metadata"] = candidate.get("metadata", {})
        item["score"] = float(rerank_score)
        item["rerank_method"] = "local_overlap"
        reranked.append(item)

    reranked.sort(key=lambda item: item["score"], reverse=True)
    return reranked[:top_k]


def rerank_mmr(
    query_embedding: list[float],
    candidates: list[dict],
    top_k: int = 5,
    lambda_param: float = 0.7,
) -> list[dict]:
    """
    Maximal Marginal Relevance.

    MMR = lambda * relevance(query, doc) - (1 - lambda) * max_sim(doc, selected)
    It favors relevant documents while reducing near-duplicates.
    """
    if top_k <= 0 or not candidates:
        return []

    selected: list[int] = []
    remaining = set(range(len(candidates)))
    embeddings = [candidate.get("embedding", []) for candidate in candidates]

    while remaining and len(selected) < top_k:
        best_index = None
        best_score = float("-inf")

        for index in remaining:
            relevance = _cosine(query_embedding, embeddings[index])
            diversity_penalty = 0.0
            if selected:
                diversity_penalty = max(_cosine(embeddings[index], embeddings[chosen]) for chosen in selected)
            mmr_score = lambda_param * relevance - (1.0 - lambda_param) * diversity_penalty

            if mmr_score > best_score:
                best_score = mmr_score
                best_index = index

        if best_index is None:
            break
        selected.append(best_index)
        remaining.remove(best_index)

    results: list[dict] = []
    for index in selected:
        item = candidates[index].copy()
        item["metadata"] = candidates[index].get("metadata", {})
        item["score"] = float(item.get("score", 0.0))
        item["rerank_method"] = "mmr"
        results.append(item)
    return results


def rerank_rrf(ranked_lists: list[list[dict]], top_k: int = 5, k: int = 60) -> list[dict]:
    """
    Reciprocal Rank Fusion.

    RRF(d) = sum(1 / (k + rank_r(d))) across rankers. It is robust because each
    ranker contributes by position, not raw score scale.
    """
    if top_k <= 0:
        return []

    fused_scores: dict[str, float] = {}
    item_by_key: dict[str, dict] = {}

    for ranked_list in ranked_lists:
        for rank, item in enumerate(ranked_list, start=1):
            key = item.get("metadata", {}).get("path") or item.get("content", "")
            if not key:
                continue
            fused_scores[key] = fused_scores.get(key, 0.0) + 1.0 / (k + rank)
            item_by_key[key] = item

    results: list[dict] = []
    for key, score in sorted(fused_scores.items(), key=lambda pair: pair[1], reverse=True)[:top_k]:
        item = item_by_key[key].copy()
        item["metadata"] = item.get("metadata", {})
        item["score"] = float(score)
        item["rerank_method"] = "rrf"
        results.append(item)

    return results


def rerank(
    query: str,
    candidates: list[dict],
    top_k: int = 5,
    method: str = "cross_encoder",
) -> list[dict]:
    """
    Re-score and re-order candidates based on relevance to query.
    """
    if method in {"cross_encoder", "local_overlap"}:
        return rerank_cross_encoder(query, candidates, top_k)
    if method == "rrf":
        return rerank_rrf([candidates], top_k=top_k)
    if method == "mmr":
        raise ValueError("Use rerank_mmr(query_embedding, candidates, ...) for MMR.")
    raise ValueError(f"Unknown rerank method: {method}")


if __name__ == "__main__":
    dummy_candidates = [
        {"content": "Dieu 248: Toi tang tru trai phep chat ma tuy", "score": 0.8, "metadata": {}},
        {"content": "Nghe si bi bat vi su dung ma tuy", "score": 0.7, "metadata": {}},
        {"content": "Python programming", "score": 0.6, "metadata": {}},
    ]
    for result in rerank("hinh phat tang tru ma tuy", dummy_candidates, top_k=2):
        print(f"[{result['score']:.3f}] {result['content']}")
