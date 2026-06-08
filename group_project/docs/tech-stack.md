# Tech Stack

## Runtime

- Python
- `.env` for local secrets
- `python-dotenv` for config loading

## Generation

Use Qwen with OpenAI-compatible SDK.

Read these docs first:

- `group_project/docs/qwen-api.md`
- `group_project/docs/qwen-generation-workflow.md`

Environment variables:

```env
QWEN_API_KEY=...
QWEN_BASE_URL=...
QWEN_MODEL_NAME=...
```

Rules:

- Do not hard-code API keys.
- Do not hard-code base URL.
- Do not hard-code model name.
- Read all values from `.env`.

## Retrieval

Primary group retrieval:

- PageIndex for uploaded PDF documents.

Read these docs first:

- `group_project/docs/page-index.md`
- `group_project/docs/pageindex-upload-workflow.md`

Existing individual retrieval:

- Task 5 semantic search
- Task 6 BM25 lexical search
- Task 7 reranking
- Task 8 PageIndex fallback
- Task 9 retrieval pipeline

Use individual modules when they are helpful, but keep group adapters simple.

Optional later:

- Weaviate for cloud vector search. Read `group_project/docs/weaviate.md`.

## UI Options

Recommended:

- Streamlit for fastest demo.

Alternative:

- Gradio for simple chat UI.
- Chainlit for conversational demo.

## Evaluation

Choose one:

- DeepEval
- RAGAS
- TruLens

For this assignment, DeepEval is a good default because the README includes a direct sample and it integrates cleanly with Python scripts.
