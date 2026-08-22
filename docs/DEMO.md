# AURA — Agentic Universal Retrieval and Analysis
## Live System Presentation & Architectural Demonstration Script

---

## Executive Summary
> **Vision:** *"You have thousands of visual desktop captures and can't find any of them. Build an engine that understands, classifies, and makes every screenshot semantically searchable by meaning, layout, and visual semantics."*

**AURA** (**Agentic Universal Retrieval and Analysis**) is a production-grade multimodal visual memory engine that bridges optical character recognition (OCR), multimodal vision reasoning, 384-dimensional dense semantic embeddings, LangGraph state orchestration, and neural graph constellation topology with deterministic Zero-Trust security shielding.

---

## 3-Minute Presentation Walkthrough

### ACT 1: The Problem & Live Engine Overview (0:00 – 0:45)
1. **Navigate to:** `http://localhost:3000`
2. **Talking Points:**
   - *"We take thousands of screenshots every month — receipts, code snippets, WiFi passwords, travel tickets, recipes — but standard operating systems treat them as dumb image files with names like `Screenshot_2026-08-15_14.png`."*
   - *"AURA solves this by turning raw pixels into an explainable, interconnected neural visual memory ledger."*
3. **Show:**
   - Editorial homepage header and live stats bar showing indexed memories and graph edges.
   - The interactive query input with instant semantic search and deep investigation modes.

---

### ACT 2: Semantic Search, Investigation & Zero-Trust Shield (0:45 – 1:45)

#### Demo Step 2.1 — Natural Language Semantic Search
- **Query:** `what food or recipes do I have`
- **What happens:**
  - AURA instantly retrieves `food_photo_japanese_ramen.png`, `recipe_pasta_carbonara.png`, and `receipt_swiggy_order.png`.
  - Notice the **100% precision**: It searches by semantic concept, not filename.
  - Click **Investigate**: AURA synthesizes a grounded answer citing the specific dish names and ingredients.

#### Demo Step 2.2 — Zero-Trust Security Gate & Credential Masking
- **Query:** `where is the wifi password stored`
- **What happens:**
  - AURA identifies `settings_wifi_password.png` (Sensitivity: **CRITICAL**).
  - The secret password is **automatically redacted and masked** on the preview card (`••••••••••••`).
  - Click the **Reveal Secret (Zero-Trust Override)** button: Enter password verification `aura2026` or click Unlock to audit the reveal event with cryptographic timestamp logging.
  - Demonstrates verified defense against credential and sensitive personal data leakage.

#### Demo Step 2.3 — Financial Intelligence & Expense Extraction
- **Query:** `laptop purchase bill and receipt`
- **What happens:**
  - Retrieves `receipt_amazon_india.png` and `receipt_laptop_amazon.png`.
  - Click into the memory card → Click **AI Actions: Extract Expense**.
  - AURA extracts structured JSON: Merchant: **Amazon India**, Total: **₹68,990.00**, Line Items: **ASUS TUF Gaming Laptop**, Payment: **HDFC Credit Card (Masked)**.

---

### ACT 3: Constellation Graph & Chronological Timeline (1:45 – 2:30)

#### Demo Step 3.1 — Constellation Graph Explorer
- **Navigate to:** `http://localhost:3000/constellation`
- **What happens:**
  - Interactive Force-Directed Graph rendering hundreds of semantic relationship edges.
  - Filter by Category (Receipts, Code, Credentials, Travel).
  - Click any node to inspect real-time semantic neighbors, shared topics, and bidirectional graph citations.

#### Demo Step 3.2 — Visual Timeline Ledger
- **Navigate to:** `http://localhost:3000/timeline`
- **What happens:**
  - Temporal audit trail organizing every screenshot by capture date and milestone.
  - Filter by security severity (Public, Personal, Sensitive, Critical).

---

### ACT 4: Drag & Drop Ingestion & Wrap-up (2:30 – 3:00)

#### Demo Step 4.1 — Live Adaptive Ingestion
- **Navigate to:** `http://localhost:3000/upload`
- **What happens:**
  - Drag and drop any test screenshot.
  - Watch the live 5-stage progress pipeline in real-time:
    `Upload & Verify` -> `Optical OCR` -> `Multimodal Vision` -> `Zero-Trust Shield` -> `Neural Embedding & Graph Linking`.
  - See the classified memory card appear inline with instant navigation to its detail page.

#### Demo Step 4.2 — Closing Statement
- *"AURA doesn't just store screenshots. It understands them, connects them, protects them, and makes them actionable."*

---

## 5 Deterministic Demo Queries for Judges

| # Query String | Expected Top Result | Demonstrated Capability |
|---|--------------|---------------------|--------------------------|
| 1 | `what food or recipes do I have` | `recipe_pasta_carbonara.png` / `food_photo_japanese_ramen.png` | Semantic understanding beyond OCR |
| 2 | `where is the wifi password stored` | `settings_wifi_password.png` | Zero-Trust Shield masking & access auditing |
| 3 | `laptop purchase bill and receipt` | `receipt_amazon_india.png` | Automated merchant & expense extraction |
| 4 | `find my machine learning code` | `ui_vscode_python.png` / `ui_github_issue.png` | Code syntax recognition & technical retrieval |
| 5 | `mumbai train route map` | `map_mumbai_local.png` / `ticket_irctc_train.png` | Geographic & transit multimodal understanding |

---

## Technology Stack
- **Frontend:** Next.js 16.3 (Turbopack, TypeScript, Tailwind CSS, Lucide Icons, Canvas / Force Graph)
- **Backend:** FastAPI (Python 3.11, Uvicorn, SQLAlchemy Async, SQLite)
- **OCR Engine:** EasyOCR / Tesseract OCR
- **Embeddings:** Sentence-Transformers (`all-MiniLM-L6-v2`, 384-dimensional dense vectors)
- **Multimodal AI:** Google Gemini 2.5/1.5 Flash Vision & Deterministic Cognitive Synthesis
- **Security Engine:** AURA Zero-Trust Shield (Regex-first pattern analyzer, SHA-256 integrity hashing, redacted rendering)
