"""
AURA — Desktop Companion & OS-Level Ingestion Router
Provides endpoints for OS-level screenshot capture, context extraction,
smart clipboard ingestion, and privacy gate configuration.
"""
import uuid
import json
import logging
from datetime import datetime, timezone
from typing import Optional
from pathlib import Path

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, desc, func

from app.database import get_db, AsyncSessionLocal
from app.models import Memory, Relationship
from app.config import UPLOADS_DIR, THUMBNAILS_DIR
from app.services.pipeline import validate_upload, safe_filename, compute_hash, process_memory

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/desktop", tags=["desktop"])

# In-memory Privacy Gate configuration (synced with desktop agent)
PRIVACY_GATE_CONFIG = {
    "capture_enabled": True,
    "is_paused": False,
    "private_mode": False,
    "hotkey": "Ctrl+Shift+A",
    "excluded_applications": [
        "1Password", "Bitwarden", "KeePass", "LastPass",
        "Chrome Incognito", "Tor Browser", "Windows Security",
        "Banking", "Authentication"
    ],
    "excluded_window_keywords": [
        "Incognito", "Private Browsing", "Password", "Master Key",
        "Sign In", "Bank", "Credit Card"
    ],
    "clipboard_memory_enabled": True,
    "last_heartbeat": None,
    "total_os_captures": 0,
}


class DesktopConfigRequest(BaseModel):
    capture_enabled: Optional[bool] = None
    is_paused: Optional[bool] = None
    private_mode: Optional[bool] = None
    clipboard_memory_enabled: Optional[bool] = None
    excluded_applications: Optional[list[str]] = None


@router.get("/status")
async def get_desktop_status(db: AsyncSession = Depends(get_db)):
    """Returns desktop companion service status, configuration, and capture metrics."""
    stmt = select(func.count(Memory.id)).where(
        Memory.source_type == "desktop_capture",
        Memory.is_deleted == False
    )
    res = await db.execute(stmt)
    os_memories_count = res.scalar() or 0

    # Check if companion is connected (heartbeat within last 60 seconds)
    is_connected = False
    if PRIVACY_GATE_CONFIG["last_heartbeat"]:
        delta = (datetime.now(timezone.utc) - PRIVACY_GATE_CONFIG["last_heartbeat"]).total_seconds()
        is_connected = delta < 60

    return {
        "status": "connected" if is_connected else "ready",
        "config": PRIVACY_GATE_CONFIG,
        "metrics": {
            "total_desktop_captures": os_memories_count,
            "privacy_gate_active": True,
            "clipboard_tracking_active": PRIVACY_GATE_CONFIG["clipboard_memory_enabled"],
        }
    }


@router.post("/heartbeat")
async def desktop_heartbeat():
    """Heartbeat signal sent by desktop agent background service."""
    PRIVACY_GATE_CONFIG["last_heartbeat"] = datetime.now(timezone.utc)
    return {"status": "ok", "config": PRIVACY_GATE_CONFIG}


@router.post("/config")
async def update_desktop_config(req: DesktopConfigRequest):
    """Update privacy gate configuration."""
    if req.capture_enabled is not None:
        PRIVACY_GATE_CONFIG["capture_enabled"] = req.capture_enabled
    if req.is_paused is not None:
        PRIVACY_GATE_CONFIG["is_paused"] = req.is_paused
    if req.private_mode is not None:
        PRIVACY_GATE_CONFIG["private_mode"] = req.private_mode
    if req.clipboard_memory_enabled is not None:
        PRIVACY_GATE_CONFIG["clipboard_memory_enabled"] = req.clipboard_memory_enabled
    if req.excluded_applications is not None:
        PRIVACY_GATE_CONFIG["excluded_applications"] = req.excluded_applications

    return {"status": "updated", "config": PRIVACY_GATE_CONFIG}


