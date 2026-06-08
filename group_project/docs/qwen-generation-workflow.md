# Qwen Generation Workflow

## Purpose

Use Qwen to generate final answers from retrieved context.

Qwen is called through the OpenAI-compatible SDK.

## Required `.env`

```env
QWEN_API_KEY=your_key
QWEN_BASE_URL=https://dashscope-intl.aliyuncs.com/compatible-mode/v1
QWEN_MODEL_NAME=your_model_name
```

## Generation Rules

- Use only retrieved context.
- Every factual claim should include a citation.
- Citation format: `[Source, Year]`.
- If context does not support the answer, return:

```text
I cannot verify this information
```

## Basic Prompt Shape

```text
System:
You answer questions using only provided context.
Every factual claim must include citation [Source, Year].
If evidence is missing, say "I cannot verify this information".

User:
Question:
{question}

Context:
{retrieved_context}
```

## Source Naming

Use stable source labels:

- `luat-phong-chong-ma-tuy-2021`
- `nghi-dinh-105-2021`
- `nghi-dinh-57-2022`

Example answer:

```text
Luật Phòng, chống ma túy quy định các biện pháp phòng ngừa, kiểm soát và xử lý liên quan đến ma túy [luat-phong-chong-ma-tuy-2021, 2021].
```

## Suggested Function Boundary

Keep generation separate from retrieval:

```python
def generate_answer(question: str, contexts: list[dict]) -> dict:
    ...
```

Return:

```python
{
    "answer": "...",
    "sources": contexts,
}
```

