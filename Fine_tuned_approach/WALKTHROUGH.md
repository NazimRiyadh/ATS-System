# System Walkthrough & Demo

This document demonstrates the capabilities of the **Retrieve-Rank-Reason** ATS system. This 2-Stage architecture balances speed (Vector Search) with reasoning depth (Graph RAG).

## Architecture Overview

1.  **Stage 1: Fast Filter (Vector Search)**

    - **Goal**: Reduce 500+ candidates to Top 20.
    - **Method**: Uses `sentence-transformers` text embeddings + HyDE to matching the Job Description.
    - **Logic**: High-speed retrieval to discard irrelevant candidates.

2.  **Stage 2: Deep Index (Ephemeral Graphs)**

    - **Goal**: Build a knowledge graph just for the "Shortlist".
    - **Method**: Creates a temporary `LightRAG` instance (`rag_storage/job_{id}`) for the Top 20 candidates.
    - **Logic**: Extracts detailed relationships (Skills, Experience, Location) specifically for these candidates.

3.  **Stage 3: Reasoning (Chat)**
    - **Goal**: Answer complex recruiter questions.
    - **Method**: Queries the ephemeral graph.
    - **Example**: "Compare candidate A and B on their leadership experience."

## 🚀 Usage

### 1. Start the API

The system now uses **FastAPI**.

```bash
uvicorn main:app --reload
```

_Note_: Ensure `python-multipart` is installed (`pip install python-multipart`).

### 2. Rank Candidates (Stage 1 & 2)

Trigger the analysis for a specific job.

**Endpoint**: `POST /analyze_job`

```bash
curl -X POST "http://localhost:8000/analyze_job" \
     -H "Content-Type: application/json" \
     -d '{"query": "Senior Python Backend Engineer", "job_id": "job_python_01"}'
```

**Response**:

```json
{
  "status": "completed",
  "job_id": "job_python_01",
  "candidates_found": 15,
  "candidates_preview": ["resume_john.pdf", "resume_jane.pdf"],
  "message": "Graph built successfully. You can now use /chat_job."
}
```

### 3. Chat with the Shortlist (Stage 3)

Ask complex questions about the screened candidates.

**Endpoint**: `POST /chat_job`

```bash
curl -X POST "http://localhost:8000/chat_job" \
     -H "Content-Type: application/json" \
     -d '{"job_id": "job_python_01", "message": "Which candidate has the most relevant cloud experience?"}'
```

**Response**:

```json
{
  "response": "John Doe has 5 years of AWS experience including Lambda and EC2..."
}
```
