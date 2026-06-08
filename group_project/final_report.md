# RAG Chatbot MVP: Final Report

## 1. Project Overview
This project delivers a Minimum Viable Product (MVP) for a Retrieval-Augmented Generation (RAG) chatbot specializing in Vietnamese drug law and related news. 

**Key Objectives:**
- Answer user queries strictly based on provided legal contexts.
- Enforce strict citation rules (`[Source, Year]`) for all factual claims.
- Safely refuse to answer (graceful fallback) with exactly `"I cannot verify this information"` when evidence is missing, entirely eliminating LLM hallucination.

## 2. System Architecture
The system is built upon a modular 3-Layer architecture:
- **Layer 1: Data / Retrieval:** Managed by PageIndex API. Responsible for uploading PDFs, tracking processing status via a local manifest, and retrieving relevant text chunks based on semantic similarity.
- **Layer 2: RAG / Generation:** Powered by Qwen (via OpenAI-compatible SDK). Receives contexts from Layer 1 and the user question, applies a strict system prompt, and generates the final cited answer.
- **Layer 3: Interface / Evaluation:** A user-friendly Streamlit UI with lightweight session memory, paired with a custom Python-based evaluation pipeline to automatically score the RAG agent's performance.

## 3. Implemented Components
The following core modules have been fully implemented and integrated:
- `pageindex_client.py`: Handles secure API connections, PDF uploads, status polling, and retrieval logic.
- `qwen_client.py`: Configures the LLM, injects contexts into the prompt, and enforces citation/fallback rules.
- `rag_pipeline.py`: The central orchestrator connecting Layer 1 and Layer 2, catching errors, and ensuring safe fallback routing.
- `app.py`: The Streamlit web interface.
- `golden_dataset.json`: A curated list of 10 test questions (in-domain and out-of-domain) to evaluate pipeline safety.
- `eval_pipeline.py`: An automated script to score the RAG pipeline against the golden dataset.

## 4. Current Evaluation Result
**Score: 10/10 PASS**

> **IMPORTANT CONTEXT:** 
> The current 10/10 score **does not** reflect the semantic retrieval or reasoning quality of the LLM. 
> Due to a quota limit on the PageIndex API (see Limitations), no documents were successfully uploaded. Consequently, the retrieval layer returns zero contexts for every query. 
> 
> However, this test proves that the **Fallback Safety Mechanism is 100% operational**. For all 10 questions, the pipeline successfully avoided hallucination and returned the exact required string: `"I cannot verify this information"`.

## 5. Limitations
We want to be entirely transparent about the current state of the MVP:
- **PageIndex Quota Exhausted (`LimitReached`):** The provided `PAGEINDEX_API_KEY` has reached its usage limit.
- **No Uploaded Documents:** Because of the quota issue, the 3 required legal PDFs have not been uploaded to the server.
- **Zero "Completed" Contexts:** The `pageindex_manifest.json` is currently empty.
- **Untested Generation Quality:** Because the LLM is never fed actual context, its ability to synthesize information and format citations (`[Source, Year]`) from Vietnamese legal text has not been empirically evaluated yet.
- **UI State:** The UI currently functions primarily as a demonstration of error-handling and fallback mechanics.

## 6. How to Run

**Run the Web UI:**
```powershell
.\.venv\Scripts\python.exe -m streamlit run group_project/app.py
```

**Run the Evaluation Pipeline:**
```powershell
$env:PYTHONIOENCODING="utf-8"; .\.venv\Scripts\python.exe group_project/evaluation/eval_pipeline.py
```

**Upload & Check Documents (When Quota is Restored):**
```powershell
.\.venv\Scripts\python.exe group_project/src/pageindex_client.py --upload
.\.venv\Scripts\python.exe group_project/src/pageindex_client.py --status
```

## 7. Next Steps
To transition this MVP from a "safety demonstration" to a fully functional RAG Chatbot, the following steps are required:
1. **Refresh Credentials:** Provide a new `PAGEINDEX_API_KEY` with available quota in the root `.env` file.
2. **Populate Database:** Run the upload command to ingest the 3 required PDFs and run the status command until they are marked as `completed`.
3. **Re-Evaluate:** Run `eval_pipeline.py` again. The system will shift from testing fallbacks to testing actual context retrieval and citation accuracy.
4. **Final Report Update:** Append the true RAG evaluation scores to this document.
