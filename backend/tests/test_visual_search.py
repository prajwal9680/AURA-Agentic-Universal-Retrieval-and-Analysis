import urllib.request
import json
import io
from pathlib import Path

def test_visual_search():
    img_path = Path(__file__).resolve().parent.parent.parent / "demo_data" / "screenshots" / "food_photo_truffle_pizza.png"
    with open(img_path, "rb") as f:
        img_bytes = f.read()

    boundary = "----WebKitFormBoundarySearchTest"
    body = io.BytesIO()
    body.write(f"--{boundary}\r\n".encode("utf-8"))
    body.write(b'Content-Disposition: form-data; name="file"; filename="query.png"\r\n')
    body.write(b"Content-Type: image/png\r\n\r\n")
    body.write(img_bytes)
    body.write(f"\r\n--{boundary}--\r\n".encode("utf-8"))

    req = urllib.request.Request(
        "http://127.0.0.1:8000/api/memories/search-by-image?top_k=3",
        data=body.getvalue(),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST"
    )

    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        print(f"Visual Search Success!")
        print(f"Extracted Query: {res.get('query_extracted')[:80]}...")
        print(f"Total Results: {res.get('total')}")
        for i, r in enumerate(res.get("results", [])):
            print(f"  [{i+1}] {r['original_filename']} (Score: {r['relevance_score']:.2f}, Category: {r['category']})")
        assert len(res.get("results", [])) > 0

if __name__ == "__main__":
    test_visual_search()
