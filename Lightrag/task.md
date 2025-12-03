# Implementation Roadmap: Flask API & Infrastructure

- [ ] **Phase 1: Flask API Development**
    - [ ] Install Flask and dependencies (`flask`, `flask-cors`). <!-- id: 0 -->
    - [ ] Create `app.py` with basic structure and error handling. <!-- id: 1 -->
    - [ ] Implement `POST /rank` endpoint to wrap `rank_candidates` logic. <!-- id: 2 -->
    - [ ] Implement `POST /ingest` endpoint for resume uploading. <!-- id: 3 -->
    - [ ] Test API endpoints locally. <!-- id: 4 -->

- [ ] **Phase 2: Local LLM Integration (Ollama)**
    - [ ] Configure `src/config.py` to support Local LLM (e.g., Qwen2.5 via Ollama). <!-- id: 5 -->
    - [ ] Update `src/rag_engine.py` to switch between OpenAI/Local based on config. <!-- id: 6 -->
    - [ ] Verify `src/query_processor.py` works with Local LLM. <!-- id: 7 -->

- [ ] **Phase 3: Containerization (Docker)**
    - [ ] Create `Dockerfile` for the Flask application. <!-- id: 8 -->
    - [ ] Create `docker-compose.yml` to orchestrate App, Neo4j, and Ollama. <!-- id: 9 -->
    - [ ] Verify container communication and persistence. <!-- id: 10 -->

- [ ] **Phase 4: Kubernetes (K8s) Deployment**
    - [ ] Create `k8s/deployment.yaml` for the application. <!-- id: 11 -->
    - [ ] Create `k8s/service.yaml` for exposing the API. <!-- id: 12 -->
    - [ ] Create `k8s/neo4j-deployment.yaml` (or use Helm chart). <!-- id: 13 -->

- [ ] **Phase 5: Performance Testing**
    - [ ] Benchmark Local LLM latency vs. OpenAI. <!-- id: 14 -->
    - [ ] Load test the Flask API. <!-- id: 15 -->
