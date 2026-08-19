"""
AURA — End-to-End Ingestion & Lifecycle Verification Test
Tests the complete real pipeline:
Upload -> OCR -> Vision -> Shield -> Embedding -> SQLite -> Searchable -> AI Action -> Lock -> Delete
"""
import sys
import os
import io
import json
import urllib.request
import urllib.parse
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

BASE_URL = "http://127.0.0.1:8000"


def run_e2e_test():
    print("=" * 75)
    print("AURA END-TO-END INGESTION, PROCESSING & LIFECYCLE ACCEPTANCE TEST")
    print("=" * 75)

    test_image_path = backend_dir.parent / "demo_data" / "screenshots" / "receipt_headphones_amazon.png"
    if not test_image_path.exists():
        print(f"ERROR: Sample test image not found at {test_image_path}")
        return False

    with open(test_image_path, "rb") as f:
        image_bytes = f.read()

    print(f"1. Prepared test image: {test_image_path.name} ({len(image_bytes)} bytes)")

    # 1. Upload via multipart/form-data
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    body = io.BytesIO()
    body.write(f"--{boundary}\r\n".encode("utf-8"))
    body.write(f'Content-Disposition: form-data; name="file"; filename="e2e_test_headphones_receipt.png"\r\n'.encode("utf-8"))
    body.write(b"Content-Type: image/png\r\n\r\n")
    body.write(image_bytes)
    body.write(f"\r\n--{boundary}--\r\n".encode("utf-8"))

    req = urllib.request.Request(
        f"{BASE_URL}/api/memories/upload",
        data=body.getvalue(),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )

    with urllib.request.urlopen(req) as resp:
        upload_resp = json.loads(resp.read().decode("utf-8"))
        print(f"2. Upload Response: status={upload_resp.get('status')}, id={upload_resp.get('id')}")

    mem_id = upload_resp.get("id")
    if not mem_id:
        print("ERROR: No memory ID returned from upload.")
        return False

    # 2. Wait for async processing pipeline to complete
    import time
    max_wait = 20
    processed = False
    mem_data = {}
    for attempt in range(max_wait):
        time.sleep(1)
        with urllib.request.urlopen(f"{BASE_URL}/api/memories/{mem_id}") as resp:
            mem_data = json.loads(resp.read().decode("utf-8"))
            status = mem_data.get("processing_status")
            if status == "done":
                processed = True
                print(f"3. Processing completed in ~{attempt+1}s: status={status}")
                break
            elif status == "error":
                print(f"ERROR: Processing failed with error: {mem_data.get('processing_error')}")
                return False

    if not processed:
        print(f"ERROR: Processing timed out after {max_wait}s (status={mem_data.get('processing_status')})")
        return False

    print(f"   * Summary: {mem_data.get('summary')[:80]}...")
    print(f"   * Category: {mem_data.get('category')}")
    print(f"   * Sensitivity: {mem_data.get('sensitivity_level')}")
    print(f"   * OCR Extracted Text Length: {len(mem_data.get('ocr_text') or '')} chars")
    print(f"   * Entities Identified: {mem_data.get('entities')}")

    # 3. Test Searchability
    search_req = urllib.request.Request(
        f"{BASE_URL}/api/search",
        data=json.dumps({"query": "headphones receipt", "top_k": 5}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(search_req) as resp:
        search_results = json.loads(resp.read().decode("utf-8")).get("results", [])
        found_in_search = any(r.get("id") == mem_id for r in search_results)
        print(f"4. Search Verification ('headphones receipt'): found_in_top5={found_in_search}")
        if found_in_search:
            print(f"   * Ranked at score: {next(r['relevance_score'] for r in search_results if r['id'] == mem_id):.2f}")

    # 4. Test AI Action on the new memory
    action_req = urllib.request.Request(
        f"{BASE_URL}/api/actions/summarize",
        data=json.dumps({"memory_id": mem_id}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(action_req) as resp:
        action_resp = json.loads(resp.read().decode("utf-8"))
        print(f"5. AI Action Execution ('summarize'):")
        print(f"   * Result: {str(action_resp.get('result', {}))[:100]}...")

    # 5. Test Lock / Unlock
    lock_req = urllib.request.Request(f"{BASE_URL}/api/memories/{mem_id}/lock", method="POST")
    with urllib.request.urlopen(lock_req) as resp:
        lock_resp = json.loads(resp.read().decode("utf-8"))
        print(f"6. Lock Toggle: is_locked={lock_resp.get('is_locked')}")

    # Verify locked memory is hidden from search
    with urllib.request.urlopen(search_req) as resp:
        post_lock_results = json.loads(resp.read().decode("utf-8")).get("results", [])
        locked_hidden = all(r.get("id") != mem_id for r in post_lock_results)
        print(f"   * Verification: Locked memory excluded from search = {locked_hidden}")

    # 6. Test Delete
    del_req = urllib.request.Request(f"{BASE_URL}/api/memories/{mem_id}", method="DELETE")
    with urllib.request.urlopen(del_req) as resp:
        del_resp = json.loads(resp.read().decode("utf-8"))
        print(f"7. Delete Operation: status={del_resp.get('status')}")

    # Verify deleted memory is completely gone from search and returns 404 on direct lookup
    with urllib.request.urlopen(search_req) as resp:
        post_del_results = json.loads(resp.read().decode("utf-8")).get("results", [])
        deleted_hidden = all(r.get("id") != mem_id for r in post_del_results)
        print(f"   * Verification: Deleted memory excluded from search = {deleted_hidden}")

    try:
        urllib.request.urlopen(f"{BASE_URL}/api/memories/{mem_id}")
        deleted_404 = False
    except urllib.error.HTTPError as e:
        deleted_404 = (e.code == 404)
    print(f"   * Verification: Direct GET on deleted memory returns 404 = {deleted_404}")

    print("=" * 75)
    success = (processed and found_in_search and locked_hidden and deleted_hidden and deleted_404)
    print(f"END-TO-END PIPELINE RESULT: {'ALL PASS (100%)' if success else 'FAIL'}")
    print("=" * 75)
    return success


if __name__ == "__main__":
    ok = run_e2e_test()
    sys.exit(0 if ok else 1)
