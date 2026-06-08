# PageIndex Guide

## Dung de lam gi?

PageIndex dung de upload PDF, process tai lieu, va lay `doc_id` de retrieval.

Trong project nay PageIndex la retrieval source cho chatbot:

```text
PDF legal -> PageIndex -> retrieve context -> Qwen -> answer co citation
```

## File can upload

Dashboard PageIndex chi cho upload PDF, nen upload 3 file nay:

```text
data/landing/legal/luat-phong-chong-ma-tuy-2021.pdf
data/landing/legal/nghi-dinh-105-2021-huong-dan-luat-phong-chong-ma-tuy.pdf
data/landing/legal/nghi-dinh-57-2022-danh-muc-chat-ma-tuy-va-tien-chat.pdf
```

Khong upload:

- `.env`
- file code
- markdown trong `data/standardized/`
- local vector store trong `data/index/`
- cache/test files

## Bien trong `.env`

Can co:

```env
PAGEINDEX_API_KEY=your_pageindex_api_key
```

Rule quan trong:

- Khong hard-code API key.
- Luon doc `PAGEINDEX_API_KEY` tu `.env`.
- Sau khi upload, phai luu `doc_id`.
- Chi query document khi status la `completed`.

## Code mau connect

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
1. Chon 3 PDF legal
2. submit_document(file_path)
3. Lay doc_id
4. get_document(doc_id) de check status
5. Neu status == completed thi luu vao manifest
6. Khi user hoi, dung doc_id de query/retrieve
```

## Manifest nen luu

Nen luu file:

```text
group_project/pageindex_manifest.json
```

Vi du:

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

## Prompt mau cho Codex

```text
Doc group_project/docs/page-index.md va group_project/docs/pageindex-upload-workflow.md.
Viet group_project/src/pageindex_client.py.
Yeu cau:
- upload dung 3 PDF legal
- doc PAGEINDEX_API_KEY tu .env
- luu doc_id vao group_project/pageindex_manifest.json
- check status completed
- khong hard-code secret
```

