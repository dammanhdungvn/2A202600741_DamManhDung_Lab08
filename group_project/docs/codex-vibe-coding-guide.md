# Codex Vibe Coding Guide

## Mục tiêu

File này hướng dẫn cách dùng Codex để vibe coding hiệu quả cho group project.

Nếu bạn dùng nhiều IDE/agent khác nhau, đọc thêm:

```text
group_project/docs/multi-platform-agent-setup.md
```

## Ý tưởng chính

Dùng chung một bộ docs:

- `AGENTS.md`
- `group_project/docs/project-brief.md`
- `group_project/docs/page-index.md`
- `group_project/docs/qwen-api.md`
- `group_project/docs/weaviate.md`

Sau đó mỗi tool sẽ có một file adapter riêng:

- Codex: `AGENTS.md`
- Cursor: `.cursor/rules/rag-group-project.mdc`
- Copilot/VS Code: `.github/copilot-instructions.md`
- Claude Code: `CLAUDE.md`
- Gemini CLI: `GEMINI.md`
- Windsurf: `.windsurfrules`

## Hiểu nhanh `/` và `@`

### `/`

`/` thường là command của tool.

Ví dụ:

```text
/plan
/review
/fix
/test
```

Không phải tool nào cũng có các command này. Nếu không chắc, cứ viết bằng ngôn ngữ bình thường.

### `@`

`@` thường dùng để tag file cho AI đọc.

Ví dụ:

```text
@AGENTS.md
@group_project/docs/page-index.md
@group_project/docs/qwen-api.md
```

Nếu tool không hỗ trợ `@`, viết đường dẫn file bằng text là đủ.

## Workflow nên dùng

### 1. Bắt AI đọc context trước

Prompt mẫu:

```text
Trước khi code, hãy đọc:
- AGENTS.md
- group_project/docs/project-brief.md
- group_project/docs/page-index.md
- group_project/docs/qwen-api.md

Sau đó tóm tắt bạn hiểu task này thế nào. Chưa sửa file.
```

### 2. Yêu cầu plan nhỏ

Prompt mẫu:

```text
Hãy lập plan build PageIndex client.
Yêu cầu:
- chỉ upload 3 PDF legal trong page-index.md
- đọc PAGEINDEX_API_KEY từ .env
- lưu doc_id vào manifest
- chưa code vội
```

### 3. Cho code từng phần nhỏ

Prompt mẫu:

```text
Chỉ sửa group_project/src/pageindex_client.py.
Viết function upload_documents() và save_manifest().
Không hard-code API key.
Sau khi code xong chạy smoke test.
```

### 4. Bắt verify sau khi code

Prompt mẫu:

```text
Hãy chạy smoke test cho file vừa viết.
Nếu lỗi thì sửa tối thiểu. Không sửa file không liên quan.
```

## Prompt mẫu cho task PageIndex

```text
Đọc:
- AGENTS.md
- group_project/docs/page-index.md

Viết group_project/src/pageindex_client.py.
Yêu cầu:
- đọc PAGEINDEX_API_KEY từ .env
- upload 3 PDF legal
- lưu doc_id vào group_project/pageindex_manifest.json
- chỉ dùng document status completed
- không hard-code secret
- chạy smoke test sau khi code
```

## Prompt mẫu cho task Qwen

```text
Đọc:
- AGENTS.md
- group_project/docs/qwen-api.md

Viết group_project/src/qwen_client.py.
Yêu cầu:
- đọc QWEN_API_KEY, QWEN_BASE_URL, QWEN_MODEL_NAME từ .env
- dùng OpenAI SDK compatible
- viết function generate_answer(question, contexts)
- answer phải có citation [Source, Year]
- nếu thiếu evidence trả "I cannot verify this information"
- không hard-code secret
```

## Prompt mẫu cho RAG pipeline

```text
Đọc:
- group_project/src/pageindex_client.py
- group_project/src/qwen_client.py

Viết group_project/src/rag_pipeline.py.
Yêu cầu:
- nhận question
- retrieve context từ PageIndex
- gọi Qwen để generate answer
- return dict gồm answer và sources
- code đơn giản để demo
```

## Prompt mẫu cho UI

```text
Viết group_project/app.py bằng Streamlit.
Yêu cầu:
- ô chat nhập câu hỏi
- gọi rag_pipeline
- hiển thị answer
- hiển thị sources
- dùng session_state lưu history đơn giản
- không làm UI phức tạp
```

## Prompt mẫu cho review

```text
Review file này:
@group_project/src/rag_pipeline.py

Chỉ tìm bug, hard-code secret, thiếu citation, thiếu error handling.
Chưa sửa file.
```

## Checklist trước khi giao việc cho AI

Hãy nói rõ:

- AI cần đọc file nào.
- AI được sửa file nào.
- Output mong muốn là gì.
- Command test/smoke test cần chạy.
- Điều gì không được làm.

Ví dụ tốt:

```text
Đọc AGENTS.md và group_project/docs/page-index.md.
Chỉ sửa group_project/src/pageindex_client.py.
Viết upload_documents().
Không hard-code API key.
Sau khi code xong chạy: python group_project/src/pageindex_client.py
```

## Lỗi thường gặp

### Task quá rộng

Không nên:

```text
Build full chatbot.
```

Nên:

```text
Viết pageindex_client.py trước.
```

### Không đưa context

Không nên:

```text
Sửa giúp tôi.
```

Nên:

```text
Đọc AGENTS.md và group_project/docs/qwen-api.md trước.
```

### Không bắt test

Không nên:

```text
Code xong báo tôi.
```

Nên:

```text
Code xong chạy smoke test và báo output quan trọng.
```