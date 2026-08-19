"""AURA — Shield Router"""
import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.database import get_db
from app.models import Memory
from app.services.shield import scan_text, scan_with_ai
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

router = APIRouter(prefix="/api/shield", tags=["shield"])


class ScanRequest(BaseModel):
    text: str


@router.post("/scan")
async def scan(req: ScanRequest, db: AsyncSession = Depends(get_db)):
    result = scan_text(req.text)
    return result


@router.get("/stats")
async def shield_stats(db: AsyncSession = Depends(get_db)):
    """Summary of Shield zero-trust protection state."""
    critical = (await db.execute(select(func.count(Memory.id)).where(
        Memory.is_deleted == False, Memory.sensitivity_level == "CRITICAL"
    ))).scalar() or 0
    sensitive = (await db.execute(select(func.count(Memory.id)).where(
        Memory.is_deleted == False, Memory.sensitivity_level == "SENSITIVE"
    ))).scalar() or 0
    personal = (await db.execute(select(func.count(Memory.id)).where(
        Memory.is_deleted == False, Memory.sensitivity_level == "PERSONAL"
    ))).scalar() or 0
    total = (await db.execute(select(func.count(Memory.id)).where(
        Memory.is_deleted == False
    ))).scalar() or 0

    return {
        "status": "active",
        "zero_trust_enabled": True,
        "critical_protected": critical,
        "sensitive_protected": sensitive,
        "personal_tagged": personal,
        "total_monitored": total,
    }


@router.post("/unmask/{memory_id}")
async def unmask_memory(memory_id: str, db: AsyncSession = Depends(get_db)):
    """User-authorized unmasking of protected secrets."""
    memory = await db.get(Memory, memory_id)
    if not memory or memory.is_deleted:
        raise HTTPException(status_code=404, detail="Memory not found.")

    findings = []
    if memory.sensitivity_findings:
        try:
            findings = json.loads(memory.sensitivity_findings)
        except Exception:
            findings = []

    return {
        "id": memory_id,
        "success": True,
        "unmasked_content": memory.ocr_text or memory.summary or "",
        "sensitivity_level": memory.sensitivity_level,
        "findings": findings,
    }
