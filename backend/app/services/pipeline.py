"""
AURA — Ingestion Pipeline
Full processing chain: upload → thumbnail → OCR → vision → embed → shield → index → relationships
"""
import uuid
import hashlib
import json
import logging
import shutil
from pathlib import Path
from datetime import datetime, timezone

from app.config import settings, UPLOADS_DIR, THUMBNAILS_DIR
from app.services import ocr, vision, embeddings, shield, relationships

logger = logging.getLogger(__name__)

ALLOWED_MIME_TYPES = {
    "image/png", "image/jpeg", "image/gif", "image/webp",
    "image/bmp", "image/tiff"
}
MAX_SIZE_BYTES = settings.max_upload_size_mb * 1024 * 1024


def validate_upload(filename: str, content: bytes) -> tuple[bool, str]:
    """Validate file before processing. Returns (is_valid, error_message)."""
    # Size check
    if len(content) > MAX_SIZE_BYTES:
        return False, f"File too large ({len(content) // 1024 // 1024}MB). Max {settings.max_upload_size_mb}MB."

    # Extension check (basic)
    ext = Path(filename).suffix.lower()
    if ext not in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".tiff"}:
        return False, f"Unsupported file type: {ext}"

    # Magic bytes check
    magic_map = {
        b"\x89PNG": "image/png",
        b"\xff\xd8\xff": "image/jpeg",
        b"GIF8": "image/gif",
        b"RIFF": "image/webp",
        b"BM": "image/bmp",
    }
    for magic, mime in magic_map.items():
        if content[:4].startswith(magic):
            return True, ""

    # Fallback: allow if extension was fine
    return True, ""


def safe_filename(original: str) -> str:
    """Generate a safe, unique storage key from original filename."""
    stem = Path(original).stem
    # Remove dangerous characters, keep alphanumeric + dashes
    import re
    safe_stem = re.sub(r"[^a-zA-Z0-9_\-]", "_", stem)[:50]
    uid = str(uuid.uuid4())[:8]
    ext = Path(original).suffix.lower() or ".png"
    return f"{uid}_{safe_stem}{ext}"


