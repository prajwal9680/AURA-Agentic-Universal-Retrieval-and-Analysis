"""
AURA — Desktop Companion & OS Ingestion Test Suite
Verifies:
1. Desktop status & configuration endpoints
2. Privacy Gate application & window title exclusions (HTTP 403)
3. Private Mode blocking
4. Ingestion of OS context (app name, window title, smart clipboard)
5. End-to-end memory pipeline processing for desktop captures
"""
import sys
import io
import time
import requests
from PIL import Image

API_URL = "http://localhost:8000"

def run_tests():
    print("=" * 65)
    print("[TEST] AURA DESKTOP COMPANION & PRIVACY GATE TEST SUITE")
    print("=" * 65)
    passed = 0
    total = 0

    def assert_test(condition, label, detail=""):
        nonlocal passed, total
        total += 1
        if condition:
            passed += 1
            print(f"  PASS  {label} {detail}")
        else:
            print(f"  FAIL  {label} {detail}")

    # 1. Desktop Status
    resp = requests.get(f"{API_URL}/api/desktop/status")
    assert_test(resp.status_code == 200, "GET /api/desktop/status returns 200")
    data = resp.json()
    assert_test("config" in data and "metrics" in data, "Status response contains config and metrics")
    assert_test(data["config"]["hotkey"] == "Ctrl+Shift+A", "Default hotkey configured", f"[{data['config']['hotkey']}]")
    assert_test("1Password" in data["config"]["excluded_applications"], "1Password in default exclusion list")

    # 2. Heartbeat
    hb_resp = requests.post(f"{API_URL}/api/desktop/heartbeat")
    assert_test(hb_resp.status_code == 200, "POST /api/desktop/heartbeat returns 200")

    # 3. Privacy Gate Block on Excluded App
    img = Image.new("RGB", (400, 300), (int(time.time()*100)%256, 120, 200))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    img_bytes = buf.getvalue()

    blocked_resp = requests.post(
        f"{API_URL}/api/desktop/capture",
        files={"file": ("screen.png", img_bytes, "image/png")},
        data={
            "app_name": "1Password.exe",
            "window_title": "1Password Master Vault",
            "clipboard_context": "",
        }
    )
    assert_test(blocked_resp.status_code == 403, "Privacy Gate blocks excluded app 1Password (HTTP 403)", f"[{blocked_resp.status_code}]")
    assert_test("Privacy Gate" in blocked_resp.text, "Response explains Privacy Gate block reason")

    # 4. Privacy Gate Block on Sensitive Window Title Keyword
    win_block_resp = requests.post(
        f"{API_URL}/api/desktop/capture",
        files={"file": ("screen.png", img_bytes, "image/png")},
        data={
            "app_name": "Google Chrome",
            "window_title": "Google Chrome - Private Browsing Incognito Mode",
            "clipboard_context": "",
        }
    )
    assert_test(win_block_resp.status_code == 403, "Privacy Gate blocks Incognito window (HTTP 403)", f"[{win_block_resp.status_code}]")

    # 5. Successful OS Capture with Context & Smart Clipboard
    valid_resp = requests.post(
        f"{API_URL}/api/desktop/capture",
        files={"file": ("screen_test.png", img_bytes, "image/png")},
        data={
            "app_name": "Visual Studio Code",
            "window_title": "train_yolo.py — ultralytics-cv-engine",
            "clipboard_context": "https://github.com/ultralytics/ultralytics",
        }
    )
    assert_test(valid_resp.status_code == 200, "POST /api/desktop/capture succeeds for valid app", f"[{valid_resp.status_code}]")
    cap_data = valid_resp.json()
    assert_test("id" in cap_data, "Capture response returns memory ID", f"[{cap_data.get('id')}]")
    assert_test(cap_data.get("app_name") == "Visual Studio Code", "App name assigned correctly")
    assert_test(cap_data.get("clipboard_attached") is True, "Smart clipboard context attached")

    # 6. Verify Memory Record in Database
    created_id = cap_data.get("id")
    time.sleep(1.5) # Allow background pipeline to initialize
    mem_resp = requests.get(f"{API_URL}/api/memories/{created_id}")
    assert_test(mem_resp.status_code == 200, f"Memory {created_id} accessible via GET /api/memories/{created_id}")
    mem_data = mem_resp.json()
    assert_test(mem_data.get("application") == "Visual Studio Code", "Memory application matches OS context")
    assert_test(mem_data.get("window_title") == "train_yolo.py — ultralytics-cv-engine", "Memory window title preserved")
    assert_test(mem_data.get("source_type") == "desktop_capture", "Source type marked as desktop_capture")
    assert_test("https://github.com/ultralytics/ultralytics" in (mem_data.get("clipboard_context") or ""), "Clipboard context preserved")

    # Cleanup test memory
    requests.delete(f"{API_URL}/api/memories/{created_id}")

    # 7. Private Mode Toggle Test
    toggle_resp = requests.post(f"{API_URL}/api/desktop/config", json={"private_mode": True})
    assert_test(toggle_resp.status_code == 200, "POST /api/desktop/config updates private mode")

    priv_block_resp = requests.post(
        f"{API_URL}/api/desktop/capture",
        files={"file": ("screen_test2.png", img_bytes, "image/png")},
        data={"app_name": "Notepad", "window_title": "Notes.txt"}
    )
    assert_test(priv_block_resp.status_code == 403, "Capture rejected when Private Mode is True (HTTP 403)")

    # Reset Private Mode back to False
    requests.post(f"{API_URL}/api/desktop/config", json={"private_mode": False})

    print("=" * 65)
    print(f"RESULT: {passed}/{total} PASSED ({passed/total*100:.0f}%)")
    print("=" * 65)

    if passed == total:
        print("[SUCCESS] ALL DESKTOP COMPANION & PRIVACY GATE TESTS PASSED!")
        return 0
    else:
        print("[FAILURE] SOME TESTS FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())
