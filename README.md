# AURA: Agentic Universal Retrieval and Analysis

**Architecture**: PostgreSQL 16 + pgvector · LangGraph StateGraph · Cross-Encoder Reranker · Zero-Trust Privacy Gate · Multi-Signal Knowledge Graph · Gemini Vision VLM · Next.js 16 UI

---

## Technical Overview

AURA (Agentic Universal Retrieval and Analysis) is a multimodal retrieval-augmented generation (RAG) and visual knowledge graph system for desktop environments. It indexes desktop visual streams into a structured, searchable knowledge graph with sub-200ms retrieval latencies, calibrated citations, and client-side privacy controls.

Standard desktop search engines rely primarily on optical character recognition (OCR), which indexes only raw text and fails on non-textual visual structures such as architecture diagrams, loss curves, schematic workflows, and UI layouts. AURA addresses this with a dual-path pipeline:
1. **Multimodal VLM Path**: Extracts structural visual features (document format, visual entities, layout topology).
2. **Optical Text Path**: Extracts and normalizes lexical tokens.
3. **Dense Vector Space**: Synthesizes visual descriptors and OCR tokens into unified 384-dimensional dense vectors indexed via pgvector HNSW graphs.
4. **Agentic RAG Engine**: Executes multi-hop query decomposition, dynamic image candidate inspection, graph traversal, and reflection-based answer synthesis via LangGraph.

---

## System Architecture

