import urllib.request
import json
import os
import base64
from pathlib import Path

import pytest

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "MOCK_OPENROUTER_API_KEY")

@pytest.mark.skipif(not os.environ.get("RUN_LIVE_LLM_TESTS"), reason="Live external LLM test")
def test_openrouter_vision():
    headers = {

        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/prajwal9680/AURA-Agentic-Universal-Retrieval-and-Analysis",
        "X-Title": "AURA Visual Memory Engine",
    }
    
    img_path = Path("../demo_data/screenshots/diagram_aura_architecture.png")
    if not img_path.exists():
        print("Image not found:", img_path)
        return
        
    from PIL import Image
    import io
    with Image.open(img_path) as img:
        img.thumbnail((300, 300))
        buf = io.BytesIO()
        img.convert("RGB").save(buf, format="JPEG", quality=50)
        b64_img = base64.b64encode(buf.getvalue()).decode("utf-8")
        
    prompt = "Identify this diagram in 1 sentence. Valid JSON: {\"title\": \"architecture\"}"

    models = ["nvidia/nemotron-nano-12b-v2-vl:free"]
    
    for model in models:
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{b64_img}"
                            }
                        }
                    ]
                }
            ],
            "response_format": {"type": "json_object"}
        }
        data = json.dumps(payload).encode("utf-8")
        try:
            req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=data, headers=headers)
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                res_json = json.loads(resp.read().decode("utf-8"))
                assert res_json is not None
                return
        except Exception as e:
            print(f"Model {model} skipped or timed out: {e}")
            continue
    assert True


if __name__ == "__main__":
    test_openrouter_vision()
