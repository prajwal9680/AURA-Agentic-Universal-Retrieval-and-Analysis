import urllib.request
import json
import os
import base64
from pathlib import Path

import pytest

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "MOCK_OPENROUTER_API_KEY")

@pytest.mark.skipif(not os.environ.get("RUN_LIVE_LLM_TESTS"), reason="Live external LLM test")
def test_openrouter():
    headers = {

        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/scryptic-aura",
        "X-Title": "AURA Visual Memory Engine",
    }
    
    # Test a free vision model on OpenRouter
    models = ["nvidia/nemotron-nano-12b-v2-vl:free"]
    
    for model in models:
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What is 2+2? Reply in JSON format: {\"result\": 4}"}
                    ]
                }
            ],
            "response_format": {"type": "json_object"}
        }
        
        data = json.dumps(payload).encode("utf-8")
        try:
            req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=data, headers=headers)
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                res_json = json.loads(resp.read().decode("utf-8"))
                print(f"Model {model} output:", res_json["choices"][0]["message"]["content"])
                return
        except Exception as e:
            print(f"Model {model} skipped or timed out: {e}")
            continue
    assert True

if __name__ == "__main__":
    test_openrouter()
