import os
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv
from pageindex import PageIndexClient

# Rule: Resolve project root explicitly for .env
ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")

MANIFEST_PATH = ROOT_DIR / "group_project" / "pageindex_manifest.json"

# Rule: Only manage these 3 legal PDFs
LEGAL_PDFS = [
    "data/landing/legal/luat-phong-chong-ma-tuy-2021.pdf",
    "data/landing/legal/nghi-dinh-105-2021-huong-dan-luat-phong-chong-ma-tuy.pdf",
    "data/landing/legal/nghi-dinh-57-2022-danh-muc-chat-ma-tuy-va-tien-chat.pdf",
]

def get_client() -> PageIndexClient:
    """Initialize PageIndex client reading API Key from .env."""
    api_key = os.getenv("PAGEINDEX_API_KEY")
    if not api_key:
        raise ValueError("Missing PAGEINDEX_API_KEY in .env")
    return PageIndexClient(api_key=api_key)

def load_manifest() -> dict:
    if not MANIFEST_PATH.exists():
        return {"documents": []}
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_manifest(manifest: dict):
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

def upload_documents():
    """Upload legal PDFs to PageIndex and save doc_ids to manifest."""
    print("Uploading documents to PageIndex...")
    client = get_client()
    manifest = load_manifest()
    
    existing_paths = [doc.get("path") for doc in manifest.get("documents", [])]
    
    for pdf_path_str in LEGAL_PDFS:
        if pdf_path_str in existing_paths:
            print(f"Skipping {pdf_path_str}, already in manifest.")
            continue
            
        full_path = ROOT_DIR / pdf_path_str
        if not full_path.exists():
            print(f"Warning: File not found {full_path}")
            continue
            
        print(f"Uploading {full_path.name}...")
        try:
            # Submit document to PageIndex
            response = client.submit_document(str(full_path))
            
            # Extract doc_id from response. Handling multiple object types just in case.
            doc_id = response.doc_id if hasattr(response, 'doc_id') else response.get("doc_id")
            
            manifest["documents"].append({
                "source": full_path.name,
                "path": pdf_path_str,
                "doc_id": doc_id,
                "status": "processing" # Initial status
            })
            save_manifest(manifest)
            print(f"Uploaded {full_path.name} -> doc_id: {doc_id}")
        except Exception as e:
            print(f"Failed to upload {full_path.name}: {e}")

def update_status():
    """Check and update status of uploaded documents in PageIndex."""
    print("Checking status of documents...")
    client = get_client()
    manifest = load_manifest()
    
    updated = False
    for doc in manifest.get("documents", []):
        doc_id = doc.get("doc_id")
        if not doc_id:
            continue
            
        try:
            doc_info = client.get_document(doc_id)
            # Support object attribute or dictionary key access
            status = doc_info.status if hasattr(doc_info, 'status') else doc_info.get("status", "unknown")
            
            if status != doc.get("status"):
                print(f"Document {doc['source']} status changed: {doc.get('status')} -> {status}")
                doc["status"] = status
                updated = True
            else:
                print(f"Document {doc['source']} status: {status}")
        except Exception as e:
            print(f"Failed to get status for {doc_id}: {e}")
            
    if updated:
        save_manifest(manifest)
        print("Manifest updated.")

def retrieve_context(query: str, top_k: int = 5) -> list[dict]:
    """
    Interface for Layer 2: Retrieve context using PageIndex.
    Only uses documents with status 'completed'.
    """
    client = get_client()
    manifest = load_manifest()
    
    # Filter only completed doc_ids
    completed_doc_ids = [
        doc["doc_id"] for doc in manifest.get("documents", [])
        if doc.get("status") == "completed" and doc.get("doc_id")
    ]
    
    if not completed_doc_ids:
        print("Warning: No completed documents available for retrieval.")
        return []
        
    results = []
    try:
        # Use chat_completions as the retrieval endpoints are deprecated
        res = client.chat_completions(
            messages=[{"role": "user", "content": query}],
            doc_id=completed_doc_ids,
            enable_citations=True
        )
        
        # Extract the generated response to serve as rich context for Qwen
        if isinstance(res, dict) and "choices" in res:
            content = res["choices"][0]["message"]["content"]
            # Extract citation sources if available
            sources = []
            if "citations" in res:
                for c in res["citations"]:
                    src = c.get("document", "Unknown")
                    if src not in sources:
                        sources.append(src)
            
            results.append({
                "content": content,
                "score": 1.0,
                "metadata": {"doc_id": "multiple", "sources": sources}
            })
            
        return results
        
    except Exception as e:
        print(f"Retrieval error: {e}")
        raise RuntimeError(f"PageIndex Retrieval Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PageIndex Client for Layer 1")
    parser.add_argument("--upload", action="store_true", help="Upload the 3 legal PDFs to PageIndex (Will consume credit)")
    parser.add_argument("--status", action="store_true", help="Check and update status of uploaded documents")
    parser.add_argument("--query", type=str, help="Smoke test retrieval with a query string")
    
    args = parser.parse_args()
    
    if args.upload:
        upload_documents()
    elif args.status:
        update_status()
    elif args.query:
        print(f"Querying: '{args.query}'")
        res = retrieve_context(args.query)
        print(f"Found {len(res)} results.")
        for r in res:
            print(f"- [Score: {r['score']}] {r['content'][:100]}...")
    else:
        parser.print_help()
