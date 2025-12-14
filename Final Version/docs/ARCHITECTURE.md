# LightRAG ATS - Inner Architecture

## 🧠 Techniques & Algorithms Used

### Stage 1: Resume Ingestion

| Step                    | Technique                   | Implementation                                         |
| ----------------------- | --------------------------- | ------------------------------------------------------ |
| **Text Extraction**     | Rule-based parsing          | `PyMuPDF` (PDF), `python-docx` (DOCX)                  |
| **Chunking**            | Token-based splitting       | Split at ~1200 tokens with 100 overlap                 |
| **Embedding**           | Dense Vector Encoding       | `BAAI/bge-m3` → 1024-dimensional vectors               |
| **Entity Extraction**   | LLM Prompting               | Ollama `qwen2.5:7b` extracts: skills, roles, companies |
| **Relation Extraction** | LLM Prompting               | "Person → WORKED_AT → Company" triples                 |
| **Storage**             | Vector DB + Knowledge Graph | NanoVectorDB + NetworkX                                |

---

### Stage 2: Candidate Filtering (`/analyze`)

```
┌─────────────────────────────────────────────────────────────────┐
│                    VECTOR SIMILARITY SEARCH                      │
├─────────────────────────────────────────────────────────────────┤
│  Technique: Cosine Similarity on Dense Embeddings                │
│                                                                  │
│  1. Job Description → Embed with bge-m3 → Query Vector (1024d)  │
│  2. Compare with stored resume chunks using cosine similarity    │
│  3. Return top-k most similar chunks                             │
│                                                                  │
│  Formula: similarity = cos(query_vec, doc_vec)                   │
│           = (q · d) / (||q|| × ||d||)                           │
└─────────────────────────────────────────────────────────────────┘
```

**Algorithm:** Approximate Nearest Neighbor (ANN) via NanoVectorDB
**Metric:** Cosine similarity (range: -1 to 1, higher = more similar)

---

### Stage 3: Chat Query (`/chat/query`)

```
┌─────────────────────────────────────────────────────────────────┐
│                 RETRIEVAL-AUGMENTED GENERATION (RAG)            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     │
│  │   RETRIEVAL  │ ──→ │   CONTEXT    │ ──→ │  GENERATION  │     │
│  │              │     │  ASSEMBLY    │     │              │     │
│  └──────────────┘     └──────────────┘     └──────────────┘     │
│                                                                  │
│  Mode: naive   → Vector search only (fastest)                   │
│  Mode: local   → Entity-specific from Knowledge Graph           │
│  Mode: global  → Relationship patterns from KG                  │
│  Mode: hybrid  → local + global combined                        │
│  Mode: mix     → Vector + Graph (dual-level, recommended)       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Retrieval Modes Explained:**

| Mode       | What It Does                                   | Best For                        |
| ---------- | ---------------------------------------------- | ------------------------------- |
| **naive**  | Pure vector similarity search                  | Fast lookups, simple queries    |
| **local**  | Finds specific entities (skills, people) in KG | "Who knows Python?"             |
| **global** | Analyzes relationship patterns                 | "What companies work with AWS?" |
| **hybrid** | Combines local + global                        | Complex analysis                |
| **mix**    | Vector results + Graph context                 | Best overall (default)          |

---

### Stage 4: Response Generation

```
┌─────────────────────────────────────────────────────────────────┐
│                    LLM RESPONSE GENERATION                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Model: Ollama qwen2.5:7b (7 billion parameters)                │
│  Type: Instruction-tuned decoder-only transformer               │
│                                                                  │
│  Prompt Structure:                                               │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ SYSTEM: You are an ATS assistant...                       │  │
│  │                                                            │  │
│  │ CONTEXT: [Retrieved chunks + KG entities/relations]       │  │
│  │                                                            │  │
│  │ USER: {query}                                              │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  Output: Natural language answer grounded in context            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Summary: Techniques by Stage

| Stage                 | Primary Technique     | Model/Algorithm        |
| --------------------- | --------------------- | ---------------------- |
| **Ingestion**         | Chunking + Embedding  | bge-m3 (1024d vectors) |
| **Entity Extraction** | LLM Prompting         | qwen2.5:7b             |
| **Filtering**         | Vector Similarity     | Cosine, ANN search     |
| **Graph Retrieval**   | Knowledge Graph Query | NetworkX traversal     |
| **Response**          | RAG + LLM Generation  | qwen2.5:7b             |

---

├── api/ # FastAPI Application Layer
│ ├── main.py # App entry, lifespan, health endpoints
│ ├── models.py # Pydantic request/response models
│ ├── middleware.py # Logging, error handling
│ └── routes/
│ ├── analyze.py # POST /analyze - candidate ranking
│ ├── chat.py # POST /chat/_ - RAG queries
│ └── ingest.py # POST /ingest - resume upload
│
├── src/ # Core Business Logic
│ ├── config.py # Settings from .env
│ ├── rag*config.py # LightRAG initialization
│ ├── llm_adapter.py # Ollama API wrapper
│ ├── embedding.py # BAAI/bge-m3 embeddings
│ ├── ingestion.py # Resume processing pipeline
│ ├── resume_parser.py # PDF/DOCX/TXT extraction
│ ├── dual_retrieval.py # Vector + Graph retrieval
│ └── reranker.py # Cross-encoder reranking
│
├── rag_storage/ # Persisted Data (JSON files)
│ ├── vdb_entities.json # Entity embeddings
│ ├── vdb_relationships.json # Relation embeddings
│ ├── vdb_chunks.json # Document chunk embeddings
│ ├── kv_store*_.json # Key-value stores
│ └── graph\_\*.graphml # NetworkX graph
│
└── scripts/ # CLI Tools
├── ingest_resumes.py # Batch ingestion
└── test_query.py # Query testing

