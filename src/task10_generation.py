"""
Task 10 - RAG generation with citations.

The module can call OpenAI when OPENAI_API_KEY is configured. For local/offline
tests it falls back to an extractive answer assembled from retrieved chunks,
still enforcing citations and "I cannot verify this information" when evidence
is missing.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from dotenv import load_dotenv

from .task9_retrieval_pipeline import retrieve

load_dotenv()


# top_k=5 gives enough evidence diversity for legal/news questions while
# keeping context compact; this reduces the chance of lost-in-the-middle.
TOP_K = 5

# top_p=0.9 allows modest linguistic variation while keeping factual RAG
# answers controlled. temperature=0.2 keeps the model grounded and low-random.
TOP_P = 0.9
TEMPERATURE = 0.2
MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

INSUFFICIENT_EVIDENCE = "I cannot verify this information"


SYSTEM_PROMPT = """Answer the following question comprehensively.
For every statement of fact or claim, immediately insert a citation in brackets
linking to the specific source (e.g., [Author/Platform Name, Year]).
If the information is not explicitly stated in the provided context or knowledge
base, state 'I cannot verify this information' rather than guessing."""


def reorder_for_llm(chunks: list[dict]) -> list[dict]:
    """
    Reorder chunks to reduce lost-in-the-middle.

    Input sorted by relevance: [1, 2, 3, 4, 5]
    Output pattern:           [1, 3, 5, 4, 2]
    Best evidence stays at the beginning; second-best is placed at the end.
    """
    if len(chunks) <= 2:
        return list(chunks)

    front = [chunks[index] for index in range(0, len(chunks), 2)]
    back = [chunks[index] for index in range(1, len(chunks), 2)]
    return front + list(reversed(back))


def _source_name(chunk: dict, fallback: str = "Unknown Source") -> str:
    metadata = chunk.get("metadata", {})
    source = metadata.get("source") or metadata.get("path") or fallback
    return Path(str(source)).stem


def _infer_year(chunk: dict) -> str:
    metadata = chunk.get("metadata", {})
    text = " ".join(
        str(value)
        for value in [
            metadata.get("source", ""),
            metadata.get("path", ""),
            metadata.get("date_crawled", ""),
            chunk.get("content", "")[:500],
        ]
    )
    match = re.search(r"\b(20\d{2}|19\d{2})\b", text)
    return match.group(1) if match else "n.d."


def citation_for_chunk(chunk: dict) -> str:
    return f"[{_source_name(chunk)}, {_infer_year(chunk)}]"


def format_context(chunks: list[dict]) -> str:
    """
    Format chunks as prompt context with citation labels.
    """
    context_parts: list[str] = []
    for index, chunk in enumerate(chunks, start=1):
        metadata = chunk.get("metadata", {})
        source = _source_name(chunk, fallback=f"Source {index}")
        year = _infer_year(chunk)
        doc_type = metadata.get("type", "unknown")
        score = float(chunk.get("score", 0.0))
        context_parts.append(
            f"[Document {index} | Citation: [{source}, {year}] | Type: {doc_type} | Score: {score:.3f}]\n"
            f"{chunk.get('content', '').strip()}"
        )
    return "\n\n---\n\n".join(context_parts)


def _sentence_candidates(text: str) -> list[str]:
    cleaned = re.sub(r"\s+", " ", text).strip()
    pieces = re.split(r"(?<=[.!?。])\s+|\n+", cleaned)
    return [piece.strip(" -") for piece in pieces if len(piece.strip()) > 40]


def _local_generate(query: str, chunks: list[dict]) -> str:
    if not chunks:
        return INSUFFICIENT_EVIDENCE

    answer_lines: list[str] = []
    for chunk in chunks[:3]:
        sentences = _sentence_candidates(chunk.get("content", ""))
        if not sentences:
            continue
        sentence = sentences[0]
        answer_lines.append(f"{sentence} {citation_for_chunk(chunk)}")

    if not answer_lines:
        return INSUFFICIENT_EVIDENCE

    return "\n".join(answer_lines)


def _call_openai(query: str, context: str) -> str | None:
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        return None

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\n---\n\nQuestion: {query}",
                },
            ],
            temperature=TEMPERATURE,
            top_p=TOP_P,
        )
        return response.choices[0].message.content or INSUFFICIENT_EVIDENCE
    except Exception:
        return None


def generate_with_citation(query: str, top_k: int = TOP_K) -> dict:
    """
    End-to-end RAG generation with citation.

    Returns:
        {
            'answer': str,
            'sources': list[dict],
            'retrieval_source': str
        }
    """
    query = (query or "").strip()
    if not query:
        return {"answer": INSUFFICIENT_EVIDENCE, "sources": [], "retrieval_source": "none"}

    chunks = retrieve(query, top_k=top_k)
    reordered = reorder_for_llm(chunks)
    context = format_context(reordered)

    answer = _call_openai(query, context)
    if not answer:
        answer = _local_generate(query, reordered)

    return {
        "answer": answer,
        "sources": reordered,
        "retrieval_source": reordered[0].get("source", "none") if reordered else "none",
        "context": context,
    }


if __name__ == "__main__":
    result = generate_with_citation("Hinh phat cho toi tang tru trai phep chat ma tuy?")
    print(result["answer"])
    print(f"\nSources: {len(result['sources'])} via {result['retrieval_source']}")
