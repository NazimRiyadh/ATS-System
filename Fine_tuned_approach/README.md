# AI-Powered ATS Implementation 🚀

A next-generation Applicant Tracking System (ATS) powered by **LightRAG**, **PostgreSQL (pgvector)**, **Neo4j**, and **Local LLMs**. This system goes beyond keyword matching to understand candidate profiles deeply using Knowledge Graphs and Vector Retrieval with Cross-Encoder Re-ranking.

## 🌟 Key Features

- **Hybrid Retrieval**: Combines **Vector Search** (Semantic Similarity) with **Knowledge Graph** interactions (Deep Relations).
- **High Precision**: Uses a **Cross-Encoder Re-ranker** to filter unrelated candidates (Threshold: 0.15).
- **Auto-Ingestion**: Automatically indexes resumes upon upload.
- **Explainable AI**: Provides reasoning for why a candidate was selected or rejected.
- **Local Privacy**: Runs fully local with **Ollama** (LLM) and **Local Embeddings** (BAAI/bge-m3).

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI
- **RAG Engine**: [LightRAG-HKU](https://github.com/HKUDS/LightRAG)
- **Vector DB**: PostgreSQL + `pgvector`
- **Graph DB**: Neo4j
- **LLM**: Qwen 2.5 (via Ollama)
- **Embeddings**: BAAI/bge-m3
- **Reranker**: Cross-Encoder (`ms-marco-MiniLM-L-6-v2`)

## ⚡ Prerequisites

1.  **Python 3.10+**
2.  **PostgreSQL 16+** (running on port `5433` or mapped in `.env`)
    - Extension enabled: `CREATE EXTENSION vector;`
3.  **Neo4j Desktop/Server** (running on port `7687`)
4.  **Ollama** (running locally)
    - Pull model: `ollama pull qwen2.5:7b`

## 🚀 Installation

1.  **Clone & Install Dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure Environment**:
    Copy `.env.example` to `.env` and update credentials:

    ```ini
    POSTGRES_URI=postgresql+asyncpg://postgres:password@localhost:5433/postgres
    NEO4J_URI=bolt://localhost:7687
    NEO4J_USERNAME=neo4j
    NEO4J_PASSWORD=password
    ```

3.  **Start the API Server**:
    ```bash
    uvicorn main:app --reload
    ```
    _API running at: `http://localhost:8000`_

## 📚 Usage Guide

### 1. Ingest Resumes

Upload resumes (PDF/TXT) via the API to automatically index them.

- **POST** `/ingest` (multipart/form-data)

### 2. Search Candidates

Run a job description query to find the best 20 matches.

- **POST** `/analyze_job`
  ```json
  {
    "job_id": "JOB_001",
    "query": "Senior DevOps Engineer with Kubernetes and AWS",
    "top_k": 20
  }
  ```

### 3. Ask Questions

Chat with the AI about the shortlisted candidates.

- **POST** `/chat_job`
  ```json
  {
    "job_id": "JOB_001",
    "message": "Which candidate has the most leadership experience?"
  }
  ```

## 📂 Project Structure

- `main.py`: Main FastAPI application.
- `src/`: Core logic (RAG engine, Embeddings, Reranker).
- `resumes/`: Directory where uploaded resumes are stored.
- `batch_ingest.py`: Utility to bulk ingest existing files.
- `reset_full_system.py`: **CAUTION**. Wipes Database to start fresh.

## 🛡️ Reranking Logic

The system uses a 2-stage retrieval:

1.  **Vector Search**: Retrieves top `K` candidates.
2.  **Re-ranker**: Scores candidates (0-1) and filters out those below `RERANK_THRESHOLD` (Configurable in `src/config.py`).

## 🧠 Hybrid Architecture Explained

Why use both **Vector DB** and **Knowledge Graph**?

- **Vector DB (Speed)**: Used for the initial "Broad Search". It quickly finds candidates who are _semantically similar_ to the job description (e.g., "Python" ≈ "Django").
- **Knowledge Graph (Depth)**: Used for **Ingestion & Reasoning**.
  - **Ingestion**: Extracts entities and maps relationships (e.g., `(Candidate)-[:HAS_SKILL]->(Kubernetes)`).
  - **Context**: Provides structured data to the LLM, ensuring it understands _how_ a candidate knows a skill (e.g., used in "Project X" vs just listed in "Skills").
