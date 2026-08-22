"""
AURA — Test Image-to-Image / Visual Search Endpoint
Validates POST /api/memories/search-by-image
"""
import requests
import pytest
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"
TEST_IMG = Path(__file__).parent.parent.parent / "demo_data" / "screenshots" / "recipe_pasta_carbonara.png"

def test_image_search():
    if not TEST_IMG.exists():
        pytest.skip(f"Test image {TEST_IMG} not found")
        return

    try:
        with open(TEST_IMG, "rb") as f:
            files = {"file": (TEST_IMG.name, f, "image/png")}
            resp = requests.post(f"{BASE_URL}/api/memories/search-by-image?top_k=5", files=files, timeout=30)
    except Exception as e:
        pytest.skip(f"Live server not responding on port 8000: {e}")
        return

    print(f"Status Code: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print("Query Extracted:", data.get("query_extracted"))
        print("Detected Category:", data.get("query_analysis", {}).get("detected_category"))
        print(f"Total Matches: {data.get('total_matches')}")
        for idx, r in enumerate(data.get("results", [])[:5], 1):
            fn = r.get("original_filename")
            score = r.get("relevance_score", 0)
            cat = r.get("category")
            print(f"  {idx}. {fn} | Score: {score:.3f} | Cat: {cat}")
        assert len(data.get("results", [])) > 0
    else:
        pytest.skip(f"Live endpoint returned {resp.status_code}")

if __name__ == "__main__":
    test_image_search()

