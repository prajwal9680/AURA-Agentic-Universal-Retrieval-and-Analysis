"""
AURA — Relationship Graph Enrichment
Computes pairwise relationships across all indexed memories in the database.
Populates the Relationship table with rich links for the Memory Constellation.
"""
import sys
import os
import asyncio
import json
from pathlib import Path

# Fix Windows console UTF-8
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.database import init_db, AsyncSessionLocal
from app.models import Memory, Relationship
from app.services.relationships import compute_relationship, _safe_list
from app.services.embeddings import hex_to_embedding, cosine_similarity
from sqlalchemy import select, delete


async def enrich():
    print("=" * 60)
    print("AURA Relationship Graph Enrichment")
    print("=" * 60)

    await init_db()

    async with AsyncSessionLocal() as db:
        # Clear existing relationships
        await db.execute(delete(Relationship))
        await db.commit()

        # Load all done memories
        stmt = select(Memory).where(Memory.is_deleted == False, Memory.processing_status == "done")
        result = await db.execute(stmt)
        memories = result.scalars().all()
        print(f"Loaded {len(memories)} indexed memories.")

        mem_dicts = [
            {
                "id": m.id,
                "filename": m.original_filename,
                "summary": m.summary or "",
                "category": m.category or "other",
                "entities": _safe_list(m.entities),
                "topics": _safe_list(m.topics),
                "ocr_text": m.ocr_text or "",
                "embedding": m.embedding,
                "created_at": m.created_at,
            }
            for m in memories
        ]

        total_created = 0

        for i, m_a in enumerate(mem_dicts):
            for j, m_b in enumerate(mem_dicts):
                if i >= j:
                    continue  # Undirected pairwise

                rel = compute_relationship(m_a, m_b)
                if not rel:
                    # Additional heuristic check for related categories & project keywords
                    text_a = (m_a["filename"] + " " + m_a["summary"] + " " + m_a["ocr_text"]).lower()
                    text_b = (m_b["filename"] + " " + m_b["summary"] + " " + m_b["ocr_text"]).lower()

                    # Common project themes
                    cv_terms = ["yolo", "vit", "transformer", "computer vision", "training", "epoch", "detection", "satellite", "isro", "dota"]
                    shared_cv = [t for t in cv_terms if t in text_a and t in text_b]
                    
                    shopping_terms = ["amazon", "flipkart", "order", "receipt", "invoice", "gst", "total", "rupees", "paid"]
                    shared_shop = [t for t in shopping_terms if t in text_a and t in text_b]

                    travel_terms = ["goa", "hotel", "booking", "restaurant", "trip", "deluxe"]
                    shared_travel = [t for t in travel_terms if t in text_a and t in text_b]

                    if len(shared_cv) >= 2:
                        rel = {
                            "type": "same_project",
                            "confidence": 0.88,
                            "reason": f"Computer Vision project: shared concepts ({', '.join(shared_cv[:3])})",
                        }
                    elif len(shared_shop) >= 2:
                        rel = {
                            "type": "related_topic",
                            "confidence": 0.78,
                            "reason": f"Purchases & invoices: shared commerce terms ({', '.join(shared_shop[:3])})",
                        }
                    elif len(shared_travel) >= 2:
                        rel = {
                            "type": "same_event",
                            "confidence": 0.82,
                            "reason": f"Goa travel: shared location & booking details ({', '.join(shared_travel[:2])})",
                        }

                if rel:
                    # Add bidirectional edges
                    ev_text = rel.get("evidence") or rel.get("reason", "")
                    r1 = Relationship(
                        source_memory_id=m_a["id"],
                        target_memory_id=m_b["id"],
                        relationship_type=rel["type"],
                        confidence=rel["confidence"],
                        reason=rel["reason"],
                        evidence=ev_text,
                    )
                    r2 = Relationship(
                        source_memory_id=m_b["id"],
                        target_memory_id=m_a["id"],
                        relationship_type=rel["type"],
                        confidence=rel["confidence"],
                        reason=rel["reason"],
                        evidence=ev_text,
                    )
                    db.add(r1)
                    db.add(r2)
                    total_created += 2

        await db.commit()
        print(f"Created {total_created} relationship edges across the memory graph.")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(enrich())
