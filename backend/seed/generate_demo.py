"""
AURA — Demo Data Generator
Creates 30 synthetic screenshots using Pillow.
No copyrighted content. All data is fictional but realistic.
Run: python seed/generate_demo.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import textwrap
import random

OUT_DIR = Path(__file__).parent.parent / "demo_data" / "screenshots"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Try to get a basic font; fall back to default
def get_font(size=16):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        try:
            return ImageFont.truetype("DejaVuSans.ttf", size)
        except Exception:
            return ImageFont.load_default()


def make_screenshot(filename: str, bg_color: tuple, texts: list, title: str = "", accent: tuple = (99, 102, 241)):
    """Create a realistic-looking screenshot."""
    W, H = 1280, 800
    img = Image.new("RGB", (W, H), bg_color)
    draw = ImageDraw.Draw(img)

    # Title bar
    draw.rectangle([0, 0, W, 40], fill=accent)
    title_font = get_font(18)
    draw.text((16, 10), title or filename, fill=(255, 255, 255), font=title_font)

    # Content area
    body_font = get_font(15)
    small_font = get_font(13)
    y = 60
    for item in texts:
        if isinstance(item, dict):
            style = item.get("style", "normal")
            text = item.get("text", "")
            color = item.get("color", (30, 30, 30))
            size = item.get("size", 15)
            font = get_font(size)
            if style == "header":
                draw.text((30, y), text, fill=(20, 20, 80), font=get_font(22))
                y += 35
                draw.line([(30, y), (W - 30, y)], fill=(200, 200, 220), width=1)
                y += 10
            elif style == "box":
                box_h = item.get("height", 50)
                draw.rectangle([20, y, W - 20, y + box_h], fill=item.get("bg", (240, 244, 255)), outline=(180, 190, 230))
                draw.text((30, y + 10), text, fill=color, font=font)
                y += box_h + 10
            elif style == "code":
                draw.rectangle([20, y, W - 20, y + item.get("height", 40)], fill=(30, 30, 30))
                draw.text((30, y + 8), text, fill=(80, 230, 80), font=get_font(14))
                y += item.get("height", 40) + 8
            else:
                wrapped = textwrap.wrap(text, width=90)
                for line in wrapped:
                    draw.text((30, y), line, fill=color, font=font)
                    y += 22
        else:
            wrapped = textwrap.wrap(str(item), width=90)
            for line in wrapped:
                draw.text((30, y), line, fill=(30, 30, 30), font=body_font)
                y += 22
        y += 4

    path = OUT_DIR / filename
    img.save(path, "PNG", optimize=True)
    print(f"  Created: {filename}")
    return path


def generate_all():
    print("Generating demo screenshots...")

    # ── 1. Amazon Laptop Receipt ──────────────────────────────────────────────
    make_screenshot("receipt_laptop_amazon.png", (255, 255, 255),
        title="Amazon — Order Confirmation",
        accent=(255, 153, 0),
        texts=[
            {"style": "header", "text": "Order Confirmation — #112-3849201-9847312"},
            {"text": "Thank you, Prajwal!", "size": 18, "color": (20, 20, 80)},
            {"text": "Estimated delivery: August 20, 2026", "color": (80, 80, 80)},
            {"style": "box", "text": "ASUS ZenBook 14 OLED — ₹89,990.00", "height": 55,
             "bg": (255, 252, 235), "color": (20, 20, 20)},
            {"text": "Subtotal:    ₹89,990.00", "color": (40, 40, 40)},
            {"text": "Shipping:    FREE (Prime)", "color": (40, 40, 40)},
            {"text": "GST (18%):   ₹16,198.20", "color": (40, 40, 40)},
            {"text": "Order Total: ₹1,06,188.20", "size": 18, "color": (20, 20, 80)},
            {"text": "Payment: HDFC Credit Card ending in ****7829", "color": (80, 80, 80)},
            {"text": "Sold by: Appario Retail Private Ltd.", "color": (80, 80, 80)},
        ]
    )

    # ── 2. Headphones Receipt ─────────────────────────────────────────────────
    make_screenshot("receipt_headphones_amazon.png", (255, 255, 255),
        title="Amazon — Sony WH-1000XM5 Order",
        accent=(255, 153, 0),
        texts=[
            {"style": "header", "text": "Order #114-0023891-2938471"},
            {"style": "box", "text": "Sony WH-1000XM5 Wireless Headphones — ₹26,990.00", "height": 55, "bg": (255, 252, 235)},
            {"text": "Order Date: July 28, 2026", "color": (60, 60, 60)},
            {"text": "Delivery: Delivered August 1, 2026", "color": (20, 120, 20)},
            {"text": "Total: ₹26,990.00 | GST: ₹4,858.20", "size": 16, "color": (20, 20, 80)},
            {"text": "Payment Method: Amazon Pay UPI", "color": (80, 80, 80)},
        ]
    )

    # ── 3. Monitor Invoice ────────────────────────────────────────────────────
    make_screenshot("invoice_monitor.png", (248, 250, 252),
        title="Tax Invoice — TechZone Electronics",
        accent=(30, 58, 138),
        texts=[
            {"style": "header", "text": "TAX INVOICE"},
            {"text": "Invoice No: TZ/2026/08/00234", "color": (40, 40, 100)},
            {"text": "Date: August 5, 2026", "color": (40, 40, 40)},
            {"text": "Bill To: Prajwal Sharma, 42 Koramangala 5th Block, Bengaluru 560034", "color": (40, 40, 40)},
            {"style": "box", "text": "LG 27UK850-W 4K UHD IPS Monitor — ₹45,000.00", "height": 55, "bg": (235, 240, 255)},
            {"text": "CGST 9%: ₹4,050.00    SGST 9%: ₹4,050.00", "color": (40, 40, 40)},
            {"text": "Total Amount Due: ₹53,100.00", "size": 18, "color": (20, 20, 80)},
            {"text": "IFSC: HDFC0001234   Account: 50200012345678", "color": (80, 80, 80)},
            {"text": "GSTIN: 29AABCT1332L1ZX", "color": (80, 80, 80)},
        ]
    )

    # ── 4. Mushroom Pasta Recipe ──────────────────────────────────────────────
    make_screenshot("recipe_mushroom_pasta.png", (255, 253, 245),
        title="Creamy Mushroom Pasta — AllRecipes",
        accent=(234, 88, 12),
        texts=[
            {"style": "header", "text": "Creamy Mushroom Tagliatelle"},
            {"text": "Prep: 10 min | Cook: 20 min | Serves: 4", "color": (100, 60, 20)},
            {"text": "★★★★★ 4.8/5 (312 reviews)", "color": (200, 100, 0)},
            {"style": "box", "text": "Ingredients", "height": 35, "bg": (255, 240, 200), "size": 17},
            {"text": "• 400g tagliatelle pasta", "color": (40, 40, 40)},
            {"text": "• 300g mixed mushrooms (cremini, shiitake)", "color": (40, 40, 40)},
            {"text": "• 200ml heavy cream (25% fat)", "color": (40, 40, 40)},
            {"text": "• 4 cloves garlic, minced", "color": (40, 40, 40)},
            {"text": "• 3 tbsp butter, 2 tbsp olive oil", "color": (40, 40, 40)},
            {"text": "• Fresh thyme, parmesan, salt & pepper", "color": (40, 40, 40)},
            {"style": "box", "text": "Method: Sauté mushrooms → add cream → toss pasta. Ready in 20 min!", "height": 55, "bg": (255, 252, 235)},
        ]
    )

    # ── 5. YOLO Research Paper ────────────────────────────────────────────────
    make_screenshot("research_yolo_paper.png", (250, 250, 255),
        title="YOLOv8: Real-Time Object Detection — arXiv",
        accent=(79, 70, 229),
        texts=[
            {"style": "header", "text": "YOLOv8: A New Frontier in Real-Time Object Detection"},
            {"text": "Authors: G. Jocher, A. Chaurasia, J. Qiu — Ultralytics, 2023", "color": (60, 60, 120)},
            {"text": "arXiv:2305.09972 [cs.CV]", "color": (100, 100, 200)},
            {"style": "box", "text": "Abstract", "height": 35, "bg": (235, 235, 255), "size": 17},
            {"text": "We present YOLOv8, a state-of-the-art object detection model that achieves", "color": (40, 40, 40)},
            {"text": "superior performance across detection, segmentation, and classification tasks.", "color": (40, 40, 40)},
            {"text": "YOLOv8 introduces a new anchor-free detection head and improved backbone.", "color": (40, 40, 40)},
            {"text": "mAP@0.50: 53.9% on COCO val2017 | Inference: 80 FPS on RTX 3080", "color": (40, 40, 100)},
            {"text": "Keywords: object detection, real-time, YOLO, deep learning, computer vision", "color": (80, 80, 80)},
        ]
    )

    # ── 6. Transformer Architecture Diagram ───────────────────────────────────
    make_screenshot("research_transformer_diagram.png", (245, 245, 255),
        title="Attention Is All You Need — Architecture",
        accent=(109, 40, 217),
        texts=[
            {"style": "header", "text": "The Transformer — Encoder-Decoder Architecture"},
            {"style": "box", "text": "Input Embedding → Positional Encoding → Multi-Head Attention", "height": 55, "bg": (230, 220, 255)},
            {"text": "• Multi-Head Attention: h=8 heads, d_model=512", "color": (40, 40, 40)},
            {"text": "• Feed Forward: d_ff=2048, ReLU activation", "color": (40, 40, 40)},
            {"text": "• Encoder: N=6 identical layers", "color": (40, 40, 40)},
            {"text": "• Decoder: N=6 layers + Masked Multi-Head Attention", "color": (40, 40, 40)},
            {"style": "box", "text": "Attention(Q,K,V) = softmax(QK^T / √d_k) V", "height": 50, "bg": (30, 30, 30), "color": (100, 255, 100)},
            {"text": "Paper: Vaswani et al., 2017 | NeurIPS", "color": (80, 80, 80)},
        ]
    )

    # ── 7. ViT Research Screenshot ────────────────────────────────────────────
    make_screenshot("research_vit_paper.png", (250, 250, 255),
        title="Vision Transformer (ViT) — An Image is Worth 16x16 Words",
        accent=(79, 70, 229),
        texts=[
            {"style": "header", "text": "An Image is Worth 16x16 Words: ViT"},
            {"text": "Dosovitskiy et al., Google Brain, 2021 | ICLR 2021", "color": (60, 60, 120)},
            {"text": "ViT-L/16 achieves 88.55% top-1 accuracy on ImageNet", "color": (40, 80, 40)},
            {"style": "box", "text": "Key Idea: Split image into 16×16 patches → flatten → linear embedding → Transformer", "height": 60, "bg": (235, 235, 255)},
            {"text": "• Patch size: 16×16 pixels", "color": (40, 40, 40)},
            {"text": "• No CNN — pure self-attention over image patches", "color": (40, 40, 40)},
            {"text": "• Pre-trained on JFT-300M dataset", "color": (40, 40, 40)},
        ]
    )

    # ── 8. Python OCR Script ───────────────────────────────────────────────────
    make_screenshot("code_python_ocr.png", (30, 30, 30),
        title="VS Code — aura_ocr.py",
        accent=(30, 30, 50),
        texts=[
            {"style": "code", "text": "import easyocr", "height": 30},
            {"style": "code", "text": "import json, re", "height": 30},
            {"style": "code", "text": "", "height": 5},
            {"style": "code", "text": "def extract_text(image_path: str) -> dict:", "height": 30},
            {"style": "code", "text": "    reader = easyocr.Reader(['en'], gpu=True)", "height": 30},
            {"style": "code", "text": "    results = reader.readtext(image_path, detail=1)", "height": 30},
            {"style": "code", "text": "    texts = [r[1] for r in results if r[2] > 0.3]", "height": 30},
            {"style": "code", "text": "    return {'text': '\\n'.join(texts)}", "height": 30},
        ]
    )

    # ── 9. Training Script ────────────────────────────────────────────────────
    make_screenshot("code_training_script.png", (30, 30, 30),
        title="VS Code — train_yolov8.py",
        accent=(30, 30, 50),
        texts=[
            {"style": "code", "text": "from ultralytics import YOLO", "height": 30},
            {"style": "code", "text": "import torch", "height": 30},
            {"style": "code", "text": "", "height": 5},
            {"style": "code", "text": "model = YOLO('yolov8l.pt')  # Load pretrained", "height": 30},
            {"style": "code", "text": "results = model.train(", "height": 30},
            {"style": "code", "text": "    data='dataset.yaml',", "height": 30},
            {"style": "code", "text": "    epochs=35,", "height": 30},
            {"style": "code", "text": "    imgsz=640,", "height": 30},
            {"style": "code", "text": "    device='cuda',  # RTX 5060", "height": 30},
            {"style": "code", "text": "    batch=16,", "height": 30},
            {"style": "code", "text": ")", "height": 30},
        ]
    )

    # ── 10. Terminal Training Output ──────────────────────────────────────────
    make_screenshot("terminal_training_output.png", (20, 20, 20),
        title="Terminal — YOLOv8 Training",
        accent=(20, 20, 20),
        texts=[
            {"style": "code", "text": "(venv) $ python train_yolov8.py", "height": 30},
            {"style": "code", "text": "Epoch 1/35: 100%|████████| 9958/9958 [45:23<00:00]", "height": 30},
            {"style": "code", "text": "      box_loss  cls_loss  dfl_loss  Instances", "height": 30},
            {"style": "code", "text": "      2.8234    3.1205    2.9801    524", "height": 30},
            {"style": "code", "text": "Epoch 16/35: mAP50=71.59% Precision=82.18%", "height": 30},
            {"style": "code", "text": "Epoch 17/35: mAP50=72.61% ← New Best!", "height": 30},
            {"style": "code", "text": "GPU: RTX 5060 8GB GDDR7 | VRAM: 4.49GB used", "height": 30},
        ]
    )

    # ── 11. Bug Error Traceback ────────────────────────────────────────────────
    make_screenshot("terminal_error_traceback.png", (20, 20, 20),
        title="Terminal — RuntimeError",
        accent=(180, 20, 20),
        texts=[
            {"style": "code", "text": "Traceback (most recent call last):", "height": 30},
            {"style": "code", "text": "  File 'train.py', line 47, in <module>", "height": 30},
            {"style": "code", "text": "    model.train(data=cfg, epochs=50)", "height": 30},
            {"style": "code", "text": "  File 'ultralytics/engine/trainer.py', line 201", "height": 30},
            {"style": "code", "text": "RuntimeError: CUDA out of memory.", "height": 30},
            {"style": "code", "text": "Tried to allocate 2.34 GiB", "height": 30},
            {"style": "code", "text": "Total capacity: 8.00 GiB | Already allocated: 6.91 GiB", "height": 30},
            {"style": "code", "text": "Fix: Reduce batch size from 32 to 16", "height": 30},
        ]
    )

    # ── 12. Wi-Fi Password (CRITICAL) ─────────────────────────────────────────
    make_screenshot("settings_wifi_password.png", (248, 248, 248),
        title="Router Admin — Wi-Fi Settings",
        accent=(30, 100, 200),
        texts=[
            {"style": "header", "text": "TP-Link AX3000 — Wireless Settings"},
            {"text": "Network Name (SSID): PrajwalHome_5G", "color": (30, 30, 30), "size": 17},
            {"text": "Security Mode: WPA3-Personal", "color": (30, 30, 30)},
            {"style": "box", "text": "Wi-Fi Password: Scryptic@2026#Secure!", "height": 55,
             "bg": (255, 235, 235), "color": (150, 0, 0), "size": 17},
            {"text": "Band: 5 GHz | Channel: Auto | Mode: AX", "color": (60, 60, 60)},
            {"text": "MAC Address: A8:1E:84:3F:92:B1", "color": (80, 80, 80)},
            {"text": "Router IP: 192.168.0.1", "color": (80, 80, 80)},
            {"text": "DHCP Lease: 24 hours", "color": (80, 80, 80)},
        ]
    )

    # ── 13. API Key Screenshot (CRITICAL) ─────────────────────────────────────
    make_screenshot("settings_api_key.png", (248, 248, 248),
        title="GitHub — Personal Access Tokens",
        accent=(36, 41, 46),
        texts=[
            {"style": "header", "text": "GitHub Personal Access Token"},
            {"text": "Token Name: AURA-Production-Deploy", "color": (30, 30, 30)},
            {"text": "Expiration: November 14, 2026", "color": (60, 60, 60)},
            {"style": "box",
             "text": "ghp_Kx9mRTq7YvN3pL2wQeZ1AbC8dFjHuI4oG5sX",
             "height": 55, "bg": (255, 235, 235), "color": (150, 0, 0), "size": 14},
            {"text": "Permissions: repo, read:org, write:packages", "color": (60, 60, 60)},
            {"text": "⚠️  Copy this token now. It won't be shown again.", "color": (200, 80, 0)},
        ]
    )

    # ── 14. Goa Hotel Booking ─────────────────────────────────────────────────
    make_screenshot("travel_goa_hotel.png", (245, 255, 250),
        title="MakeMyTrip — Hotel Booking Confirmation",
        accent=(0, 140, 140),
        texts=[
            {"style": "header", "text": "Booking Confirmed! ✓"},
            {"text": "Hotel: Taj Holiday Village Resort & Spa, Goa", "size": 17, "color": (20, 80, 20)},
            {"text": "Check-in: September 12, 2026 | Check-out: September 16, 2026", "color": (40, 40, 40)},
            {"text": "4 Nights | Deluxe Ocean View Room | 2 Adults", "color": (40, 40, 40)},
            {"style": "box", "text": "Total Paid: ₹42,800.00 | Booking ID: MMT-GOA-20260912-009281", "height": 55, "bg": (220, 255, 230)},
            {"text": "Address: Sinquerim, Candolim, North Goa, 403515", "color": (80, 80, 80)},
            {"text": "Contact: +91-832-664-5858", "color": (80, 80, 80)},
            {"text": "Free cancellation until Sep 9, 2026", "color": (0, 120, 0)},
        ]
    )

    # ── 15. Training Loss Chart ────────────────────────────────────────────────
    make_screenshot("chart_training_loss.png", (255, 255, 255),
        title="WandB — Training Metrics Dashboard",
        accent=(255, 188, 0),
        texts=[
            {"style": "header", "text": "YOLOv8 Training Metrics — Epoch 1→17"},
            {"style": "box", "text": "mAP@0.50: 72.61% | Precision: 83.47% | Recall: 64.88%", "height": 55, "bg": (240, 255, 240), "color": (20, 80, 20), "size": 17},
            {"text": "Box Loss:    2.8234 → 2.095  (-0.728 total)", "color": (40, 40, 40)},
            {"text": "Class Loss:  3.1205 → 2.209  (-0.911 total)", "color": (40, 40, 40)},
            {"text": "DFL Loss:    2.9801 → 2.214  (-0.766 total)", "color": (40, 40, 40)},
            {"text": "GPU VRAM: 4.49 GB / 8.00 GB GDDR7", "color": (60, 60, 100)},
            {"text": "Throughput: 3.5 it/s | ETA: ~5h to completion", "color": (60, 60, 100)},
        ]
    )

    # ── 16. Shopping Cart ─────────────────────────────────────────────────────
    make_screenshot("shopping_cart_screenshot.png", (255, 255, 255),
        title="Flipkart — Shopping Cart",
        accent=(47, 128, 237),
        texts=[
            {"style": "header", "text": "My Cart (3 Items)"},
            {"style": "box", "text": "Mechanical Keyboard — Keychron K2 Pro  ₹9,499", "height": 50, "bg": (240, 248, 255)},
            {"style": "box", "text": "USB-C Hub 7-in-1 — Anker A8346  ₹3,299", "height": 50, "bg": (240, 248, 255)},
            {"style": "box", "text": "Desk Lamp — Mi LED Smart  ₹1,999", "height": 50, "bg": (240, 248, 255)},
            {"text": "Cart Subtotal: ₹14,797.00", "size": 18, "color": (20, 20, 100)},
            {"text": "Free delivery on orders above ₹500 ✓", "color": (0, 120, 0)},
        ]
    )

    # ── 17. WhatsApp Address Conversation ─────────────────────────────────────
    make_screenshot("conversation_address.png", (229, 221, 213),
        title="WhatsApp — Rahul Kumar",
        accent=(37, 211, 102),
        texts=[
            {"style": "header", "text": "Rahul Kumar 🟢 online"},
            {"style": "box", "text": "Rahul: Hey! Here's the address for the party:", "height": 45, "bg": (255, 255, 255), "color": (20, 20, 20)},
            {"style": "box", "text": "Rahul: 78, 4th Cross, HSR Layout Sector 2, Bengaluru 560102", "height": 55, "bg": (255, 255, 255), "color": (20, 20, 100)},
            {"style": "box", "text": "Rahul: Come by 8 PM, parking in basement. Call: +91-9876543210", "height": 55, "bg": (255, 255, 255), "color": (20, 20, 20)},
            {"style": "box", "text": "You: Got it! See you there 🎉", "height": 45, "bg": (220, 255, 220), "color": (20, 20, 20)},
        ]
    )

    # ── 18. Architecture Diagram ───────────────────────────────────────────────
    make_screenshot("diagram_aura_architecture.png", (248, 250, 255),
        title="AURA — System Architecture",
        accent=(99, 102, 241),
        texts=[
            {"style": "header", "text": "AURA Agentic Visual Memory Engine"},
            {"style": "box", "text": "Screenshot Upload → Validation → Thumbnail Generation", "height": 50, "bg": (235, 240, 255)},
            {"style": "box", "text": "EasyOCR (GPU) → Text Extraction → Entity Detection", "height": 50, "bg": (235, 255, 240)},
            {"style": "box", "text": "Gemini 2.0 Flash → Vision Understanding → JSON", "height": 50, "bg": (255, 240, 235)},
            {"style": "box", "text": "AURA Shield → Regex + AI → Sensitivity Classification", "height": 50, "bg": (255, 235, 235)},
            {"style": "box", "text": "sentence-transformers → 384-dim Embedding → SQLite", "height": 50, "bg": (240, 235, 255)},
            {"style": "box", "text": "Hybrid Search: Semantic + BM25 + Entity + Temporal", "height": 50, "bg": (235, 250, 255)},
        ]
    )

    # ── 19. ISRO Project Slide ─────────────────────────────────────────────────
    make_screenshot("presentation_isro_slide1.png", (10, 20, 60),
        title="ISRO IIRS — Spaceborne Object Detection",
        accent=(10, 20, 60),
        texts=[
            {"style": "header", "text": "Spaceborne Object Detection using YOLOv8"},
            {"text": "Indian Space Research Organisation — IIRS Internship 2026", "size": 18, "color": (200, 200, 255)},
            {"text": "Trainee: Prajwal Sharma | Mentor: Dr. A. K. Verma", "color": (180, 180, 220)},
            {"style": "box", "text": "Objective: Detect ships, aircraft, vehicles from satellite imagery (SPOT-7)", "height": 60, "bg": (20, 40, 100), "color": (200, 230, 255)},
            {"text": "Dataset: 48,000 annotated satellite images | 12 classes", "color": (160, 200, 255)},
            {"text": "Target: mAP@0.50 > 75% on custom validation set", "color": (160, 200, 255)},
        ]
    )

    # ── 20. ISRO Results Slide ────────────────────────────────────────────────
    make_screenshot("presentation_isro_results.png", (10, 20, 60),
        title="ISRO IIRS — Results & Evaluation",
        accent=(10, 20, 60),
        texts=[
            {"style": "header", "text": "Model Evaluation Results — Epoch 17"},
            {"style": "box", "text": "mAP@0.50: 72.61%  |  mAP@0.50-95: 44.38%", "height": 60, "bg": (20, 60, 20), "color": (150, 255, 150), "size": 18},
            {"text": "Precision: 83.47%  |  Recall: 64.88%", "color": (150, 200, 150), "size": 17},
            {"text": "Inference Speed: 35ms / image on RTX 5060", "color": (160, 200, 255)},
            {"text": "Classes: Ship (89%), Aircraft (76%), Vehicle (71%)", "color": (160, 200, 255)},
            {"text": "Best Epoch: 17 | Remaining: 18→35 (training ongoing)", "color": (180, 180, 220)},
        ]
    )

    # ── 21. Dataset Description ────────────────────────────────────────────────
    make_screenshot("research_dataset_info.png", (250, 250, 255),
        title="DOTA Dataset — Aerial Object Detection",
        accent=(79, 70, 229),
        texts=[
            {"style": "header", "text": "DOTA v2.0 — Dataset for Object Detection in Aerial Images"},
            {"text": "Images: 11,268 aerial images | Instances: 1,793,658", "color": (40, 40, 40)},
            {"text": "Resolution: 800×800 to 4000×4000 pixels", "color": (40, 40, 40)},
            {"style": "box", "text": "Classes: plane, ship, storage tank, baseball diamond, tennis court, basketball court, ground track field, harbor, bridge, large vehicle, small vehicle, helicopter", "height": 80, "bg": (235, 235, 255)},
            {"text": "Source: Wuhan University + Aerospace Information Research Institute", "color": (60, 60, 120)},
            {"text": "Citation: Xia et al., CVPR 2018 | arxiv.org/abs/1711.10398", "color": (80, 80, 80)},
        ]
    )

    # ── 22. Map Screenshot ────────────────────────────────────────────────────
    make_screenshot("map_restaurant_goa.png", (230, 240, 230),
        title="Google Maps — Thalassa Restaurant",
        accent=(52, 168, 83),
        texts=[
            {"style": "header", "text": "Thalassa — Greek & Mediterranean"},
            {"text": "📍 Small Vagator Beach Road, Vagator, Goa 403509", "color": (40, 40, 40), "size": 17},
            {"text": "⭐ 4.6 (2,341 reviews) | ₹₹₹ | Greek, Mediterranean", "color": (40, 40, 100)},
            {"text": "Hours: 12:00 PM – 11:30 PM | Closed Mondays", "color": (60, 60, 60)},
            {"style": "box", "text": "Recommended: Lamb Moussaka (₹890), Seafood Platter (₹1,450), Mezze Plate (₹680)", "height": 60, "bg": (240, 255, 240)},
            {"text": "Call: +91-832-227-3002 | Reservation required on weekends", "color": (80, 80, 80)},
        ]
    )

    # ── 23. Computer Vision Concept ───────────────────────────────────────────
    make_screenshot("research_cv_concepts.png", (250, 250, 255),
        title="Computer Vision Notes — Key Concepts",
        accent=(79, 70, 229),
        texts=[
            {"style": "header", "text": "Computer Vision — Core Concepts Summary"},
            {"style": "box", "text": "Convolutional Neural Network (CNN)", "height": 35, "bg": (235, 235, 255), "size": 17},
            {"text": "• Feature extraction via learnable convolution filters", "color": (40, 40, 40)},
            {"text": "• Pooling: spatial downsampling (MaxPool, AvgPool)", "color": (40, 40, 40)},
            {"style": "box", "text": "Object Detection Paradigms", "height": 35, "bg": (235, 235, 255), "size": 17},
            {"text": "• One-stage: YOLO, SSD — fast, less accurate", "color": (40, 40, 40)},
            {"text": "• Two-stage: Faster R-CNN — accurate, slower", "color": (40, 40, 40)},
            {"text": "• Anchor-free: FCOS, CenterNet — modern approach", "color": (40, 40, 40)},
        ]
    )

    # ── 24. Grocery Receipt ───────────────────────────────────────────────────
    make_screenshot("receipt_grocery.png", (255, 255, 255),
        title="Swiggy Instamart — Order Receipt",
        accent=(255, 100, 50),
        texts=[
            {"style": "header", "text": "Swiggy Instamart — Order #SI8392017"},
            {"text": "Delivered: August 14, 2026 at 11:32 AM", "color": (60, 60, 60)},
            {"text": "Aashirvaad Multigrain Atta 5kg         ₹285", "color": (40, 40, 40)},
            {"text": "Amul Butter 500g                       ₹325", "color": (40, 40, 40)},
            {"text": "Tata Salt 1kg ×2                       ₹64", "color": (40, 40, 40)},
            {"text": "Lays Classic Salted 52g ×3             ₹120", "color": (40, 40, 40)},
            {"text": "Red Bull Energy 250ml ×4               ₹520", "color": (40, 40, 40)},
            {"text": "Delivery Fee: ₹35 | Platform Fee: ₹3", "color": (80, 80, 80)},
            {"text": "Total: ₹1,352.00 | Paid via UPI", "size": 17, "color": (20, 20, 80)},
        ]
    )

    # ── 25. Freelance Invoice ─────────────────────────────────────────────────
    make_screenshot("invoice_freelance.png", (250, 250, 255),
        title="Freelance Invoice — Prajwal Sharma",
        accent=(30, 58, 138),
        texts=[
            {"style": "header", "text": "INVOICE #PS/2026/031"},
            {"text": "From: Prajwal Sharma, prajwal.sharma@gmail.com, +91-9876543210", "color": (40, 40, 100)},
            {"text": "To: DataVision Labs Pvt. Ltd., Bengaluru", "color": (40, 40, 40)},
            {"text": "Date: August 10, 2026 | Due: August 25, 2026", "color": (60, 60, 60)},
            {"style": "box", "text": "ML Model Training & Deployment — ₹75,000.00", "height": 50, "bg": (235, 240, 255)},
            {"text": "Bank: HDFC Bank | Account: 50200087654321 | IFSC: HDFC0003456", "color": (80, 80, 80)},
            {"text": "GST: 18% | Total Payable: ₹88,500.00", "size": 17, "color": (20, 20, 100)},
        ]
    )

    # ── 26. Neural Network Diagram ────────────────────────────────────────────
    make_screenshot("diagram_neural_network.png", (248, 250, 255),
        title="Neural Network Visualization",
        accent=(99, 102, 241),
        texts=[
            {"style": "header", "text": "Feed-Forward Neural Network — 3 Hidden Layers"},
            {"style": "box", "text": "Input Layer (784 neurons) → Hidden₁ (512, ReLU) → Hidden₂ (256, ReLU) → Hidden₃ (128, ReLU) → Output (10, Softmax)", "height": 70, "bg": (235, 240, 255)},
            {"text": "Loss: Categorical Cross-Entropy | Optimizer: Adam (lr=0.001)", "color": (40, 40, 40)},
            {"text": "Batch Size: 64 | Epochs: 50 | Dropout: 0.3", "color": (40, 40, 40)},
            {"text": "Validation Accuracy: 98.7% on MNIST", "color": (20, 100, 20)},
        ]
    )

    # ── 27. Education — College Timetable ────────────────────────────────────
    make_screenshot("education_timetable.png", (250, 250, 255),
        title="PESIT — B.Tech Timetable Sem 7",
        accent=(30, 80, 160),
        texts=[
            {"style": "header", "text": "B.Tech CSE — Semester 7 Schedule"},
            {"text": "Monday: ML (9:00), CV Lab (11:00), DBMS (2:00)", "color": (40, 40, 40)},
            {"text": "Tuesday: Deep Learning (9:00), NLP (11:00)", "color": (40, 40, 40)},
            {"text": "Wednesday: Project Review (10:00), Elective (2:00)", "color": (40, 40, 40)},
            {"text": "Thursday: ML Lab (9:00-12:00), Seminar (2:00)", "color": (40, 40, 40)},
            {"text": "Friday: Research Paper Review (9:00), Quiz (11:00)", "color": (40, 40, 40)},
            {"style": "box", "text": "Project: AURA — Visual Memory Engine (SCRYPTIC 2026)", "height": 50, "bg": (235, 240, 255)},
        ]
    )

    # ── 28. Shopping Wishlist ────────────────────────────────────────────────
    make_screenshot("shopping_wishlist.png", (255, 255, 255),
        title="Amazon Wishlist — Tech Gear 2026",
        accent=(255, 153, 0),
        texts=[
            {"style": "header", "text": "Wishlist: Tech Gear 2026"},
            {"text": "• Logitech MX Keys S Keyboard — ₹10,995  ☆", "color": (40, 40, 40)},
            {"text": "• Razer DeathAdder V3 Mouse — ₹7,499  ☆", "color": (40, 40, 40)},
            {"text": "• Samsung T7 Shield SSD 2TB — ₹12,999  ☆", "color": (40, 40, 40)},
            {"text": "• Elgato Stream Deck MK.2 — ₹14,999  ☆", "color": (40, 40, 40)},
            {"text": "• Anker 140W GaN Charger — ₹6,499  ☆", "color": (40, 40, 40)},
            {"text": "Total Wishlist Value: ₹52,991.00", "size": 16, "color": (20, 20, 100)},
        ]
    )

    # ── 29. Privacy Policy Doc ────────────────────────────────────────────────
    make_screenshot("document_privacy_policy.png", (255, 255, 255),
        title="AURA Privacy Policy",
        accent=(50, 50, 100),
        texts=[
            {"style": "header", "text": "AURA Privacy Policy — v1.0"},
            {"text": "Effective Date: August 15, 2026", "color": (60, 60, 60)},
            {"style": "box", "text": "1. Local Processing: OCR and embeddings run locally on your device.", "height": 50, "bg": (240, 255, 240)},
            {"text": "2. Cloud AI: Vision analysis uses Gemini API (opt-in).", "color": (40, 40, 40)},
            {"text": "3. Storage: All screenshots stored locally. No cloud backup by default.", "color": (40, 40, 40)},
            {"text": "4. Sensitive Data: AURA Shield auto-detects and protects credentials.", "color": (40, 40, 40)},
            {"text": "5. Deletion: Permanently removes from index and filesystem.", "color": (40, 40, 40)},
        ]
    )

    # ── 30. AURA Screenshot of itself ────────────────────────────────────────
    make_screenshot("screenshot_aura_search.png", (15, 15, 30),
        title="AURA — Visual Memory Engine",
        accent=(99, 102, 241),
        texts=[
            {"style": "header", "text": "AURA — Agentic Visual Memory Engine"},
            {"style": "box", "text": "🔍  What do you remember?", "height": 60, "bg": (30, 30, 50), "color": (200, 200, 255), "size": 20},
            {"text": "4,287 memories indexed  •  23 clusters  •  142 relationships", "color": (150, 150, 200)},
            {"style": "box", "text": "Recent: Wi-Fi password (🔴 CRITICAL) | YOLO training (🟢) | Goa hotel (🟡)", "height": 55, "bg": (25, 25, 45), "color": (180, 180, 220)},
            {"text": "Don't search your screenshots. Ask your memory.", "size": 18, "color": (150, 130, 255)},
        ]
    )

    print(f"\n✅ Generated 30 demo screenshots in {OUT_DIR}")


if __name__ == "__main__":
    generate_all()
