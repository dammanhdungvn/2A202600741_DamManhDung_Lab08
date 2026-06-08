# Codex Vibe Coding Guide

## Mục tiêu

File này hướng dẫn cách dùng Codex để vibe coding hiệu quả cho group project RAG chatbot/evaluation.

Codex sẽ làm tốt hơn nếu bạn luôn đưa đúng ngữ cảnh:

- `AGENTS.md`
- docs trong `group_project/docs/`
- file code cụ thể đang muốn sửa
- yêu cầu nhỏ, rõ, có tiêu chí kiểm tra

## Hiểu nhanh `/` và `@`

Trong Codex/AI coding tools, thường có hai kiểu thao tác hay gặp:

### `/`

`/` thường là command hoặc workflow shortcut.

Ví dụ có thể gặp:

```text
/plan
/review
/fix
/test
```

Tùy app/tool mà command có sẵn khác nhau. Nếu không chắc command có tồn tại không, cứ viết bằng câu thường cũng được.

Ví dụ thay vì:

```text
/plan build rag chatbot
```

bạn có thể viết:

```text
Hãy lập kế hoạch build RAG chatbot theo AGENTS.md và docs trong group_project/docs. Chưa code vội.
```

### `@`

`@` thường dùng để tag file/folder/context cho AI đọc.

Ví dụ:

```text
@AGENTS.md
@group_project/docs/project-brief.md
@group_project/docs/pageindex-upload-workflow.md
@group_project/src/pageindex_client.py
```

Khi tag file, bạn đang nói với Codex: "Hãy đọc file này làm ngữ cảnh chính".

Nếu UI không hỗ trợ tag `@`, bạn vẫn có thể viết đường dẫn bình thường:

```text
Hãy đọc AGENTS.md và group_project/docs/pageindex-upload-workflow.md trước.
```

## Quy trình vibe coding khuyến nghị

### Bước 1: Luôn bắt Codex đọc context trước

Prompt mẫu:

```text
Bạn là senior AI Engineer. Trước khi code, hãy đọc:
@AGENTS.md
@group_project/docs/project-brief.md
@group_project/docs/tech-stack.md
@group_project/docs/page-index.md
@group_project/docs/qwen-api.md
@group_project/docs/pageindex-upload-workflow.md
@group_project/docs/qwen-generation-workflow.md

Sau đó tóm tắt ngắn bạn hiểu task này thế nào. Chưa sửa file.
```

Mục tiêu: tránh Codex đoán sai.

### Bước 2: Yêu cầu plan nhỏ

Prompt mẫu:

```text
Dựa trên docs đã đọc, hãy lập plan build PageIndex client cho group project.
Yêu cầu:
- chỉ upload 3 PDF legal đã ghi trong docs
- đọc PAGEINDEX_API_KEY từ .env
- lưu doc_id vào manifest
- chưa code vội
```

Mục tiêu: kiểm tra hướng đi trước khi cho code.

### Bước 3: Cho code từng phần nhỏ

Prompt mẫu:

```text
Đọc @group_project/docs/page-index.md trước.
Thực hiện bước 1 trong plan: viết file group_project/src/pageindex_client.py.

Yêu cầu:
- đọc .env từ root
- dùng PageIndexClient
- upload 3 PDF trong docs
- lưu manifest vào group_project/pageindex_manifest.json
- không hard-code API key
- sau khi code xong chạy smoke test phù hợp
```

Không nên nói:

```text
Build full app luôn.
```

Vì task quá rộng, Codex dễ làm lan man.

### Bước 4: Sau mỗi lần code, bắt Codex verify

Prompt mẫu:

```text
Hãy chạy smoke test cho file vừa viết.
Nếu test lỗi, sửa lỗi. Không sửa file không liên quan.
```

Hoặc:

```text
Kiểm tra git diff và giải thích file nào đã thay đổi.
```

### Bước 5: Build Qwen client

Prompt mẫu:

```text
Đọc:
@group_project/docs/qwen-api.md
@group_project/docs/qwen-generation-workflow.md

Viết group_project/src/qwen_client.py.
Yêu cầu:
- dùng OpenAI SDK compatible
- api_key từ QWEN_API_KEY
- base_url từ QWEN_BASE_URL
- model từ QWEN_MODEL_NAME
- function generate_answer(question, contexts)
- nếu thiếu evidence thì trả "I cannot verify this information"
- không hard-code secret
```

### Bước 6: Build RAG pipeline

Prompt mẫu:

```text
Viết group_project/src/rag_pipeline.py.

Yêu cầu:
- nhận question
- gọi pageindex_client để retrieve context
- gọi qwen_client để generate answer
- return dict gồm answer và sources
- citation format [Source, Year]
- code đơn giản để demo
```

### Bước 7: Build UI

Prompt mẫu:

