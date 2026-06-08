# Multi-Platform Agent Setup

## Goal

Use the same project docs with many AI coding tools, not only Codex.

The main idea:

```text
Shared docs = source of truth
Tool-specific files = small adapters
```

## Shared docs

These files are useful for every AI coding tool:

- `AGENTS.md`
- `group_project/docs/project-brief.md`
- `group_project/docs/page-index.md`
- `group_project/docs/qwen-api.md`
- `group_project/docs/weaviate.md`
- `group_project/docs/codex-vibe-coding-guide.md`

## Tool-specific files

### Codex

Uses:

```text
AGENTS.md
```

### Cursor

Uses:

```text
.cursor/rules/rag-group-project.mdc
```

You can also tag docs manually in chat:

```text
@group_project/docs/page-index.md
@group_project/docs/qwen-api.md
```

### GitHub Copilot / VS Code

Uses:

```text
.github/copilot-instructions.md
```

### Claude Code

Uses:

```text
CLAUDE.md
```

### Gemini CLI

Uses:

```text
GEMINI.md
```

### Windsurf

Uses:

```text
.windsurfrules
```

## Best prompt for any platform

Use this when starting a new task:

```text
Before coding, read:
- AGENTS.md
- group_project/docs/project-brief.md
- group_project/docs/page-index.md
- group_project/docs/qwen-api.md

Task:
<your task here>

Rules:
- Keep code simple.
- Do not hard-code secrets.
- Run a smoke test after coding.
```

## Keep docs simple

Do not duplicate long explanations in every tool file.

If project rules change:

1. Update `AGENTS.md`.
2. Update the related doc in `group_project/docs/`.
3. Only update tool-specific files if the rule is very important.

