# ATS System Integration Guide

## Overview

This document outlines how the **External Recruiter System** (or any other client) should integrate with the **AI-Powered ATS Backend**.

The ATS Backend exposes a RESTful API (FastAPI) that handles:

1.  **Ingestion**: Receiving resume files directly from the Recruiter System.
2.  **Analysis**: Ranking candidates for a specific Job Description.
3.  **Chat**: Answering specific questions about the ranked candidates.

---

## Base Configuration

- **Base URL**: `http://<HOST_IP>:8000` (Default connection)
- **Protocol**: HTTP / HTTPS (if configured with reverse proxy)
- **Authentication**: _Currently Open/Internal_ (Ensure network security or add API Key middleware if exposed public).

---

## 1. Resume Ingestion (Integration Point)

**Endpoint**: `POST /ingest`

**Purpose**:
Your system should call this endpoint **immediately** when a recruiter uploads a resume. This triggers the AI to index the file instantly, making it searchable within seconds.

**Request:**

- **Content-Type**: `multipart/form-data`
- **Body**:
  - `file`: The binary file object (PDF, TXT, DOCX).

**Example (Python/Requests):**

```python
import requests

url = "http://localhost:8000/ingest"
files = {'file': open('John_Doe_Resume.pdf', 'rb')}

response = requests.post(url, files=files)
print(response.json())
```

**Response (Success - 200 OK):**

```json
{
  "message": "Saved and Ingested John_Doe_Resume.pdf",
  "path": "./resumes/John_Doe_Resume.pdf"
}
```

_Note: The system acts synchronously. It returns only after the AI has successfully indexed the document._

---

## 2. Job Analysis (Search Trigger)

**Endpoint**: `POST /analyze_job`

**Purpose**:
Call this when the recruiter wants to screen candidates for a specific Job Description (JD).

**Request:**

- **Content-Type**: `application/json`
- **Body**:

```json
{
  "job_id": "JOB_12345",
  "query": "Looking for a Senior Python Developer with Kubernetes and AWS experience...",
  "top_k": 20
}
```

- `top_k`: Number of candidates to consider (Default: 20).

**Response (Success):**

```json
{
  "status": "completed",
  "job_id": "JOB_12345",
  "candidates_found": 5,
  "candidates_preview": ["John_Doe.txt", "Jane_Smith.pdf", ...],
  "message": "Graph built successfully. You can now use /chat_job."
}
```

- `candidates_found`: Number of candidates who passed the AI Filter (Re-ranker). If 0, the query might be too strict.

---

## 3. Chat / Querying (Reasoning)

**Endpoint**: `POST /chat_job`

**Purpose**:
Ask questions about the _specific candidates_ identified in step 2.

**Request:**

- **Content-Type**: `application/json`
- **Body**:

```json
{
  "job_id": "JOB_12345",
  "message": "Who has the best experience with AWS Lambda and why?"
}
```

**Response:**

```json
{
  "response": "Based on the profiles, **Leonard** is the strongest candidate because..."
}
```

---

## Workflow Summary for Backend Engineer

1.  **On Resume Upload** (Recruiter Portal):

    - Trigger `POST /ingest` with the file.
    - Wait for "200 OK" to confirm AI indexing.

2.  **On "Find Candidates" Click**:

    - Send the Job Description to `POST /analyze_job`.
    - Display the number of `candidates_found` to the user.

3.  **On "Ask AI"**:
    - Send user question to `POST /chat_job` using the same `job_id`.
    - Display the `response` text.

## Technical Constraints

- **Supported Formats**: `.txt`, `.pdf` (Text extraction enabled).
- **Latency**:
  - Ingest: ~2-5 seconds per file. //differs from original
  - Analyze: ~2-10 seconds (depending on database size).
  - Chat: ~3-10 seconds (LLM Inference).
