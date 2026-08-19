"""
AURA — Visual Reasoning Test Suite
Covers 10 critical visual-first test cases where OCR alone is insufficient
and multimodal vision understanding is decisive.
"""

import pytest
import asyncio
from pathlib import Path
import sys

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.database import AsyncSessionLocal
from app.models import Memory
from app.services.search import search_memories, parse_query
from app.routers.memories import _serialize, _safe_json
from sqlalchemy import select


@pytest.mark.asyncio
async def get_all_indexed_memories():
    async with AsyncSessionLocal() as db:
        stmt = select(Memory).where(Memory.is_deleted == False, Memory.processing_status == "done")
        res = await db.execute(stmt)
        mems = res.scalars().all()
        return [
            {
                "id": m.id,
                "file_path": m.file_path,
                "original_filename": m.original_filename,
                "summary": m.summary or "",
                "visual_summary": getattr(m, "visual_summary", "") or m.summary or "",
                "category": m.category or "other",
                "document_type": getattr(m, "document_type", "") or "",
                "visual_objects": _safe_json(getattr(m, "visual_objects", "[]")),
                "visual_details": getattr(m, "visual_details", "{}"),
                "entities": _safe_json(m.entities),
                "topics": _safe_json(m.topics),
                "ocr_text": m.ocr_text or "",
                "embedding": m.embedding,
                "created_at": m.created_at,
                "sensitivity_level": m.sensitivity_level or "PUBLIC",
                "is_deleted": m.is_deleted,
                "is_locked": m.is_locked,
                "importance_score": m.importance_score or 0.5,
            }
            for m in mems
        ]


@pytest.mark.asyncio
class TestVisualReasoningBenchmarks:
    """10 compulsory visual reasoning queries tested against the visual memory engine."""

    async def test_query_1_laptop_comparison(self):
        """1. Find the screenshot showing a laptop comparison."""
        memories = await get_all_indexed_memories()
        assert len(memories) > 0, "No indexed memories found in database"
        results = await search_memories("Find the screenshot showing a laptop comparison", memories, top_k=5)
        top_filenames = [r["original_filename"].lower() for r in results[:3]]
        assert any("comparison" in fn or "laptop" in fn for fn in top_filenames), (
            f"Expected laptop comparison in top 3, got: {top_filenames}"
        )

    async def test_query_2_dark_themed_code_editor(self):
        """2. Find the screenshot where I was looking at a dark-themed code editor."""
        memories = await get_all_indexed_memories()
        results = await search_memories("Find the screenshot where I was looking at a dark-themed code editor", memories, top_k=5)
        top_filenames = [r["original_filename"].lower() for r in results[:3]]
        assert any("vscode" in fn or "code" in fn or "dark" in fn for fn in top_filenames), (
            f"Expected dark code editor in top 3, got: {top_filenames}"
        )

    async def test_query_3_ml_architecture(self):
        """3. Find screenshots related to my ML architecture."""
        memories = await get_all_indexed_memories()
        results = await search_memories("Find screenshots related to my ML architecture", memories, top_k=5)
        top_filenames = [r["original_filename"].lower() for r in results[:3]]
        assert any("diagram" in fn or "architecture" in fn or "neural" in fn or "transformer" in fn for fn in top_filenames), (
            f"Expected architecture diagram in top 3, got: {top_filenames}"
        )

    async def test_query_4_laptop_purchase_receipt(self):
        """4. Find the receipt containing the laptop purchase."""
        memories = await get_all_indexed_memories()
        results = await search_memories("Find the receipt containing the laptop purchase", memories, top_k=5)
        top_filenames = [r["original_filename"].lower() for r in results[:3]]
        assert any("receipt_laptop" in fn or "receipt_amazon" in fn for fn in top_filenames), (
            f"Expected laptop receipt in top 3, got: {top_filenames}"
        )

    async def test_query_5_model_performance_graph(self):
        """5. Find the screenshot with a graph showing model performance."""
        memories = await get_all_indexed_memories()
        results = await search_memories("Find the screenshot with a graph showing model performance", memories, top_k=5)
        top_filenames = [r["original_filename"].lower() for r in results[:3]]
        assert any("chart" in fn or "loss" in fn or "matrix" in fn or "tsne" in fn for fn in top_filenames), (
            f"Expected performance graph in top 3, got: {top_filenames}"
        )

    async def test_query_6_project_visual_cluster(self):
        """6. Find screenshots visually related to this project."""
        memories = await get_all_indexed_memories()
        results = await search_memories("Show me everything related to my computer vision project", memories, top_k=6)
        categories = set(r["category"] for r in results)
        assert len(results) >= 3, "Expected at least 3 project artifacts"
        assert any(c in categories for c in ["code", "research", "chart", "presentation"]), (
            f"Expected multi-category project cluster, got categories: {categories}"
        )

    async def test_query_7_aura_architecture_diagram(self):
        """7. Find the architecture diagram for AURA."""
        memories = await get_all_indexed_memories()
        results = await search_memories("Find the architecture diagram for AURA", memories, top_k=5)
        top_filenames = [r["original_filename"].lower() for r in results[:3]]
        assert any("diagram_aura" in fn or "architecture" in fn for fn in top_filenames), (
            f"Expected AURA architecture diagram in top 3, got: {top_filenames}"
        )

    async def test_query_8_error_traceback_screen(self):
        """8. Find the screenshot where the application was showing an error."""
        memories = await get_all_indexed_memories()
        results = await search_memories("Find the screenshot where the application was showing an error", memories, top_k=5)
        top_filenames = [r["original_filename"].lower() for r in results[:3]]
        assert any("error" in fn or "traceback" in fn or "conflict" in fn or "issue" in fn for fn in top_filenames), (
            f"Expected error screen in top 3, got: {top_filenames}"
        )

    async def test_query_9_dashboard_vs_document(self):
        """9. Find screenshots containing a dashboard rather than a document."""
        memories = await get_all_indexed_memories()
        results = await search_memories("Find screenshots containing a dashboard rather than a document", memories, top_k=5)
        top_filenames = [r["original_filename"].lower() for r in results[:3]]
        assert any("dashboard" in fn or "grafana" in fn or "metrics" in fn for fn in top_filenames), (
            f"Expected dashboard in top 3, got: {top_filenames}"
        )

    async def test_query_10_shopping_records(self):
        """10. Find the screenshots related to shopping."""
        memories = await get_all_indexed_memories()
        results = await search_memories("Find the screenshots related to shopping", memories, top_k=5)
        top_filenames = [r["original_filename"].lower() for r in results[:3]]
        assert any("shopping" in fn or "cart" in fn or "product" in fn or "receipt" in fn for fn in top_filenames), (
            f"Expected shopping records in top 3, got: {top_filenames}"
        )
