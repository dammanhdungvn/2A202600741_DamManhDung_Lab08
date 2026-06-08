# Multi-Platform Agent Setup

## Mục tiêu

Dùng cùng một bộ docs project với nhiều AI coding tools, không chỉ Codex.

Ý tưởng chính:

```text
Shared docs = nguồn sự thật chung
Tool-specific files = adapter nhỏ cho từng tool
```

## Shared docs

Các file này hữu ích cho mọi AI coding tool:

- `AGENTS.md`
- `group_project/docs/project-brief.md`
- `group_project/docs/page-index.md`
- `group_project/docs/qwen-api.md`
- `group_project/docs/weaviate.md`
- `group_project/docs/codex-vibe-coding-guide.md`

## Tool-specific files

### Codex

Dùng:

```text
AGENTS.md
```

### Cursor

Dùng:

```text
.cursor/rules/rag-group-project.mdc
```

Bạn cũng có thể tag docs thủ công trong chat:

```text
@group_project/docs/page-index.md
@group_project/docs/qwen-api.md
```

### GitHub Copilot / VS Code

Dùng:

```text
.github/copilot-instructions.md
```

### Claude Code

Dùng:

```text
CLAUDE.md
```

### Gemini CLI

Dùng:

```text
GEMINI.md
```

### Windsurf

Dùng:

```text
.windsurfrules
```

## Prompt tốt nhất cho mọi platform

Dùng prompt này khi bắt đầu task mới:

```text
Trước khi code, hãy đọc:
- AGENTS.md
- group_project/docs/project-brief.md
- group_project/docs/page-index.md
- group_project/docs/qwen-api.md

Task:
<task của bạn ở đây>

Rules:
- Giữ code đơn giản.
- Không hard-code secrets.
- Chạy smoke test sau khi code.
```

## Giữ docs đơn giản

Không duplicate giải thích dài trong mọi tool file.

Nếu rule project thay đổi:

1. Update `AGENTS.md`.
2. Update doc liên quan trong `group_project/docs/`.
3. Chỉ update tool-specific files nếu rule đó rất quan trọng.