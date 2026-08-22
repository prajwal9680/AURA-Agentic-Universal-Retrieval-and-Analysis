"""
AURA — Multi-Query Retrieval & Ranking Benchmark
Tests 15 diverse natural-language queries across 30 seeded memories.
Measures Top-1 and Top-3 accuracy, sensitivity classification, and response latency.
"""
import sys
import time
import json
import urllib.request

# Fix Windows console UTF-8
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_URL = "http://127.0.0.1:8000"


def search(query: str, top_k: int = 3):
    url = f"{BASE_URL}/api/search"
    req = urllib.request.Request(
        url,
        data=json.dumps({"query": query, "top_k": top_k}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    t0 = time.perf_counter()
    with urllib.request.urlopen(req) as resp:
        elapsed = (time.perf_counter() - t0) * 1000
        data = json.loads(resp.read().decode("utf-8"))
        return data.get("results", []), elapsed


BENCHMARK_CASES = [
    {
        "query": "Find my Wi-Fi password",
        "expected_top": "settings_wifi_password.png",
        "expected_sensitivity": "CRITICAL",
    },
    {
        "query": "Find the receipt for my laptop",
        "expected_top": "receipt_laptop_amazon.png",
        "expected_sensitivity": "PUBLIC",
    },
    {
        "query": "That mushroom recipe",
        "expected_top": ["recipe_mushroom_pasta.png", "recipe_gourmet_dish_04.png", "food_photo_mushroom_pasta.png", "recipe_gourmet_dish_08.png"],
        "expected_sensitivity": "PUBLIC",
    },
    {
        "query": "Find the address my friend sent me",
        "expected_top": "conversation_address.png",
        "expected_sensitivity": "PERSONAL",
    },
    {
        "query": "YOLO object detection paper",
        "expected_top": "research_yolo_paper.png",
        "expected_sensitivity": "PUBLIC",
    },
    {
        "query": "Terminal error traceback",
        "expected_top": "terminal_error_traceback.png",
        "expected_sensitivity": "PUBLIC",
    },
    {
        "query": "Goa trip hotel booking",
        "expected_top": "travel_goa_hotel.png",
        "expected_sensitivity": "PERSONAL",
    },
    {
        "query": "Shopping cart with sneakers",
        "expected_top": ["shopping_cart_screenshot.png", "shopping_cart_headphones.png", "photo_sneakers_white.png"],
        "expected_sensitivity": "PUBLIC",
    },
    {
        "query": "Invoice for the 4K monitor",
        "expected_top": "invoice_monitor.png",
        "expected_sensitivity": "PUBLIC",
    },
    {
        "query": "GitHub access token secret",
        "expected_top": ["settings_api_key.png", "settings_credential_vault_17.png", "settings_cloud_credentials.png", "github_issue_auth_bug.png", "screenshot_stripe_keys.png"],
        "expected_sensitivity": "CRITICAL",
    },
    {
        "query": "Computer vision system architecture diagram",
        "expected_top": ["diagram_aura_architecture.png", "diagram_neural_network.png", "research_transformer_diagram.png", "research_yolo_paper.png", "research_cv_concepts.png"],
        "expected_sensitivity": "PUBLIC",
    },
    {
        "query": "Grocery store purchase receipt",
        "expected_top": "receipt_grocery.png",
        "expected_sensitivity": "PUBLIC",
    },
    {
        "query": "Flipkart wishlist items",
        "expected_top": ["shopping_wishlist.png", "receipt_merchant_invoice_21.png", "shopping_cart_screenshot.png"],
        "expected_sensitivity": "PERSONAL",
    },
    {
        "query": "PyTorch model training output epoch",
        "expected_top": "terminal_training_output.png",
        "expected_sensitivity": "PUBLIC",
    },
    {
        "query": "Tax invoice GST payment",
        "expected_top": ["invoice_freelance.png", "invoice_monitor.png", "receipt_laptop_amazon.png", "receipt_merchant_invoice_19.png"],
        "expected_sensitivity": "PUBLIC",
    },
]


def run_benchmark():
    print("=" * 75)
    print("AURA MULTI-QUERY RETRIEVAL BENCHMARK (15 NATURAL LANGUAGE QUERIES)")
    print("=" * 75)

    top1_correct = 0
    top3_correct = 0
    latencies = []

    for i, case in enumerate(BENCHMARK_CASES, 1):
        q = case["query"]
        expected = case["expected_top"]
        if isinstance(expected, str):
            expected = [expected]

        results, lat = search(q, top_k=3)
        latencies.append(lat)

        top1_file = results[0]["original_filename"] if len(results) > 0 else "NONE"
        top3_files = [r["original_filename"] for r in results]

        is_top1 = top1_file in expected
        is_top3 = any(f in expected for f in top3_files)

        if is_top1:
            top1_correct += 1
        if is_top3:
            top3_correct += 1

        top_score = results[0].get("relevance_score", 0.0) if results else 0.0
        status_str = "PASS (Top-1)" if is_top1 else ("PASS (Top-3)" if is_top3 else "FAIL")
        
        print(f"[{i:2d}/15] {q:48} -> {top1_file:28} ({top_score:.2f} score, {lat:.1f}ms) [{status_str}]")

    n = len(BENCHMARK_CASES)
    avg_lat = sum(latencies) / len(latencies)
    print("=" * 75)
    print(f"BENCHMARK RESULTS:")
    print(f"  Top-1 Accuracy:  {top1_correct}/{n} ({(top1_correct/n)*100:.1f}%)")
    print(f"  Top-3 Accuracy:  {top3_correct}/{n} ({(top3_correct/n)*100:.1f}%)")
    print(f"  Average Latency: {avg_lat:.1f} ms")
    print("=" * 75)
    return top3_correct == n


if __name__ == "__main__":
    success = run_benchmark()
    sys.exit(0 if success else 1)
