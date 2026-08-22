"""
AURA — Comprehensive Button & Route Audit Suite
Simulates 100% of user clicks, buttons, filters, AI actions, and routes to ensure zero dummy behaviors.
"""
import sys
import io
import json
import urllib.request
import urllib.error
from pathlib import Path

BASE = "http://127.0.0.1:8000"

def get(path: str):
    url = f"{BASE}{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "AURA-Audit"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status, json.loads(r.read().decode())

def post(path: str, data: dict):
    url = f"{BASE}{path}"
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json", "User-Agent": "AURA-Audit"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status, json.loads(r.read().decode())

def delete_req(path: str):
    url = f"{BASE}{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "AURA-Audit"}, method="DELETE")
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status, json.loads(r.read().decode())

def run_all_checks():
    passed = 0
    total = 0

    def check(name, condition, extra=""):
        nonlocal passed, total
        total += 1
        if condition:
            passed += 1
            print(f"  \033[92mPASS\033[0m  {name} {extra}")
        else:
            print(f"  \033[91mFAIL\033[0m  {name} {extra}")

    print("\n" + "="*70)
    print("AURA ZERO-DUMMY BUTTON & ROUTE AUDIT")
    print("="*70)

    # 1. Home / Navigation & Stats
    print("\n--- 1. NAVIGATION & SYSTEM STATS ---")
    status, health = get("/api/health")
    check("Health Check (/api/health)", status == 200 and health.get("status") in ("ok", "healthy"))
    
    status, stats = get("/api/stats")
    check("Stats Bar (/api/stats)", status == 200 and stats.get("total_memories", 0) >= 50, f"({stats.get('total_memories')} memories, {stats.get('total_relationships')} edges)")

    status, overview = get("/api/memories/stats/overview")
    check("Overview Stats (/api/memories/stats/overview)", status == 200 and overview.get("processed", 0) > 0)

    # 2. Home Search & Investigation Modes
    print("\n--- 2. HOME SEARCH & INVESTIGATION MODES ---")
    status, search_res = post("/api/search", {"query": "wifi password", "top_k": 5})
    check("Search Mode (POST /api/search)", status == 200 and len(search_res.get("results", [])) > 0, f"({len(search_res.get('results', []))} matches)")

    status, inv_res = post("/api/investigate", {"query": "computer vision training results", "deep": True})
    check("Investigate Mode (POST /api/investigate)", status == 200 and bool(inv_res.get("answer")) and len(inv_res.get("key_findings", [])) > 0)

    # 3. 8 Capability Bubble Triggers
    print("\n--- 3. 8 CAPABILITY BUBBLE PATHS ---")
    bubble_queries = [
        ("Wi-Fi Password", "Find my Wi-Fi password", "search"),
        ("Laptop Receipt", "Find the receipt for my laptop", "search"),
        ("CV Project Investigation", "Show me everything related to my computer vision project", "investigate"),
        ("Mushroom Recipe", "That mushroom recipe", "search"),
        ("Training Graph", "Find the graph where accuracy improved after training", "search"),
        ("Friend Address", "Find the address my friend sent me", "search"),
        ("Red Sports Car", "Find the photo of the red sports car", "search"),
        ("Terminal Traceback", "Terminal error traceback", "search"),
    ]
    for name, q, m in bubble_queries:
        if m == "search":
            st, res = post("/api/search", {"query": q, "top_k": 5})
            check(f"Bubble: '{name}'", st == 200 and len(res.get("results", [])) > 0, f"({len(res.get('results', []))} results)")
        else:
            st, res = post("/api/investigate", {"query": q, "deep": True})
            check(f"Bubble: '{name}'", st == 200 and bool(res.get("answer")), f"(confidence {res.get('confidence')})")

    # 4. Gallery Filtering & Multi-field Search
    print("\n--- 4. GALLERY FILTERS & SEARCH ---")
    st, g_all = get("/api/memories?page=1&per_page=12")
    check("Gallery All Artifacts (/api/memories)", st == 200 and len(g_all.get("memories", [])) > 0, f"(Total: {g_all.get('total')})")

    st, g_search = get("/api/memories?search=amazon")
    check("Gallery Search Keyword ('amazon')", st == 200 and len(g_search.get("memories", [])) > 0, f"({len(g_search.get('memories', []))} matching)")

    st, g_code = get("/api/memories?category=code")
    check("Gallery Category Filter ('code')", st == 200 and all(m.get("category") in ("code", "ide", "terminal") for m in g_code.get("memories", [])))

    st, g_crit = get("/api/memories?sensitivity=CRITICAL")
    check("Gallery Sensitivity Filter ('CRITICAL')", st == 200 and all(m.get("sensitivity_level") == "CRITICAL" for m in g_crit.get("memories", [])))

    # 5. Constellation Topological Graph
    print("\n--- 5. CONSTELLATION GRAPH ---")
    st, const_all = get("/api/constellation")
    nodes = const_all.get("nodes", [])
    edges = const_all.get("edges", []) or const_all.get("links", [])
    check("Constellation All Nodes & Links", st == 200 and len(nodes) >= 50 and len(edges) >= 50, f"({len(nodes)} nodes, {len(edges)} edges)")

    st, const_filt = get("/api/constellation?category=code")
    check("Constellation Category Filter ('code')", st == 200 and len(const_filt.get("nodes", [])) > 0)

    # 6. Timeline Ledger
    print("\n--- 6. TIMELINE LEDGER ---")
    st, tl = get("/api/timeline")
    groups = tl.get("groups", []) or tl.get("timeline", [])
    check("Timeline Groups (/api/timeline)", st == 200 and len(groups) > 0, f"({len(groups)} date groups)")

    # 7. Memory Detail Page Actions (Lock, Redact, AI Actions, Relationships)
    print("\n--- 7. MEMORY DETAIL & AI ACTIONS ---")
    target_mem = g_all.get("memories", [])[0]
    target_id = target_mem["id"]

    st, single = get(f"/api/memories/{target_id}")
    check("Single Memory Detail", st == 200 and single.get("id") == target_id)

    st, rels = get(f"/api/memories/{target_id}/relationships")
    check("Memory Relationships", st == 200 and "relationships" in rels)

    # Lock Toggle
    st, lock_res = post(f"/api/memories/{target_id}/lock", {})
    check("Lock Toggle Button", st == 200 and "is_locked" in lock_res)
    # Toggle back
    post(f"/api/memories/{target_id}/lock", {})

    # AI Action 1: Summarize
    st, act_sum = post("/api/actions/summarize", {"memory_id": target_id})
    check("AI Action: Summarize", st == 200 and ("summary" in act_sum.get("result", {}) or "overview" in act_sum.get("result", {})))

    # AI Action 2: Extract Expense (on a receipt)
    receipt_mems = g_search.get("memories", [])
    receipt_id = receipt_mems[0]["id"] if receipt_mems else target_id
    st, act_exp = post("/api/actions/extract-expense", {"memory_id": receipt_id})
    check("AI Action: Extract Expense", st == 200 and ("merchant" in act_exp.get("result", {}) or "total_amount" in act_exp.get("result", {})))

    # AI Action 3: Debug Code (on code)
    code_mems = g_code.get("memories", [])
    code_id = code_mems[0]["id"] if code_mems else target_id
    st, act_dbg = post("/api/actions/debug-code", {"memory_id": code_id})
    check("AI Action: Debug Code", st == 200 and ("error_type" in act_dbg.get("result", {}) or "root_cause" in act_dbg.get("result", {})))

    # 8. Zero-Trust Shield Unmasking
    print("\n--- 8. ZERO-TRUST SHIELD ---")
    st, shield_stats = get("/api/shield/stats")
    check("Shield Stats (/api/shield/stats)", st == 200 and shield_stats.get("zero_trust_enabled") is True, f"(Protected: {shield_stats.get('critical_protected')} critical)")

    crit_mems = g_crit.get("memories", [])
    if crit_mems:
        crit_id = crit_mems[0]["id"]
        st, unmask = post(f"/api/shield/unmask/{crit_id}", {})
        check("Zero-Trust Unmask Endpoint", st == 200 and unmask.get("success") is True, f"(ID: {crit_id[:8]})")

    # 9. Multimodal Image-to-Memory Visual Search
    print("\n--- 9. MULTIMODAL IMAGE SEARCH ---")
    # Test image search using synthetic multipart form data
    boundary = "----WebKitFormBoundaryAURA2026Test"
    sample_png = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06"
        b"\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01"
        b"\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="test_visual_query.png"\r\n'
        f"Content-Type: image/png\r\n\r\n"
    ).encode("utf-8") + sample_png + f"\r\n--{boundary}--\r\n".encode("utf-8")

    req = urllib.request.Request(
        f"{BASE}/api/memories/search-by-image?top_k=3",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}", "User-Agent": "AURA-Audit"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        img_res = json.loads(r.read().decode())
        check("Multimodal Visual Search (/api/memories/search-by-image)", r.status == 200 and "results" in img_res)

    print("\n" + "="*70)
    print(f"AUDIT SUMMARY: {passed}/{total} CHECKS PASSED ({(passed/total)*100:.1f}%)")
    print("="*70)
    return passed == total

if __name__ == "__main__":
    success = run_all_checks()
    sys.exit(0 if success else 1)