```
 ┌────────────────────────────────────────────────────────────────────────────────┐
 │                       OS-Level Ingestion & Context Capture                     │
 │          (PrtScn / Win+Shift+S / Hotkey · Active Window · Clipboard)           │
 └───────────────────────────────────────┬────────────────────────────────────────┘
                                         │
 ┌───────────────────────────────────────▼────────────────────────────────────────┐
 │                      Zero-Trust Privacy Gate (AURA Shield)                     │
 │     Client Process Filtering · Regex Credential Redaction · Sandbox Isolation  │
 └───────────────────────────────────────┬────────────────────────────────────────┘
                                         │
            ┌────────────────────────────┴────────────────────────────┐
            │                                                         │
 ┌──────────▼───────────────┐                             ┌───────────▼───────────────┐
 │   Lexical OCR Pipeline   │                             │  Multimodal Vision (VLM)  │
 │  EasyOCR (CRAFT + ResNet)│                             │ Gemini Flash Vision Model │
 │ (Tokens, Raw Text, BBox) │                             │(Layout, Objects, Entities)│
 └──────────┬───────────────┘                             └───────────┬───────────────┘
            │                                                         │
            └────────────────────────────┬────────────────────────────┘
                                         │
 ┌───────────────────────────────────────▼────────────────────────────────────────┐
 │                   Canonical Schema & Provenance Ledger Audit                   │
 │          Confidence Scores · Source Field Tracking · Sensitivity Level         │
 └───────────────────────────────────────┬────────────────────────────────────────┘
                                         │
            ┌────────────────────────────┴────────────────────────────┐
            │                                                         │
 ┌──────────▼───────────────┐                             ┌───────────▼───────────────┐
 │  Dense Vector Embedding  │                             │ Multi-Signal Graph Engine │
 │ all-MiniLM-L6-v2 (384-d) │                             │  15,500+ Semantic / Causal│
 │  HNSW Index (pgvector)   │                             │    Typed Affinity Edges   │
 └──────────┬───────────────┘                             └───────────┬───────────────┘
            │                                                         │
            └────────────────────────────┬────────────────────────────┘
                                         │
 ┌───────────────────────────────────────▼────────────────────────────────────────┐
 │             Unified Relational & Vector Persistence Layer                      │
 │        PostgreSQL 16 + pgvector (HNSW) · SQLite + NumPy SIMD Fallback          │
 └───────────────────────────────────────┬────────────────────────────────────────┘
                                         │
            ┌────────────────────────────┴────────────────────────────┐
            │                                                         │
 ┌──────────▼─────────────────────────────┐       ┌───────────────────▼───────────────┐
 │ Two-Stage Hybrid Retrieval (186ms P50) │       │   Multi-Hop LangGraph Agent RAG   │
 │   Stage 1: pgvector ANN + BM25 Lexical │       │   Planner -> Tool Gateway ->      │
 │   Stage 2: Cross-Encoder (ms-marco)    │       │   Critic Reflection -> Synthesis  │
 └──────────┬─────────────────────────────┘       └───────────────────┬───────────────┘
            │                                                         │
            └────────────────────────────┬────────────────────────────┘
                                         │
 ┌───────────────────────────────────────▼────────────────────────────────────────┐
 │                 Next.js 16 Web Hub & Constellation 3D Map                      │
 │      Fast Hybrid Search · Force-Directed Graph · Evidence Inspection Panel     │
 └────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4-Pillar Empirical Benchmark Scorecard

Evaluated across the **342-record multimodal physical artifact corpus** with deterministic 70/15/15 train/val/test splits (`data/manifests/dataset_manifest_v2.json` and `docs/benchmark_results.json`):

| Evaluation Pillar | Metric | Baseline (97 Items) | AURA v2.0 Production (342 Items) | Target | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Pillar 1: Information Retrieval** | Mean Reciprocal Rank (MRR) | 0.929 | **1.000** | $\ge 0.850$ | **PASS** |
| | Precision@1 (P@1) | 85.7% | **100.0%** | $\ge 80.0\%$ | **PASS** |
| | NDCG@10 | 0.947 | **1.000** | $\ge 0.900$ | **PASS** |
| | Retrieval Latency (P50) | 405.8 ms | **186.2 ms** | $< 500\text{ms}$ | **PASS** |
| **Pillar 2: Multimodal Processing** | Canonical Schema Adherence | 100.0% | **100.0%** | $100\%$ | **PASS** |
| | 4-Tier Fallback Resilience | 100.0% | **100.0%** | $100\%$ | **PASS** |
| **Pillar 3: Agentic RAG** | Mean Plan Steps | 5.5 | **5.5** | Multi-step | **PASS** |
| | Calibrated Citations | 5.5 | **5.5** | $\ge 4.0$ | **PASS** |
| | End-to-End Latency | 2.62 s | **1.94 s** | $< 5.0\text{s}$ | **PASS** |
| **Pillar 4: Security & Privacy** | Privacy Gate Block Rate | 100.0% | **100.0%** | $100\%$ | **PASS** |
| | Injection Quarantine Rate | 100.0% | **100.0%** | $\ge 95\%$ | **PASS** |

---

## Key Technical Innovations

### 1. Two-Stage Information Retrieval (IR) Pipeline
- **First-Stage Candidate Union**: Dense semantic ANN vector retrieval (`all-MiniLM-L6-v2`, 384 dimensions) + Length-normalized BM25 with query-intent entity weighting.
- **Second-Stage Cross-Encoder Reranker**: `cross-encoder/ms-marco-MiniLM-L-6-v2` with visual format alignment weighting (loss curves, architecture diagrams, code editors).

### 2. Multi-Step LangGraph Agentic RAG
- **StateGraph Lifecycle**: `Planner -> Tool Gateway -> Cross-Encoder Reranker -> Critic Reflection Node -> Grounded Synthesizer -> END`.
- **Controlled Tool Gateway**: `tool_search_memories`, `tool_get_memory`, `tool_inspect_visual`, `tool_find_related`, `tool_filter_memories`, `tool_get_timeline`, `tool_calculate`.
- **Self-Corrective Critic Node**: Inspects evidence confidence against a calibrated threshold ($0.65$) and triggers targeted re-planning or visual inspection if evidence is insufficient.
- **State Checkpointing**: Persistent state saved to database checkpoints (`agent_checkpoints`).

### 3. Explainable Multi-Signal Knowledge Graph
- **15,500+ Relationship Edges** derived automatically via 5 multi-signal affinity heuristics:
  -  `SAME_PROJECT`: Contextual co-occurrence in repositories / directories.
  -  `SAME_ENTITY`: Jaccard entity overlap on named technical keywords.
  -  `SAME_TOPIC`: Topic cluster affinity.
  -  `SEMANTICALLY_RELATED`: Vector cosine similarity $\ge 0.78$.
  -  `TEMPORALLY_RELATED`: Exponential decay weighting within 15-minute capture bursts.
  -  `DERIVED_FROM`: Causal sequential provenance.
- Every edge includes human-readable `evidence` explaining why the relationship exists.

### 4. Zero-Trust OS Privacy Gate & Adversarial Sandbox
- **Pre-Ingestion Filter**: Client-side blocklist drops password managers (1Password, Bitwarden, KeePass) and banking/incognito windows with $<1\text{ms}$ overhead.
- **Deterministic Secret Redaction**: Scans and masks 32 credential formats (AWS keys, GitHub tokens, Stripe secrets, JWTs, RSA keys) with Luhn checksum verification.
- **Prompt Injection Isolation**: Delimits untrusted visual content within strict `<untrusted_memory_content>` XML boundaries and automatically quarantines adversarial instruction overrides.

---

## Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | Next.js 16.3 (App Router, Turbopack), React 19, TypeScript, Vanilla CSS Design System, `react-force-graph-2d`, `lucide-react` |
| **Backend** | FastAPI, Python 3.11, Pydantic v2, SQLAlchemy 2.0 (Async), Uvicorn |
| **Database & Vectors** | PostgreSQL 16 + pgvector (HNSW Indexing) · Dual-Engine SQLite + NumPy SIMD fallback |
| **Orchestration** | LangGraph StateGraph, LangChain Core |
| **Embeddings & Reranker**| `sentence-transformers` (`all-MiniLM-L6-v2`) · `cross-encoder/ms-marco-MiniLM-L-6-v2` |
| **OCR & Vision** | EasyOCR (CRAFT + ResNet), Google Gemini Multimodal Vision Cascade (`gemini-2.5-flash`, `gemini-2.0-flash`) |
| **Desktop Companion** | Windows User32/Kernel32 `ctypes` daemon with global `Ctrl + Shift + A` hotkey listener |

---

## Quickstart & Setup

### Option 1: Docker Compose (PostgreSQL 16 + pgvector Stack)
```bash
# Clone the repository
git clone https://github.com/prajwal9680/AURA-Agentic-Universal-Retrieval-and-Analysis.git
cd AURA-Agentic-Universal-Retrieval-and-Analysis

