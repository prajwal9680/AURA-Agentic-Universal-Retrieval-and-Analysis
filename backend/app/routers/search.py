"""
AURA — Search & Investigation Router
Hybrid search + multi-step agentic investigation engine.
"""
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import Memory, Relationship, SearchSession
from app.services.search import search_memories, parse_query
from app.services.vision import generate_reasoning
from app.routers.memories import _serialize, _safe_json

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["search"])


class SearchRequest(BaseModel):
    query: str
    top_k: int = 20
    include_sensitive: bool = False
    category_filter: Optional[str] = None


class InvestigateRequest(BaseModel):
    query: str
    deep: bool = True


# ─── Simple Search ────────────────────────────────────────────────────────────

@router.post("/search")
async def search(req: SearchRequest, db: AsyncSession = Depends(get_db)):
    """Hybrid semantic + lexical + multimodal visual search."""
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    # Load all non-deleted memories
    stmt = select(Memory).where(Memory.is_deleted == False, Memory.processing_status == "done")
    result = await db.execute(stmt)
    all_memories = result.scalars().all()

    memory_dicts = []
    for m in all_memories:
        d = {
            "id": m.id,
            "file_path": m.file_path,
            "original_filename": m.original_filename,
            "summary": m.summary or "",
            "visual_summary": getattr(m, "visual_summary", "") or m.summary or "",
            "category": m.category or "other",
            "document_type": getattr(m, "document_type", "") or "",
            "visual_objects": _safe_json(getattr(m, "visual_objects", "[]")),
            "visual_details": _safe_json(getattr(m, "visual_details", "{}")),
            "entities": _safe_json(m.entities),
            "topics": _safe_json(m.topics),
            "ocr_text": m.ocr_text or "",
            "embedding": m.embedding,
            "created_at": m.created_at,
            "sensitivity_level": m.sensitivity_level or "PUBLIC",
            "is_deleted": m.is_deleted,
            "is_locked": m.is_locked,
            "importance_score": m.importance_score or 0.5,
        }
        if req.category_filter and d["category"] != req.category_filter:
            continue
        memory_dicts.append(d)

    ranked = await search_memories(req.query, memory_dicts, top_k=req.top_k)

    # Count sensitive results
    sensitive_count = sum(
        1 for r in ranked
        if r.get("sensitivity_level") in ("SENSITIVE", "CRITICAL")
    )

    results = []
    for r in ranked:
        mem = await db.get(Memory, r["id"])
        if not mem:
            continue
        serialized = _serialize(mem)
        serialized["relevance_score"] = r["relevance_score"]
        serialized["score_breakdown"] = r.get("score_breakdown", {})
        # Protect sensitive content
        if mem.sensitivity_level in ("SENSITIVE", "CRITICAL") and not req.include_sensitive:
            serialized["_protected"] = True
            serialized["ocr_text"] = None
        results.append(serialized)

    # Save session
    session = SearchSession(
        id=str(uuid.uuid4()),
        query=req.query,
        result_ids=json.dumps([r["id"] for r in results[:20]]),
        confidence=results[0]["relevance_score"] if results else 0.0,
        mode="search",
    )
    db.add(session)
    await db.commit()

    top_conf = results[0]["relevance_score"] if results else 0.0
    from app.services.vision_provider import get_vision_provider
    provider_info = get_vision_provider().get_provider_info()

    return {
        "query": req.query,
        "total": len(results),
        "confidence": top_conf,
        "sensitive_count": sensitive_count,
        "provider_info": provider_info,
        "results": results,
    }


# ─── Investigation Engine ─────────────────────────────────────────────────────

@router.post("/investigate")
@router.post("/search/investigate")
async def investigate(req: InvestigateRequest, db: AsyncSession = Depends(get_db)):
    """
    LangGraph Multimodal Agentic Investigation Engine:
    Planner -> Controlled Tool Execution -> Multimodal Inspection -> Relation Traversal -> Reranker -> Critic Reflection -> Grounded Synthesis.
    """
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    from app.services.agent import run_agentic_investigation
    from app.services.vision_provider import get_vision_provider

    provider_info = get_vision_provider().get_provider_info()
    agent_output = await run_agentic_investigation(req.query, db)

    results = agent_output.get("results", [])
    result_ids = [r["id"] for r in results]

    # Fetch serialized memories for frontend display
    final_results = []
    for r in results:
        mem = await db.get(Memory, r["id"])
        if not mem:
            continue
        s = _serialize(mem, full=True)
        s["relevance_score"] = r.get("relevance_score", 0.5)
        s["visual_evidence"] = r.get("visual_evidence", mem.visual_summary or mem.summary or "")
        s["rerank_breakdown"] = r.get("rerank_breakdown", {})
        if mem.sensitivity_level in ("SENSITIVE", "CRITICAL"):
            s["_protected"] = True
        final_results.append(s)

    # Fetch relationships among final results
    final_ids = set(r["id"] for r in final_results[:20])
    final_rels = []
    if final_ids:
        final_rels_stmt = select(Relationship).where(
            Relationship.source_memory_id.in_(final_ids),
            Relationship.target_memory_id.in_(final_ids),
        )
        final_rels_result = await db.execute(final_rels_stmt)
        final_rels = final_rels_result.scalars().all()

    clusters = _build_clusters(final_results)
    sensitive_ids = [r["id"] for r in final_results if r.get("sensitivity_level") in ("SENSITIVE", "CRITICAL")]

    return {
        "investigation_id": agent_output.get("investigation_id"),
        "query": req.query,
        "answer": agent_output.get("answer", ""),
        "confidence": agent_output.get("confidence", 0.0),
        "key_findings": agent_output.get("key_findings", []),
        "plan": agent_output.get("plan", []),
        "execution_trace": agent_output.get("execution_trace", []),
        "evidence_trace": agent_output.get("evidence_trace", []),
        "provider_info": provider_info,
        "results": final_results,
        "clusters": clusters,
        "relationships": [
            {
                "source": rel.source_memory_id,
                "target": rel.target_memory_id,
                "type": rel.relationship_type,
                "confidence": rel.confidence,
                "reason": rel.reason,
                "evidence": rel.evidence or rel.reason,
            }
            for rel in final_rels
        ],
        "critic_verdict": agent_output.get("critic_verdict", {}),
        "iterations": agent_output.get("iterations", 1),
        "stats": {
            "total_found": len(final_results),
            "clusters": len(clusters),
            "relationships": len(final_rels),
            "sensitive_protected": len(sensitive_ids),
            "iterations": agent_output.get("iterations", 1),
        },
    }


def _build_clusters(memories: list) -> list:
    """Group memories by category/topic into clusters."""
    cat_groups = {}
    for m in memories:
        cat = m.get("category", "other")
        if cat not in cat_groups:
            cat_groups[cat] = []
        cat_groups[cat].append(m["id"])

    clusters = []
    for cat, ids in cat_groups.items():
        if len(ids) >= 1:
            clusters.append({
                "name": cat.title(),
                "category": cat,
                "memory_ids": ids,
                "count": len(ids),
            })
    clusters.sort(key=lambda c: c["count"], reverse=True)
    return clusters

