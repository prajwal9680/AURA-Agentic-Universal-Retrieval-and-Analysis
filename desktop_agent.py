"""
AURA — Desktop Companion & OS Ingestion Agent
Secure, lightweight desktop capture service with built-in Privacy Gate,
active application/window context detection, smart clipboard memory,
and AUTOMATIC ingestion for both 'Ctrl+Shift+A' and normal Windows screenshots (Win+Shift+S / Snipping Tool / PrtScn).
"""
import os
import sys

# Fix Windows console UTF-8 output and enable unbuffered output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
        sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    except Exception:
        pass

import time
import json
import re
import hashlib
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from io import BytesIO
from PIL import Image, ImageGrab

# Optional Windows API imports via ctypes (pure standard library)
import ctypes
from ctypes import wintypes

API_BASE_URL = os.environ.get("AURA_API_URL", "http://localhost:8000")

# Local Privacy Gate Configuration
EXCLUDED_APPS = {
    "1password.exe", "bitwarden.exe", "keepass.exe", "lastpass.exe",
    "keepassxc.exe", "tor.exe", "securityhealthsystray.exe"
}
EXCLUDED_WINDOW_KEYWORDS = {
    "incognito", "private browsing", "password", "master key",
    "sign in", "login", "bank", "credit card", "vault"
}

# Cache of recently processed screenshot hashes to avoid duplicate processing
INGESTED_HASHES = set()


# ─── Windows OS Context Detection ────────────────────────────────────────────

def get_active_window_info() -> tuple[str, str]:
    """
    Returns (app_name, window_title) of the currently active foreground window.
    Uses pure Windows User32 and Kernel32 APIs via ctypes.
    """
    if sys.platform != "win32":
        return ("Generic Desktop", "Desktop Screen")

    try:
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32

        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return ("Desktop", "Desktop")

        # Get window title
        length = user32.GetWindowTextLengthW(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buff, length + 1)
        window_title = buff.value or "Active Window"

        # Get process ID and process name
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))

        # Open process to query name
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        h_process = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid.value)
        app_name = "Desktop"

        if h_process:
            try:
                buff_proc = ctypes.create_unicode_buffer(1024)
                size = wintypes.DWORD(1024)
                if kernel32.QueryFullProcessImageNameW(h_process, 0, buff_proc, ctypes.byref(size)):
                    full_path = buff_proc.value
                    app_name = Path(full_path).name
            finally:
                kernel32.CloseHandle(h_process)

        # Friendly app name mapping
        friendly_names = {
            "chrome.exe": "Google Chrome",
            "msedge.exe": "Microsoft Edge",
            "firefox.exe": "Mozilla Firefox",
            "code.exe": "Visual Studio Code",
            "slack.exe": "Slack",
            "spotify.exe": "Spotify",
            "notion.exe": "Notion",
            "cursor.exe": "Cursor IDE",
            "windowsterminal.exe": "Windows Terminal",
            "explorer.exe": "Windows Explorer",
            "figma.exe": "Figma",
            "snippingtool.exe": "Snipping Tool",
            "screensketch.exe": "Snipping Tool",
        }
        clean_app = friendly_names.get(app_name.lower(), app_name)
        return (clean_app, window_title)

    except Exception:
        return ("Desktop", "Active Screen")


# ─── Windows Clipboard Context Extractor ─────────────────────────────────────

def get_smart_clipboard_context() -> str:
    """
    Safely retrieves text or URL from clipboard.
    Filters out credit cards, passwords, and sensitive tokens.
    """
    if sys.platform != "win32":
        return ""

    try:
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32

        CF_UNICODETEXT = 13
        if not user32.OpenClipboard(None):
            return ""

        try:
            h_glb = user32.GetClipboardData(CF_UNICODETEXT)
            if not h_glb:
                return ""

            p_text = kernel32.GlobalLock(h_glb)
            if not p_text:
                return ""

            try:
                text = ctypes.c_wchar_p(p_text).value or ""
            finally:
                kernel32.GlobalUnlock(h_glb)
        finally:
            user32.CloseClipboard()

        text = text.strip()
        if not text or len(text) > 1000:
            return ""

        # Privacy Filter: Discard credit card numbers
        if re.search(r"\b(?:\d[ -]*?){13,16}\b", text):
            return ""
        # Privacy Filter: Discard secret tokens / long hex keys
        if re.search(r"\b(?:sk-[a-zA-Z0-9]{20,}|AKIA[0-9A-Z]{16})\b", text):
            return ""

        return text
    except Exception:
        return ""


# ─── Multi-part HTTP Form Post Helper ────────────────────────────────────────

