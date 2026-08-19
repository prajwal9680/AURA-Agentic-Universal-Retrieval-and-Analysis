"""
AURA — Real-Time Incremental Graph Event Engine
Provides event-driven graph updates for the Memory Constellation:
- MemoryCreated: Triggers O(k) neighbor discovery & edge insertion
- MemoryUpdated: Re-evaluates edge weights & metadata
- MemoryDeleted: Prunes cascade edges
- GraphStream: Server-Sent Events (SSE) broadcaster for live frontend constellation sync
"""
import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, or_

from app.models import Memory, Relationship
from app.services.relationships import compute_relationship
from app.services.embeddings import hex_to_embedding, cosine_similarity

logger = logging.getLogger(__name__)


# ─── In-Memory Event Subscribers Bus ──────────────────────────────────────────

class GraphEventBus:
    def __init__(self):
        self._subscribers: Set[asyncio.Queue] = set()

    def subscribe(self) -> asyncio.Queue:
        q = asyncio.Queue(maxsize=100)
        self._subscribers.add(q)
        return q

    def unsubscribe(self, q: asyncio.Queue):
        self._subscribers.discard(q)

    async def publish(self, event_type: str, payload: Dict[str, Any]):
        """Broadcast event to all active SSE subscribers."""
        event_data = {
            "event": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": payload,
        }
        for q in list(self._subscribers):
            try:
                q.put_nowait(event_data)
            except asyncio.QueueFull:
                logger.warning("Subscriber queue full. Discarding event.")
            except Exception as e:
                logger.warning(f"Failed to deliver event to subscriber: {e}")


# Singleton event bus
event_bus = GraphEventBus()


# ─── Incremental Memory Ingestion Graph Updater ───────────────────────────────

async def handle_memory_created(new_memory_id: str, db: AsyncSession) -> List[Dict[str, Any]]:
    """
    Incrementally compute and store edges for a newly created memory in O(k) time.
    Publishes real-time events for frontend graph synchronization.
    """
    mem = await db.get(Memory, new_memory_id)
    if not mem or mem.is_deleted:
        return []

    mem_dict = {
        "id": mem.id,
        "filename": mem.original_filename,
        "summary": mem.summary or "",
        "category": mem.category or "other",
        "entities": mem.get_entities(),
        "topics": mem.get_topics(),
        "ocr_text": mem.ocr_text or "",
        "embedding": mem.embedding,
        "created_at": mem.created_at,
    }

    # Fetch top candidate neighbors (same category OR active memories)
    stmt = select(Memory).where(
        Memory.id != new_memory_id,
        Memory.is_deleted == False,
        Memory.processing_status == "done",
    ).order_by(Memory.created_at.desc()).limit(50)

    res = await db.execute(stmt)
    neighbors = res.scalars().all()

    created_edges = []
    for other in neighbors:
        other_dict = {
            "id": other.id,
            "filename": other.original_filename,
            "summary": other.summary or "",
            "category": other.category or "other",
            "entities": other.get_entities(),
            "topics": other.get_topics(),
            "ocr_text": other.ocr_text or "",
            "embedding": other.embedding,
            "created_at": other.created_at,
        }

        rel = compute_relationship(mem_dict, other_dict)
        if rel:
            ev_text = rel.get("evidence") or rel.get("reason", "")
            r1 = Relationship(
                source_memory_id=mem.id,
                target_memory_id=other.id,
                relationship_type=rel["type"],
                confidence=rel["confidence"],
                reason=rel["reason"],
                evidence=ev_text,
            )
            r2 = Relationship(
                source_memory_id=other.id,
                target_memory_id=mem.id,
                relationship_type=rel["type"],
                confidence=rel["confidence"],
                reason=rel["reason"],
                evidence=ev_text,
            )
            db.add(r1)
            db.add(r2)
            created_edges.append({
                "source": mem.id,
                "target": other.id,
                "type": rel["type"],
                "confidence": rel["confidence"],
                "reason": rel["reason"],
                "evidence": ev_text,
            })

    if created_edges:
        await db.commit()

    # Broadcast event to real-time subscribers
    await event_bus.publish("MemoryCreated", {
        "memory": {
            "id": mem.id,
            "title": mem.original_filename,
            "category": mem.category,
            "summary": mem.summary,
        },
        "new_edges": created_edges,
        "edges_count": len(created_edges),
    })

    return created_edges


async def handle_memory_deleted(memory_id: str, db: AsyncSession):
    """Prunes edges and broadcasts MemoryDeleted event."""
    await db.execute(
        delete(Relationship).where(
            or_(
                Relationship.source_memory_id == memory_id,
                Relationship.target_memory_id == memory_id,
            )
        )
    )
    await db.commit()

    await event_bus.publish("MemoryDeleted", {
        "memory_id": memory_id,
    })
