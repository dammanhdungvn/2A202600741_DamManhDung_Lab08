"""
Task 8 - PageIndex vectorless RAG fallback.

When PAGEINDEX_API_KEY is configured, upload_documents() submits Markdown files
to PageIndex and stores returned document IDs in data/pageindex/. Without an API
key, pageindex_search() uses a local vectorless fallback based on token overlap
over the standardized Markdown files. The return shape is the same in both
modes, and every result is marked with source='pageindex'.
"""

from __future__ import annotations

import json
import os
import re
import time
from collections import Counter
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY", "")
PROJECT_DIR = Path(__file__).parent.parent
STANDARDIZED_DIR = PROJECT_DIR / "data" / "standardized"
PAGEINDEX_DIR = PROJECT_DIR / "data" / "pageindex"
PAGEINDEX_MANIFEST = PAGEINDEX_DIR / "pageindex_manifest.json"


def tokenize(text: str) -> list[str]:
    return re.findall(r"[\wÀ-ỹ]+", (text or "").lower(), flags=re.UNICODE)


def _read_markdown_documents() -> list[dict]:
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
                },
            }
        )
    return documents


def _chunk_for_pageindex(content: str, chunk_size: int = 900, overlap: int = 120) -> list[str]:
    """Small vectorless fallback chunker for local PageIndex-style search."""
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", content) if part.strip()]
    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:
        if len(current) + len(paragraph) + 2 <= chunk_size:
            current = f"{current}\n\n{paragraph}".strip()
            continue
        if current:
            chunks.append(current)
            current = current[-overlap:] if overlap > 0 else ""
        if len(paragraph) <= chunk_size:
            current = f"{current}\n\n{paragraph}".strip()
        else:
            step = chunk_size - overlap
            for start in range(0, len(paragraph), step):
                piece = paragraph[start : start + chunk_size].strip()
                if piece:
                    chunks.append(piece)
            current = ""

    if current:
        chunks.append(current)
    return chunks


def _overlap_score(query: str, content: str) -> float:
    query_terms = Counter(tokenize(query))
    content_terms = Counter(tokenize(content))
    if not query_terms or not content_terms:
        return 0.0

    matched = sum(min(count, content_terms.get(term, 0)) for term, count in query_terms.items())
    recall = matched / sum(query_terms.values())
    unique_overlap = len(set(query_terms).intersection(content_terms)) / len(set(query_terms))
    density = matched / max(sum(content_terms.values()), 1)
    return 0.65 * recall + 0.25 * unique_overlap + 0.10 * density


def _write_manifest(manifest: dict) -> None:
    PAGEINDEX_DIR.mkdir(parents=True, exist_ok=True)
    PAGEINDEX_MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def _load_manifest() -> dict:
    if not PAGEINDEX_MANIFEST.exists():
        return {}
    return json.loads(PAGEINDEX_MANIFEST.read_text(encoding="utf-8"))


def _extract_doc_id(response: dict) -> str | None:
    for key in ("doc_id", "document_id", "id"):
        if response.get(key):
            return str(response[key])
    data = response.get("data")
    if isinstance(data, dict):
        for key in ("doc_id", "document_id", "id"):
            if data.get(key):
                return str(data[key])
    return None


def upload_documents() -> dict:
    """
    Upload Markdown documents to PageIndex when PAGEINDEX_API_KEY exists.

    Without an API key, creates a local manifest so the vectorless fallback can
    still be queried and demoed offline.
    """
    documents = _read_markdown_documents()
    if not PAGEINDEX_API_KEY:
        manifest = {
            "mode": "local_vectorless_fallback",
            "document_count": len(documents),
            "documents": [doc["metadata"] for doc in documents],
        }
        _write_manifest(manifest)
        return manifest

    try:
        from pageindex import PageIndexClient
    except ImportError as exc:
        raise RuntimeError("pageindex SDK is not installed. Run: pip install pageindex") from exc

    client = PageIndexClient(api_key=PAGEINDEX_API_KEY)
    uploaded: list[dict] = []
    for doc in documents:
        md_path = STANDARDIZED_DIR / doc["metadata"]["path"]
        response = client.submit_document(str(md_path))
        doc_id = _extract_doc_id(response)
        uploaded.append({**doc["metadata"], "doc_id": doc_id, "response": response})

    manifest = {
        "mode": "pageindex_sdk",
        "document_count": len(uploaded),
        "uploaded_at": int(time.time()),
        "documents": uploaded,
    }
    _write_manifest(manifest)
    return manifest


def _parse_pageindex_response(response: dict, metadata: dict, top_k: int) -> list[dict]:
    candidates = response.get("results") or response.get("chunks") or response.get("data") or []
    if isinstance(candidates, dict):
        candidates = candidates.get("results") or candidates.get("chunks") or [candidates]

    parsed: list[dict] = []
    for item in candidates:
        if not isinstance(item, dict):
            continue
        content = item.get("text") or item.get("content") or item.get("answer") or item.get("markdown") or ""
        if not content:
            continue
        parsed.append(
            {
                "content": content,
                "score": float(item.get("score", item.get("relevance_score", 1.0))),
                "metadata": {**metadata, **item.get("metadata", {})},
                "source": "pageindex",
            }
        )
    parsed.sort(key=lambda result: result["score"], reverse=True)
    return parsed[:top_k]


def _pageindex_sdk_search(query: str, top_k: int) -> list[dict]:
    if not PAGEINDEX_API_KEY:
        return []

    manifest = _load_manifest()
    if not manifest or manifest.get("mode") != "pageindex_sdk":
        manifest = upload_documents()

    from pageindex import PageIndexClient

    client = PageIndexClient(api_key=PAGEINDEX_API_KEY)
    all_results: list[dict] = []
    for document in manifest.get("documents", []):
        doc_id = document.get("doc_id")
        if not doc_id:
            continue
        response = client.submit_query(doc_id=doc_id, query=query)
        all_results.extend(_parse_pageindex_response(response, document, top_k=top_k))

    all_results.sort(key=lambda result: result["score"], reverse=True)
    return all_results[:top_k]


def _local_vectorless_search(query: str, top_k: int) -> list[dict]:
    results: list[dict] = []
    for document in _read_markdown_documents():
        for chunk_index, chunk in enumerate(_chunk_for_pageindex(document["content"])):
            score = _overlap_score(query, chunk)
            if score <= 0:
                continue
            results.append(
                {
                    "content": chunk,
                    "score": float(score),
                    "metadata": {**document["metadata"], "chunk_index": chunk_index, "mode": "local_vectorless"},
                    "source": "pageindex",
                }
            )
    results.sort(key=lambda result: result["score"], reverse=True)
    return results[:top_k]


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """
    Vectorless retrieval using PageIndex.

    Falls back to a local vectorless search when PAGEINDEX_API_KEY is not set or
    the remote PageIndex call fails.
    """
    query = (query or "").strip()
    if not query or top_k <= 0:
        return []

    try:
        remote_results = _pageindex_sdk_search(query, top_k)
        if remote_results:
            return remote_results
    except Exception:
        # Keep fallback retrieval reliable for offline demos/tests.
        pass

    return _local_vectorless_search(query, top_k)


if __name__ == "__main__":
    if PAGEINDEX_API_KEY:
        print("Uploading documents to PageIndex...")
        upload_documents()
    else:
        print("PAGEINDEX_API_KEY is not set. Using local vectorless fallback.")

    for result in pageindex_search("hinh phat su dung ma tuy", top_k=3):
        print(f"[{result['score']:.3f}] [{result['source']}] {result['content'][:100]}...")
