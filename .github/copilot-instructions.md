# Copilot Instructions

This repository is a Vietnamese drug-law RAG chatbot/evaluation project.

Before coding, use these context files:

- `AGENTS.md`
- `group_project/docs/project-brief.md`
- `group_project/docs/page-index.md`
- `group_project/docs/qwen-api.md`
- `group_project/docs/codex-vibe-coding-guide.md`

Project rules:

- Keep code simple enough for a fresher/junior to understand.
- Do not over-engineer production architecture.
- Never hard-code API keys, base URLs, model names, or PageIndex document IDs.
- Load secrets/config from `.env`.
- Use PageIndex for the 3 legal PDF files listed in `group_project/docs/page-index.md`.
- Use Qwen through the OpenAI-compatible SDK as described in `group_project/docs/qwen-api.md`.
- Generated answers must use retrieved context and citation format `[Source, Year]`.
- If evidence is missing, return `I cannot verify this information`.
- Do not modify tests unless the user explicitly asks.
- After edits, run a focused smoke test or relevant pytest command.

