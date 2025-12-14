# LightRAG ATS - Applicant Tracking System

Production-ready Applicant Tracking System with dual-level retrieval combining vector search and knowledge graph queries.

## Features

- **Dual-Level Retrieval**: Combines vector similarity search (PostgreSQL/pgvector) with knowledge graph traversal (Neo4j)
- **5 Retrieval Modes**: naive, local, global, hybrid, mix - with automatic fallback
- **Resume Ingestion**: Supports PDF, DOCX, and TXT formats
- **Job-Based Analysis**: Shortlist candidates based on job descriptions
- **Conversational Chat**: AI-powered Q&A about candidates
- **Source Attribution**: Responses include context sources

## Tech Stack

| Component  | Technology                           |
| ---------- | ------------------------------------ |
| Backend    | FastAPI (Python 3.10+)               |
| RAG System | LightRAG                             |
| Vector DB  | PostgreSQL 16 + pgvector             |
| Graph DB   | Neo4j                                |
| LLM        | Ollama + Qwen 2.5:7b                 |
| Embeddings | BAAI/bge-m3 (1024 dim)               |
| Reranking  | cross-encoder/ms-marco-MiniLM-L-6-v2 |

## Quick Start

### 1. Prerequisites

- Docker & Docker Compose
- Python 3.10+
- Ollama (with `qwen2.5:7b` model)

### 2. Start Databases

```powershell
docker-compose up -d
```

This starts:

- PostgreSQL (port 5432) with pgvector
- Neo4j (ports 7474, 7687)

### 3. Install Dependencies

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Pull Ollama Model

```powershell
ollama pull qwen2.5:7b
```

### 5. Initialize Databases

```powershell
python scripts/init_db.py
```

### 6. Ingest Resumes

```powershell
# Place resume files in data/resumes/
python scripts/ingest_resumes.py --dir data/resumes --batch-size 5
```

### 7. Start API Server

```powershell
cd api
uvicorn main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

## API Endpoints

### Ingestion

| Endpoint        | Method | Description                 |
| --------------- | ------ | --------------------------- |
| `/ingest`       | POST   | Upload single resume        |
| `/ingest/batch` | POST   | Batch ingest from directory |

### Analysis

| Endpoint            | Method | Description                     |
| ------------------- | ------ | ------------------------------- |
| `/analyze`          | POST   | Analyze job and find candidates |
| `/analyze/{job_id}` | GET    | Get stored analysis             |

### Chat

| Endpoint      | Method | Description                                |
| ------------- | ------ | ------------------------------------------ |
| `/chat/job`   | POST   | Chat about job candidates (dual retrieval) |
| `/chat/query` | POST   | Direct query without job context           |
| `/chat/modes` | GET    | Get available retrieval modes              |

### Health

| Endpoint  | Method | Description         |
| --------- | ------ | ------------------- |
| `/health` | GET    | System health check |
| `/stats`  | GET    | System statistics   |

## Usage Example

```python
import httpx

# 1. Analyze a job
response = httpx.post("http://localhost:8000/analyze", json={
    "query": "Senior Python developer with 5+ years experience",
    "job_id": "job-001",
    "top_k": 20
})
print(response.json())

# 2. Chat about candidates
response = httpx.post("http://localhost:8000/chat/job", json={
    "job_id": "job-001",
    "message": "Who has the most Python experience?",
    "mode": "mix"
})
print(response.json()["response"])
```

## Retrieval Modes

| Mode   | Description        | Speed   | Use Case                   |
| ------ | ------------------ | ------- | -------------------------- |
| naive  | Vector search only | Fastest | General search             |
| local  | Entity-specific    | Fast    | "Who has skill X?"         |
| global | Relationship-based | Medium  | Pattern analysis           |
| hybrid | Local + Global     | Medium  | Complex queries            |
| mix    | Full dual-level    | Slower  | Best results (recommended) |

## Project Structure

```
├── docker-compose.yml      # Database containers
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
├── src/                   # Core modules
│   ├── config.py          # Configuration
│   ├── llm_adapter.py     # Ollama integration
│   ├── embedding.py       # BGE-M3 embeddings
│   ├── reranker.py        # Cross-encoder
│   ├── rag_config.py      # LightRAG setup
│   ├── dual_retrieval.py  # Dual retrieval logic
│   ├── resume_parser.py   # PDF/DOCX parsing
│   └── ingestion.py       # Batch ingestion
├── api/                   # FastAPI application
│   ├── main.py            # Entry point
│   ├── models.py          # Pydantic schemas
│   ├── middleware.py      # Logging, CORS
│   └── routes/            # Endpoint handlers
├── scripts/               # CLI tools
│   ├── init_db.py         # Database init
│   ├── ingest_resumes.py  # Batch ingestion
│   └── test_retrieval.py  # Mode testing
├── tests/                 # Test suite
└── data/resumes/          # Resume files
```

## Running Tests

```powershell
python -m pytest tests/ -v
```

## Troubleshooting

### Port Conflicts

```powershell
# Check ports
netstat -an | findstr "5432 7474 7687"
```

### Database Connection

```powershell
# Verify containers
docker-compose ps
docker-compose logs postgres
```

### Ollama Issues

```powershell
# Check model
ollama list
ollama pull qwen2.5:7b
```

## License

MIT License
