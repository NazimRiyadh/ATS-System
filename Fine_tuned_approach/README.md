# LightRAG ATS (Applicant Tracking System)

A powerful, local-first Applicant Tracking System built with **LightRAG**, **Neo4j**, and **Local LLMs**. This system ingests resumes, builds a knowledge graph, and allows for semantic search and ranking of candidates based on complex queries.
    *   GPU: Optional but recommended for faster ingestion/inference.

## 📦 Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd lightRAG
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment:**
    *   Copy `.env.example` to `.env` (if available) or create a `.env` file.
    *   Set your API keys (if using OpenAI) and Neo4j credentials:
        ```env
        OPENAI_API_KEY=sk-...
        NEO4J_URI=bolt://localhost:7687
        NEO4J_USERNAME=neo4j
        NEO4J_PASSWORD=your_password
        ```

4.  **Verify Configuration:**
    *   Check `src/config.py` to ensure `EMBEDDING_MODEL` and `RERANK_MODEL` are set correctly.

## 🏃 Usage

### 1. Ingest Resumes
Place your resume text files in the `resumes/` directory.
```bash
python batch_ingest.py
```
This will:
*   Read all `.txt` files in `resumes/`.
*   Generate embeddings and graph nodes.
*   Store data in Neo4j and local vector indices.

### 2. Rank Candidates
Run a query to find the best candidates.
```bash
python rank_candidates.py --query "Machine Learning Engineer with Python and TensorFlow"
```
*   **--query**: The job description or search terms.
*   **--top_k**: (Optional) Number of results to return (default: 5).

## 🧠 Models Used

| Component | Model | Type | Source |
| :--- | :--- | :--- | :--- |
| **Embeddings** | `BAAI/bge-m3` | Local | HuggingFace |
| **Reranking** | `BAAI/bge-reranker-v2-m3` | Local | HuggingFace |
| **LLM** | `gpt-4o-mini` (or Local Qwen) | API/Local | OpenAI/Ollama |

## 📂 Project Structure

*   `src/`: Core source code.
    *   `rag_engine.py`: Main LightRAG integration.
    *   `embeddings.py`: Local embedding logic.
    *   `rerank.py`: Local reranking logic.
    *   `config.py`: Configuration settings.
*   `resumes/`: Directory for input resume files.
*   `rag_storage/`: Local storage for vector indices and KV stores.