@router.post("/capture")
async def ingest_desktop_capture(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    app_name: str = Form(""),
    window_title: str = Form(""),
    clipboard_context: str = Form(""),
    captured_at: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
):
    """
    OS-Level Screenshot Ingestion Endpoint.
    Applies strict server-side Privacy Gate checks before storing and processing.
    """
    # 1. Privacy Gate Verification
    if not PRIVACY_GATE_CONFIG["capture_enabled"]:
        raise HTTPException(status_code=403, detail="OS Capture is currently disabled.")
    if PRIVACY_GATE_CONFIG["is_paused"]:
        raise HTTPException(status_code=403, detail="AURA is currently paused.")
    if PRIVACY_GATE_CONFIG["private_mode"]:
        raise HTTPException(status_code=403, detail="AURA is in Private Mode.")

    # Check application exclusion
    app_lower = app_name.lower()
    for excl in PRIVACY_GATE_CONFIG["excluded_applications"]:
        if excl.lower() in app_lower:
            raise HTTPException(
                status_code=403,
                detail=f"Capture blocked by Privacy Gate: Application '{app_name}' is in exclusion list."
            )

    # Check window title exclusion
    win_lower = window_title.lower()
    for excl_kw in PRIVACY_GATE_CONFIG["excluded_window_keywords"]:
        if excl_kw.lower() in win_lower:
            raise HTTPException(
                status_code=403,
                detail=f"Capture blocked by Privacy Gate: Window title contains sensitive keyword '{excl_kw}'."
            )

    # 2. Read and validate image content
    content = await file.read()
    ok, err = validate_upload(file.filename or "desktop_capture.png", content)
    if not ok:
        raise HTTPException(status_code=400, detail=err)

    # 3. Check for duplicates
    content_hash = compute_hash(content)
    existing = await db.execute(
        select(Memory).where(Memory.content_hash == content_hash, Memory.is_deleted == False)
    )
    dup = existing.scalar_one_or_none()
    if dup:
        return {
            "id": dup.id,
            "status": "duplicate",
            "message": "Identical screenshot already exists in visual memory."
        }

    # 4. Save file
    storage_name = safe_filename(f"os_{app_name or 'screen'}_{file.filename or 'capture.png'}")
    file_path = UPLOADS_DIR / storage_name
    file_path.write_bytes(content)

    # 5. Parse capture timestamp
    cap_time = datetime.now(timezone.utc)
    if captured_at:
        try:
            cap_time = datetime.fromisoformat(captured_at.replace("Z", "+00:00"))
        except Exception:
            pass

    # 6. Create Memory record with full OS context
    memory_id = str(uuid.uuid4())
    memory = Memory(
        id=memory_id,
        file_path=str(file_path),
        original_filename=file.filename or f"OS_Capture_{app_name}.png",
        mime_type=file.content_type or "image/png",
        content_hash=content_hash,
        application=app_name,
        window_title=window_title,
        source_type="desktop_capture",
        clipboard_context=clipboard_context[:1000] if PRIVACY_GATE_CONFIG["clipboard_memory_enabled"] else "",
        captured_at=cap_time,
        processing_status="pending",
    )
    db.add(memory)
    await db.commit()

    PRIVACY_GATE_CONFIG["total_os_captures"] += 1

    # 7. Queue pipeline processing
    background_tasks.add_task(_run_desktop_pipeline, memory_id, str(file_path))

    return {
        "id": memory_id,
        "status": "pending",
        "app_name": app_name,
        "window_title": window_title,
        "clipboard_attached": bool(clipboard_context and PRIVACY_GATE_CONFIG["clipboard_memory_enabled"]),
        "message": f"Captured from {app_name or 'Desktop'} and queued for visual intelligence analysis."
    }


async def _run_desktop_pipeline(memory_id: str, file_path: str):
    """Process OS capture asynchronously."""
    async with AsyncSessionLocal() as db:
        await process_memory(memory_id, file_path, db)
