"""
AURA — Full Database Seeder with Gemini 3.7 Flash
Clean session-per-item architecture for SQLite async safety.
"""
import sys
import os
import asyncio
import uuid
import shutil
import random
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Fix Windows console UTF-8
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.database import init_db, engine, Base, AsyncSessionLocal
from app.models import Memory, Relationship, Collection, CollectionMemory, Evidence, ActionHistory, SearchSession
from app.services.pipeline import safe_filename, compute_hash, process_memory
from app.config import UPLOADS_DIR, THUMBNAILS_DIR
from sqlalchemy import select, delete

ROOT_DIR = backend_dir.parent
DEMO_DIR = ROOT_DIR / "demo_data" / "screenshots"


async def main():
    print("=" * 60, flush=True)
    print("AURA Database Seeder -- Gemini 3.7 Flash + EasyOCR", flush=True)
    print("=" * 60, flush=True)

    # 1. Reset tables
    print("\n1. Resetting database tables...", flush=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("   Database schema created.", flush=True)

    # 2. Find screenshots
    screenshots = sorted(DEMO_DIR.glob("*.png"))
    print(f"\n2. Found {len(screenshots)} screenshots in {DEMO_DIR}", flush=True)
    if len(screenshots) == 0:
        print("   Generating screenshots first...", flush=True)
        from seed.run_seed import generate_all_screenshots
        generate_all_screenshots()
        screenshots = sorted(DEMO_DIR.glob("*.png"))

    base_time = datetime.now(timezone.utc) - timedelta(days=30)

    # 3. Process each screenshot
    print("\n3. Processing screenshots through full AURA pipeline...", flush=True)
    for i, img_path in enumerate(screenshots):
        content = img_path.read_bytes()
        content_hash = compute_hash(content)

        storage_name = safe_filename(img_path.name)
        dest_path = UPLOADS_DIR / storage_name
        shutil.copy2(img_path, dest_path)

        memory_id = str(uuid.uuid4())
        offset_days = (i / max(len(screenshots) - 1, 1)) * 28
        jitter_hours = random.uniform(-2, 2)
        created = base_time + timedelta(days=offset_days, hours=jitter_hours)

        async with AsyncSessionLocal() as db:
            memory = Memory(
                id=memory_id,
                file_path=str(dest_path),
                original_filename=img_path.name,
                mime_type="image/png",
                content_hash=content_hash,
                processing_status="pending",
                created_at=created,
                updated_at=created,
            )
            db.add(memory)
            await db.commit()

            print(f"\n  [{i+1}/{len(screenshots)}] Ingesting: {img_path.name}...", flush=True)
            result = await process_memory(memory_id, str(dest_path), db)
            
            # Fetch updated record
            stmt = select(Memory).where(Memory.id == memory_id)
            res = await db.execute(stmt)
            mem = res.scalar_one_or_none()
            if mem:
                print(f"       Category: {mem.category} | Sensitivity: {mem.sensitivity_level}", flush=True)
                print(f"       Summary: {(mem.summary or '')[:75]}...", flush=True)
                print(f"       Relationships: {result.get('relationships_created', 0)}", flush=True)

    # 4. Enrich relationship graph constellation
    print("\n4. Enriching relationship constellation graph...", flush=True)
    from seed.enrich_relationships import enrich
    await enrich()

    # 5. Print summary
    async with AsyncSessionLocal() as db:
        from sqlalchemy import func
        total_mems = (await db.execute(select(func.count(Memory.id)))).scalar()
        total_rels = (await db.execute(select(func.count(Relationship.id)))).scalar()
        crit_mems = (await db.execute(select(func.count(Memory.id)).where(Memory.sensitivity_level == 'CRITICAL'))).scalar()

        print("\n" + "=" * 60, flush=True)
        print("AURA Seeding Complete!", flush=True)
        print(f"   Total Memories Indexed: {total_mems}", flush=True)
        print(f"   Total Relationships:    {total_rels}", flush=True)
        print(f"   Critical Protected:     {crit_mems}", flush=True)
        print("=" * 60, flush=True)


if __name__ == "__main__":
    asyncio.run(main())
