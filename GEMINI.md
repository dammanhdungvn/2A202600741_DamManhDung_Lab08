# Gemini CLI Instructions

Use this repo as a simple RAG chatbot/evaluation project.

Read first:

- `AGENTS.md`
- `group_project/docs/project-brief.md`
- `group_project/docs/page-index.md`
- `group_project/docs/qwen-api.md`
- `group_project/docs/codex-vibe-coding-guide.md`

Coding rules:

- Keep code beginner-friendly.
- Avoid production complexity unless asked.
- Do not hard-code secrets or model names.
- Load `.env` explicitly from the project root.
- Use PageIndex for the 3 legal PDF files in `page-index.md`.
- Use Qwen for answer generation through OpenAI-compatible API.
- Every factual answer should include citation `[Source, Year]`.
- If evidence is missing, return `I cannot verify this information`.
- Run a small test after changes.

