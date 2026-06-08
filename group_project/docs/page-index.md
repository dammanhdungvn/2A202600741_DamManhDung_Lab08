# PageIndex Guide

## Dùng để làm gì?

PageIndex dùng để upload PDF, process tài liệu, và lấy `doc_id` để retrieval.

Trong project này, PageIndex là retrieval source cho chatbot:

```text
PDF legal -> PageIndex -> retrieve context -> Qwen -> answer có citation
```

## File cần upload

Dashboard PageIndex chỉ cho upload PDF, nên upload 3 file này:

```text
data/landing/legal/luat-phong-chong-ma-tuy-2021.pdf
data/landing/legal/nghi-dinh-105-2021-huong-dan-luat-phong-chong-ma-tuy.pdf
data/landing/legal/nghi-dinh-57-2022-danh-muc-chat-ma-tuy-va-tien-chat.pdf
```

Không upload:

- `.env`
- file code
- markdown trong `data/standardized/`
- local vector store trong `data/index/`
- cache/test files

## Biến trong `.env`

Cần có:

```env
PAGEINDEX_API_KEY=your_pageindex_api_key
```

Rule quan trọng:

- Không hard-code API key.
- Luôn đọc `PAGEINDEX_API_KEY` từ `.env`.
- Sau khi upload, phải lưu `doc_id`.
- Chỉ query document khi status là `completed`.

## Code mẫu connect

```python
import os
from pathlib import Path
from dotenv import load_dotenv
from pageindex import PageIndexClient

ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")

api_key = os.getenv("PAGEINDEX_API_KEY")
if not api_key:
    raise ValueError("Missing PAGEINDEX_API_KEY in .env")

client = PageIndexClient(api_key=api_key)
```

## Upload flow

```text
1. Chọn 3 PDF legal
2. submit_document(file_path)
3. Lấy doc_id
4. get_document(doc_id) để check status
5. Nếu status == completed thì lưu vào manifest
6. Khi user hỏi, dùng doc_id để query/retrieve
```

## Manifest nên lưu

Nên lưu file:

```text
group_project/pageindex_manifest.json
```

Ví dụ:

```json
{
  "documents": [
    {
      "source": "luat-phong-chong-ma-tuy-2021.pdf",
      "path": "data/landing/legal/luat-phong-chong-ma-tuy-2021.pdf",
      "doc_id": "doc_id_from_pageindex",
      "status": "completed"
    }
  ]
}
```

## Prompt mẫu cho Codex

```text
Đọc group_project/docs/page-index.md.
Viết group_project/src/pageindex_client.py.
Yêu cầu:
- upload đúng 3 PDF legal
- đọc PAGEINDEX_API_KEY từ .env
- lưu doc_id vào group_project/pageindex_manifest.json
- check status completed
- không hard-code secret
```