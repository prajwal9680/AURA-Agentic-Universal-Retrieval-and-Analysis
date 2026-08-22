# AURA — Agentic Universal Retrieval and Analysis
## System Architecture & Technical Specifications

## System Overview
AURA (Agentic Universal Retrieval and Analysis) is a multimodal retrieval-augmented generation (RAG) and visual knowledge graph system. It processes desktop visual streams into a searchable, relational knowledge graph with sub-200ms retrieval latencies, verifiable citations, and client-side security controls.

---

## 1. High-Level Architectural Topology

```
                                  ┌─────────────────────────────┐
                                  │   Desktop / OS Ingestion    │
                                  │  (Active Window + Hotkey)   │
                                  └──────────────┬──────────────┘
                                                 │
                                  ┌──────────────▼──────────────┐
                                  │   Zero-Trust Privacy Gate   │
                                  │ (Process Block + Secret OCR)│
                                  └──────────────┬──────────────┘
                                                 │
                       ┌─────────────────────────┴─────────────────────────┐
                       │                                                   │
        ┌──────────────▼──────────────┐                     ┌──────────────▼──────────────┐
        │   OCR Text Extraction Path  │                     │   Multimodal VLM Analysis   │
        │   (Tesseract / Text Engine) │                     │ (Gemini 2.5 / Verified Cache│
        └──────────────┬──────────────┘                     └──────────────┬──────────────┘
                       │                                                   │
                       └─────────────────────────┬─────────────────────────┘
                                                 │
                                  ┌──────────────▼──────────────┐
                                  │ Canonical Schema Formatter  │
                                  │  + Provenance Ledger Audit  │
                                  └──────────────┬──────────────┘
                                                 │
                       ┌─────────────────────────┴─────────────────────────┐
                       │                                                   │
        ┌──────────────▼──────────────┐                     ┌──────────────▼──────────────┐
        │    Dense Embedding Engine   │                     │  Relationship Graph Engine  │
        │ (all-MiniLM-L6-v2, 384-dim) │                     │  (6 Explainable Edge Types) │
        └──────────────┬──────────────┘                     └──────────────┬──────────────┘
                       │                                                   │
                       └─────────────────────────┬─────────────────────────┘
                                                 │
                                  ┌──────────────▼──────────────┐
                                  │ Dual-Engine Persistence:    │
                                  │ PostgreSQL 16 + pgvector    │
                                  │ (SQLite Fallback Engine)    │
                                  └──────────────┬──────────────┘
                                                 │
                        ┌────────────────────────┴────────────────────────┐
                        │                                                 │
         ┌──────────────▼──────────────┐                   ┌──────────────▼──────────────┐
         │ Two-Stage Information       │                   │ LangGraph Agentic RAG       │
         │ Retrieval (IR) Engine       │                   │ Orchestrator                │
         │ (pgvector ANN + Cross-Enc)  │                   │ (Planner/Critic Reflection) │
         └──────────────┬──────────────┘                   └──────────────┬──────────────┘
                        │                                                 │
                        └────────────────────────┬────────────────────────┘
                                                 │
                                  ┌──────────────▼──────────────┐
                                  │  Next.js Memory Hub &       │
                                  │  Constellation 3D UI        │
                                  └─────────────────────────────┘
```

---

## 2. Core Subsystems

### A. Dual-Engine Persistence (PostgreSQL + pgvector & SQLite Fallback)
- **Primary Engine**: PostgreSQL 16 with native `pgvector` extension.
- **Connection Management**: Async SQLAlchemy engine with connection pooling (`pool_size=20`, `max_overflow=10`, `pool_timeout=30s`).
- **Data Types**: `VectorType(384)` mapped dynamically to `pgvector.sqlalchemy.Vector(384)` on PostgreSQL and structured `Text` on SQLite fallback.
- **Composite Indexes**:
  - `ix_memories_status_deleted (processing_status, is_deleted)`
  - `ix_memories_cat_deleted (category, is_deleted)`
  - `ix_memories_created_deleted (created_at, is_deleted)`
  - `HNSW index on embedding` using cosine distance operator `<=>`.

### B. Two-Stage Information Retrieval (IR) System
1. **First-Stage Candidate Pool Union**:
   - Dense semantic vector search via HNSW / Cosine Similarity.
   - Lexical keyword matching via length-normalized BM25 with query-intent entity weighting.
   - Generates top-30 candidate union pool in $< 45\text{ms}$.
2. **Second-Stage Deep Cross-Encoder Reranking**:
   - Model: `cross-encoder/ms-marco-MiniLM-L-6-v2`.
   - Computes full cross-attention token interactions between query and candidate text + visual summary.
   - Applies visual format alignment boost (e.g. diagrams, charts, code syntax).
   - Produces calibrated relevance score $[0.0, 1.0]$.

### C. Multi-Signal Explainable Knowledge Graph
- **Edge Types**:
  - `SAME_ENTITY`: Shared named entities (devices, vendors, algorithms).
  - `SAME_PROJECT`: Shared repository or project cluster context.
  - `SAME_TOPIC`: High topic distribution overlap.
  - `SEMANTICALLY_RELATED`: Embedding cosine similarity $\ge 0.72$.
  - `TEMPORALLY_RELATED`: Captured within 2 hours in the same workspace.
  - `DERIVED_FROM`: Direct causal lineage (e.g. terminal traceback from Python script).
- **Explainability**: Every edge contains an explicit `evidence` string explaining why the connection exists.
- **Real-Time Streaming**: Incremental $O(k)$ edge insertion with Server-Sent Events (`/api/events/graph-stream`).

### D. LangGraph Agentic RAG Orchestration
- StateGraph workflow: `Planner -> Tool Gateway -> Cross-Encoder Reranker -> Critic Reflection Loop -> Synthesizer -> END`.
- Checkpoint persistence in database tables (`agent_checkpoints`).
- 7 Controlled Tools:
  1. `tool_search_memories`: Hybrid candidate search.
  2. `tool_get_memory`: Complete metadata, OCR, and visual object inspection.
  3. `tool_inspect_visual`: Fine-grained VLM grounding on charts, UI, and diagrams.
  4. `tool_find_related`: Multi-hop graph traversal.
  5. `tool_filter_memories`: Multi-criteria filtering.
  6. `tool_get_timeline`: Chronological workflow grouping.
  7. `tool_calculate`: Sandboxed mathematical evaluation.