def compute_hash(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def create_thumbnail(image_path: str, thumb_path: str, size: tuple = (400, 300)) -> bool:
    """Create a thumbnail of the screenshot."""
    try:
        from PIL import Image
        with Image.open(image_path) as img:
            img.thumbnail(size, Image.LANCZOS)
            # Convert to RGB if needed (RGBA PNG → JPEG needs this)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            img.save(thumb_path, "JPEG", quality=85, optimize=True)
        return True
    except Exception as e:
        logger.error(f"Thumbnail creation failed: {e}")
        return False


async def process_memory(memory_id: str, file_path: str, db) -> dict:
    """
    Full async processing pipeline for a single memory.
    Updates DB at each stage so UI can show progress.
    """
    from sqlalchemy import select, update
    from app.models import Memory, Relationship
    from app.services.embeddings import embedding_to_hex

    async def _update_status(status: str, **kwargs):
        stmt = update(Memory).where(Memory.id == memory_id).values(
            processing_status=status,
            updated_at=datetime.now(timezone.utc),
            **kwargs
        )
        await db.execute(stmt)
        await db.commit()

    try:
        # 1. Thumbnail
        await _update_status("processing")
        thumb_path = str(THUMBNAILS_DIR / f"{memory_id}_thumb.jpg")
        create_thumbnail(file_path, thumb_path)

        # Fetch existing memory record for metadata
        stmt_curr = select(Memory).where(Memory.id == memory_id)
        r_curr = await db.execute(stmt_curr)
        curr_mem = r_curr.scalar_one_or_none()
        orig_fn = curr_mem.original_filename if curr_mem else Path(file_path).name

        # 2. PATH A: Optical OCR Text Extraction
        await _update_status("ocr")
        ocr_result = ocr.extract_text(file_path)
        ocr_text = ocr_result["cleaned"]
        ocr_raw = ocr_result["raw"]
        ocr_entities = ocr_result.get("entities", {})

        # 3. PATH B: True Multimodal Vision-Language Pipeline (sending ACTUAL IMAGE)
        await _update_status("vision")
        vision_result = vision.analyze_image(
            file_path,
            ocr_text=ocr_text,
            original_filename=orig_fn
        )

        visual_summary = vision_result.get("visual_summary") or vision_result.get("summary", "")
        visual_details = vision_result.get("visual_details", {})
        visual_objects = vision_result.get("visual_objects", vision_result.get("objects", []))
        visual_entities = vision_result.get("visual_entities", vision_result.get("entities", []))
        document_type = vision_result.get("document_type", "")
        multimodal_provider = vision_result.get("multimodal_provider", "gemini_vision")
        multimodal_status = vision_result.get("multimodal_status", "live_vision")
        category = vision_result.get("category", "other")
        topics = vision_result.get("topics", [])

        # Merge OCR entities into vision entities
        all_entities = list(set(
            visual_entities
            + vision_result.get("entities", [])
            + ocr_entities.get("emails", [])
        ))

        # Build provenance ledger
        provenance = vision_result.get("provenance_ledger", [])
        if not provenance:
            provenance = [
                {"field": "visual_summary", "source": "VISION" if multimodal_status == "live_vision" else "DETERMINISTIC", "confidence": vision_result.get("confidence", 0.95)},
                {"field": "visual_objects", "source": "VISION" if multimodal_status == "live_vision" else "DETERMINISTIC", "confidence": 0.90},
                {"field": "visual_details", "source": "VISION" if multimodal_status == "live_vision" else "DETERMINISTIC", "confidence": 0.90},
                {"field": "category", "source": "VISION" if multimodal_status == "live_vision" else "DETERMINISTIC", "confidence": vision_result.get("confidence", 0.95)},
                {"field": "document_type", "source": "VISION" if multimodal_status == "live_vision" else "DETERMINISTIC", "confidence": 0.90},
                {"field": "ocr_text", "source": "OCR", "confidence": 0.98 if ocr_text else 0.0},
            ]

        # 4. Shield scan (deterministic regex-first engine executing before/alongside storage)
        await _update_status("shield")
        combined_text = f"{ocr_raw}\n{ocr_text}\n{visual_summary}\n{' '.join(all_entities)}"
        shield_result = shield.scan_text(combined_text)
        if shield_result.get("findings"):
            provenance.append({
                "field": "sensitivity_findings",
                "source": "DETERMINISTIC",
                "confidence": 1.0
            })

        # 5. Canonical Embedding (combining multimodal visual understanding + OCR + OS context)
        await _update_status("embedding")
        app_name = (curr_mem.application if curr_mem and curr_mem.application else vision_result.get("application", ""))
        win_title = curr_mem.window_title if curr_mem else ""
        clip_ctx = curr_mem.clipboard_context if curr_mem else ""

        emb_vec = embeddings.embed_memory(
            summary=vision_result.get("summary", ""),
            ocr_text=ocr_text,
            entities=all_entities,
            topics=topics,
            category=category,
            application=app_name,
            window_title=win_title,
            clipboard_context=clip_ctx,
            visual_summary=visual_summary,
            visual_objects=visual_objects,
            document_type=document_type,
            visual_details=visual_details,
        )
        emb_hex = embeddings.embedding_to_hex(emb_vec) if emb_vec is not None else None

        # 6. Compute importance score
        importance = _compute_importance(
            ocr_length=len(ocr_text),
            has_entities=bool(all_entities),
            sensitivity=shield_result["sensitivity_level"],
            category=category,
        )

        # 7. Save all structured multimodal fields to DB
        await _update_status(
            "done",
            thumbnail_path=thumb_path,
            ocr_text=ocr_text,
            ocr_raw=ocr_raw,
            visual_summary=visual_summary,
            visual_details=json.dumps(visual_details) if isinstance(visual_details, dict) else str(visual_details),
            visual_objects=json.dumps(visual_objects) if isinstance(visual_objects, list) else str(visual_objects),
            visual_entities=json.dumps(visual_entities) if isinstance(visual_entities, list) else str(visual_entities),
            multimodal_provider=multimodal_provider,
            multimodal_status=multimodal_status,
            provenance_ledger=json.dumps(provenance),
            summary=visual_summary or vision_result.get("summary", ""),
            category=category,
            entities=json.dumps(all_entities),
            topics=json.dumps(topics),
            objects=json.dumps(visual_objects),
            application=app_name,
            document_type=document_type,
            important_information=json.dumps(vision_result.get("important_information", [])),
            sensitivity_level=shield_result["sensitivity_level"],
            sensitivity_findings=json.dumps(shield_result.get("findings", [])),
            embedding=emb_hex,
            importance_score=importance,
        )

        # 8. Discover relationships
        await _update_status("connecting")
        stmt = select(Memory).where(
            Memory.id != memory_id,
            Memory.processing_status == "done",
            Memory.is_deleted == False,
        )
        result = await db.execute(stmt)
        all_memories_orm = result.scalars().all()
        all_memories_dicts = [_memory_to_dict(m) for m in all_memories_orm]

        # Current memory
        stmt2 = select(Memory).where(Memory.id == memory_id)
        r2 = await db.execute(stmt2)
        new_mem_orm = r2.scalar_one_or_none()
        rels = []
        if new_mem_orm:
            new_mem_dict = _memory_to_dict(new_mem_orm)
            rels = await relationships.discover_relationships_for_memory(
                new_mem_dict, all_memories_dicts
            )
            for rel in rels:
                rel_obj = Relationship(
                    source_memory_id=rel["source_memory_id"],
                    target_memory_id=rel["target_memory_id"],
                    relationship_type=rel["relationship_type"],
                    confidence=rel["confidence"],
                    reason=rel["reason"],
                )
                db.add(rel_obj)
            await db.commit()

        await _update_status("done")
        logger.info(f"Memory {memory_id} processed successfully.")
        return {"status": "done", "relationships_created": len(rels) if new_mem_orm else 0}

    except Exception as e:
        logger.error(f"Pipeline failed for {memory_id}: {e}", exc_info=True)
        await _update_status("error", processing_error=str(e)[:500])
        return {"status": "error", "error": str(e)}


def _compute_importance(ocr_length: int, has_entities: bool, sensitivity: str, category: str) -> float:
    """Heuristic importance score."""
    score = 0.5
    if ocr_length > 100:
        score += 0.1
    if has_entities:
        score += 0.1
    if sensitivity in ("SENSITIVE", "CRITICAL"):
        score += 0.15
    if category in ("receipt", "invoice", "research", "code", "credentials"):
        score += 0.1
    return min(score, 1.0)


def _memory_to_dict(m) -> dict:
    """Convert ORM Memory to plain dict for service layer."""
    return {
        "id": m.id,
        "file_path": m.file_path,
        "original_filename": m.original_filename,
        "ocr_text": m.ocr_text or "",
        "visual_summary": getattr(m, "visual_summary", "") or m.summary or "",
        "visual_details": getattr(m, "visual_details", "{}") or "{}",
        "visual_objects": getattr(m, "visual_objects", "[]") or "[]",
        "visual_entities": getattr(m, "visual_entities", "[]") or "[]",
        "multimodal_provider": getattr(m, "multimodal_provider", "gemini_vision") or "gemini_vision",
        "multimodal_status": getattr(m, "multimodal_status", "live_vision") or "live_vision",
        "provenance_ledger": getattr(m, "provenance_ledger", "[]") or "[]",
        "summary": m.summary or "",
        "category": m.category or "other",
        "document_type": getattr(m, "document_type", "") or "",
        "entities": m.entities or "[]",
        "topics": m.topics or "[]",
        "application": m.application or "",
        "window_title": getattr(m, "window_title", "") or "",
        "source_type": getattr(m, "source_type", "upload") or "upload",
        "clipboard_context": getattr(m, "clipboard_context", "") or "",
        "captured_at": getattr(m, "captured_at", None),
        "embedding": m.embedding,
        "sensitivity_level": m.sensitivity_level or "PUBLIC",
        "created_at": m.created_at,
        "processing_status": m.processing_status,
        "is_deleted": m.is_deleted,
        "is_locked": m.is_locked,
    }
