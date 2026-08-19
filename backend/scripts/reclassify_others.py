"""
AURA — Reclassify 'other' Memories Script
Scans all memories in the SQLite DB, applies enhanced forced-choice classification,
and updates category, summary, and importance score.
"""
import sys
import os
import asyncio
import json
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import AsyncSessionLocal
from app.models import Memory
from app.services.vision import classify_category
from app.services.pipeline import _compute_importance
from sqlalchemy import select, update

async def reclassify_all():
    print("=== AURA Category Reclassification Audit ===")
    async with AsyncSessionLocal() as db:
        stmt = select(Memory).where(Memory.is_deleted == False)
        res = await db.execute(stmt)
        memories = res.scalars().all()
        print(f"Total memories in database: {len(memories)}")

        before_cats = {}
        for m in memories:
            c = m.category or "other"
            before_cats[c] = before_cats.get(c, 0) + 1

        print(f"\nBefore Reclassification:")
        for k, v in sorted(before_cats.items(), key=lambda x: -x[1]):
            print(f"  {k:20s}: {v:3d} ({round(100*v/len(memories)):2d}%)")

        updated_count = 0
        for m in memories:
            old_cat = m.category or "other"
            new_cat = classify_category(
                filename=m.original_filename,
                ocr_text=m.ocr_text or "",
                vision_cat=old_cat,
                summary=m.summary or ""
            )

            if new_cat != old_cat:
                m.category = new_cat
                # Update importance if needed
                importance = _compute_importance(
                    ocr_length=len(m.ocr_text or ""),
                    has_entities=bool(m.entities and m.entities != "[]"),
                    sensitivity=m.sensitivity_level or "PUBLIC",
                    category=new_cat,
                )
                m.importance_score = importance

                # If summary was a generic "other" summary, update it
                if "containing extracted graphical" in (m.summary or ""):
                    m.summary = f"Visual capture of {m.original_filename.replace('_', ' ').replace('.png', '').replace('.jpg', '').title()} ({new_cat})."

                updated_count += 1
                print(f"  [RECLASSIFIED] {m.original_filename[:35]:35s} : {old_cat:10s} -> {new_cat:10s}")

        await db.commit()

        # Check after
        res2 = await db.execute(select(Memory).where(Memory.is_deleted == False))
        memories2 = res2.scalars().all()
        after_cats = {}
        for m in memories2:
            c = m.category or "other"
            after_cats[c] = after_cats.get(c, 0) + 1

        print(f"\nAfter Reclassification ({updated_count} updated):")
        for k, v in sorted(after_cats.items(), key=lambda x: -x[1]):
            print(f"  {k:20s}: {v:3d} ({round(100*v/len(memories2)):2d}%)")

        other_count = after_cats.get("other", 0)
        pct = round(100 * other_count / len(memories2))
        print(f"\nResult: 'other' is now {other_count}/{len(memories2)} ({pct}%)")
        if other_count <= 10:
            print("SUCCESS: Target achieved ('other' <= 10 memories).")
        else:
            print("WARNING: 'other' is still above 10 memories.")

if __name__ == "__main__":
    asyncio.run(reclassify_all())
