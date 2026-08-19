"""
AURA — Demo Data Seeder
Generates demo screenshots then uploads them through the pipeline.
Run: python seed/seed_demo.py
"""
import sys
import os

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import asyncio
import json
import uuid
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Generate images first
print("Step 1: Generating demo screenshots...")
from seed.generate_demo import generate_all
generate_all()

print("\nStep 2: Seeding into AURA database...")

async def seed():
    from app.database import init_db, AsyncSessionLocal
    from app.models import Memory
    from app.services.pipeline import (
        validate_upload, safe_filename, compute_hash,
        create_thumbnail, process_memory
    )
    from app.config import UPLOADS_DIR, THUMBNAILS_DIR
    from pathlib import Path
    import shutil
    from datetime import datetime, timezone, timedelta
    import random

    await init_db()

    demo_dir = Path(__file__).parent.parent.parent / "demo_data" / "screenshots"
    screenshots = sorted(demo_dir.glob("*.png"))
    print(f"Found {len(screenshots)} demo screenshots")

    # Assign realistic timestamps spread over past 30 days
    base_time = datetime.now(timezone.utc) - timedelta(days=30)

    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        for i, img_path in enumerate(screenshots):
            # Check for duplicate
            content = img_path.read_bytes()
            content_hash = compute_hash(content)
            existing = await db.execute(
                select(Memory).where(Memory.content_hash == content_hash)
            )
            if existing.scalar_one_or_none():
                print(f"  Skip (duplicate): {img_path.name}")
                continue

            # Copy to uploads
            storage_name = safe_filename(img_path.name)
            dest_path = UPLOADS_DIR / storage_name
            shutil.copy2(img_path, dest_path)

            # Create memory record
            memory_id = str(uuid.uuid4())
            # Spread timestamps over 30 days with some clustering (project-like)
            offset_days = (i / max(len(screenshots) - 1, 1)) * 28
            jitter_hours = random.uniform(-2, 2)
            created = base_time + timedelta(days=offset_days, hours=jitter_hours)

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

            print(f"  Processing [{i+1}/{len(screenshots)}]: {img_path.name}")
            result = await process_memory(memory_id, str(dest_path), db)
            status = result.get("status", "?")
            rels = result.get("relationships_created", 0)
            print(f"    → {status} | {rels} relationships created")

    print("\n✅ Demo seeding complete!")
    print("   Start AURA backend and open http://localhost:3000 to explore.")


asyncio.run(seed())
