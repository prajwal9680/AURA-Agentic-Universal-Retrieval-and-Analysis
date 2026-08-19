# AURA (Agentic Universal Retrieval and Analysis) — Operational & CLI Reference Manual

This guide provides complete operational procedures, CLI workflows, API endpoints, and verification harnesses for running, testing, and developing **AURA (Agentic Universal Retrieval and Analysis)**.

---

## 1. Quick Start & Service Orchestration

### Launch Backend Server (FastAPI + PostgreSQL 16 / Dual Engine)
```powershell
& "c:\Users\prajw\Desktop\hackathon scryptic\backend\venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Launch Frontend Server (Next.js 15 App Router)
```powershell
cd "c:\Users\prajw\Desktop\hackathon scryptic\frontend"
npm run dev
```

### Verify Endpoints
- **Health Check**: `GET http://127.0.0.1:8000/api/health`
- **Telemetry & Stats**: `GET http://127.0.0.1:8000/api/stats`
- **Swagger Documentation**: `http://127.0.0.1:8000/api/docs`
- **Frontend Dashboard**: `http://localhost:3000`

---

## 2. Ingestion & Graph Enrichment

### Fast Batch Indexing (Indexes all 342 physical multimodal screenshots & 15,500+ edges)
```powershell
& "c:\Users\prajw\Desktop\hackathon scryptic\backend\venv\Scripts\python.exe" backend/seed/fast_batch_indexer.py
```

### Re-enrich Constellation Knowledge Graph Relationships
```powershell
& "c:\Users\prajw\Desktop\hackathon scryptic\backend\venv\Scripts\python.exe" backend/seed/enrich_relationships.py
```

---

## 3. Automated Testing & 4-Pillar Benchmark Suite

### Run 4-Pillar Empirical Benchmark Suite
```powershell
& "c:\Users\prajw\Desktop\hackathon scryptic\backend\venv\Scripts\python.exe" backend/tests/run_all_benchmarks.py
```

### Run Unit Test Suite
```powershell
& "c:\Users\prajw\Desktop\hackathon scryptic\backend\venv\Scripts\python.exe" -m pytest backend/tests/ -v
```

---

## 4. API Reference Summary

| Endpoint | Method | Description |
|:---|:---:|:---|
| `/api/memories/upload` | POST | Upload and process screenshots through 8-stage pipeline |
| `/api/memories` | GET | List indexed memories with pagination, category & constellation filters |
| `/api/memories/{id}` | GET | Get full memory object and AI multimodal understanding |
| `/api/memories/{id}/thumbnail` | GET | Stream visual thumbnail |
| `/api/memories/{id}/redact` | POST | Permanently redact sensitive patterns |
| `/api/memories/{id}/lock` | POST | Lock/unlock memory from search index |
| `/api/search` | POST | Hybrid semantic + lexical BM25 search with Cross-Encoder reranking |
| `/api/investigate` | POST | Multi-step LangGraph agentic investigation orchestrator |
| `/api/constellation` | GET | Graph topology (350 nodes & 2000 edges) for 3D force visualization |
| `/api/timeline` | GET | Chronological grouping by calendar days |
| `/api/shield/scan` | POST | Direct text/OCR regex scanner for secrets and PII |
| `/api/actions/extract-expense` | POST | Structured expense extractor for receipts/invoices |
| `/api/actions/debug` | POST | Code explainer and error debugger |
| `/api/actions/summarize` | POST | Research paper & document summarizer |
