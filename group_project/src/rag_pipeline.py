import sys
from pathlib import Path

# Add project root to path so we can import modules cleanly
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

# Import Layer 1 and Layer 2
from group_project.src.chroma_client import retrieve_context
from group_project.src.qwen_client import generate_answer

def ask_question(question: str, chat_history: list = None) -> dict:
    """
    Main pipeline to answer a user question using RAG.
    
    Args:
        question (str): The user's question.
        chat_history (list): Lightweight chat history (optional).
        
    Returns:
        dict: A dictionary containing 'answer', 'sources', 'contexts_used', and 'error' (if any).
    """
    if chat_history is None:
        chat_history = []
        
    result = {
        "answer": "",
        "sources": [],
        "contexts_used": 0,
        "error": None
    }
    
    try:
        # Step 1: Retrieval (Layer 1)
        # Using a default top_k of 5. For lightweight memory, we could 
        # potentially include recent history in the query, but we keep it simple here.
        contexts = retrieve_context(query=question, top_k=5)
        result["contexts_used"] = len(contexts)
        
        # Graceful fallback if no contexts are retrieved (e.g., no completed docs)
        if not contexts:
            result["answer"] = "I cannot verify this information"
            return result
            
        # Step 2: Generation (Layer 2)
        qwen_response = generate_answer(question=question, contexts=contexts)
        
        # Populate result object
        result["answer"] = qwen_response.get("answer", "")
        
        # Extract sources nicely for the UI
        # We can extract the doc_id from metadata of the returned sources
        returned_sources = qwen_response.get("sources", [])
        unique_docs = set()
        for src in returned_sources:
            doc_id = src.get("metadata", {}).get("doc_id")
            if doc_id:
                unique_docs.add(doc_id)
        
        result["sources"] = list(unique_docs)
        
    except Exception as e:
        result["error"] = str(e)
        result["answer"] = "An error occurred during the RAG process."
        
    return result

if __name__ == "__main__":
    print("--- SMOKE TEST: RAG Pipeline ---")
    
    test_question = "Theo luật, danh mục chất ma túy được quy định ở đâu?"
    print(f"User Question: '{test_question}'\n")
    
    print("Running pipeline...\n")
    pipeline_result = ask_question(test_question)
    
    print("--- PIPELINE OUTPUT ---")
    print(f"Answer: {pipeline_result['answer']}")
    print(f"Sources: {pipeline_result['sources']}")
    print(f"Contexts Used: {pipeline_result['contexts_used']}")
    if pipeline_result['error']:
        print(f"Error: {pipeline_result['error']}")
    print("-----------------------")
