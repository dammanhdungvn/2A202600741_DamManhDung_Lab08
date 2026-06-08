# Codex Vibe Coding Guide

## Muc tieu

File nay huong dan cach dung Codex de vibe coding hieu qua cho group project.

Neu ban dung nhieu IDE/agent khac nhau, doc them:

```text
group_project/docs/multi-platform-agent-setup.md
```

## Y tuong chinh

Dung chung mot bo docs:

- `AGENTS.md`
- `group_project/docs/project-brief.md`
- `group_project/docs/page-index.md`
- `group_project/docs/qwen-api.md`
- `group_project/docs/weaviate.md`

Sau do moi tool se co mot file adapter rieng:

- Codex: `AGENTS.md`
- Cursor: `.cursor/rules/rag-group-project.mdc`
- Copilot/VS Code: `.github/copilot-instructions.md`
- Claude Code: `CLAUDE.md`
- Gemini CLI: `GEMINI.md`
- Windsurf: `.windsurfrules`

## Hieu nhanh `/` va `@`

### `/`

`/` thuong la command cua tool.

Vi du:

```text
/plan
/review
/fix
/test
```

Khong phai tool nao cung co cac command nay. Neu khong chac, cu viet bang ngon ngu binh thuong.

### `@`

`@` thuong dung de tag file cho AI doc.

Vi du:

```text
@AGENTS.md
@group_project/docs/page-index.md
@group_project/docs/qwen-api.md
```

Neu tool khong ho tro `@`, viet duong dan file bang text la du.

## Workflow nen dung

### 1. Bat AI doc context truoc

Prompt mau:

```text
Truoc khi code, hay doc:
- AGENTS.md
- group_project/docs/project-brief.md
- group_project/docs/page-index.md
- group_project/docs/qwen-api.md

Sau do tom tat ban hieu task nay the nao. Chua sua file.
```

### 2. Yeu cau plan nho

Prompt mau:

```text
Hay lap plan build PageIndex client.
Yeu cau:
- chi upload 3 PDF legal trong page-index.md
- doc PAGEINDEX_API_KEY tu .env
- luu doc_id vao manifest
- chua code voi
```

### 3. Cho code tung phan nho

Prompt mau:

```text
Chi sua group_project/src/pageindex_client.py.
Viet function upload_documents() va save_manifest().
Khong hard-code API key.
Sau khi code xong chay smoke test.
```

### 4. Bat verify sau khi code

Prompt mau:

```text
Hay chay smoke test cho file vua viet.
Neu loi thi sua toi thieu. Khong sua file khong lien quan.
```

## Prompt mau cho task PageIndex

```text
Doc:
- AGENTS.md
- group_project/docs/page-index.md

Viet group_project/src/pageindex_client.py.
Yeu cau:
- doc PAGEINDEX_API_KEY tu .env
- upload 3 PDF legal
- luu doc_id vao group_project/pageindex_manifest.json
- chi dung document status completed
- khong hard-code secret
- chay smoke test sau khi code
```

## Prompt mau cho task Qwen

```text
Doc:
- AGENTS.md
- group_project/docs/qwen-api.md

Viet group_project/src/qwen_client.py.
Yeu cau:
- doc QWEN_API_KEY, QWEN_BASE_URL, QWEN_MODEL_NAME tu .env
- dung OpenAI SDK compatible
- viet function generate_answer(question, contexts)
- answer phai co citation [Source, Year]
- neu thieu evidence tra "I cannot verify this information"
- khong hard-code secret
```

## Prompt mau cho RAG pipeline

```text
Doc:
- group_project/src/pageindex_client.py
- group_project/src/qwen_client.py

Viet group_project/src/rag_pipeline.py.
Yeu cau:
- nhan question
- retrieve context tu PageIndex
- goi Qwen de generate answer
- return dict gom answer va sources
- code don gian de demo
```

## Prompt mau cho UI

```text
Viet group_project/app.py bang Streamlit.
Yeu cau:
- o chat nhap cau hoi
- goi rag_pipeline
- hien thi answer
- hien thi sources
- dung session_state luu history don gian
- khong lam UI phuc tap
```

## Prompt mau cho review

```text
Review file nay:
@group_project/src/rag_pipeline.py

Chi tim bug, hard-code secret, thieu citation, thieu error handling.
Chua sua file.
```

## Checklist truoc khi giao viec cho AI

Hay noi ro:

- AI can doc file nao.
- AI duoc sua file nao.
- Output mong muon la gi.
- Command test/smoke test can chay.
- Dieu gi khong duoc lam.

Vi du tot:

```text
Doc AGENTS.md va group_project/docs/page-index.md.
Chi sua group_project/src/pageindex_client.py.
Viet upload_documents().
Khong hard-code API key.
Sau khi code xong chay: python group_project/src/pageindex_client.py
```

## Loi thuong gap

### Task qua rong

Khong nen:

```text
Build full chatbot.
```

Nen:

```text
Viet pageindex_client.py truoc.
```

### Khong dua context

Khong nen:

```text
Sua giup toi.
```

Nen:

```text
Doc AGENTS.md va group_project/docs/qwen-api.md truoc.
```

### Khong bat test

Khong nen:

```text
Code xong bao toi.
```

Nen:

```text
Code xong chay smoke test va bao output quan trong.
```

