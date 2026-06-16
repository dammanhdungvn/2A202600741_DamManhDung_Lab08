import os
import argparse
from pathlib import Path
from dotenv import load_dotenv

import chromadb
from chromadb.utils import embedding_functions
import PyPDF2
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Resolve project root explicitly for .env
ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")

DB_DIR = ROOT_DIR / "group_project" / "chroma_db"

LEGAL_PDFS = [
    "data/landing/legal/luat-phong-chong-ma-tuy-2021.pdf",
    "data/landing/legal/nghi-dinh-105-2021-huong-dan-luat-phong-chong-ma-tuy.pdf",
    "data/landing/legal/nghi-dinh-57-2022-danh-muc-chat-ma-tuy-va-tien-chat.pdf",
]

# Custom Embedding Function using Qwen API
class QwenEmbeddingFunction(embedding_functions.EmbeddingFunction):
    def __init__(self):
        from openai import OpenAI
        api_key = os.getenv("QWEN_API_KEY")
        base_url = os.getenv("QWEN_BASE_URL")
        if not api_key or not base_url:
            raise ValueError("Missing Qwen credentials for embeddings")
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        
    def __call__(self, input: chromadb.Documents) -> chromadb.Embeddings:
        all_embeddings = []
        batch_size = 10
        for i in range(0, len(input), batch_size):
            batch = input[i:i+batch_size]
            response = self.client.embeddings.create(
                model="text-embedding-v3",
                input=batch
            )
            all_embeddings.extend([item.embedding for item in response.data])
        return all_embeddings

embedding_function = QwenEmbeddingFunction()

def get_chroma_client():
    # Ensure db directory exists
    DB_DIR.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(DB_DIR))

def get_collection():
    client = get_chroma_client()
    # Create or get the collection
    collection = client.get_or_create_collection(
        name="legal_docs",
        embedding_function=embedding_function
    )
    return collection

def extract_text_from_pdf(pdf_path: Path) -> str:
    text = ""
    try:
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
    return text

def build_vector_db():
    print("Building ChromaDB vector database...")
    collection = get_collection()
    
    # Text splitter setup
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )

    for pdf_path_str in LEGAL_PDFS:
        full_path = ROOT_DIR / pdf_path_str
        if not full_path.exists():
            print(f"Warning: File not found {full_path}")
            continue
            
        print(f"Processing {full_path.name}...")
        
        # Check if already processed
        existing = collection.get(where={"source": full_path.name})
        if existing and existing['ids']:
            print(f"Skipping {full_path.name}, already in collection.")
            continue

        text = extract_text_from_pdf(full_path)
        if not text:
            print(f"Warning: No text extracted from {full_path.name}")
            continue
            
        chunks = text_splitter.split_text(text)
        
        # Prepare for ChromaDB
        documents = []
        metadatas = []
        ids = []
        
        for i, chunk in enumerate(chunks):
            documents.append(chunk)
            # Add doc_id so it mimics PageIndex structure
            metadatas.append({"source": full_path.name, "doc_id": full_path.name})
            ids.append(f"{full_path.name}_chunk_{i}")
            
        if documents:
            # Batch upsert to ChromaDB
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            print(f"Added {len(documents)} chunks for {full_path.name}.")

def retrieve_context(query: str, top_k: int = 5) -> list[dict]:
    """
    Interface for Layer 2: Retrieve context using ChromaDB.
    Returns a list of dicts to match what rag_pipeline.py expects.
    """
    try:
        collection = get_collection()
        
        results = collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        formatted_results = []
        
        if not results['documents'] or not results['documents'][0]:
            return []
            
        docs = results['documents'][0]
        distances = results['distances'][0] if 'distances' in results and results['distances'] else [1.0] * len(docs)
        metas = results['metadatas'][0] if 'metadatas' in results and results['metadatas'] else [{}] * len(docs)
        
        for doc, distance, meta in zip(docs, distances, metas):
            source = meta.get("source", "Unknown")
            doc_id = meta.get("doc_id", "Unknown")
            
            formatted_results.append({
                "content": doc,
                "score": distance,
                "metadata": {
                    "doc_id": doc_id,
                    "sources": [source]
                }
            })
            
        return formatted_results
        
    except Exception as e:
        print(f"Retrieval error: {e}")
        raise RuntimeError(f"ChromaDB Retrieval Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ChromaDB Client for Layer 1")
    parser.add_argument("--build", action="store_true", help="Build ChromaDB vector store from legal PDFs")
    parser.add_argument("--query", type=str, help="Smoke test retrieval with a query string")
    
    args = parser.parse_args()
    
    if args.build:
        build_vector_db()
    elif args.query:
        print(f"Querying: '{args.query}'")
        res = retrieve_context(args.query)
        print(f"Found {len(res)} results.")
        for r in res:
            print(f"- [Score: {r['score']}] {r['content'][:100]}...")
            print(f"  Source: {r['metadata']['sources']}")
    else:
        parser.print_help()
