# AURA (Agentic Universal Retrieval and Analysis) — Operational & CLI Reference Manual

This manual provides operational procedures, CLI workflows, service health checks, and API reference contracts for running and evaluating **AURA (Agentic Universal Retrieval and Analysis)**.

---

## 1. Service Orchestration

### Prerequisites
- Python 3.11+ with virtual environment activated
- Node.js 20+ / npm 10+
- PostgreSQL 16 with `pgvector` extension (or local dual-engine SQLite fallback)

### Launch Backend Service (FastAPI + Async SQLAlchemy)
```bash
# From repository root
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Launch Frontend Web Application (Next.js 16 / Turbopack)
```bash
# From repository root
cd frontend
npm install
npm run dev
```

### Health Probes & Telemetry
| Interface | Protocol / URI | Expected Output |
| :--- | :--- | :--- |
| **Liveness & Readiness** | `GET http://127.0.0.1:8000/api/health` | `{"status": "healthy", "service": "AURA", "database": "PostgreSQL 16 / pgvector (Active)"}` |
| **System Diagnostics** | `GET http://127.0.0.1:8000/api/system/diagnostics` | Provider status, memory count, graph edges, latency metrics |
| **Interactive API Specs** | `GET http://127.0.0.1:8000/api/docs` | OpenAPI 3.1 / Swagger UI |
| **Web Dashboard** | `http://localhost:3000` | Full tactile frontend interface |

---

## 2. Ingestion & Graph Seeding

### Execute Batch Ingestion Pipeline (342 Multimodal Artifacts)
```bash
# Ingests image corpus, executes OCR + VLM cascade, indexes 384-d vectors, and constructs graph
python backend/seed/fast_batch_indexer.py
```

### Recompute Knowledge Graph Relationships
```bash
# Executes 5-signal affinity algorithm across indexed artifacts to build 15,500+ edges
python backend/seed/enrich_relationships.py
```

---

## 3. Automated Test Suite & Empirical Benchmarks

### Execute 4-Pillar Empirical Benchmark Suite
```bash
python backend/tests/run_all_benchmarks.py
```
*Outputs quantified metrics to `docs/benchmark_results.json`.*

### Execute Pytest Unit & Integration Test Suite
```bash
cd backend
pytest tests/ -v --tb=short
```

---

## 4. REST API Endpoint Contract

| Endpoint | Method | Input Payload | Response Structure | Description |
| :--- | :---: | :--- | :--- | :--- |
| `/api/health` | `GET` | None | `{status, service, version, database}` | Health probe |
| `/api/ready` | `GET` | None | `{status, database}` | Readiness probe verifying DB connectivity |
| `/api/stats` | `GET` | None | `{total_memories, total_relationships, sensitive_count}` | Aggregate corpus metrics |
| `/api/memories` | `GET` | Query params: `page`, `per_page`, `category`, `sort_by` | `{memories: [...], total, page, pages}` | Paginated memory gallery |
| `/api/memories/{id}` | `GET` | Path param: `id` | Full serialized `Memory` object | Single memory metadata & visual details |
| `/api/memories/upload` | `POST` | `multipart/form-data` (file) | `{id, status, message}` | Queues screenshot for asynchronous processing |
| `/api/search` | `POST` | `{"query": str, "top_k": int}` | `{query, total, confidence, results: [...]}` | Two-stage hybrid search (Vector + BM25 + Rerank) |
| `/api/investigate` | `POST` | `{"query": str, "deep": bool}` | `{investigation_id, answer, key_findings, plan, results, evidence_trace}` | LangGraph multi-hop agentic investigation |
| `/api/constellation` | `GET` | Query param: `category` (optional) | `{constellations: [...], nodes: [...], edges: [...]}` | Graph topology for 3D force visualization |
| `/api/timeline` | `GET` | None | `{timeline: [{date, memories, count}], total_days}` | Chronological timeline grouping |
| `/api/shield/scan` | `POST` | `{"text": str}` | `{sensitivity_level, findings: [...], confidence}` | Deterministic regex & PII detection |
| `/api/actions/{action}` | `POST` | `{"memory_id": str}` | `{action, status, result: {...}}` | Contextual AI actions (`extract-expense`, `debug_code`, `summarize`) |
| `/api/desktop/status` | `GET` | None | `{status, config: {...}, metrics: {...}}` | OS companion status and exclusion list |

