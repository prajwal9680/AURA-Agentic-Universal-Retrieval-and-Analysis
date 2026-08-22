# AURA — Agentic RAG Architecture & LangGraph Design

## 1. Executive Summary
AURA implements a true multi-step **Agentic RAG State Machine** orchestrated via **LangGraph**. Unlike naive RAG pipelines that execute single-pass retrieval and immediate generation, AURA uses explicit query planning, iterative tool execution, cross-encoder reranking, a self-reflective critic node, and calibrated citation synthesis.

---

## 2. LangGraph State Machine Architecture

```
                    ┌─────────────────────────┐
                    │     AURA State Input    │
                    │   (User Query, Context) │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │      Planner Node       │
                    │ (Intent, Visual Strategy│
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │  Tool Execution Gateway │
                    │ (Search/Inspect/Graph/  │
                    │   Timeline/Calculate)   │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │ Cross-Encoder Reranker  │
                    │ (Contextual Relevance)  │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │       Critic Node       │
                    │ (Sufficiency Reflection)│
                    └────────────┬────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │ Is Evidence Sufficient? │
                    └──────┬───────────┬──────┘
                           │           │
                     [No & i < max]  [Yes or i >= max]
                           │           │
                           │     ┌─────▼──────────────────┐
                           │     │    Synthesizer Node    │
                           │     │ (Grounded Calibration) │
                           │     └─────┬──────────────────┘
                           │           │
                           └───────────┼──────────────────┐
                                       │                  │
                                       ▼                  ▼
                                  (Re-Plan)             (END)
```

---

## 3. The 7 Controlled Agent Tools

| Tool Name | Scope | Purpose |
| :--- | :--- | :--- |
| `tool_search_memories` | Global Search | Executes two-stage vector + BM25 retrieval over candidate memories. |
| `tool_get_memory` | Single Memory | Retrieves full metadata, raw OCR text, visual entities, and provenance. |
| `tool_inspect_visual` | VLM Grounding | Performs targeted visual inspection of charts, diagrams, and layout structures. |
| `tool_find_related` | Graph Traversal | Traverses multi-hop explainable knowledge graph edges. |
| `tool_filter_memories` | Categorical | Filters memories by application, sensitivity, date, and chart presence. |
| `tool_get_timeline` | Temporal | Chronologically groups memories across application sessions. |
| `tool_calculate` | Math Engine | Sandboxed arithmetic evaluation for expenses and tax breakdowns. |

---

## 4. Critic Node Reflection & Loop Convergence
- **Evidence Verification**: The critic inspects the top evidence confidence score against `settings.agent_critic_threshold` (0.65).
- **Missing Aspect Diagnosis**: If the top score is below threshold, the critic diagnoses missing aspects (e.g. `visual_inspection`, `graph_expansion`) and feeds structured feedback back to the planner.
- **Forced Convergence Safeguard**: The loop strictly enforces `iteration_count >= max_iterations` (default: 3) to prevent infinite cycles.
- **State Checkpointing**: Every investigation run writes state checkpoints to `agent_checkpoints` for full execution auditability and state recovery.
