# Claude Code Instructions

Use `AGENTS.md` as the main project instruction file.

Also read:

- `group_project/docs/project-brief.md`
- `group_project/docs/page-index.md`
- `group_project/docs/qwen-api.md`
- `group_project/docs/codex-vibe-coding-guide.md`

Important rules:

- Keep solutions small, clear, and demo-ready.
- Do not hard-code secrets.
- Read all API config from `.env`.
- PageIndex uploads only the 3 legal PDFs listed in `page-index.md`.
- Qwen generation must use retrieved context and citations.
- Citation format: `[Source, Year]`.
- If context is not enough, answer `I cannot verify this information`.
- Do not change unit tests unless explicitly requested.
- Run a focused verification command after implementation.

