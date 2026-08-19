"""
AURA — Agentic RAG Controlled Tools Gateway
Provides deterministic, secure, and explainable tool execution for the LangGraph state machine:
- search_memories(query, category, top_k)
- get_memory(memory_id)
- inspect_visual(memory_id, question)
- find_related(memory_id, relationship_types)
- filter_memories(criteria)
- get_timeline(start_date, end_date, app)
- calculate(expression)
"""
import logging
import json
import re
import ast
import operator
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from app.database import AsyncSessionLocal
from app.models import Memory, Relationship
from app.services.search import search_memories as _core_search
from app.services.vision import inspect_candidates_for_query
from app.routers.memories import _safe_json, _serialize

logger = logging.getLogger(__name__)


# ─── Tool 1: Search Memories ──────────────────────────────────────────────────

async def tool_search_memories(
    db: Optional[AsyncSession] = None,
    query: str = "",
    category: Optional[str] = None,
    top_k: int = 10,
) -> Dict[str, Any]:
    """Hybrid semantic + lexical + multimodal candidate search."""
    if db is None:
        async with AsyncSessionLocal() as session:
            return await tool_search_memories(session, query, category, top_k)

    stmt = select(Memory).where(Memory.is_deleted == False, Memory.processing_status == "done")
    if category:
        stmt = stmt.where(Memory.category == category)
    result = await db.execute(stmt)
    all_mems = result.scalars().all()

    memory_dicts = [
        {
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
        for m in all_mems
    ]

    ranked = await _core_search(query, memory_dicts, top_k=top_k)
    return {
        "tool": "search_memories",
        "query": query,
        "category": category,
        "count": len(ranked),
        "results": ranked,
    }


# ─── Tool 2: Get Single Memory ────────────────────────────────────────────────

async def tool_get_memory(db: Optional[AsyncSession] = None, memory_id: str = "") -> Dict[str, Any]:
    """Retrieve complete metadata, OCR text, and visual understanding for a single memory."""
    if db is None:
        async with AsyncSessionLocal() as session:
            return await tool_get_memory(session, memory_id)

    mem = await db.get(Memory, memory_id)
    if not mem or mem.is_deleted:
        return {"tool": "get_memory", "found": False, "memory_id": memory_id}

    serialized = _serialize(mem, full=True)
    return {"tool": "get_memory", "found": True, "memory": serialized}


# ─── Tool 3: Inspect Visual (VLM Multimodal Grounding) ────────────────────────

async def tool_inspect_visual(
    db: Optional[AsyncSession] = None,
    memory_id: str = "",
    visual_query: str = "",
) -> Dict[str, Any]:
    """Inspect actual visual image details, layout, charts, or UI elements with the VLM provider."""
    if db is None:
        async with AsyncSessionLocal() as session:
            return await tool_inspect_visual(session, memory_id, visual_query)

    mem = await db.get(Memory, memory_id)
    if not mem or mem.is_deleted:
        return {"tool": "inspect_visual", "found": False, "memory_id": memory_id}

    cand = {
        "id": mem.id,
        "file_path": mem.file_path,
        "original_filename": mem.original_filename,
        "summary": mem.summary or "",
        "visual_summary": mem.visual_summary or "",
        "document_type": mem.document_type or "",
        "visual_objects": mem.get_visual_objects(),
        "visual_details": mem.get_visual_details(),
        "ocr_text": mem.ocr_text or "",
    }

    import asyncio
    inspected = await asyncio.to_thread(inspect_candidates_for_query, [cand], visual_query)
    result_data = inspected[0] if inspected else cand

    return {
        "tool": "inspect_visual",
        "memory_id": memory_id,
        "filename": mem.original_filename,
        "visual_evidence": result_data.get("visual_evidence", mem.visual_summary),
        "visual_verification_score": result_data.get("visual_verification_score", 0.90),
        "verification_provenance": result_data.get("verification_provenance", "VISION"),
    }


# ─── Tool 4: Find Related Graph Nodes ─────────────────────────────────────────

async def tool_find_related(
    db: Optional[AsyncSession] = None,
    memory_id: str = "",
    relationship_types: Optional[List[str]] = None,
    min_confidence: float = 0.50,
) -> Dict[str, Any]:
    """Traverse knowledge graph edges connected to a source memory."""
    if db is None:
        async with AsyncSessionLocal() as session:
            return await tool_find_related(session, memory_id, relationship_types, min_confidence)

    stmt = select(Relationship).where(
        or_(
            Relationship.source_memory_id == memory_id,
            Relationship.target_memory_id == memory_id,
        ),
        Relationship.confidence >= min_confidence,
    )
    if relationship_types:
        stmt = stmt.where(Relationship.relationship_type.in_(relationship_types))

    res = await db.execute(stmt)
    rels = res.scalars().all()

    connected_ids = set()
    edge_records = []
    for r in rels:
        other_id = r.target_memory_id if r.source_memory_id == memory_id else r.source_memory_id
        connected_ids.add(other_id)
        edge_records.append({
            "relationship_id": r.id,
            "connected_memory_id": other_id,
            "type": r.relationship_type,
            "confidence": r.confidence,
            "reason": r.reason,
            "evidence": r.evidence or r.reason,
        })

    # Fetch connected memories
    connected_mems = []
    if connected_ids:
        mem_stmt = select(Memory).where(Memory.id.in_(connected_ids), Memory.is_deleted == False)
        mem_res = await db.execute(mem_stmt)
        for m in mem_res.scalars().all():
            connected_mems.append({
                "id": m.id,
                "title": m.original_filename,
                "category": m.category,
                "document_type": m.document_type,
                "visual_summary": m.visual_summary or m.summary or "",
            })

    return {
        "tool": "find_related",
        "memory_id": memory_id,
        "edges_count": len(edge_records),
        "edges": edge_records,
        "connected_memories": connected_mems,
    }


# ─── Tool 5: Filter Memories by Criteria ──────────────────────────────────────

async def tool_filter_memories(
    db: Optional[AsyncSession] = None,
    criteria: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """Filter memories by application, sensitivity, date range, or category."""
    if criteria is None:
        criteria = {}
    if db is None:
        async with AsyncSessionLocal() as session:
            return await tool_filter_memories(session, criteria)

    stmt = select(Memory).where(Memory.is_deleted == False)

    if "category" in criteria and criteria["category"]:
        stmt = stmt.where(Memory.category == criteria["category"])
    if "application" in criteria and criteria["application"]:
        stmt = stmt.where(Memory.application.ilike(f"%{criteria['application']}%"))
    if "sensitivity_level" in criteria and criteria["sensitivity_level"]:
        stmt = stmt.where(Memory.sensitivity_level == criteria["sensitivity_level"])
    if "has_charts" in criteria and criteria["has_charts"]:
        stmt = stmt.where(Memory.visual_details.ilike("%has_charts_or_graphs\": true%"))

    res = await db.execute(stmt.limit(50))
    mems = res.scalars().all()

    return {
        "tool": "filter_memories",
        "criteria": criteria,
        "count": len(mems),
        "results": [
            {
                "id": m.id,
                "title": m.original_filename,
                "category": m.category,
                "document_type": m.document_type,
                "summary": m.summary or "",
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in mems
        ],
    }


# ─── Tool 6: Get Timeline ─────────────────────────────────────────────────────

async def tool_get_timeline(
    db: Optional[AsyncSession] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    app: Optional[str] = None,
) -> Dict[str, Any]:
    """Group memories chronologically by calendar days and applications."""
    if db is None:
        async with AsyncSessionLocal() as session:
            return await tool_get_timeline(session, start_date, end_date, app)

    stmt = select(Memory).where(Memory.is_deleted == False)
    if app:
        stmt = stmt.where(Memory.application.ilike(f"%{app}%"))

    res = await db.execute(stmt.order_by(Memory.created_at.desc()).limit(100))
    mems = res.scalars().all()

    days_map: Dict[str, List[Dict[str, Any]]] = {}
    for m in mems:
        day_key = m.created_at.strftime("%Y-%m-%d") if m.created_at else "Unknown Date"
        if day_key not in days_map:
            days_map[day_key] = []
        days_map[day_key].append({
            "id": m.id,
            "title": m.original_filename,
            "application": m.application,
            "category": m.category,
            "summary": m.summary,
        })

    return {
        "tool": "get_timeline",
        "total_events": len(mems),
        "days": [{"date": d, "count": len(items), "items": items} for d, items in days_map.items()],
    }


# ─── Tool 7: Safe Math & Unit Calculator ──────────────────────────────────────

def tool_calculate(expression: str) -> Dict[str, Any]:
    """Safely evaluate arithmetic expressions (e.g. expenses, totals, percentages)."""
    clean_expr = expression.replace("$", "").replace("₹", "").replace(",", "")
    
    # Safe AST operator mapping
    operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.USub: operator.neg,
    }

    def _eval(node):
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.BinOp):
            return operators[type(node.op)](_eval(node.left), _eval(node.right))
        elif isinstance(node, ast.UnaryOp):
            return operators[type(node.op)](_eval(node.operand))
        else:
            raise TypeError(node)

    try:
        parsed = ast.parse(clean_expr, mode="eval")
        val = _eval(parsed.body)
        return {"tool": "calculate", "expression": expression, "result": val, "success": True}
    except Exception as e:
        return {"tool": "calculate", "expression": expression, "error": str(e), "success": False}
