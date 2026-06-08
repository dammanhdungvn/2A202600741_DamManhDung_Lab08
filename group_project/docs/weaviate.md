# Weaviate Guide

## Dung de lam gi?

Weaviate la vector database. No dung de luu chunks + embeddings va search theo vector/hybrid.

Trong project nay Weaviate la optional:

- Neu lam theo PageIndex: co the chua can Weaviate.
- Neu muon dung pipeline ca nhan Task 4-9 nang cap len cloud: dung Weaviate.

## Khi nao dung Weaviate?

Dung Weaviate khi ban muon:

- luu chunks len cloud
- semantic search bang vector
- hybrid search vector + keyword
- demo retrieval nhanh hon local file

Khong bat buoc dung Weaviate neu group chi lam:

```text
PageIndex PDF retrieval -> Qwen generation -> chatbot
```

## Bien trong `.env`

Can co:

```env
WEAVIATE_URL=https://your-cluster.weaviate.cloud
WEAVIATE_API_KEY=your_weaviate_api_key
```

Rule quan trong:

- Khong hard-code API key.
- Luon doc tu `.env`.
- `WEAVIATE_URL` phai co `https://`.
- Sau khi dung xong, goi `client.close()`.

## Code mau connect

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

Ket qua mong doi:

```text
True
```

## Luu y cho fresher/junior

Neu ban dang build demo group nhanh, hay lam PageIndex truoc. Weaviate chi nen lam sau khi:

1. Qwen da call duoc.
2. PageIndex da upload 3 PDF va co `doc_id`.
3. Chatbot da tra loi duoc cau hoi co citation.

Sau do moi tinh toi Weaviate de cai thien retrieval.

## Prompt mau cho Codex

```text
Doc group_project/docs/weaviate.md.
Chi viet script test connect Weaviate.
Yeu cau:
- doc WEAVIATE_URL va WEAVIATE_API_KEY tu .env
- print client.is_ready()
- close client sau khi xong
- khong hard-code secret
```

