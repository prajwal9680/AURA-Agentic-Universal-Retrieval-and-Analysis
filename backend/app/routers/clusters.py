"""AURA — Clusters & Timeline Router"""
import json
import logging
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import Memory, Relationship, Collection, CollectionMemory
from app.routers.memories import _serialize, _safe_json

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["clusters"])


@router.get("/clusters")
async def get_clusters(db: AsyncSession = Depends(get_db)):
    """Auto-generated clusters based on category grouping."""
    stmt = select(
        Memory.category,
        func.count(Memory.id).label("count")
    ).where(
        Memory.is_deleted == False,
        Memory.processing_status == "done"
    ).group_by(Memory.category).order_by(func.count(Memory.id).desc())

    result = await db.execute(stmt)
    rows = result.all()

    CLUSTER_COLORS = {
        "receipt": "#10b981", "invoice": "#f59e0b", "recipe": "#f97316",
        "code": "#6366f1", "research": "#8b5cf6", "chart": "#06b6d4",
        "diagram": "#14b8a6", "terminal": "#64748b", "travel": "#ec4899",
        "finance": "#eab308", "shopping": "#84cc16", "education": "#3b82f6",
        "credentials": "#ef4444", "presentation": "#a855f7", "other": "#6b7280",
        "conversation": "#22c55e", "settings": "#94a3b8",
    }

    clusters = []
    for row in rows:
        cat = row.category or "other"
        # Get sample memories for this cluster
        sample_stmt = select(Memory).where(
            Memory.is_deleted == False,
            Memory.category == cat,
            Memory.processing_status == "done",
        ).limit(6)
        sample_result = await db.execute(sample_stmt)
        samples = sample_result.scalars().all()

        clusters.append({
            "id": f"cluster_{cat}",
            "name": cat.replace("_", " ").title(),
            "category": cat,
            "count": row.count,
            "color": CLUSTER_COLORS.get(cat, "#6b7280"),
            "samples": [_serialize(m) for m in samples],
        })

    return {"clusters": clusters, "total": len(clusters)}


@router.get("/clusters/{category}")
async def get_cluster_detail(category: str, db: AsyncSession = Depends(get_db)):
    """Full cluster view with all memories and internal relationships."""
    stmt = select(Memory).where(
        Memory.is_deleted == False,
        Memory.category == category,
        Memory.processing_status == "done",
    ).order_by(Memory.created_at.desc())
    result = await db.execute(stmt)
    memories = result.scalars().all()

    mem_ids = [m.id for m in memories]
    # Internal relationships
    rel_stmt = select(Relationship).where(
        Relationship.source_memory_id.in_(mem_ids),
        Relationship.target_memory_id.in_(mem_ids),
    )
    rel_result = await db.execute(rel_stmt)
    rels = rel_result.scalars().all()

    return {
        "category": category,
        "name": category.replace("_", " ").title(),
        "count": len(memories),
        "memories": [_serialize(m, full=False) for m in memories],
        "relationships": [
            {
                "source": r.source_memory_id,
                "target": r.target_memory_id,
                "type": r.relationship_type,
                "confidence": r.confidence,
                "reason": r.reason,
            }
            for r in rels
        ],
    }


def _format_unique_title(m: Memory) -> str:
    fn = m.original_filename or ""
    base = fn.rsplit(".", 1)[0]
    words = base.replace("_", " ").replace("-", " ").title().split()
    clean_name = " ".join(words)
    if (len(clean_name) < 4 or clean_name.lower().startswith("screenshot")) and m.summary:
        clean_name = m.summary.split(".")[0][:45]
    return clean_name or "Visual Memory Artifact"


