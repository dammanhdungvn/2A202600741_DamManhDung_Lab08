# AGENTS.md

## Project Overview

This repo is a Day 8 RAG pipeline project for Vietnamese drug law and related news. The group project should build a simple RAG chatbot and/or evaluation pipeline using the individual tasks as reusable modules.

Primary group goal:
- Chatbot answers questions about Vietnamese drug law and related news.
- Answers must include citations.
- UI should show source documents used.
- Follow-up questions should be supported with lightweight conversation memory.

Current intended stack:
- Python
- Streamlit, Gradio, or Chainlit for UI
- PageIndex for PDF document processing/retrieval
- Qwen API for generation via OpenAI-compatible SDK
- Existing individual pipeline modules in `src/`
- Group code under `group_project/`

## Important Context Files

Read these before coding:
- `README.md`
- `group_project/README.md`
- `group_project/docs/qwen-api.md`
- `group_project/docs/page-index.md`
- `group_project/docs/project-brief.md`
- `group_project/docs/tech-stack.md`
- `group_project/docs/pageindex-upload-workflow.md`
- `group_project/docs/qwen-generation-workflow.md`
- `group_project/docs/vibe-coding-plan.md`

## Environment Rules

Always read configuration from `.env`.

Required variables:
- `QWEN_API_KEY`
- `QWEN_BASE_URL`
- `QWEN_MODEL_NAME`
- `PAGEINDEX_API_KEY`

Never hard-code API keys, base URLs, model names, PageIndex document IDs, or secrets.

When loading `.env` from files inside subfolders, resolve the project root explicitly:

```python
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")
```

Adjust `parents[...]` according to file depth.

## PageIndex Rules

PageIndex only accepts PDF uploads in this workflow.

Upload these three source PDFs:
- `data/landing/legal/luat-phong-chong-ma-tuy-2021.pdf`
- `data/landing/legal/nghi-dinh-105-2021-huong-dan-luat-phong-chong-ma-tuy.pdf`
- `data/landing/legal/nghi-dinh-57-2022-danh-muc-chat-ma-tuy-va-tien-chat.pdf`

After upload:
- Save each returned `doc_id`.
- Check document status.
- Only use documents whose status is `completed`.
- Store local mapping in a JSON manifest under `group_project/` or `data/pageindex/`.

Do not upload:
- local vector indexes
- Python code
- Markdown files if the dashboard/API only accepts PDF
- `.env`

## Qwen Rules

Use Qwen through the OpenAI-compatible SDK:
- `api_key` from `QWEN_API_KEY`
- `base_url` from `QWEN_BASE_URL`
- `model` from `QWEN_MODEL_NAME`

Every generated answer must be grounded in retrieved context. If evidence is insufficient, answer:

```text
I cannot verify this information
```

Citation format:

```text
[Source, Year]
```

## Build Workflow

For every task:
1. Read relevant docs and existing code first.
2. Make the smallest useful implementation.
3. Keep code simple and demo-ready.
4. Do not build production-grade abstractions unless required.
5. Run the relevant smoke test or script.
6. Explain what changed and what to run next.

## Suggested Group Implementation Order

1. PageIndex upload script for 3 PDFs.
2. PageIndex retrieval wrapper.
3. Qwen generation wrapper.
4. RAG pipeline: query -> retrieve -> prompt -> answer with citations.
5. Simple UI.
6. Golden dataset and evaluation script.
7. Results report.

## What Not To Do

- Do not commit `.env` or API keys.
- Do not hard-code secrets.
- Do not silently invent facts.
- Do not return uncited legal claims.
- Do not change unit tests unless explicitly asked.
- Do not replace the individual task modules unless the group code needs a thin adapter.
- Do not over-engineer the demo.

