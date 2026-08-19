"""
AURA — High-Throughput Batch Vector Indexer & Graph Constellation Populator
Indexes all 342 physical multimodal screenshots with batch-encoded 384-d dense embeddings
and enriches the multi-signal knowledge graph in seconds.
"""
import sys
import os
import json
import uuid
import shutil
import time
import asyncio
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Fix Windows console UTF-8 output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))
root_dir = backend_dir.parent

from app.database import init_db, engine, Base, AsyncSessionLocal
from app.models import Memory, Relationship
from app.services.embeddings import _get_model, build_memory_text
from app.services.pipeline import safe_filename, compute_hash
from app.config import UPLOADS_DIR, THUMBNAILS_DIR
from sqlalchemy import select, delete

manifest_file = root_dir / "data" / "manifests" / "dataset_manifest_v2.json"
screenshots_dir = root_dir / "demo_data" / "screenshots"


async def main():
    print("=" * 70)
    print("  AURA HIGH-THROUGHPUT MULTIMODAL BATCH INDEXER (342 ARTIFACTS)")
    print("=" * 70)
    t0 = time.perf_counter()

    await init_db()

    with open(manifest_file, "r", encoding="utf-8") as f:
        manifest_data = json.load(f)

    records = manifest_data.get("records", [])
    print(f"Loaded {len(records)} ground-truth records from dataset_manifest_v2.json")

    # 1. Prepare batch texts for vector encoding
    texts_to_encode = []
    mem_objects = []
    base_time = datetime.now(timezone.utc) - timedelta(days=30)

    for i, r in enumerate(records):
        fn = r["filename"]
        src_path = screenshots_dir / fn
        if not src_path.exists():
            continue

        content = src_path.read_bytes()
        c_hash = compute_hash(content)

        storage_name = safe_filename(fn)
        dest_path = UPLOADS_DIR / storage_name
        shutil.copy2(src_path, dest_path)

        # Build semantic representation
        sem_text = build_memory_text(
            summary=r.get("visual_summary", ""),
            ocr_text=r.get("visual_summary", "") + " " + " ".join(r.get("entities", [])),
            entities=r.get("entities", []),
            topics=r.get("topics", []),
            category=r.get("category", "document"),
            application=r.get("app_name", ""),
            window_title=r.get("window_title", ""),
            visual_summary=r.get("visual_summary", ""),
            document_type=r.get("document_type", ""),
        )
        texts_to_encode.append(sem_text)

        created = base_time + timedelta(days=(i / max(len(records) - 1, 1)) * 28)
        mem_objects.append({
            "id": r["id"],
            "file_path": str(dest_path),
            "original_filename": fn,
            "mime_type": "image/png",
            "content_hash": c_hash,
            "title": r.get("window_title", fn),
            "summary": r.get("visual_summary", ""),
            "ocr_text": r.get("visual_summary", "") + " " + " ".join(r.get("entities", [])),
            "category": r.get("category", "document"),
            "application_name": r.get("app_name", "Desktop"),
            "window_title": r.get("window_title", fn),
            "entities": r.get("entities", []),
            "topics": r.get("topics", []),
            "sensitivity_level": r.get("sensitivity_level", "SAFE"),
            "document_type": r.get("document_type", "screenshot"),
            "processing_status": "done",
            "created_at": created,
            "updated_at": created,
        })

    # 2. Vectorize batch embeddings
    print(f"\nVectorizing {len(texts_to_encode)} semantic memory embeddings with all-MiniLM-L6-v2...")
    model = _get_model()
    embeddings = model.encode(texts_to_encode, batch_size=64, show_progress_bar=False, normalize_embeddings=True)
    print(f"✓ Vectorized {len(embeddings)} dense 384-d embeddings in {(time.perf_counter() - t0):.2f}s")

    # 3. Insert or update in database
    print("\nPersisting all memories to PostgreSQL / SQLite database...")
    async with AsyncSessionLocal() as db:
        # Clear existing memories and relationships
        await db.execute(delete(Relationship))
        await db.execute(delete(Memory))
        await db.commit()

        for mem_dict, emb in zip(mem_objects, embeddings):
            emb_list = emb.tolist() if hasattr(emb, "tolist") else list(emb)
            mem = Memory(
                id=mem_dict["id"],
                file_path=mem_dict["file_path"],
                original_filename=mem_dict["original_filename"],
                mime_type=mem_dict["mime_type"],
                content_hash=mem_dict["content_hash"],
                summary=mem_dict["summary"],
                ocr_text=mem_dict["ocr_text"],
                category=mem_dict["category"],
                application=mem_dict["application_name"],
                window_title=mem_dict["window_title"],
                entities=json.dumps(mem_dict["entities"]),
                topics=json.dumps(mem_dict["topics"]),
                visual_summary=mem_dict["summary"],
                visual_objects=json.dumps(mem_dict["entities"]),
                visual_details=json.dumps({"theme": "dark" if "code" in mem_dict["category"] or "dashboard" in mem_dict["category"] else "light"}),
                sensitivity_level=mem_dict["sensitivity_level"],
                document_type=mem_dict["document_type"],
                embedding=json.dumps(emb_list),
                processing_status="done",
                created_at=mem_dict["created_at"],
                updated_at=mem_dict["updated_at"],
            )
            db.add(mem)
        await db.commit()
    print(f"✓ Stored {len(mem_objects)} memories in database.")

    # 4. Re-enrich Knowledge Graph
    print("\nEnriching multi-signal explainable knowledge graph edges across all 342 nodes...")
    from seed.enrich_relationships import enrich
    await enrich()
    print(f"✓ Multi-signal relationship graph enriched in {(time.perf_counter() - t0):.2f}s total!")


if __name__ == "__main__":
    asyncio.run(main())
