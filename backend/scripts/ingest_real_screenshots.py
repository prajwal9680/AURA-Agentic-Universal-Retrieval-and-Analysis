"""
AURA — Ingest 8 Real Programmatic Screenshots into SQLite Database
Runs the full AURA pipeline on the 8 new screenshots.
"""
import os
import sys
import uuid
import shutil
import asyncio
from pathlib import Path
from datetime import datetime, timezone

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import AsyncSessionLocal, init_db
from app.models import Memory
from app.config import UPLOADS_DIR
from app.services.pipeline import process_memory, compute_hash, safe_filename

TARGET_FILES = [
    "receipt_swiggy_order.png",
    "receipt_amazon_india.png",
    "ui_vscode_python.png",
    "map_mumbai_local.png",
    "recipe_pasta_carbonara.png",
    "ticket_irctc_train.png",
    "ui_github_issue.png",
    "dashboard_analytics.png",
]

async def ingest_real_screenshots():
    await init_db()
    screenshots_dir = Path(__file__).parent.parent.parent / "demo_data" / "screenshots"

    async with AsyncSessionLocal() as db:
        for fname in TARGET_FILES:
            src_path = screenshots_dir / fname
            if not src_path.exists():
                print(f"Skipping (not found): {fname}")
                continue

            content = src_path.read_bytes()
            content_hash = compute_hash(content)

            # Check if already exists by hash or original_filename
            from sqlalchemy import select
            res = await db.execute(select(Memory).where(Memory.content_hash == content_hash))
            existing = res.scalar_one_or_none()
            if existing:
                print(f"Already indexed: {fname} (ID: {existing.id}, Cat: {existing.category})")
                continue

            # Save to uploads
            storage_name = safe_filename(fname)
            dest_path = UPLOADS_DIR / storage_name
            shutil.copy2(src_path, dest_path)

            mem_id = str(uuid.uuid4())
            mem = Memory(
                id=mem_id,
                file_path=str(dest_path),
                original_filename=fname,
                mime_type="image/png",
                content_hash=content_hash,
                processing_status="pending",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            db.add(mem)
            await db.commit()

            print(f"Processing pipeline for: {fname} (ID: {mem_id})...")
            try:
                res_dict = await process_memory(mem_id, str(dest_path), db)
                print(f"  -> Done! Category: {res_dict.get('category')} | Shield: {res_dict.get('sensitivity_level')}")
            except Exception as e:
                print(f"  -> Error: {e}")

    print("\nAll 8 real screenshots processed into database!")

if __name__ == "__main__":
    asyncio.run(ingest_real_screenshots())
