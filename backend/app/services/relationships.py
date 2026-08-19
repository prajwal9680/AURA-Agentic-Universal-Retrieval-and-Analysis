"""
AURA — Explainable Relationship Knowledge Graph Engine
Computes multi-signal semantic, entity, project, and temporal relationships.

Standardized explainable edge types:
- SAME_ENTITY: Shared named entities/components
- SAME_PROJECT: Shared project or repository context
- SAME_TOPIC: Shared semantic concepts & topics
- SEMANTICALLY_RELATED: Dense embedding similarity >= 0.72
- TEMPORALLY_RELATED: Captured close in time during active session
- DERIVED_FROM: Causal/lineage relationship (e.g. traceback from code, receipt from order)
"""
import json
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple

from app.config import settings
from app.services.embeddings import hex_to_embedding, cosine_similarity

logger = logging.getLogger(__name__)

RELATIONSHIP_TYPES = {
    "SAME_PROJECT": "Same project or codebase effort",
    "SAME_ENTITY": "Shared key entities or system components",
    "SAME_TOPIC": "Related conceptual and technical topics",
    "SEMANTICALLY_RELATED": "High semantic similarity in dense embedding space",
    "TEMPORALLY_RELATED": "Temporal sequence — captured in close chronological proximity",
    "DERIVED_FROM": "Direct causal derivation or data artifact lineage",
}


def _safe_list(val) -> list:
    if isinstance(val, list):
        return val
    if isinstance(val, str):
        try:
            return json.loads(val)
        except Exception:
            return []
    return []


def _entity_overlap(a: list, b: list) -> tuple:
    """Returns (jaccard_score, shared_entities_list)."""
    sa = set(str(x).lower().strip() for x in a if x)
    sb = set(str(x).lower().strip() for x in b if x)
    shared = sa & sb
    union = sa | sb
    score = len(shared) / len(union) if union else 0.0
    return score, list(shared)


def _topic_overlap(a: list, b: list) -> tuple:
    sa = set(str(x).lower().strip() for x in a if x)
    sb = set(str(x).lower().strip() for x in b if x)
    if not sa or not sb:
        return 0.0, []
    shared = sa & sb
    union = sa | sb
    score = len(shared) / len(union) if union else 0.0
    return score, list(shared)


def _temporal_gap_hours(dt_a, dt_b) -> float:
    """Returns gap in hours between two datetimes."""
    try:
        if isinstance(dt_a, str):
            dt_a = datetime.fromisoformat(dt_a.replace("Z", "+00:00"))
        if isinstance(dt_b, str):
            dt_b = datetime.fromisoformat(dt_b.replace("Z", "+00:00"))
        if dt_a.tzinfo is None:
            dt_a = dt_a.replace(tzinfo=timezone.utc)
        if dt_b.tzinfo is None:
            dt_b = dt_b.replace(tzinfo=timezone.utc)
        return abs((dt_a - dt_b).total_seconds()) / 3600.0
    except Exception:
        return 999.0


