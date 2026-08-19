# Contributing to AURA

Thank you for your interest in contributing to **AURA (Agentic Universal Retrieval and Analysis)**. We welcome technical contributions, benchmark improvements, retrieval optimizations, and security patches.

---

## 🏗️ Development Setup

### 1. Prerequisites
- **Python 3.10+** (Python 3.11 recommended)
- **Node.js 18+** (Node 20 recommended) & `npm`
- **PostgreSQL 16** with `pgvector` extension (Optional; SQLite fallback is supported automatically for local dev)

### 2. Setting Up the Backend
```bash
cd backend
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app.main:app --reload --port 8000
```

### 3. Setting Up the Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## 🧪 Testing & Verification Protocols

Before submitting any Pull Request, ensure that all automated benchmark suites and unit tests pass:

### 1. Run Unit Tests
```bash
pytest backend/tests/ -v
```

### 2. Run the 4-Pillar Empirical Benchmark Suite
```bash
python backend/tests/run_all_benchmarks.py
```

### 3. Frontend Build Validation
```bash
cd frontend
npm run build
```

---

## 📐 Code Standards & Conventions

1. **Type Safety**:
   - Python: Use strict type hints and Pydantic v2 schemas for all request/response payloads.
   - Frontend: Use TypeScript without `any` types.
2. **Security by Design**:
   - Never commit API keys, secrets, or raw passwords.
   - Any new ingestion or extraction pipelines must route through `PrivacyGate` (`desktop/privacy_gate.py`) and `scan_text` (`backend/app/services/shield.py`).
3. **Retrieval Grounding**:
   - All RAG responses must provide verbatim artifact citations with calibrated relevance confidence scores.

---

## 📄 License
By contributing to AURA, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).
