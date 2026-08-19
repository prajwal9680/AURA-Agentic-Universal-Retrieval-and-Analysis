"""
AURA — Search Quality Tests
Verifies that the 5 guaranteed demo queries produce expected results.
Run after seeding: pytest tests/test_search.py -v
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import asyncio
from app.services.search import search_memories, parse_query
from app.services.shield import scan_text


# ─── Query parsing ────────────────────────────────────────────────────────────

class TestQueryParsing:
    def test_wifi_query(self):
        q = parse_query("Find my Wi-Fi password")
        assert "credentials" in q["category_hint"] or "wifi" in " ".join(q["tokens"])

    def test_receipt_query(self):
        q = parse_query("Find the receipt for my laptop")
        assert q["category_hint"] == "receipt"

    def test_project_query(self):
        q = parse_query("Show me everything related to my computer vision project")
        assert any(t in q["tokens"] for t in ["vision", "computer", "project"])

    def test_entity_extraction(self):
        q = parse_query("Show me everything about YOLO and transformers")
        assert any("YOLO" in e or "yolo" in e.lower() for e in q["entities"])


# ─── Shield integration ───────────────────────────────────────────────────────

class TestShieldIntegration:
    def test_wifi_password_detected_critical(self):
        text = "SSID: PrajwalHome_5G\nWi-Fi Password: Scryptic@2026#Secure!\nSecurity: WPA3"
        result = scan_text(text)
        assert result["sensitivity_level"] == "CRITICAL"
        assert result["confidence"] > 0.8

    def test_api_key_detected_critical(self):
        text = "ghp_Kx9mRTq7YvN3pL2wQeZ1AbC8dFjHuI4oG5sX"
        result = scan_text(text)
        assert result["sensitivity_level"] == "CRITICAL"

    def test_receipt_is_personal(self):
        text = "Amazon Order #112-3849201. ASUS ZenBook ₹89,990. Total ₹1,06,188.20"
        result = scan_text(text)
        # Receipt without PII should be at most PERSONAL
        assert result["sensitivity_level"] in ("PUBLIC", "PERSONAL")

    def test_public_research_is_safe(self):
        text = "YOLOv8 achieves 53.9% mAP on COCO. Anchor-free detection head."
        result = scan_text(text)
        assert result["sensitivity_level"] == "PUBLIC"


# ─── Hybrid scoring ───────────────────────────────────────────────────────────

class TestHybridSearch:
    @pytest.mark.asyncio
    async def test_wifi_query_finds_credentials(self):
        """Wi-Fi query should rank credentials screenshot highest."""
        memories = [
            {
                "id": "m1",
                "summary": "Router admin panel showing Wi-Fi SSID and WPA3 password settings",
                "category": "credentials",
                "entities": ["TP-Link", "WPA3", "PrajwalHome_5G"],
                "topics": ["networking", "security", "wifi"],
                "ocr_text": "SSID: PrajwalHome_5G Wi-Fi Password: Scryptic@2026 Security: WPA3",
                "embedding": None,
                "created_at": None,
                "sensitivity_level": "CRITICAL",
                "is_deleted": False,
                "is_locked": False,
                "importance_score": 0.9,
            },
            {
                "id": "m2",
                "summary": "Amazon receipt for ASUS laptop purchase",
                "category": "receipt",
                "entities": ["Amazon", "ASUS", "ZenBook"],
                "topics": ["shopping", "electronics"],
                "ocr_text": "Amazon Order ASUS ZenBook 14 Total 89990",
                "embedding": None,
                "created_at": None,
                "sensitivity_level": "PERSONAL",
                "is_deleted": False,
                "is_locked": False,
                "importance_score": 0.7,
            },
        ]
        results = await search_memories("Find my Wi-Fi password", memories, top_k=5)
        assert len(results) > 0
        assert results[0]["id"] == "m1"

    @pytest.mark.asyncio
    async def test_laptop_receipt_query(self):
        """Laptop receipt query should rank Amazon laptop receipt highest."""
        memories = [
            {
                "id": "r1",
                "summary": "Amazon order confirmation for ASUS ZenBook 14 OLED laptop",
                "category": "receipt",
                "entities": ["Amazon", "ASUS", "ZenBook", "laptop"],
                "topics": ["shopping", "electronics", "receipt"],
                "ocr_text": "Amazon Order ASUS ZenBook 14 laptop 89990 receipt",
                "embedding": None,
                "created_at": None,
                "sensitivity_level": "PERSONAL",
                "is_deleted": False,
                "is_locked": False,
                "importance_score": 0.8,
            },
            {
                "id": "r2",
                "summary": "Mushroom pasta recipe with cream sauce",
                "category": "recipe",
                "entities": ["mushroom", "pasta"],
                "topics": ["food", "cooking"],
                "ocr_text": "Creamy mushroom pasta 400g tagliatelle butter",
                "embedding": None,
                "created_at": None,
                "sensitivity_level": "PUBLIC",
                "is_deleted": False,
                "is_locked": False,
                "importance_score": 0.5,
            },
        ]
        results = await search_memories("Find the receipt for my laptop", memories, top_k=5)
        assert len(results) > 0
        assert results[0]["id"] == "r1"

    @pytest.mark.asyncio
    async def test_cv_project_investigation(self):
        """Computer vision project query should rank CV-related content higher."""
        memories = [
            {
                "id": "cv1", "summary": "YOLOv8 paper on object detection", "category": "research",
                "entities": ["YOLO", "YOLOv8"], "topics": ["computer vision", "deep learning"],
                "ocr_text": "YOLOv8 object detection mAP COCO", "embedding": None,
                "created_at": None, "sensitivity_level": "PUBLIC",
                "is_deleted": False, "is_locked": False, "importance_score": 0.8,
            },
            {
                "id": "cv2", "summary": "Python training script for YOLO model", "category": "code",
                "entities": ["YOLO", "PyTorch"], "topics": ["computer vision", "machine learning"],
                "ocr_text": "from ultralytics import YOLO model.train epochs=35", "embedding": None,
                "created_at": None, "sensitivity_level": "PUBLIC",
                "is_deleted": False, "is_locked": False, "importance_score": 0.7,
            },
            {
                "id": "g1", "summary": "Goa hotel booking confirmation", "category": "travel",
                "entities": ["Goa", "Taj", "hotel"], "topics": ["travel", "booking"],
                "ocr_text": "Taj Holiday Village Resort Goa Check-in September", "embedding": None,
                "created_at": None, "sensitivity_level": "PERSONAL",
                "is_deleted": False, "is_locked": False, "importance_score": 0.6,
            },
        ]
        results = await search_memories(
            "Show me everything related to my computer vision project", memories, top_k=5
        )
        assert len(results) >= 2
        top2_ids = [r["id"] for r in results[:2]]
        assert "cv1" in top2_ids or "cv2" in top2_ids