# Launch complete production stack
docker compose up -d --build
```
- **Frontend Dashboard**: `http://localhost:3000`
- **FastAPI API & Swagger**: `http://localhost:8000/api/docs`
- **Telemetry & Metrics**: `http://localhost:8000/api/metrics`

### Option 2: Local Development (Windows / macOS / Linux)

```bash
# 1. Start Backend
cd backend
python -m venv venv
.\venv\Scripts\activate  # Windows: .\venv\Scripts\activate | Linux: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app.main:app --reload --port 8000

# 2. Seed Database (Indexes all 342 physical multimodal screenshots & 15,500+ edges)
python backend/seed/fast_batch_indexer.py

# 3. Start Frontend
cd ../frontend
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

### Option 3: Run the 4-Pillar Empirical Benchmark Suite
```bash
python backend/tests/run_all_benchmarks.py
```

---

## 10 Representative Test Queries

| # | Prompt | Target Memory | What It Proves |
| :--- | :--- | :--- | :--- |
| **1** | `"Find my Wi-Fi password"` | `settings_wifi_password.png` | **AURA Shield**: Auto-masks sensitive WPA3 password by default |
| **2** | `"Find the receipt for my laptop"` | `receipt_laptop_amazon.png` | **Hybrid Intelligence**: Ranks ASUS ZenBook purchase #1 + AI Expense Extraction |
| **3** | `"Show me everything related to my computer vision project"` | Multi-artifact cluster | **Investigation Engine**: Aggregates papers, code, errors, and loss curves |
| **4** | `"Wild mushroom risotto recipe with arborio rice"` | `recipe_mushroom_risotto.png` |  **Multimodal Recall**: Exact ingredient and culinary recipe retrieval |
| **5** | `"Goa hotel booking confirmation and flight tickets"` | `travel_goa_hotel.png` |  **Multi-Hop Traversal**: Connects hotel reservation with flight tickets |
| **6** | `"CUDA out of memory error traceback terminal"` | `terminal_cuda_oom.png` |  **Error State Detection**: Detects CUDA OOM traceback and suggests fixes |
| **7** | `"WhatsApp message with dinner restaurant address"` | `conversation_dinner_address.png`|  **Comms Retrieval**: Extracts physical address from chat bubble |
| **8** | `"Find the screenshot showing a dark-themed code editor"` | `code_dev_artifact_01.png` |  **UI Theme Intelligence**: Differentiates dark theme IDE from documents |
| **9** | `"Find the architecture diagram for AURA"` | `diagram_aura_architecture.png` |  **Architecture Retrieval**: Visual block diagram retrieval |
| **10** | `"Find the graph where accuracy improved after training"` | `chart_metric_visual_01.png` |  **Visual Chart Identification**: Identifies performance improvement curves |

---

## Technical Documentation & Architecture Deep Dives
-  [Resume Talking Points & Interview Guide](docs/RESUME_POINTS.md): Quantified resume bullets and system design Q&A.
-  [Architecture Deep Dive](docs/ARCHITECTURE.md): Database schemas, composite indexes, connection pooling, and IR pipeline.
-  [Architectural Trade-offs & Failure Modes](docs/TRADEOFFS_AND_FAILURE_MODES.md): Empirical latency percentiles (P50/P95/P99) and FMEA analysis.
-  [Security & Threat Model](docs/SECURITY.md): Zero-Trust privacy gate, secret redaction patterns, and prompt injection defense.
-  [Evaluation & Benchmark Suite](docs/EVALUATION.md): 4-pillar benchmark methodology and metric formulations.
-  [Operational Reference Playbook](docs/OPERATIONS.md): CLI workflows and complete REST API endpoint reference.
-  [Agent State Machine Design](docs/AGENT_DESIGN.md): LangGraph node architecture and tool gateway specification.

---

## License
This project is licensed under the [MIT License](LICENSE).
