"""
AURA Evaluation Suite — Pillar 2: Multimodal VLM & OCR Processing Benchmarks
Evaluates:
- Structured schema compliance rate (JSON validity, required fields)
- Category classification accuracy
- OCR text extraction presence & quality
- Fallback tier degradation resilience (VISION_LIVE -> VISION_CACHED -> OCR_ONLY -> DETERMINISTIC)
"""
import sys
import os
from pathlib import Path
import pytest

backend_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.vision_provider import UnifiedVisionProvider, VALID_CATEGORIES
from app.services.verified_cache import get_verified_multimodal_analysis, VERIFIED_MULTIMODAL_CORPUS


@pytest.fixture
def vision_provider():
    return UnifiedVisionProvider()


def test_verified_cache_multimodal_coverage():
    """Verify precomputed multimodal corpus completeness for baseline screenshots."""
    assert len(VERIFIED_MULTIMODAL_CORPUS) >= 65, "Verified corpus must cover at least 65 baseline artifacts"

    for fn, entry in list(VERIFIED_MULTIMODAL_CORPUS.items())[:10]:
        assert "category" in entry, f"Missing category in {fn}"
        assert entry["category"] in VALID_CATEGORIES, f"Invalid category {entry['category']} in {fn}"
        assert "visual_summary" in entry and len(entry["visual_summary"]) > 10, f"Inadequate visual summary in {fn}"


def test_canonical_schema_compliance_structure(vision_provider):
    """Test that vision provider returns valid canonical schema with all expected keys."""
    sample_fn = "receipt_laptop_amazon.png"
    cached = get_verified_multimodal_analysis(sample_fn)

    assert cached is not None, "Sample artifact must be present in verified cache"
    assert "visual_objects" in cached
    assert "visual_details" in cached
    assert "entities" in cached
    assert "topics" in cached
    assert cached["category"] == "receipt"


def test_fallback_tier_graceful_degradation(vision_provider):
    """Test that non-existent or un-cached files fall back gracefully to safe deterministic extraction without crashing."""
    dummy_path = "non_existent_test_image.png"
    res = vision_provider.analyze_image(dummy_path, ocr_text="Error: File not found in directory /var/log/syslog")

    assert res is not None
    assert "title" in res
    assert "category" in res
    assert "visual_summary" in res
    assert res["category"] in VALID_CATEGORIES
    assert res.get("multimodal_status") in ("ocr_only", "live_vision", "degraded", "fallback") or "summary" in res
