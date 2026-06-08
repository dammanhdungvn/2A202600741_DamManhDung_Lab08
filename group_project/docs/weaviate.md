# Weaviate Guide

## Dùng để làm gì?

Weaviate là vector database. Nó dùng để lưu chunks + embeddings và search theo vector/hybrid.

Trong project này, Weaviate là optional:

- Nếu làm theo PageIndex: có thể chưa cần Weaviate.
- Nếu muốn dùng pipeline cá nhân Task 4-9 nâng cấp lên cloud: dùng Weaviate.

## Khi nào dùng Weaviate?

Dùng Weaviate khi bạn muốn:

- lưu chunks lên cloud
- semantic search bằng vector
- hybrid search vector + keyword
- demo retrieval nhanh hơn local file

Không bắt buộc dùng Weaviate nếu group chỉ làm:

```text
PageIndex PDF retrieval -> Qwen generation -> chatbot
```

## Biến trong `.env`

Cần có:

```env
WEAVIATE_URL=https://your-cluster.weaviate.cloud
WEAVIATE_API_KEY=your_weaviate_api_key
```

Rule quan trọng:

- Không hard-code API key.
- Luôn đọc từ `.env`.
- `WEAVIATE_URL` phải có `https://`.
- Sau khi dùng xong, gọi `client.close()`.

## Code mẫu connect

```python
import os
from pathlib import Path
from dotenv import load_dotenv
import weaviate
from weaviate.classes.init import Auth

ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")

weaviate_url = os.getenv("WEAVIATE_URL")
weaviate_api_key = os.getenv("WEAVIATE_API_KEY")

if not weaviate_url:
    raise ValueError("Missing WEAVIATE_URL in .env")
if not weaviate_api_key:
    raise ValueError("Missing WEAVIATE_API_KEY in .env")

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_url,
    auth_credentials=Auth.api_key(weaviate_api_key),
)

print(client.is_ready())

client.close()
```

Kết quả mong đợi:

```text
True
```

## Lưu ý cho fresher/junior

Nếu bạn đang build demo group nhanh, hãy làm PageIndex trước. Weaviate chỉ nên làm sau khi:

1. Qwen đã call được.
2. PageIndex đã upload 3 PDF và có `doc_id`.
3. Chatbot đã trả lời được câu hỏi có citation.

Sau đó mới tính tới Weaviate để cải thiện retrieval.

## Prompt mẫu cho Codex

```text
Đọc group_project/docs/weaviate.md.
Chỉ viết script test connect Weaviate.
Yêu cầu:
- đọc WEAVIATE_URL và WEAVIATE_API_KEY từ .env
- print client.is_ready()
- close client sau khi xong
- không hard-code secret
```