````

---

## Component Architecture

```mermaid
classDiagram
    class FastAPI {
        +lifespan()
        +health_check()
        +get_stats()
    }

    class AnalyzeRouter {
        +analyze_job(request)
        +get_job_analysis(job_id)
        -parse_candidates_from_response()
    }

    class ChatRouter {
        +chat_about_job(request)
        +direct_query(request)
    }

    class RAGManager {
        -_rag: LightRAG
        -_initialized: bool
        +initialize()
        +close()
        +rag: LightRAG
    }

    class LightRAG {
        +ainsert(text)
        +aquery(query, param)
        +initialize_storages()
        -full_docs
        -text_chunks
        -entities_vdb
        -relationships_vdb
        -chunk_entity_relation_graph
    }

    class OllamaAdapter {
        +generate(prompt)
        +check_health()
        -_client: httpx.AsyncClient
    }

    class EmbeddingModel {
        +encode(texts)
        +aencode(texts)
        -model: SentenceTransformer
    }

    class DualLevelRetrieval {
        +retrieve(query, mode)
        -_vector_search()
        -_graph_search()
    }

    FastAPI --> AnalyzeRouter
    FastAPI --> ChatRouter
    AnalyzeRouter --> RAGManager
    ChatRouter --> RAGManager
    ChatRouter --> DualLevelRetrieval
    RAGManager --> LightRAG
    LightRAG --> OllamaAdapter
    LightRAG --> EmbeddingModel
    DualLevelRetrieval --> LightRAG
````

---

## Data Flow Inside LightRAG

```mermaid
flowchart LR
    subgraph ainsert["ainsert() - Document Ingestion"]
        A1[Input Text] --> A2[Chunking<br/>~1200 tokens]
        A2 --> A3[Embed Chunks]
        A3 --> A4[Store in VectorDB]
        A2 --> A5[LLM: Extract Entities]
        A5 --> A6[Build Knowledge Graph]
    end

    subgraph aquery["aquery() - Retrieval"]
        Q1[Query] --> Q2[Embed Query]
        Q2 --> Q3{Mode?}
        Q3 -->|naive| Q4[Vector Search Only]
        Q3 -->|local| Q5[Entity Retrieval]
        Q3 -->|global| Q6[Relationship Retrieval]
        Q3 -->|mix| Q7[Vector + Graph]
        Q4 & Q5 & Q6 & Q7 --> Q8[Build Context]
        Q8 --> Q9[LLM Generate Response]
    end
```

---

## Key Classes

### `RAGManager` (src/rag_config.py)

```python
class RAGManager:
    """Singleton managing LightRAG lifecycle"""

    async def initialize(self):
        # 1. Create LightRAG instance
        # 2. Configure LLM (Ollama)
        # 3. Configure embeddings (bge-m3)
        # 4. Call initialize_storages() ← CRITICAL!

    @property
    def rag(self) -> LightRAG:
        # Returns initialized LightRAG instance
```

### `OllamaAdapter` (src/llm_adapter.py)

```python
class OllamaAdapter:
    """Async wrapper for Ollama API"""

    async def generate(prompt, system_prompt, **kwargs):
        # POST to http://localhost:11434/api/chat
        # Returns: Generated text
```

### `DualLevelRetrieval` (src/dual_retrieval.py)

```python
class DualLevelRetrieval:
    """Combines vector and graph retrieval"""

    async def retrieve(query, candidates, mode):
        # 1. Try requested mode
        # 2. Fallback to simpler modes on error
        # 3. Inject candidate context
        # 4. Return LLM response
```

---

## Storage Internals

| File                                  | Contents                  | Format                          |
| ------------------------------------- | ------------------------- | ------------------------------- |
| `vdb_entities.json`                   | Entity embeddings         | `{id: [1024-dim vector]}`       |
| `vdb_chunks.json`                     | Document chunk embeddings | `{chunk_id: [vector]}`          |
| `kv_store_full_docs.json`             | Full document text        | `{doc_id: {content: "..."}}`    |
| `kv_store_text_chunks.json`           | Chunked text              | `{chunk_id: {content, tokens}}` |
| `graph_chunk_entity_relation.graphml` | Knowledge graph           | NetworkX GraphML                |

---

## Request Processing

### POST /analyze

```
Request → analyze.py
    ↓
get_rag() → RAGManager.rag
    ↓
rag.aquery(job_description, mode="naive")
    ↓
LightRAG:
    1. Embed query
    2. Search vdb_chunks.json
    3. Return top-k similar chunks
    ↓
parse_candidates_from_response()
    ↓
Response: [{name, score, highlights}]
```

### POST /chat/query

```
Request → chat.py
    ↓
chat_with_dual_retrieval()
    ↓
DualLevelRetrieval.retrieve(mode="mix")
    ↓
LightRAG.aquery() with fallback chain:
    mix → hybrid → local → naive
    ↓
Response: {response, mode_used, sources}
```
