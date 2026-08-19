"""AURA — Actions Router (summarize, extract-expense, debug-code)"""
import json
import uuid
import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import Memory, ActionHistory
from app.services.vision import run_action

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/actions", tags=["actions"])


class ActionRequest(BaseModel):
    memory_id: str


import asyncio

@router.post("/summarize")
@router.post("/summary")
async def summarize(req: ActionRequest, db: AsyncSession = Depends(get_db)):
    mem = await _get_memory(req.memory_id, db)
    result = await asyncio.to_thread(run_action, "summarize", mem.summary or "", mem.ocr_text or "", mem.category or "", mem.file_path)
    await _log_action(db, mem.id, "summarize", mem.summary or "", result)
    return {"memory_id": mem.id, "action": "summarize", "result": result}


@router.post("/extract-expense")
@router.post("/extract_expense")
async def extract_expense(req: ActionRequest, db: AsyncSession = Depends(get_db)):
    mem = await _get_memory(req.memory_id, db)
    result = await asyncio.to_thread(run_action, "extract_expense", mem.summary or "", mem.ocr_text or "", mem.category or "", mem.file_path)
    await _log_action(db, mem.id, "extract_expense", mem.ocr_text or "", result)
    return {"memory_id": mem.id, "action": "extract_expense", "result": result}


@router.post("/debug-code")
@router.post("/debug_code")
async def debug_code(req: ActionRequest, db: AsyncSession = Depends(get_db)):
    mem = await _get_memory(req.memory_id, db)
    result = await asyncio.to_thread(run_action, "debug_code", mem.summary or "", mem.ocr_text or "", mem.category or "", mem.file_path)
    await _log_action(db, mem.id, "debug_code", mem.ocr_text or "", result)
    return {"memory_id": mem.id, "action": "debug_code", "result": result}


@router.post("/{action_name}")
async def dynamic_action(action_name: str, req: ActionRequest, db: AsyncSession = Depends(get_db)):
    norm = action_name.replace("-", "_").lower()
    if norm in ("extract_expense", "extract_expenses", "expense"):
        return await extract_expense(req, db)
    elif norm in ("debug_code", "debug"):
        return await debug_code(req, db)
    elif norm in ("summarize", "summary"):
        return await summarize(req, db)
    else:
        mem = await _get_memory(req.memory_id, db)
        result = await asyncio.to_thread(run_action, norm, mem.summary or "", mem.ocr_text or "", mem.category or "", mem.file_path)
        await _log_action(db, mem.id, norm, mem.summary or "", result)
        return {"memory_id": mem.id, "action": norm, "result": result}


async def _get_memory(memory_id: str, db: AsyncSession) -> Memory:
    mem = await db.get(Memory, memory_id)
    if not mem or mem.is_deleted:
        raise HTTPException(status_code=404, detail="Memory not found.")
    return mem


async def _log_action(db: AsyncSession, memory_id: str, action_type: str, input_text: str, output: dict):
    entry = ActionHistory(
        id=str(uuid.uuid4()),
        memory_id=memory_id,
        action_type=action_type,
        input_text=input_text[:500],
        output_text=json.dumps(output),
    )
    db.add(entry)
    await db.commit()