CONSTELLATIONS = {
    "vision": {
        "id": "hub_vision",
        "constellation_key": "vision",
        "name": "Project Cartosat & Vision AI",
        "icon": "🛰️",
        "color": "#D97757",
        "description": "Satellite aerial segmentation, YOLO benchmarks, PyTorch models & computer vision research",
    },
    "commerce": {
        "id": "hub_commerce",
        "constellation_key": "commerce",
        "name": "Commerce & Hardware Ledger",
        "icon": "🧾",
        "color": "#B87B28",
        "description": "Electronics purchase invoices, laptop receipts, product specs & payment confirmations",
    },
    "security": {
        "id": "hub_security",
        "constellation_key": "security",
        "name": "Zero-Trust Security Vault",
        "icon": "🔒",
        "color": "#B83A2E",
        "description": "Wi-Fi credentials, Pre-Shared Keys, router settings & cloud authentication tokens",
    },
    "culinary": {
        "id": "hub_culinary",
        "constellation_key": "culinary",
        "name": "Culinary & Gastronomy",
        "icon": "🍄",
        "color": "#387B58",
        "description": "Wild mushroom risotto, authentic pasta recipes, bistro menus & food photos",
    },
    "runtime": {
        "id": "hub_runtime",
        "constellation_key": "runtime",
        "name": "Terminal & Runtime Logs",
        "icon": "⚡",
        "color": "#E06C75",
        "description": "CUDA Out-Of-Memory exceptions, stack tracebacks, build pipelines & shell sessions",
    },
    "travel": {
        "id": "hub_travel",
        "constellation_key": "travel",
        "name": "Transit & Goa Travel Diary",
        "icon": "🗺️",
        "color": "#4A7C59",
        "description": "Flight bookings, Namma Metro transit passes, Goa resort reservations & city navigation",
    },
    "comms": {
        "id": "hub_comms",
        "constellation_key": "comms",
        "name": "Communications & War Rooms",
        "icon": "💬",
        "color": "#6366F1",
        "description": "WhatsApp dinner addresses, team coordination channels & meeting minutes",
    },
    "automotive": {
        "id": "hub_automotive",
        "constellation_key": "automotive",
        "name": "Automotive & Supercars",
        "icon": "🏎️",
        "color": "#8B5CF6",
        "description": "Ferrari F8 Tributo, Porsche 911 GT3, sports car photography & vehicle specs",
    },
}


def _assign_constellation(m: Memory) -> str:
    fn = (m.original_filename or "").lower()
    cat = (m.category or "").lower()
    sens = (m.sensitivity_level or "").upper()
    summary = (m.summary or "").lower()

    if "wifi" in fn or "password" in fn or "secret" in fn or "token" in fn or "credential" in fn or sens == "CRITICAL":
        return "security"
    if "car" in fn or "ferrari" in fn or "porsche" in fn or "supercar" in fn:
        return "automotive"
    if "recipe" in fn or "mushroom" in fn or "pasta" in fn or "food" in fn or "bistro" in fn or "menu" in fn or cat == "recipe":
        return "culinary"
    if "receipt" in fn or "invoice" in fn or "amazon" in fn or "cart" in fn or "bought" in fn or cat in ("receipt", "invoice", "finance", "shopping"):
        return "commerce"
    if "terminal" in fn or "error" in fn or "traceback" in fn or "cuda" in fn or "oom" in fn or cat == "terminal":
        return "runtime"
    if "goa" in fn or "flight" in fn or "hotel" in fn or "map" in fn or "metro" in fn or "travel" in fn or cat in ("travel", "map"):
        return "travel"
    if "conversation" in fn or "address" in fn or "chat" in fn or "slack" in fn or "whatsapp" in fn or cat == "conversation":
        return "comms"
    if "yolo" in fn or "isro" in fn or "satellite" in fn or "paper" in fn or "chart" in fn or "loss" in fn or "vit" in fn or "transformer" in fn or cat in ("research", "diagram", "code", "chart"):
        return "vision"
    return "vision"


