"""
AURA — Comprehensive Backend API Surface Audit
Tests all 16 endpoints for correctness, edge-cases, data schemas, and error handling.
"""
import sys
import json
import urllib.request
import urllib.error
from pathlib import Path

# Fix Windows console UTF-8
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_URL = "http://127.0.0.1:8000"


def req(method: str, path: str, data: dict = None, expected_status: int = 200):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"} if data is not None else {}
    body = json.dumps(data).encode("utf-8") if data is not None else None
    
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request) as resp:
            status = resp.status
            content = resp.read()
            try:
                parsed = json.loads(content.decode("utf-8"))
            except Exception:
                parsed = content
            return status, parsed
    except urllib.error.HTTPError as e:
        content = e.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(content)
        except Exception:
            parsed = content
        return e.code, parsed
    except Exception as e:
        return 0, str(e)


def run_audit():
    print("=" * 70)
    print("AURA DEEP BACKEND API SURFACE & EDGE-CASE AUDIT")
    print("=" * 70)

    total_tests = 0
    passed_tests = 0

    def test(name: str, passed: bool, detail: str = ""):
        nonlocal total_tests, passed_tests
        total_tests += 1
        if passed:
            passed_tests += 1
            print(f"  [PASS] {name}" + (f" -> {detail}" if detail else ""))
        else:
            print(f"  [FAIL] {name} -> {detail}")

    # 1. Health Endpoint
    status, body = req("GET", "/api/health")
    test("GET /api/health returns 200 OK", status == 200 and body.get("status") == "ok", f"status={body.get('status')}")

    # 2. Stats Endpoint
    status, body = req("GET", "/api/stats")
    test("GET /api/stats returns counts", status == 200 and body.get("total_memories", 0) >= 30, f"memories={body.get('total_memories')}, rels={body.get('total_relationships')}")

    # 3. Memories List & Pagination
    status, body = req("GET", "/api/memories?limit=5&offset=0")
    test("GET /api/memories pagination limit 5", status == 200 and len(body.get("memories", [])) == 5, f"count={len(body.get('memories', []))}, total={body.get('total')}")

    # 4. Memories Filter by Category
    status, body = req("GET", "/api/memories?category=receipt")
    all_receipts = all(m.get("category") == "receipt" for m in body.get("memories", []))
    test("GET /api/memories?category=receipt filter", status == 200 and len(body.get("memories", [])) > 0 and all_receipts, f"count={len(body.get('memories', []))}")

    # 5. Memories Filter by Sensitivity
    status, body = req("GET", "/api/memories?sensitivity=CRITICAL")
    all_crit = all(m.get("sensitivity_level") == "CRITICAL" for m in body.get("memories", []))
    test("GET /api/memories?sensitivity=CRITICAL filter", status == 200 and len(body.get("memories", [])) >= 2 and all_crit, f"critical_count={len(body.get('memories', []))}")

    # 6. Single Memory Detail
    status, mems_body = req("GET", "/api/memories?limit=1")
    sample_id = mems_body["memories"][0]["id"]
    status, body = req("GET", f"/api/memories/{sample_id}")
    has_keys = all(k in body for k in ["id", "original_filename", "ocr_text", "summary", "category", "entities", "topics", "sensitivity_level"])
    test(f"GET /api/memories/{sample_id} schema completeness", status == 200 and has_keys, f"filename={body.get('original_filename')}")

    # 7. Single Memory Thumbnail
    status, body = req("GET", f"/api/memories/{sample_id}/thumbnail")
    test(f"GET /api/memories/{sample_id}/thumbnail returns image", status == 200 and isinstance(body, bytes) and len(body) > 100, f"bytes={len(body) if isinstance(body, bytes) else 0}")

    # 8. Invalid Memory ID (404 Handling)
    status, body = req("GET", "/api/memories/9999999")
    test("GET /api/memories/9999999 returns 404", status == 404, f"status={status}")

    # 9. Search: Normal Query
    status, body = req("POST", "/api/search", {"query": "Find the receipt for my laptop", "top_k": 3})
    top_file = body.get("results", [{}])[0].get("original_filename", "")
    test("POST /api/search laptop receipt ranking", status == 200 and "laptop" in top_file.lower(), f"top={top_file}")

    # 10. Search: Empty Query (400 validation)
    status, body = req("POST", "/api/search", {"query": "   ", "top_k": 5})
    test("POST /api/search empty query rejection (400)", status == 400, f"status={status}")

    # 11. Search: Adversarial Query String
    status, body = req("POST", "/api/search", {"query": "' OR '1'='1' -- !@#$%^&*()_+ <script>alert(1)</script>", "top_k": 5})
    test("POST /api/search adversarial injection resiliency", status == 200 and isinstance(body.get("results"), list), f"returned={len(body.get('results', []))} results")

    # 12. Search: Sensitive Protection Default Masking
    status, body = req("POST", "/api/search", {"query": "wifi password", "include_sensitive": False})
    crit_masked = any(r.get("_protected") is True for r in body.get("results", []) if r.get("sensitivity_level") in ("SENSITIVE", "CRITICAL"))
    test("POST /api/search sensitive results default protected", status == 200 and crit_masked, f"sensitive_count={body.get('sensitive_count')}")

    # 13. Investigate: Multi-Step Agentic Engine
    status, body = req("POST", "/api/investigate", {"query": "Show me everything related to my computer vision project"})
    has_inv_keys = all(k in body for k in ["answer", "confidence", "results", "clusters", "relationships", "plan", "stats"])
    test("POST /api/investigate multi-step decision synthesis", status == 200 and has_inv_keys and len(body.get("results", [])) >= 4, f"memories={len(body.get('results', []))}, clusters={len(body.get('clusters', []))}, rels={len(body.get('relationships', []))}")

    # 14. Constellation Graph Schema
    status, body = req("GET", "/api/constellation")
    nodes = body.get("nodes", [])
    edges = body.get("edges", [])
    node_ids = set(n["id"] for n in nodes)
    valid_edges = all(e["source"] in node_ids and e["target"] in node_ids for e in edges)
    test("GET /api/constellation topology integrity", status == 200 and len(nodes) >= 30 and len(edges) >= 25 and valid_edges, f"nodes={len(nodes)}, edges={len(edges)}, valid_links={valid_edges}")

    # 15. Timeline View
    status, body = req("GET", "/api/timeline")
    days = body.get("timeline", [])
    test("GET /api/timeline daily chronological feed", status == 200 and len(days) > 0, f"days={len(days)}, total_memories={body.get('total_memories')}")

    # 16. Clusters View
    status, body = req("GET", "/api/clusters")
    clusters = body.get("clusters", [])
    test("GET /api/clusters category clusters list", status == 200 and len(clusters) >= 5, f"cluster_count={len(clusters)}")

    # 17. Shield Standalone Scanner
    sample_text = "My secret token is ghp_Abc1234567890abcdefghijklmnopqrstuvwxyz and contact prajwal@gmail.com"
    status, body = req("POST", "/api/shield/scan", {"text": sample_text})
    findings = body.get("findings", [])
    has_pat = any(f.get("type") == "api_key" for f in findings)
    has_email = any(f.get("type") == "email" for f in findings)
    test("POST /api/shield/scan detection precision", status == 200 and has_pat and has_email, f"findings={len(findings)}, level={body.get('sensitivity_level')}")

    # 18. Lock & Unlock State Toggle
    status, body = req("POST", f"/api/memories/{sample_id}/lock")
    test(f"POST /api/memories/{sample_id}/lock toggle to True", status == 200 and body.get("is_locked") is True, f"locked={body.get('is_locked')}")
    
    # Verify locked memory is hidden from search
    status, search_body = req("POST", "/api/search", {"query": "Find"})
    not_in_search = all(r["id"] != sample_id for r in search_body.get("results", []))
    test(f"Locked memory {sample_id} excluded from search", not_in_search, "hidden=True")

    # Unlock back
    status, body = req("POST", f"/api/memories/{sample_id}/lock")
    test(f"POST /api/memories/{sample_id}/lock toggle back to False", status == 200 and body.get("is_locked") is False, f"locked={body.get('is_locked')}")

    print("=" * 70)
    print(f"AUDIT SUMMARY: {passed_tests}/{total_tests} ENDPOINT TESTS PASSED ({(passed_tests/total_tests)*100:.1f}%)")
    print("=" * 70)
    return passed_tests == total_tests


if __name__ == "__main__":
    success = run_audit()
    sys.exit(0 if success else 1)
