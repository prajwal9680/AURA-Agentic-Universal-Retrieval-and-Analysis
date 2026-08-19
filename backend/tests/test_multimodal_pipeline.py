"""
AURA — Multimodal Pipeline & Provider Unit Tests
Verifies provider abstraction, honest degraded-mode reporting,
dual-path extraction, structured fact provenance, and candidate image inspection.
"""

import pytest
import os
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.vision_provider import (
    BaseVisionProvider,
    GeminiVisionProvider,
    VerifiedCacheVisionProvider,
    SafeDegradedVisionProvider,
    UnifiedVisionProvider,
    get_vision_provider,
)
from app.services.embeddings import build_memory_text, embed_memory
from app.services.pipeline import _compute_importance
from app.services.shield import scan_text


class TestVisionProviderAbstraction:
    """Test suite for VisionProvider interface and implementations."""

    def test_safe_degraded_provider_status(self):
        """Safe degraded provider must declare DEGRADED_OCR status and is_live=False."""
        provider = SafeDegradedVisionProvider()
        info = provider.get_provider_info()
        assert info["status"] == "DEGRADED_OCR"
        assert info["is_live"] is False
        assert "ocr_deterministic_extractor" in info["provider"]

    def test_factory_returns_base_vision_provider(self):
        """Factory function must return an instance implementing BaseVisionProvider."""
        provider = get_vision_provider()
        assert isinstance(provider, BaseVisionProvider)
        assert isinstance(provider, UnifiedVisionProvider)

    def test_verified_cache_provider_structured_output(self):
        """Verified cache provider must return full AURA Vision schema with visual details and provenance."""
        provider = VerifiedCacheVisionProvider()
        result = provider.analyze_image(
            image_path="demo_data/screenshots/product_comparison_laptops.png",
            ocr_text="ASUS TUF Gaming A15 Intel Core i7 RTX 4060",
            original_filename="product_comparison_laptops.png"
        )
        assert "visual_summary" in result
        assert "visual_details" in result
        assert "visual_objects" in result
        assert "document_type" in result
        assert result["category"] == "product"
        assert result["document_type"] == "comparison_table"
        assert result["multimodal_status"] == "live_vision"
        assert len(result["provenance_ledger"]) > 0

    def test_candidate_inspection_interface(self):
        """inspect_candidates_for_query must return visual_evidence and visual_verification_score."""
        provider = UnifiedVisionProvider()
        candidates = [
            {
                "id": "mem_1",
                "original_filename": "ui_vscode_python.png",
                "file_path": "demo_data/screenshots/ui_vscode_python.png",
                "visual_summary": "VS Code dark editor showing PyTorch code",
                "document_type": "dark_code_editor",
                "category": "code",
                "visual_objects": ["VS Code editor window", "Python code"],
                "relevance_score": 0.65,
            }
        ]
        inspected = provider.inspect_candidates_for_query(candidates, "Find dark themed code editor")
        assert len(inspected) == 1
        assert "visual_evidence" in inspected[0]
        assert "visual_verification_score" in inspected[0]
        assert inspected[0]["verification_provenance"] in ["OCR", "VISION", "DETERMINISTIC"]


class TestCanonicalEmbeddings:
    """Test suite for canonical multimodal embeddings combining visual understanding + OCR."""

    def test_build_memory_text_balances_vision_and_ocr(self):
        """build_memory_text must incorporate visual summary, objects, layout, and document type."""
        text = build_memory_text(
            summary="Receipt for ASUS laptop",
            ocr_text="Tax Invoice Amazon Appario Retail ASUS TUF 106188",
            entities=["ASUS", "Amazon"],
            topics=["finance", "laptop purchase"],
            category="receipt",
            visual_summary="Scanned Amazon India tax invoice with GST calculation block",
            visual_objects=["merchant header", "itemized expense table", "price summary"],
            document_type="scanned_receipt",
            visual_details={"theme": "light", "layout_structure": "itemized receipt table"}
        )
        assert "Visual Scene:" in text
        assert "Visible Objects:" in text
        assert "Category: receipt" in text
        assert "Type: scanned receipt" in text
        assert "Text: Tax Invoice" in text

    def test_embed_memory_returns_384_dim_vector(self):
        """embed_memory must generate 384-dimensional vector."""
        vec = embed_memory(
            summary="VS Code Python script",
            ocr_text="import torch\nmodel = YOLO('yolov8n.pt')",
            category="code",
            visual_summary="Dark mode VS Code interface with terminal training log",
            document_type="dark_code_editor",
            visual_objects=["VS Code sidebar", "Python code pane"]
        )
        assert vec is not None
        assert len(vec) == 384


class TestShieldSecurityProvenance:
    """Test suite ensuring AURA Shield scans credentials and produces deterministic provenance."""

    def test_shield_scans_wifi_credentials(self):
        """AURA Shield must classify WPA3 keys as CRITICAL with deterministic provenance."""
        findings = scan_text("SSID: Pegasus_5G\nWPA3 Key: AeroP@ssw0rd!2026")
        assert findings["sensitivity_level"] == "CRITICAL"
        assert len(findings["findings"]) >= 1

    def test_shield_scans_api_keys(self):
        """AURA Shield must classify API keys as CRITICAL."""
        findings = scan_text("export OPENAI_API_KEY=sk-proj-abc12345678901234567890123456789012345678901234567890")
        assert findings["sensitivity_level"] == "CRITICAL"
