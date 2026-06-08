import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Rule: Resolve project root explicitly for .env
ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")

def get_client() -> OpenAI:
    """Initialize OpenAI client for Qwen with credentials from .env."""
    api_key = os.getenv("QWEN_API_KEY")
    base_url = os.getenv("QWEN_BASE_URL")
    
    if not api_key:
        raise ValueError("Missing QWEN_API_KEY in .env")
    if not base_url:
        raise ValueError("Missing QWEN_BASE_URL in .env")
        
    return OpenAI(api_key=api_key, base_url=base_url)

def get_model_name() -> str:
    """Read QWEN_MODEL_NAME from .env."""
    model_name = os.getenv("QWEN_MODEL_NAME")
    if not model_name:
        raise ValueError("Missing QWEN_MODEL_NAME in .env")
    return model_name

def generate_answer(question: str, contexts: list[dict]) -> dict:
    """
    Generate an answer using Qwen based only on the provided contexts.
    Enforces citation and fallback rules.
    """
    try:
        client = get_client()
        model_name = get_model_name()
    except Exception as e:
        print(f"Configuration error: {e}")
        return {"answer": "I cannot verify this information", "sources": contexts}
    
    # Format contexts into a single text block
    formatted_contexts = []
    for i, ctx in enumerate(contexts):
        content = ctx.get("content", "")
        # Assuming the doc name is in metadata['doc_id'] based on Layer 1 structure
        source = ctx.get("metadata", {}).get("doc_id", f"Document {i+1}")
        formatted_contexts.append(f"--- Context Segment ---\nSource: {source}\nContent: {content}\n")
    
    context_text = "\n".join(formatted_contexts)
    if not context_text.strip():
        context_text = "No context provided."
    
    system_prompt = """You are a helpful and factual legal assistant.
Answer the user's question comprehensively, using ONLY the information provided in the Context below.

Rules:
1. You must ONLY answer based on the provided context. Do not use outside knowledge.
2. For every statement of fact or claim, you MUST immediately insert a citation in brackets linking to the specific source provided in the context (e.g., [Source, Year]). If a specific year is not available, cite the source name.
3. If the provided context does NOT contain enough evidence to answer the user's question, you MUST reply exactly with: "I cannot verify this information" rather than guessing.

Context:
{context}
"""

    formatted_system_prompt = system_prompt.format(context=context_text)

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": formatted_system_prompt},
                {"role": "user", "content": question}
            ],
            temperature=0.1,  # Low temperature for factual RAG
            top_p=0.9
        )
        answer = response.choices[0].message.content.strip()
        
        return {
            "answer": answer,
            "sources": contexts
        }
    except Exception as e:
        print(f"Error calling Qwen API: {e}")
        return {
            "answer": "Error generating answer.",
            "sources": contexts
        }

if __name__ == "__main__":
    print("--- SMOKE TEST: Qwen Generation Client ---")
    
    fake_contexts = [
        {
            "content": "Theo Luật Phòng, chống ma túy năm 2021, hành vi trồng cây có chứa chất ma túy (như cây cần sa, cây coca) bị nghiêm cấm hoàn toàn.",
            "score": 0.9,
            "metadata": {"doc_id": "luat-phong-chong-ma-tuy-2021.pdf"}
        }
    ]
    
    print("\n[Test 1] Question with valid context:")
    fake_question_1 = "Trồng cây cần sa có bị cấm theo luật không?"
    print(f"Q: {fake_question_1}")
    res_1 = generate_answer(fake_question_1, fake_contexts)
    print(f"A: {res_1['answer']}")
    
    print("\n[Test 2] Question missing evidence in context:")
    fake_question_2 = "Gần đây có ca sĩ nào bị bắt vì sử dụng ma túy không?"
    print(f"Q: {fake_question_2}")
    res_2 = generate_answer(fake_question_2, fake_contexts)
    print(f"A: {res_2['answer']}")
    print("------------------------------------------")
