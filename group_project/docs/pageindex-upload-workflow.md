# PageIndex Upload Workflow

## Purpose

Use PageIndex to process legal PDF files and retrieve context for RAG.

## Files To Upload

Upload these three PDFs:

```text
data/landing/legal/luat-phong-chong-ma-tuy-2021.pdf
data/landing/legal/nghi-dinh-105-2021-huong-dan-luat-phong-chong-ma-tuy.pdf
data/landing/legal/nghi-dinh-57-2022-danh-muc-chat-ma-tuy-va-tien-chat.pdf
```

These are the clean source PDFs for the PageIndex workflow.

## Do Not Upload

Do not upload:

- `.env`
- source code
- `data/index/vector_store.jsonl`
- pytest caches
- local markdown if PageIndex only accepts PDF in the dashboard

## Required `.env`

```env
PAGEINDEX_API_KEY=your_key
```

## Upload Flow

1. Load `PAGEINDEX_API_KEY` from `.env`.
2. Initialize `PageIndexClient`.
3. Submit each PDF.
4. Read the returned `doc_id`.
5. Save mapping of local file path to `doc_id`.
6. Check document status.
7. Use only documents where status is `completed`.

## Suggested Manifest

Save a file like:

```text
group_project/pageindex_manifest.json
```

Example shape:

```json
{
  "documents": [
    {
      "source": "luat-phong-chong-ma-tuy-2021.pdf",
      "path": "data/landing/legal/luat-phong-chong-ma-tuy-2021.pdf",
      "doc_id": "pageindex_doc_id_here",
      "status": "completed"
    }
  ]
}
```

Do not commit real private IDs if your team treats them as sensitive.

## Retrieval Flow

```text
User query
-> choose completed PageIndex docs
-> query PageIndex by doc_id
-> collect retrieved text/context
-> pass context to Qwen
-> answer with citation
```

