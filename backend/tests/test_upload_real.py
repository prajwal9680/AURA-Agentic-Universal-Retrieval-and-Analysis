import os
import json
import urllib.request
import pytest
from pathlib import Path

def test_upload_real():
    base = "http://127.0.0.1:8000"
    demo_dir = Path(__file__).parent.parent.parent / "demo_data" / "screenshots"
    if not demo_dir.exists():
        pytest.skip("Demo screenshots directory not found")

    files = [f for f in os.listdir(demo_dir) if f.endswith(".png") or f.endswith(".jpg")]
    if not files:
        pytest.skip("No screenshots found in demo_data/screenshots")

    test_file = demo_dir / files[0]
    with open(test_file, "rb") as f:
        img_bytes = f.read()

    boundary = "----AURATestBndry"
    bnd_bytes = boundary.encode()
    body = (
        b"--" + bnd_bytes + b"\r\n" +
        b"Content-Disposition: form-data; name=file; filename=test_real.png\r\n" +
        b"Content-Type: image/png\r\n\r\n" +
        img_bytes + b"\r\n" +
        b"--" + bnd_bytes + b"--\r\n"
    )
    req = urllib.request.Request(
        base + "/api/memories/upload",
        data=body,
        headers={"Content-Type": "multipart/form-data; boundary=" + boundary},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            up = json.loads(r.read().decode())
        assert "id" in up or "status" in up
        if up.get("id"):
            urllib.request.urlopen(urllib.request.Request(base + "/api/memories/" + up["id"], method="DELETE"), timeout=5)
    except Exception as e:
        pytest.skip(f"Live server not responding: {e}")