@router.get("/constellation")
async def get_constellation(
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Graph data for the Memory Constellation visualization.
    Returns 8 Named Constellations with Central Hub Stars & Orbiting Memory Satellites.
    """
    stmt = select(Memory).where(
        Memory.is_deleted == False,
        Memory.processing_status == "done",
    )
    result = await db.execute(stmt)
    memories = result.scalars().all()

    # Get all relationships (up to 2000 for high-density multi-signal graph)
    rel_stmt = select(Relationship).order_by(Relationship.confidence.desc()).limit(2000)
    rel_result = await db.execute(rel_stmt)
    rels = rel_result.scalars().all()

    nodes = []
    edges = []

    # 1. Add 8 Constellation Hub Star Nodes
    constellation_counts = {k: 0 for k in CONSTELLATIONS}
    for c_key, c_info in CONSTELLATIONS.items():
        nodes.append({
            "id": c_info["id"],
            "type": "constellation_hub",
            "name": f"{c_info['icon']} {c_info['name']}",
            "label": f"{c_info['icon']} {c_info['name']}",
            "constellation_key": c_key,
            "constellation_name": c_info["name"],
            "description": c_info["description"],
            "category": "constellation",
            "color": c_info["color"],
            "val": 14,
            "is_hub": True,
        })

    # 2. Add Memory Satellites assigned to Constellations
    mem_id_set = set()
    for m in memories:
        c_key = _assign_constellation(m)
        constellation_counts[c_key] += 1
        c_info = CONSTELLATIONS[c_key]
        unique_title = _format_unique_title(m)
        mem_id_set.add(m.id)

        nodes.append({
            "id": m.id,
            "type": "memory",
            "name": unique_title,
            "label": unique_title,
            "original_filename": m.original_filename,
            "summary": m.summary or "",
            "category": m.category or "other",
            "constellation_key": c_key,
            "constellation_name": c_info["name"],
            "constellation_icon": c_info["icon"],
            "sensitivity_level": m.sensitivity_level or "PUBLIC",
            "color": c_info["color"],
            "thumbnail_url": f"/api/memories/{m.id}/thumbnail",
            "image_url": f"/api/memories/{m.id}/thumbnail",
            "importance": m.importance_score or 0.5,
            "application": m.application or "System",
            "window_title": m.window_title or "",
            "is_redacted": m.is_redacted,
            "val": 4.5,
            "created_at": m.created_at.isoformat() if m.created_at else None,
        })

        # Gravitational link from Constellation Hub to Memory Satellite
        edges.append({
            "id": f"hub_link_{m.id}",
            "source": c_info["id"],
            "target": m.id,
            "type": "constellation_member",
            "confidence": 0.95,
            "reason": f"Member of {c_info['name']}",
            "width": 1.2,
            "is_hub_edge": True,
        })

    # 3. Add Cross-Memory Semantic Relationships
    for r in rels:
        if r.source_memory_id in mem_id_set and r.target_memory_id in mem_id_set:
            edges.append({
                "id": r.id,
                "source": r.source_memory_id,
                "target": r.target_memory_id,
                "type": r.relationship_type,
                "confidence": r.confidence,
                "reason": r.reason,
                "width": max(1, r.confidence * 2.5),
                "is_hub_edge": False,
            })

    return {
        "constellations": list(CONSTELLATIONS.values()),
        "nodes": nodes,
        "edges": edges,
        "total_nodes": len(nodes),
        "total_edges": len(edges),
    }


@router.get("/timeline")
async def get_timeline(db: AsyncSession = Depends(get_db)):
    """Timeline view of memories grouped by day."""
    stmt = select(Memory).where(
        Memory.is_deleted == False,
        Memory.processing_status == "done",
    ).order_by(Memory.created_at.asc())
    result = await db.execute(stmt)
    memories = result.scalars().all()

    from collections import defaultdict
    by_day = defaultdict(list)
    for m in memories:
        if m.created_at:
            day = m.created_at.strftime("%Y-%m-%d")
        else:
            day = "unknown"
        by_day[day].append(_serialize(m))

    timeline = [
        {"date": day, "memories": mems, "count": len(mems)}
        for day, mems in sorted(by_day.items(), reverse=True)
    ]
    return {"timeline": timeline, "total_days": len(timeline)}


@router.get("/collections")
async def get_collections(db: AsyncSession = Depends(get_db)):
    stmt = select(Collection).order_by(Collection.created_at.desc())
    result = await db.execute(stmt)
    collections = result.scalars().all()
    return {"collections": [{"id": c.id, "name": c.name, "description": c.description, "type": c.type} for c in collections]}


@router.get("/events/graph-stream")
@router.get("/graph/stream")
async def stream_graph_events():
    """
    Server-Sent Events (SSE) stream for live Memory Constellation updates.
    Broadcasts MemoryCreated, MemoryUpdated, and MemoryDeleted graph mutations.
    """
    from fastapi.responses import StreamingResponse
    import asyncio
    from app.services.graph_events import event_bus

    async def event_generator():
        q = event_bus.subscribe()
        try:
            # Yield initial connection confirmation
            yield f"event: ping\ndata: {json.dumps({'status': 'connected', 'channel': 'graph_stream'})}\n\n"
            while True:
                try:
                    event = await asyncio.wait_for(q.get(), timeout=20.0)
                    yield f"event: {event['event']}\ndata: {json.dumps(event)}\n\n"
                except asyncio.TimeoutError:
                    # Keep-alive heartbeat
                    yield f": keepalive\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            event_bus.unsubscribe(q)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
