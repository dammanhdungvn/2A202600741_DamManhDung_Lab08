# Vibe Coding Plan

## Objective

Help Codex build the group RAG demo quickly without over-engineering.

## Recommended File Structure

```text
group_project/
  app.py
  src/
    pageindex_client.py
    qwen_client.py
    rag_pipeline.py
  docs/
    project-brief.md
    tech-stack.md
    pageindex-upload-workflow.md
    qwen-generation-workflow.md
    vibe-coding-plan.md
  evaluation/
    golden_dataset.json
    eval_pipeline.py
    results.md
```

## Implementation Steps

1. Build `pageindex_client.py`
   - read `page-index.md` and `pageindex-upload-workflow.md`
   - load `.env`
   - upload 3 PDFs
   - save `doc_id`
   - query completed docs

2. Build `qwen_client.py`
   - read `qwen-api.md` and `qwen-generation-workflow.md`
   - load `.env`
   - initialize OpenAI SDK with Qwen base URL
   - generate answer from context

3. Build `rag_pipeline.py`
   - accept user question
   - retrieve PageIndex context
   - call Qwen
   - return answer and sources

4. Build `app.py`
   - simple chat interface
   - show answer
   - show sources
   - keep small conversation memory

5. Build evaluation
   - create 15 Q&A examples
   - run at least one metric framework
   - compare two configs if possible

## Guardrails For Codex

- Read docs before coding.
- For PageIndex work, read `page-index.md`.
- For Qwen work, read `qwen-api.md`.
- For optional Weaviate work, read `weaviate.md`.
- Keep implementation minimal.
- Prefer clear functions over clever abstractions.
- Do not hard-code secrets.
- Do not change unit tests unless explicitly requested.
- Always run a small smoke test after implementing.
