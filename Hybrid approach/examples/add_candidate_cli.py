import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ats_pipeline import get_pipeline

def main():
    print("==================================================")
    print("   ATS CANDIDATE INGESTION CLI")
    print("==================================================")
    print("Paste the resume text below. Press Ctrl+Z (Windows) or Ctrl+D (Linux/Mac) on a new line to save.")
    print("--------------------------------------------------")
    
    # Read multi-line input
    try:
        resume_text = sys.stdin.read()
    except KeyboardInterrupt:
        return

    if not resume_text.strip():
        print("\n❌ No text provided. Exiting.")
        return

    print("\n--------------------------------------------------")
    print("⏳ Processing candidate... (Parsing & Embedding)")
    
    try:
        pipeline = get_pipeline()
        candidate_id = pipeline.ingest_candidate(resume_text)
        print(f"✅ Candidate successfully added!")
        print(f"🆔 Candidate ID: {candidate_id}")
    except Exception as e:
        print(f"\n❌ Error adding candidate: {e}")

if __name__ == "__main__":
    main()