def compute_relationship(mem_a: dict, mem_b: dict) -> Optional[Dict[str, Any]]:
    """
    Compute explainable relationship between two memories.
    Returns relationship dict with type, confidence, reason, and evidence.
    """
    if mem_a.get("id") == mem_b.get("id"):
        return None

    entities_a = _safe_list(mem_a.get("entities"))
    entities_b = _safe_list(mem_b.get("entities"))
    topics_a = _safe_list(mem_a.get("topics"))
    topics_b = _safe_list(mem_b.get("topics"))
    cat_a = mem_a.get("category", "other")
    cat_b = mem_b.get("category", "other")
    created_a = mem_a.get("created_at")
    created_b = mem_b.get("created_at")

    # Semantic similarity
    emb_a = hex_to_embedding(mem_a.get("embedding") or "") if isinstance(mem_a.get("embedding"), str) else mem_a.get("embedding")
    emb_b = hex_to_embedding(mem_b.get("embedding") or "") if isinstance(mem_b.get("embedding"), str) else mem_b.get("embedding")
    sem_score = cosine_similarity(emb_a, emb_b) if (emb_a is not None and emb_b is not None) else 0.0

    # Entity & topic overlap
    ent_score, shared_ents = _entity_overlap(entities_a, entities_b)
    top_score, shared_tops = _topic_overlap(topics_a, topics_b)

    # Category match
    cat_match = 1.0 if (cat_a == cat_b and cat_a != "other") else 0.0

    # OS Application & Clipboard Context
    app_a = mem_a.get("application", "")
    app_b = mem_b.get("application", "")
    clip_a = mem_a.get("clipboard_context", "")
    clip_b = mem_b.get("clipboard_context", "")
    ocr_b = (mem_b.get("ocr_text") or "").lower()
    ocr_a = (mem_a.get("ocr_text") or "").lower()
    title_a = (mem_a.get("filename") or mem_a.get("original_filename") or "").lower()
    title_b = (mem_b.get("filename") or mem_b.get("original_filename") or "").lower()
    vsum_a = (mem_a.get("visual_summary") or mem_a.get("summary") or "").lower()
    vsum_b = (mem_b.get("visual_summary") or mem_b.get("summary") or "").lower()

    # Temporal gap
    gap_hours = _temporal_gap_hours(created_a, created_b) if (created_a and created_b) else 999.0
    temp_score = 1.0 if gap_hours < 1.0 else (0.7 if gap_hours < 12.0 else (0.3 if gap_hours < 48.0 else 0.0))
    app_match = 1.0 if (app_a and app_b and app_a.lower() == app_b.lower() and gap_hours < 4.0) else 0.0

    # Heuristic project keyword discovery
    cv_terms = ["yolo", "vit", "transformer", "computer vision", "resnet", "pytorch", "epoch", "detection", "satellite", "isro", "dota"]
    shared_cv = [t for t in cv_terms if (t in title_a or t in vsum_a or t in ocr_a) and (t in title_b or t in vsum_b or t in ocr_b)]

    shopping_terms = ["amazon", "order", "receipt", "invoice", "gst", "total", "rupees", "paid", "delivery"]
    shared_shop = [t for t in shopping_terms if (t in title_a or t in vsum_a or t in ocr_a) and (t in title_b or t in vsum_b or t in ocr_b)]

    travel_terms = ["goa", "hotel", "booking", "restaurant", "trip", "flight", "boarding"]
    shared_travel = [t for t in travel_terms if (t in title_a or t in vsum_a or t in ocr_a) and (t in title_b or t in vsum_b or t in ocr_b)]

    # Decision tree for explainable relationship classification
    rel_type = None
    confidence = 0.0
    reason = ""
    evidence = ""

    if shared_cv and len(shared_cv) >= 2:
        rel_type = "SAME_PROJECT"
        confidence = 0.88
        reason = f"Computer Vision Project: shared terms ({', '.join(shared_cv[:3])})"
        evidence = f"Both memories reference computer vision components: {', '.join(shared_cv[:3])} with semantic similarity {sem_score:.2f}."

    elif shared_ents:
        rel_type = "SAME_ENTITY"
        confidence = min(0.70 + 0.30 * ent_score, 0.95)
        reason = f"Shared entities: {', '.join(shared_ents[:3])}"
        evidence = f"Both screenshots contain identical named entities ({', '.join(shared_ents[:3])})."

    elif shared_shop and len(shared_shop) >= 2:
        rel_type = "SAME_PROJECT" if "laptop" in (title_a + title_b) else "SAME_TOPIC"
        confidence = 0.80
        reason = f"Commerce & Invoices: shared terms ({', '.join(shared_shop[:3])})"
        evidence = f"Invoices and order artifacts sharing transaction terms: {', '.join(shared_shop[:3])}."

    elif shared_travel and len(shared_travel) >= 2:
        rel_type = "SAME_PROJECT"
        confidence = 0.82
        reason = f"Travel planning: shared destination ({', '.join(shared_travel[:2])})"
        evidence = f"Travel itinerary, tickets, and bookings for {', '.join(shared_travel[:2])}."

    elif ("traceback" in ocr_a or "error" in title_a) and ("code" in title_b or "python" in title_b or app_match):
        rel_type = "DERIVED_FROM"
        confidence = 0.85
        reason = "Execution error traceback derived from active script session"
        evidence = f"Error log screenshot directly derives from {mem_b.get('filename', 'code file')} session in {app_b or 'IDE'}."

    elif shared_tops and top_score >= 0.3:
        rel_type = "SAME_TOPIC"
        confidence = min(0.65 + 0.35 * top_score, 0.90)
        reason = f"Shared topics: {', '.join(shared_tops[:3])}"
        evidence = f"Both memories share domain topics: {', '.join(shared_tops[:3])}."

    elif gap_hours < 2.0 and (app_match or cat_match):
        rel_type = "TEMPORALLY_RELATED"
        confidence = 0.75
        reason = f"Captured {gap_hours:.1f}h apart in active {app_a or 'desktop'} session"
        evidence = f"Captured within {gap_hours:.1f} hours during continuous workflow in {app_a or 'desktop'}."

    elif sem_score >= 0.72:
        rel_type = "SEMANTICALLY_RELATED"
        confidence = round(sem_score, 3)
        reason = f"High semantic embedding similarity ({sem_score:.0%})"
        evidence = f"Dense visual and textual embedding cosine similarity of {sem_score:.2f}."

    if not rel_type or confidence < settings.relationship_threshold:
        return None

    return {
        "type": rel_type,
        "confidence": round(confidence, 3),
        "reason": reason,
        "evidence": evidence or reason,
    }


async def discover_relationships_for_memory(new_memory: dict, all_memories: list) -> list:
    """
    Given a newly indexed memory, incrementally discover relationships to existing memories in O(k) time.
    """
    relationships = []
    for other in all_memories:
        if other.get("id") == new_memory.get("id"):
            continue
        if other.get("is_deleted") or other.get("processing_status") != "done":
            continue

        rel = compute_relationship(new_memory, other)
        if rel:
            relationships.append({
                "source_memory_id": new_memory["id"],
                "target_memory_id": other["id"],
                "relationship_type": rel["type"],
                "confidence": rel["confidence"],
                "reason": rel["reason"],
                "evidence": rel["evidence"],
            })

    # Sort by confidence, keep top 10 per memory
    relationships.sort(key=lambda r: r["confidence"], reverse=True)
    return relationships[:10]

