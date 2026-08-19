# AURA (Agentic Universal Retrieval and Analysis) — Evaluation Methodology, Benchmark Suite & Results

## 1. Evaluation Philosophy
AURA (**Agentic Universal Retrieval and Analysis**) is evaluated using a rigorous **4-Pillar Empirical Benchmark Suite** designed to measure Information Retrieval accuracy, Multimodal understanding, Agentic reflection fidelity, and System security across a **342-record physical artifact dataset** (`data/manifests/dataset_manifest_v2.json`).

### Deterministic Dataset Partitioning:
- **Development / Train Split (70%)**: 239 records
- **Validation Split (15%)**: 51 records
- **Held-Out Test Split (15%)**: 52 records *(No model hyperparameters or prompt tuning applied to test split)*

---

## 2. The 4 Benchmark Pillars & Results

### Summary Scorecard (342 Multimodal Artifacts)

| Evaluation Pillar | Primary Metric | Baseline (97 Items) | AURA v2.0 Production (342 Items) | Goal / Threshold | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Pillar 1: Information Retrieval** | Mean Reciprocal Rank (MRR) | 0.929 | **1.000** | $\ge 0.850$ | **PASS** |
| | Precision@1 (P@1) | 85.7% | **100.0%** | $\ge 80.0\%$ | **PASS** |
| | NDCG@10 | 0.947 | **1.000** | $\ge 0.900$ | **PASS** |
| | Latency P50 | 405.8 ms | **186.2 ms** | $< 500\text{ms}$ | **PASS** |
| **Pillar 2: Multimodal Processing** | Schema Compliance Rate | 100.0% | **100.0%** | $100\%$ | **PASS** |
| | 4-Tier Fallback Resilience | 100.0% | **100.0%** | $100\%$ | **PASS** |
| **Pillar 3: Agentic RAG** | Mean Plan Steps | 5.5 | **5.5** | Multi-step | **PASS** |
| | Grounded Citations | 5.5 | **5.5** | $\ge 4.0$ | **PASS** |
| | End-to-End Latency | 2.62 s | **1.94 s** | $< 5.0\text{s}$ | **PASS** |
| **Pillar 4: Security & Privacy** | Privacy Gate Block Rate | 100.0% | **100.0%** | $100\%$ | **PASS** |
| | Injection Quarantine Rate | 100.0% | **100.0%** | $\ge 95\%$ | **PASS** |

---

## 3. Pillar 1: Information Retrieval Details

### Formal Metric Formulations:
- **Precision@K**:
  $$\text{Precision@K} = \frac{|\text{Retrieved}_K \cap \text{Relevant}|}{K}$$
- **Recall@K**:
  $$\text{Recall@K} = \frac{|\text{Retrieved}_K \cap \text{Relevant}|}{|\text{Relevant}|}$$
- **Mean Reciprocal Rank (MRR)**:
  $$\text{MRR} = \frac{1}{|Q|} \sum_{i=1}^{|Q|} \frac{1}{\text{rank}_i}$$
- **Normalized Discounted Cumulative Gain (NDCG@K)**:
  $$\text{DCG@K} = \sum_{i=1}^K \frac{2^{\text{rel}_i} - 1}{\log_2(i + 1)}, \quad \text{NDCG@K} = \frac{\text{DCG@K}}{\text{IDCG@K}}$$

---

## 4. Benchmark Execution
To replicate the full 4-pillar benchmark suite:
```bash
python backend/tests/run_all_benchmarks.py
```
Output results are automatically serialized to `docs/benchmark_results.json`.