def upload_capture_to_aura(image_bytes: bytes, app_name: str, window_title: str, clipboard_text: str = "", filename: str = "") -> dict:
    """Uploads screenshot and OS metadata to AURA backend."""
    boundary = f"----AuraBoundary{int(time.time()*1000)}"
    crlf = b"\r\n"

    body = BytesIO()

    # Form field: app_name
    body.write(f"--{boundary}".encode() + crlf)
    body.write(b'Content-Disposition: form-data; name="app_name"' + crlf + crlf)
    body.write(app_name.encode("utf-8") + crlf)

    # Form field: window_title
    body.write(f"--{boundary}".encode() + crlf)
    body.write(b'Content-Disposition: form-data; name="window_title"' + crlf + crlf)
    body.write(window_title.encode("utf-8") + crlf)

    # Form field: clipboard_context
    body.write(f"--{boundary}".encode() + crlf)
    body.write(b'Content-Disposition: form-data; name="clipboard_context"' + crlf + crlf)
    body.write(clipboard_text.encode("utf-8") + crlf)

    # Form field: captured_at
    body.write(f"--{boundary}".encode() + crlf)
    body.write(b'Content-Disposition: form-data; name="captured_at"' + crlf + crlf)
    body.write(datetime.now(timezone.utc).isoformat().encode("utf-8") + crlf)

    # File field: file
    if not filename:
        filename = f"capture_{int(time.time())}.png"
    body.write(f"--{boundary}".encode() + crlf)
    body.write(f'Content-Disposition: form-data; name="file"; filename="{filename}"'.encode() + crlf)
    body.write(b"Content-Type: image/png" + crlf + crlf)
    body.write(image_bytes + crlf)

    body.write(f"--{boundary}--".encode() + crlf)

    payload = body.getvalue()
    headers = {
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Content-Length": str(len(payload)),
        "User-Agent": "AURA-Desktop-Companion/1.0",
    }

    req = urllib.request.Request(f"{API_BASE_URL}/api/desktop/capture", data=payload, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


# ─── Screenshot & Ingestion Core ─────────────────────────────────────────────

def trigger_capture():
    """Executes manual hotkey capture flow: screen grab -> OS context -> privacy gate -> upload."""
    app_name, window_title = get_active_window_info()
    clipboard_text = get_smart_clipboard_context()

    print(f"\n📸 [AURA Hotkey Capture Triggered: Ctrl + Shift + A]")
    print(f"   🖥️  Application : {app_name}")
    print(f"   🪟 Window Title: {window_title}")
    if clipboard_text:
        print(f"   📋 Clipboard   : {clipboard_text[:60]}...")

    # Local Privacy Gate Check
    if app_name.lower() in EXCLUDED_APPS:
        print(f"   🛑 [PRIVACY GATE] Ingestion blocked: Application '{app_name}' is protected.")
        return

    for kw in EXCLUDED_WINDOW_KEYWORDS:
        if kw in window_title.lower():
            print(f"   🛑 [PRIVACY GATE] Ingestion blocked: Window contains sensitive keyword '{kw}'.")
            return

    # Grab Screen
    try:
        screen = ImageGrab.grab(all_screens=True)
        img_buf = BytesIO()
        screen.save(img_buf, format="PNG", optimize=True)
        img_bytes = img_buf.getvalue()

        img_hash = hashlib.md5(img_bytes).hexdigest()
        INGESTED_HASHES.add(img_hash)

        result = upload_capture_to_aura(img_bytes, app_name, window_title, clipboard_text)
        print(f"   ✅ [Ingested] Memory ID: {result.get('id')} | Status: {result.get('status')}")
    except Exception as e:
        print(f"   ❌ [Error] Capture failed: {e}")


def check_and_ingest_clipboard_screenshot():
    """
    Automatically detects if the user took a screenshot via standard Windows shortcuts
    (Win + Shift + S, PrintScreen, Snipping Tool) which put an image on the clipboard.
    """
    try:
        clip_img = ImageGrab.grabclipboard()
        if isinstance(clip_img, Image.Image):
            # Check if it's a valid screenshot image
            img_buf = BytesIO()
            clip_img.save(img_buf, format="PNG")
            img_bytes = img_buf.getvalue()
            img_hash = hashlib.md5(img_bytes).hexdigest()

            if img_hash not in INGESTED_HASHES:
                INGESTED_HASHES.add(img_hash)
                app_name, window_title = get_active_window_info()

                # Local Privacy Gate Check
                if app_name.lower() in EXCLUDED_APPS:
                    print(f"\n🛑 [PRIVACY GATE] Clipboard screenshot blocked: App '{app_name}' is protected.")
                    return

                for kw in EXCLUDED_WINDOW_KEYWORDS:
                    if kw in window_title.lower():
                        print(f"\n🛑 [PRIVACY GATE] Clipboard screenshot blocked: Sensitive keyword '{kw}'.")
                        return

                print(f"\n📸 [Auto-Detected Windows Screenshot from Clipboard (Win+Shift+S / PrtScn)]")
                print(f"   🖥️  Context App : {app_name}")
                print(f"   🪟 Context Win : {window_title}")
                print(f"   📐 Image Size  : {clip_img.size[0]}x{clip_img.size[1]} px")

                result = upload_capture_to_aura(img_bytes, app_name, window_title, filename=f"screenshot_{int(time.time())}.png")
                print(f"   ✅ [Ingested] Memory ID: {result.get('id')} | Status: {result.get('status')}")
    except Exception:
        pass


def check_and_ingest_screenshot_folder():
    """
    Watches standard Windows Screenshots folders for newly created screenshot files.
    """
    candidate_folders = [
        Path.home() / "Pictures" / "Screenshots",
        Path.home() / "OneDrive" / "Pictures" / "Screenshots",
    ]

    for folder in candidate_folders:
        if not folder.exists():
            continue
        try:
            for file_path in folder.glob("*.*"):
                if file_path.suffix.lower() in [".png", ".jpg", ".jpeg", ".webp"]:
                    # Only check files created in the last 60 seconds
                    mtime = file_path.stat().st_mtime
                    if time.time() - mtime < 60:
                        file_bytes = file_path.read_bytes()
                        f_hash = hashlib.md5(file_bytes).hexdigest()
                        if f_hash not in INGESTED_HASHES:
                            INGESTED_HASHES.add(f_hash)
                            app_name, window_title = get_active_window_info()
                            print(f"\n📸 [Auto-Detected Saved Screenshot in {folder.name}]")
                            print(f"   📁 File: {file_path.name}")
                            result = upload_capture_to_aura(file_bytes, app_name or "Windows Screenshots", window_title, filename=file_path.name)
                            print(f"   ✅ [Ingested] Memory ID: {result.get('id')}")
        except Exception:
            pass


def send_heartbeat():
    """Send heartbeat to AURA backend."""
    try:
        req = urllib.request.Request(f"{API_BASE_URL}/api/desktop/heartbeat", data=b"{}", headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=4) as resp:
            pass
    except Exception:
        pass


def run_companion():
    """Main Desktop Companion service loop."""
    print("=" * 65)
    print("🔮 AURA Desktop Companion — Secure Visual Memory Layer")
    print("=" * 65)
    print(f"🔗 Connected Backend : {API_BASE_URL}")
    print(f"⌨️  Global Hotkey     : Ctrl + Shift + A")
    print(f"✂️  Auto Ingestion    : Active (Win+Shift+S / Snipping Tool / PrtScn)")
    print(f"📁 Folder Watcher    : Active (~/Pictures/Screenshots)")
    print(f"🛡️  Privacy Gate      : Active (7 Excluded Apps, 9 Sensitive Filters)")
    print("-" * 65)
    print("Ready and listening for captures... (Press Ctrl+C to exit)\n")

    send_heartbeat()
    last_hb = time.time()
    last_folder_check = time.time()

    if sys.platform == "win32":
        user32 = ctypes.windll.user32
        MOD_CONTROL = 0x0002
        MOD_SHIFT = 0x0004
        VK_A = 0x41
        HOTKEY_ID = 1

        if not user32.RegisterHotKey(None, HOTKEY_ID, MOD_CONTROL | MOD_SHIFT, VK_A):
            print("⚠️  Could not register global hotkey (might already be registered). Polling fallback active.")

        try:
            msg = wintypes.MSG()
            while True:
                now = time.time()

                # Heartbeat every 20 seconds
                if now - last_hb > 20:
                    send_heartbeat()
                    last_hb = now

                # Check Windows Clipboard for normal screenshots (Win+Shift+S, PrtScn)
                check_and_ingest_clipboard_screenshot()

                # Check Screenshots directory every 3 seconds
                if now - last_folder_check > 3:
                    check_and_ingest_screenshot_folder()
                    last_folder_check = now

                # PeekMessage for Hotkey (Ctrl + Shift + A)
                if user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1): # PM_REMOVE = 1
                    if msg.message == 0x0312: # WM_HOTKEY
                        trigger_capture()
                    user32.TranslateMessage(ctypes.byref(msg))
                    user32.DispatchMessageW(ctypes.byref(msg))

                time.sleep(0.25)
        except KeyboardInterrupt:
            user32.UnregisterHotKey(None, HOTKEY_ID)
            print("\n👋 AURA Desktop Companion stopped.")
    else:
        while True:
            time.sleep(1)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--trigger-now":
        trigger_capture()
    else:
        run_companion()
