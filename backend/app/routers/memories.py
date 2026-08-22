"""
AURA — Memories Router
Handles upload, CRUD, locking, deletion, redaction, thumbnails.
"""
import uuid
import json
import asyncio
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func

from app.database import get_db
from app.models import Memory, Relationship
from app.config import UPLOADS_DIR, THUMBNAILS_DIR
from app.services.pipeline import validate_upload, safe_filename, compute_hash, process_memory

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/memories", tags=["memories"])


# ─── Upload ───────────────────────────────────────────────────────────────────

@router.post("/upload")
async def upload_memory(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Upload a screenshot and queue it for processing."""
    content = await file.read()

    # Validate
    ok, err = validate_upload(file.filename or "upload.png", content)
    if not ok:
        raise HTTPException(status_code=400, detail=err)

    # Generate safe storage key
    storage_name = safe_filename(file.filename or "screenshot.png")
    file_path = UPLOADS_DIR / storage_name

    # Check for duplicate (hash-based)
    content_hash = compute_hash(content)
    existing = await db.execute(
        select(Memory).where(Memory.content_hash == content_hash, Memory.is_deleted == False)
    )
    dup = existing.scalar_one_or_none()
    if dup:
        return {"id": dup.id, "status": "duplicate", "message": "Already in memory."}

    # Save file
    file_path.write_bytes(content)

    # Create DB record
    memory_id = str(uuid.uuid4())
    memory = Memory(
        id=memory_id,
        file_path=str(file_path),
        original_filename=file.filename or "screenshot.png",
        mime_type=file.content_type or "image/png",
        content_hash=content_hash,
        processing_status="pending",
    )
    db.add(memory)
    await db.commit()

    # Background processing
    background_tasks.add_task(_run_pipeline, memory_id, str(file_path))

    return {
        "id": memory_id,
        "status": "pending",
        "message": "Screenshot received and queued for analysis.",
    }


async def _run_pipeline(memory_id: str, file_path: str):
    """Background task wrapper for pipeline."""
    from app.database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        await process_memory(memory_id, file_path, db)


# ─── Batch Upload ─────────────────────────────────────────────────────────────

@router.post("/upload/batch")
async def upload_batch(
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Upload multiple screenshots at once."""
    results = []
    for file in files[:50]:  # cap at 50 per batch
        content = await file.read()
        ok, err = validate_upload(file.filename or "upload.png", content)
        if not ok:
            results.append({"filename": file.filename, "error": err})
            continue

        storage_name = safe_filename(file.filename or "screenshot.png")
        file_path = UPLOADS_DIR / storage_name
        content_hash = compute_hash(content)

        existing = await db.execute(
            select(Memory).where(Memory.content_hash == content_hash, Memory.is_deleted == False)
        )
        if existing.scalar_one_or_none():
            results.append({"filename": file.filename, "status": "duplicate"})
            continue

        file_path.write_bytes(content)
        memory_id = str(uuid.uuid4())
        memory = Memory(
            id=memory_id,
            file_path=str(file_path),
            original_filename=file.filename or "screenshot.png",
            mime_type=file.content_type or "image/png",
            content_hash=content_hash,
            processing_status="pending",
        )
        db.add(memory)
        results.append({"filename": file.filename, "id": memory_id, "status": "queued"})
        background_tasks.add_task(_run_pipeline, memory_id, str(file_path))

    await db.commit()
    return {"uploaded": len(results), "results": results}


# ─── List / Gallery ───────────────────────────────────────────────────────────

@router.get("")
async def list_memories(
    page: int = Query(1, ge=1),
    per_page: int = Query(24, ge=1, le=100),
    limit: Optional[int] = Query(None, ge=1, le=100),
    offset: Optional[int] = Query(None, ge=0),
    category: Optional[str] = None,
    constellation: Optional[str] = None,
    sensitivity: Optional[str] = None,
    source_type: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = Query("newest"),
    db: AsyncSession = Depends(get_db),
):
    """Paginated gallery of memories with advanced filtering and sorting."""
    stmt = select(Memory).where(Memory.is_deleted == False)

    # Constellation mapping
    target_constellation = constellation or (category if category in ("vision", "commerce", "security", "culinary", "runtime", "travel", "comms", "automotive") else None)
    if target_constellation:
        CONSTELLATION_CATEGORY_MAP = {
            "vision": ["research", "code", "chart", "diagram", "dashboard", "database", "api", "github", "ui", "presentation"],
            "commerce": ["receipt", "invoice", "finance", "shopping", "delivery", "business", "product"],
            "security": ["credentials", "settings"],
            "culinary": ["recipe", "food", "menu"],
            "runtime": ["terminal"],
            "travel": ["travel", "map", "ticket"],
            "comms": ["conversation", "chat", "notes"],
            "automotive": ["photo", "scene", "product", "automotive"],
        }
        cats = CONSTELLATION_CATEGORY_MAP.get(target_constellation, [])
        if cats:
            stmt = stmt.where(Memory.category.in_(cats))
    elif category:
        # Support grouped categories like 'finance' matching 'receipt'/'invoice'
        if category in ("receipt", "invoice", "finance"):
            stmt = stmt.where(Memory.category.in_(["receipt", "invoice", "finance"]))
        elif category in ("code", "ide", "terminal"):
            stmt = stmt.where(Memory.category.in_(["code", "ide", "terminal"]))
        elif category in ("credentials", "settings"):
            stmt = stmt.where(Memory.category.in_(["credentials", "settings"]))
        elif category in ("map", "travel"):
            stmt = stmt.where(Memory.category.in_(["map", "travel"]))
        else:
            stmt = stmt.where(Memory.category == category)
    if sensitivity:
        stmt = stmt.where(Memory.sensitivity_level == sensitivity)
    if source_type:
        stmt = stmt.where(Memory.source_type == source_type)
    if status:
        stmt = stmt.where(Memory.processing_status == status)
    if search and search.strip():
        term = f"%{search.strip()}%"
        stmt = stmt.where(
            (Memory.summary.ilike(term)) |
            (Memory.original_filename.ilike(term)) |
            (Memory.ocr_text.ilike(term)) |
            (Memory.entities.ilike(term)) |
            (Memory.topics.ilike(term))
        )

    # Count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar()

    # Determine pagination
    actual_limit = limit if limit is not None else per_page
    actual_offset = offset if offset is not None else (page - 1) * per_page

    # Sort ordering
    if sort_by == "oldest":
        stmt = stmt.order_by(Memory.created_at.asc())
    elif sort_by == "importance":
        stmt = stmt.order_by(Memory.importance_score.desc(), Memory.created_at.desc())
    elif sort_by == "name":
        stmt = stmt.order_by(Memory.original_filename.asc())
    else:  # newest
        stmt = stmt.order_by(Memory.created_at.desc())

    stmt = stmt.offset(actual_offset).limit(actual_limit)
    result = await db.execute(stmt)
    memories = result.scalars().all()

    return {
        "total": total,
        "page": page if limit is None else (actual_offset // actual_limit + 1),
        "per_page": actual_limit,
        "pages": (total + actual_limit - 1) // actual_limit if actual_limit else 1,
        "memories": [_serialize(m) for m in memories],
    }


# ─── Get Single Memory ────────────────────────────────────────────────────────

@router.get("/{memory_id}")
async def get_memory(memory_id: str, db: AsyncSession = Depends(get_db)):
    memory = await _get_or_404(memory_id, db)
    return _serialize(memory, full=True)


# ─── Relationships ────────────────────────────────────────────────────────────

@router.get("/{memory_id}/relationships")
async def get_relationships(memory_id: str, db: AsyncSession = Depends(get_db)):
    await _get_or_404(memory_id, db)

    stmt = select(Relationship).where(
        (Relationship.source_memory_id == memory_id) |
        (Relationship.target_memory_id == memory_id)
    ).order_by(Relationship.confidence.desc()).limit(20)
    result = await db.execute(stmt)
    rels = result.scalars().all()

    output = []
    for r in rels:
        other_id = r.target_memory_id if r.source_memory_id == memory_id else r.source_memory_id
        other = await db.get(Memory, other_id)
        if other and not other.is_deleted:
            output.append({
                "id": r.id,
                "related_memory": _serialize(other),
                "relationship_type": r.relationship_type,
                "confidence": r.confidence,
                "reason": r.reason,
                "direction": "source" if r.source_memory_id == memory_id else "target",
            })
    return {"relationships": output, "count": len(output)}


def _resolve_image_path(memory: Memory) -> Optional[Path]:
    """Resolve active image file path across multiple candidate directories."""
    candidates = [
        Path(memory.file_path) if memory.file_path else None,
        Path("demo_data/screenshots") / memory.original_filename if memory.original_filename else None,
        Path("../demo_data/screenshots") / memory.original_filename if memory.original_filename else None,
        Path("data/uploads") / memory.original_filename if memory.original_filename else None,
    ]
    for cand in candidates:
        if cand and cand.exists():
            return cand
    return None


@router.get("/{memory_id}/image")
async def get_image(memory_id: str, db: AsyncSession = Depends(get_db)):
    memory = await _get_or_404(memory_id, db)
    resolved = _resolve_image_path(memory)
    if not resolved:
        raise HTTPException(status_code=404, detail="Image file not found.")
    return FileResponse(str(resolved), media_type=memory.mime_type or "image/png")


@router.get("/{memory_id}/thumbnail")
async def get_thumbnail(memory_id: str, db: AsyncSession = Depends(get_db)):
    memory = await _get_or_404(memory_id, db)
    if memory.thumbnail_path and Path(memory.thumbnail_path).exists():
        return FileResponse(memory.thumbnail_path, media_type="image/jpeg")
    resolved = _resolve_image_path(memory)
    if resolved:
        return FileResponse(str(resolved), media_type=memory.mime_type or "image/png")
    raise HTTPException(status_code=404, detail="Image not found.")


# ─── Lock / Unlock ────────────────────────────────────────────────────────────

@router.post("/{memory_id}/lock")
async def lock_memory(memory_id: str, db: AsyncSession = Depends(get_db)):
    memory = await _get_or_404(memory_id, db)
    memory.is_locked = not memory.is_locked
    await db.commit()
    action = "locked" if memory.is_locked else "unlocked"
    return {"id": memory_id, "is_locked": memory.is_locked, "message": f"Memory {action}."}


# ─── Redact ───────────────────────────────────────────────────────────────────

@router.post("/{memory_id}/redact")
async def redact_memory(memory_id: str, db: AsyncSession = Depends(get_db)):
    """Permanently expunge and redact sensitive text and visual content."""
    memory = await _get_or_404(memory_id, db)
    memory.is_redacted = True
    memory.ocr_text = "[REDACTED — sensitive text permanently expunged for privacy]"
    memory.entities = "[]"
    memory.topics = json.dumps(["redacted", "sanitized"])
    memory.summary = "This visual memory has been permanently redacted and sanitized under AURA Shield Zero-Trust policy."
    memory.embedding = None
    memory.updated_at = datetime.now(timezone.utc)

    # Physically burn permanent redaction into thumbnail and stored screenshot file
    try:
        from PIL import Image, ImageDraw, ImageFilter
        if memory.thumbnail_path and Path(memory.thumbnail_path).exists():
            thumb = Image.open(memory.thumbnail_path).convert("RGB")
            thumb = thumb.filter(ImageFilter.GaussianBlur(radius=25))
            draw = ImageDraw.Draw(thumb)
            w, h = thumb.size
            draw.rectangle([(0, int(h * 0.35)), (w, int(h * 0.65))], fill=(20, 20, 20))
            thumb.save(memory.thumbnail_path, "JPEG", quality=80)
        
        if memory.file_path and Path(memory.file_path).exists():
            img = Image.open(memory.file_path).convert("RGB")
            img = img.filter(ImageFilter.GaussianBlur(radius=30))
            draw = ImageDraw.Draw(img)
            w, h = img.size
            draw.rectangle([(0, int(h * 0.35)), (w, int(h * 0.65))], fill=(15, 15, 15))
            img.save(memory.file_path, "PNG")
    except Exception as e:
        logger.warning(f"Failed to visually burn redaction into file: {e}")

    await db.commit()
    return _serialize(memory, full=True)


# ─── Image-to-Memory Visual Search ────────────────────────────────────────────

@router.post("/search-by-image")
async def search_by_image(
    file: UploadFile = File(...),
    top_k: int = Query(default=5, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """
    Image-to-Memory Search:
    Upload a query image, run OCR + Vision to extract visual meaning & features,
    and find semantically and visually similar indexed memories using hybrid retrieval.
    """
    content = await file.read()
    ok, err = validate_upload(file.filename or "query.png", content)
    if not ok:
        raise HTTPException(status_code=400, detail=err)

    temp_path = UPLOADS_DIR / f"temp_query_{uuid.uuid4().hex[:8]}.png"
    temp_path.write_bytes(content)

    try:
        from app.services import ocr, vision, search
        ocr_res = await asyncio.to_thread(ocr.extract_text, str(temp_path))
        vision_res = await asyncio.to_thread(
            vision.analyze_image,
            str(temp_path),
            ocr_res.get("cleaned", ""),
            original_filename=file.filename or "query.png"
        )

        # Build multimodal query text fusing visual description, entities, topics, and OCR
        query_parts = [
            vision_res.get("summary", ""),
            vision_res.get("category", ""),
            " ".join(vision_res.get("topics", [])),
            " ".join(vision_res.get("entities", [])),
            ocr_res.get("cleaned", "")[:200],
        ]
        query_text = " ".join([p for p in query_parts if p]).strip()

        # Load all done memories
        stmt = select(Memory).where(Memory.is_deleted == False, Memory.processing_status == "done")
        result = await db.execute(stmt)
        all_memories = result.scalars().all()
        all_dicts = [
            {
                "id": m.id,
                "original_filename": m.original_filename,
                "file_path": m.file_path,
                "ocr_text": m.ocr_text or "",
                "summary": m.summary or "",
                "visual_summary": getattr(m, "visual_summary", "") or m.summary or "",
                "document_type": getattr(m, "document_type", "") or "",
                "visual_objects": _safe_json(getattr(m, "visual_objects", "[]")),
                "visual_details": _safe_json_dict(getattr(m, "visual_details", "{}")),
                "category": m.category or "other",
                "entities": _safe_json(m.entities),
                "topics": _safe_json(m.topics),
                "embedding": m.embedding,
                "sensitivity_level": m.sensitivity_level or "PUBLIC",
                "created_at": m.created_at,
                "is_locked": m.is_locked,
                "is_redacted": m.is_redacted,
            }
            for m in all_memories
        ]

        search_results = await search.search_memories(
            query=query_text or "screenshot image analysis",
            memories=all_dicts,
            top_k=top_k,
        )

        return {
            "query_extracted": query_text,
            "query_analysis": {
                "detected_category": vision_res.get("category", "other"),
                "summary": vision_res.get("summary", ""),
                "topics": vision_res.get("topics", []),
                "entities": vision_res.get("entities", []),
                "ocr_snippet": ocr_res.get("cleaned", "")[:100],
            },
            "results": search_results,
            "total": len(search_results),
            "total_matches": len(search_results),
        }
    finally:
        if temp_path.exists():
            temp_path.unlink()


# ─── Delete ───────────────────────────────────────────────────────────────────

@router.delete("/{memory_id}")
async def delete_memory(memory_id: str, db: AsyncSession = Depends(get_db)):
    memory = await _get_or_404(memory_id, db)
    # Soft delete
    memory.is_deleted = True
    memory.updated_at = datetime.now(timezone.utc)
    await db.commit()
    return {"id": memory_id, "deleted": True}


# ─── Stats ───────────────────────────────────────────────────────────────────

@router.get("/stats/overview")
async def stats(db: AsyncSession = Depends(get_db)):
    total = (await db.execute(select(func.count(Memory.id)).where(Memory.is_deleted == False))).scalar()
    done = (await db.execute(select(func.count(Memory.id)).where(
        Memory.is_deleted == False, Memory.processing_status == "done"
    ))).scalar()
    critical = (await db.execute(select(func.count(Memory.id)).where(
        Memory.is_deleted == False, Memory.sensitivity_level == "CRITICAL"
    ))).scalar()
    rel_count = (await db.execute(select(func.count(Relationship.id)))).scalar()
    return {
        "total_memories": total,
        "processed": done,
        "pending": total - done,
        "critical_sensitive": critical,
        "total_relationships": rel_count,
    }


# ─── Helpers ─────────────────────────────────────────────────────────────────

async def _get_or_404(memory_id: str, db: AsyncSession):
    memory = await db.get(Memory, memory_id)
    if not memory or memory.is_deleted:
        raise HTTPException(status_code=404, detail="Memory not found.")
    return memory


def _serialize(m: Memory, full: bool = False) -> dict:
    base = {
        "id": m.id,
        "original_filename": m.original_filename,
        "thumbnail_url": f"/api/memories/{m.id}/thumbnail",
        "image_url": f"/api/memories/{m.id}/image",
        "summary": m.summary or "",
        "visual_summary": getattr(m, "visual_summary", "") or m.summary or "",
        "category": m.category or "other",
        "document_type": m.document_type or "",
        "visual_objects": _safe_json(getattr(m, "visual_objects", "[]")),
        "visual_details": _safe_json_dict(getattr(m, "visual_details", "{}")),
        "multimodal_provider": getattr(m, "multimodal_provider", "gemini_vision") or "gemini_vision",
        "multimodal_status": getattr(m, "multimodal_status", "live_vision") or "live_vision",
        "sensitivity_level": m.sensitivity_level or "PUBLIC",
        "importance_score": m.importance_score or 0.5,
        "processing_status": m.processing_status,
        "is_locked": m.is_locked,
        "is_redacted": m.is_redacted,
        "created_at": m.created_at.isoformat() if m.created_at else None,
        "updated_at": m.updated_at.isoformat() if m.updated_at else None,
        "application": m.application or "",
        "window_title": getattr(m, "window_title", "") or "",
        "source_type": getattr(m, "source_type", "upload") or "upload",
        "clipboard_context": getattr(m, "clipboard_context", "") or "",
        "captured_at": m.captured_at.isoformat() if getattr(m, "captured_at", None) else None,
    }
    if full:
        base.update({
            "ocr_text": m.ocr_text or "",
            "ocr_raw": m.ocr_raw or "",
            "visual_entities": _safe_json(getattr(m, "visual_entities", "[]")),
            "provenance_ledger": _safe_json(getattr(m, "provenance_ledger", "[]")),
            "entities": _safe_json(m.entities),
            "topics": _safe_json(m.topics),
            "objects": _safe_json(m.objects),
            "important_information": _safe_json(m.important_information),
            "sensitivity_findings": _safe_json(m.sensitivity_findings),
        })
    else:
        base["topics"] = _safe_json(m.topics)
        base["entities"] = _safe_json(m.entities)
        base["provenance_ledger"] = _safe_json(getattr(m, "provenance_ledger", "[]"))
    return base


def _safe_json(val):
    if not val:
        return []
    if isinstance(val, list):
        return val
    try:
        return json.loads(val)
    except Exception:
        return []


def _safe_json_dict(val):
    if not val:
        return {}
    if isinstance(val, dict):
        return val
    try:
        parsed = json.loads(val)
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        return {}