```text
Viết group_project/app.py bằng Streamlit.

Yêu cầu:
- ô chat nhập câu hỏi
- gọi rag_pipeline
- hiển thị answer
- hiển thị sources bên dưới
- có session_state lưu history đơn giản
- không làm UI phức tạp
```

### Bước 8: Build evaluation

Prompt mẫu:

```text
Đọc group_project/README.md phần Evaluation.

Tạo:
- group_project/evaluation/golden_dataset.json với 15 Q&A
- group_project/evaluation/eval_pipeline.py
- group_project/evaluation/results.md template

Chọn DeepEval nếu dễ nhất. Nếu cần API model thì dùng Qwen config từ .env.
```

## Prompt mẫu dùng hằng ngày

### Khi muốn làm PageIndex

```text
Đọc:
@group_project/docs/page-index.md
@group_project/docs/pageindex-upload-workflow.md

Sau đó viết hoặc sửa PageIndex client. Chỉ upload 3 PDF legal đã ghi trong docs.
```

### Khi muốn làm Qwen

```text
Đọc:
@group_project/docs/qwen-api.md
@group_project/docs/qwen-generation-workflow.md

Sau đó viết hoặc sửa Qwen client. Không hard-code API key, base URL, model name.
```

### Khi muốn làm Weaviate optional

```text
Đọc @group_project/docs/weaviate.md.
Chỉ viết script test connect Weaviate. Không tích hợp vào chatbot vội.
```

### Khi muốn Codex đọc và chưa code

```text
Hãy đọc các file sau và tóm tắt ngữ cảnh. Không sửa file:
@AGENTS.md
@group_project/docs/vibe-coding-plan.md
```

### Khi muốn Codex sửa đúng một file

```text
Chỉ sửa file @group_project/src/qwen_client.py.
Không sửa file khác.
Sau khi sửa, chạy smoke test.
```

### Khi muốn Codex debug

```text
Lỗi khi chạy command này:
<paste lỗi>

Hãy đọc file liên quan, tìm nguyên nhân, sửa tối thiểu và chạy lại command.
```

### Khi muốn Codex review

```text
Review code trong @group_project/src/rag_pipeline.py.
Tập trung bug, thiếu citation, thiếu error handling, và chỗ hard-code secret.
Chưa sửa file.
```

### Khi muốn Codex nối nhiều file

```text
Đọc:
@group_project/src/pageindex_client.py
@group_project/src/qwen_client.py

Viết @group_project/src/rag_pipeline.py để nối 2 module này.
```

## Checklist trước khi bảo Codex code

Trước mỗi task, hãy nói rõ:

- File nào cần đọc.
- File nào được phép sửa.
- Output mong muốn.
- Command test/smoke test cần chạy.
- Điều gì không được làm.

Ví dụ tốt:

```text
Đọc AGENTS.md và group_project/docs/pageindex-upload-workflow.md.
Chỉ sửa group_project/src/pageindex_client.py.
Viết function upload_documents() và save_manifest().
Không hard-code API key.
Sau khi code xong chạy: python group_project/src/pageindex_client.py
```

## Các lỗi thường gặp khi vibe coding

### Task quá rộng

Không nên:

```text
Build toàn bộ chatbot.
```

Nên:

```text
Viết trước pageindex_client.py để upload và lưu doc_id.
```

### Không đưa context

Không nên:

```text
Sửa giúp tôi.
```

Nên:

```text
Đọc AGENTS.md và file lỗi này trước: @group_project/src/qwen_client.py
```

### Không nói test

Không nên:

```text
Code xong báo tôi.
```

Nên:

```text
Code xong chạy smoke test và báo output quan trọng.
```

## Lộ trình prompt cho project này

Bạn có thể đi theo chuỗi prompt sau:

1. Đọc context:

```text
Đọc AGENTS.md và toàn bộ docs trong group_project/docs. Tóm tắt project. Chưa code.
```

2. PageIndex:

```text
Viết group_project/src/pageindex_client.py theo page-index.md và pageindex-upload-workflow.md.
```

3. Qwen:

```text
Viết group_project/src/qwen_client.py theo qwen-api.md và qwen-generation-workflow.md.
```

4. Pipeline:

```text
Viết group_project/src/rag_pipeline.py nối PageIndex retrieval và Qwen generation.
```

5. UI:

```text
Viết group_project/app.py bằng Streamlit để demo chatbot.
```

6. Evaluation:

```text
Viết evaluation theo group_project/README.md, ưu tiên đơn giản chạy được.
```

## Nguyên tắc vàng

Codex làm tốt nhất khi bạn giao việc như giao cho một junior engineer thông minh:

- đưa context
- giới hạn phạm vi
- nói rõ output
- bắt verify
- không yêu cầu quá nhiều thứ một lần
