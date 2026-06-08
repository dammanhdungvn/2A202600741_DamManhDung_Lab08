# Qwen API Guide

## Dung de lam gi?

Qwen la model LLM dung de viet cau tra loi cuoi cung cho chatbot.

Trong project nay:

```text
retrieved context -> Qwen -> answer co citation
```

Qwen dung OpenAI-compatible API, nen minh goi bang `OpenAI` SDK.

## Bien trong `.env`

Can co:

```env
QWEN_API_KEY=your_qwen_api_key
QWEN_BASE_URL=https://dashscope-intl.aliyuncs.com/compatible-mode/v1
QWEN_MODEL_NAME=your_model_name
```

Rule quan trong:

- Khong hard-code API key.
- Khong hard-code base URL.
- Khong hard-code model name.
- Luon doc tu `.env`.
- Khong viet `os.getenv("")`.

## Code mau don gian

```python
import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")

api_key = os.getenv("QWEN_API_KEY")
base_url = os.getenv("QWEN_BASE_URL")
model_name = os.getenv("QWEN_MODEL_NAME")

if not api_key:
    raise ValueError("Missing QWEN_API_KEY in .env")
if not base_url:
    raise ValueError("Missing QWEN_BASE_URL in .env")
if not model_name:
    raise ValueError("Missing QWEN_MODEL_NAME in .env")

client = OpenAI(api_key=api_key, base_url=base_url)

response = client.chat.completions.create(
    model=model_name,
    messages=[
        {"role": "user", "content": "Reply only: Qwen connection successful"}
    ],
)

print(response.choices[0].message.content)
```

## Cach dung trong RAG

Qwen khong nen tu doan. Hay dua context vao prompt.

Prompt nen co dang:

```text
Question:
{question}

Context:
{retrieved_context}

Rules:
- Chi tra loi dua tren context.
- Moi y quan trong phai co citation [Source, Year].
- Neu khong du bang chung, tra loi: I cannot verify this information.
```

## Output mong muon

Nen return dict:

```python
{
    "answer": "Cau tra loi co citation [Source, Year]",
    "sources": [...]
}
```

## Prompt mau cho Codex

```text
Doc group_project/docs/qwen-api.md va group_project/docs/qwen-generation-workflow.md.
Viet group_project/src/qwen_client.py.
Yeu cau:
- doc QWEN_API_KEY, QWEN_BASE_URL, QWEN_MODEL_NAME tu .env
- dung OpenAI SDK
- viet function generate_answer(question, contexts)
- answer phai co citation [Source, Year]
- neu thieu evidence thi tra "I cannot verify this information"
- khong hard-code secret
```

