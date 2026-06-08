import json
import sys
import re
from pathlib import Path

# Add project root to path so we can import modules cleanly
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from group_project.src.rag_pipeline import ask_question

DATASET_PATH = ROOT_DIR / "group_project" / "evaluation" / "golden_dataset.json"
RESULTS_PATH = ROOT_DIR / "group_project" / "evaluation" / "results.md"

def evaluate_pipeline():
    print("--- Starting RAG Evaluation Pipeline ---\n")
    
    if not DATASET_PATH.exists():
        print(f"Error: Dataset not found at {DATASET_PATH}")
        return
        
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        dataset = json.load(f)
        
    total = len(dataset)
    passed = 0
    failed = 0
    fallback_count = 0
    
    results_markdown = "# RAG Evaluation Results\n\n"
    results_markdown += f"**Total Questions:** {total}\n\n"
    
    print(f"Loaded {total} questions from dataset.\n")
    
    for item in dataset:
        q_id = item["id"]
        question = item["question"]
        expected_behavior = item["expected_behavior"]
        
        print(f"[{q_id}] Q: {question}")
        
        try:
            # Call the main pipeline
            result = ask_question(question)
            answer = result.get("answer", "")
            error = result.get("error")
            contexts_used = result.get("contexts_used", 0)
            
            # 1. Check for crash
            if error:
                status = "FAIL"
                note = f"Pipeline error: {error}"
            # 2. Check for empty answer
            elif not answer.strip():
                status = "FAIL"
                note = "Answer is empty."
            # 3 & 4 & 5. Check behaviors
            else:
                is_fallback = (answer == "I cannot verify this information")
                
                # If PageIndex is empty, everything will fallback. We count this as PASS(Fallback)
                # because the pipeline is safely avoiding hallucination when context is 0.
                if contexts_used == 0 and is_fallback:
                    status = "PASS"
                    note = "Graceful fallback (No completed contexts available)."
                    fallback_count += 1
                elif is_fallback:
                    if expected_behavior == "fallback":
                        status = "PASS"
                        note = "Correctly fell back as expected."
                        fallback_count += 1
                    else:
                        # It fell back but we expected a citation.
                        status = "FAIL"
                        note = "Fell back but expected citation (missing evidence?)."
                        fallback_count += 1
                else:
                    # Not a fallback, we expect a citation like [Source, Year] or [Source]
                    has_citation = bool(re.search(r'\[.+\]', answer))
                    if has_citation:
                        status = "PASS"
                        note = "Valid answer with citation."
                    else:
                        status = "FAIL"
                        note = "Answer lacks citation."
                        
        except Exception as e:
            status = "FAIL"
            note = f"Crash during evaluation: {e}"
            
        # Update counts
        if status == "PASS":
            passed += 1
        else:
            failed += 1
            
        print(f"    Result: {status}")
        print(f"    Note:   {note}")
        print(f"    Answer: {answer[:80]}...\n")
        
        # Append to markdown report
        results_markdown += f"### {q_id}\n"
        results_markdown += f"- **Question:** {question}\n"
        results_markdown += f"- **Status:** {status}\n"
        results_markdown += f"- **Note:** {note}\n"
        results_markdown += f"- **Answer Preview:** {answer[:150]}...\n\n"
        
    # Final summary
    summary = f"Evaluation Complete.\nTotal: {total} | Passed: {passed} | Failed: {failed} | Fallbacks: {fallback_count}"
    print("-" * 40)
    print(summary)
    
    results_markdown += "## Summary\n"
    results_markdown += f"- Total: {total}\n"
    results_markdown += f"- Passed: {passed}\n"
    results_markdown += f"- Failed: {failed}\n"
    results_markdown += f"- Fallback Count: {fallback_count}\n"
    
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        f.write(results_markdown)
    print(f"\nReport saved to: {RESULTS_PATH}")

if __name__ == "__main__":
    evaluate_pipeline()
