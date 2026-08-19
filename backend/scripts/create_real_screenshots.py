"""
AURA — Programmatic Realistic Screenshots Generator
Generates 8 high-fidelity realistic application UI screenshots using PIL:
1. receipt_swiggy_order.png
2. receipt_amazon_india.png
3. ui_vscode_python.png
4. map_mumbai_local.png
5. recipe_pasta_carbonara.png
6. ticket_irctc_train.png
7. ui_github_issue.png
8. dashboard_analytics.png
"""
import os
import sys
import asyncio
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

SCREENSHOTS_DIR = Path(__file__).parent.parent.parent / "demo_data" / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

def get_font(size=14, bold=False):
    # Try Windows system fonts
    font_paths = [
        "C:\\Windows\\Fonts\\segoeui.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\calibri.ttf",
        "C:\\Windows\\Fonts\\consola.ttf",
    ]
    if bold:
        font_paths = ["C:\\Windows\\Fonts\\segoeuib.ttf", "C:\\Windows\\Fonts\\arialbd.ttf"] + font_paths

    for fp in font_paths:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                pass
    return ImageFont.load_default()

def create_swiggy_receipt():
    img = Image.new("RGB", (650, 850), "#F4F5F8")
    d = ImageDraw.Draw(img)
    f_title = get_font(24, bold=True)
    f_bold = get_font(16, bold=True)
    f_reg = get_font(14)
    f_small = get_font(12)

    # Header Card
    d.rectangle([20, 20, 630, 110], fill="#FC8019") # Swiggy Orange
    d.text((40, 35), "SWIGGY FOOD DELIVERY", fill="#FFFFFF", font=f_title)
    d.text((40, 75), "Order #SW123456 • Delivered on 15 Aug 2026", fill="#FFF2E6", font=f_small)

    # Body Card
    d.rectangle([20, 125, 630, 830], fill="#FFFFFF", outline="#E2E8F0", width=1)

    # Restaurant info
    d.text((40, 150), "Punjab Grill & Curry House", fill="#1A202C", font=f_bold)
    d.text((40, 175), "Indiranagar 100ft Road, Bangalore • Paid via UPI (Google Pay)", fill="#718096", font=f_small)
    d.line([(40, 205), (610, 205)], fill="#EDF2F7", width=1)

    # Line Items
    items = [
        ("Butter Chicken (Chef Special)", "1", "320.00"),
        ("Butter Garlic Naan", "2", "60.00"),
        ("Jeera Rice Bowl", "1", "120.00"),
        ("Gulab Jamun (2 pcs)", "1", "70.00"),
    ]
    y = 230
    for name, qty, amt in items:
        d.text((40, y), f"{qty}x", fill="#FC8019", font=f_bold)
        d.text((80, y), name, fill="#2D3748", font=f_reg)
        d.text((520, y), f"Rs. {amt}", fill="#2D3748", font=f_reg)
        y += 45

    d.line([(40, y + 10), (610, y + 10)], fill="#EDF2F7", width=1)
    y += 30

    # Bill Details
    d.text((40, y), "Item Total", fill="#718096", font=f_reg)
    d.text((520, y), "Rs. 570.00", fill="#718096", font=f_reg)
    y += 30
    d.text((40, y), "Delivery Fee & Packaging", fill="#718096", font=f_reg)
    d.text((520, y), "Rs. 40.00", fill="#718096", font=f_reg)
    y += 30
    d.text((40, y), "GST & Restaurant Taxes (5%)", fill="#718096", font=f_reg)
    d.text((520, y), "Rs. 28.50", fill="#718096", font=f_reg)
    y += 30
    d.text((40, y), "Discount Coupon (SWIGGYIT)", fill="#38A169", font=f_reg)
    d.text((520, y), "- Rs. 100.00", fill="#38A169", font=f_reg)
    y += 40

    d.rectangle([40, y, 610, y + 60], fill="#F7FAFC", outline="#E2E8F0")
    d.text((60, y + 18), "TOTAL PAID AMOUNT", fill="#1A202C", font=f_bold)
    d.text((480, y + 18), "Rs. 538.50", fill="#1A202C", font=f_bold)

    out_path = SCREENSHOTS_DIR / "receipt_swiggy_order.png"
    img.save(out_path, "PNG")
    print(f"Saved: {out_path.name}")

def create_amazon_receipt():
    img = Image.new("RGB", (750, 800), "#FFFFFF")
    d = ImageDraw.Draw(img)
    f_title = get_font(22, bold=True)
    f_bold = get_font(16, bold=True)
    f_reg = get_font(14)
    f_small = get_font(12)

    # Top banner
    d.rectangle([0, 0, 750, 80], fill="#131921")
    d.text((30, 25), "amazon.in", fill="#FF9900", font=f_title)
    d.text((200, 32), "Order Confirmation & Tax Invoice", fill="#FFFFFF", font=f_reg)

    # Order details header
    d.text((30, 110), "Order # 402-8921823-9128312", fill="#0F1111", font=f_bold)
    d.text((30, 135), "Order Date: August 10, 2026 • Shipped to: Prajwal K.", fill="#565959", font=f_small)
    d.line([(30, 165), (720, 165)], fill="#D5D9D9", width=1)

    # Product Item
    d.rectangle([30, 185, 150, 305], fill="#EAEDED", outline="#D5D9D9")
    d.text((50, 235), "[LAPTOP]", fill="#565959", font=f_bold)

    d.text((170, 190), "ASUS TUF Gaming A15 Laptop (AMD Ryzen 7 7735HS / 16GB / 512GB SSD / RTX 4060)", fill="#007185", font=f_bold)
    d.text((170, 220), "Sold by: Appario Retail Private Ltd (GSTIN: 29AABCA1234F1Z8)", fill="#565959", font=f_small)
    d.text((170, 245), "Condition: Brand New • 1 Year Manufacturer Warranty Included", fill="#007600", font=f_small)
    d.text((170, 275), "Price: Rs. 68,990.00 (Inclusive of all taxes)", fill="#B12704", font=f_bold)

    d.line([(30, 330), (720, 330)], fill="#D5D9D9", width=1)

    # Payment Summary
    d.text((30, 350), "Payment Information", fill="#0F1111", font=f_bold)
    d.text((30, 380), "Payment Method: HDFC Bank Credit Card ending in 4242", fill="#565959", font=f_reg)
    d.text((30, 410), "Billing Address: Indiranagar, Bangalore, Karnataka 560038", fill="#565959", font=f_small)

    d.rectangle([420, 350, 720, 520], fill="#F3F3F3", outline="#D5D9D9")
    d.text((440, 370), "Items Subtotal:", fill="#565959", font=f_reg)
    d.text((610, 370), "Rs. 68,990.00", fill="#0F1111", font=f_reg)
    d.text((440, 405), "Shipping & Handling:", fill="#565959", font=f_reg)
    d.text((645, 405), "FREE", fill="#007600", font=f_reg)
    d.line([(440, 440), (700, 440)], fill="#D5D9D9", width=1)
    d.text((440, 460), "Grand Total:", fill="#0F1111", font=f_bold)
    d.text((585, 460), "Rs. 68,990.00", fill="#B12704", font=f_bold)

    out_path = SCREENSHOTS_DIR / "receipt_amazon_india.png"
    img.save(out_path, "PNG")
    print(f"Saved: {out_path.name}")

def create_vscode_screenshot():
    img = Image.new("RGB", (800, 600), "#1E1E1E")
    d = ImageDraw.Draw(img)
    f_code = get_font(13)
    f_bold = get_font(13, bold=True)
    f_ui = get_font(12)

    # VS Code Sidebar & Tab
    d.rectangle([0, 0, 50, 600], fill="#333333")
    d.rectangle([50, 0, 800, 35], fill="#252526")
    d.rectangle([50, 0, 220, 35], fill="#1E1E1E", outline="#3F3F46")
    d.text((70, 10), "train_multimodal.py", fill="#D4D4D4", font=f_ui)

    # Line numbers & Code
    lines = [
        (" 1", "import torch", "#C586C0"),
        (" 2", "import torch.nn as nn", "#C586C0"),
        (" 3", "from torchvision.models import vit_b_16, ViT_B_16_Weights", "#4EC9B0"),
        (" 4", "from transformers import AutoTokenizer, AutoModel", "#4EC9B0"),
        (" 5", "", "#D4D4D4"),
        (" 6", "class AURAEmbeddingFusion(nn.Module):", "#4EC9B0"),
        (" 7", "    def __init__(self, embed_dim: int = 384):", "#9CDCFE"),
        (" 8", "        super().__init__()", "#DCDCAA"),
        (" 9", "        self.vision_encoder = vit_b_16(weights=ViT_B_16_Weights.DEFAULT)", "#9CDCFE"),
        ("10", "        self.text_projection = nn.Linear(768, embed_dim)", "#9CDCFE"),
        ("11", "        self.layer_norm = nn.LayerNorm(embed_dim)", "#9CDCFE"),
        ("12", "", "#D4D4D4"),
        ("13", "    def forward(self, image_tensor, text_tokens):", "#DCDCAA"),
        ("14", "        img_feats = self.vision_encoder(image_tensor)", "#9CDCFE"),
        ("15", "        fused_vector = self.layer_norm(self.text_projection(img_feats))", "#9CDCFE"),
        ("16", "        return torch.nn.functional.normalize(fused_vector, p=2, dim=-1)", "#C586C0"),
        ("17", "", "#D4D4D4"),
        ("18", "# Initialize training pipeline on RTX 5060 Blackwell GPU", "#6A9955"),
        ("19", "device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')", "#9CDCFE"),
        ("20", "model = AURAEmbeddingFusion().to(device)", "#9CDCFE"),
    ]

    y = 50
    for num, code, col in lines:
        d.text((60, y), num, fill="#858585", font=f_code)
        d.text((110, y), code, fill=col, font=f_code)
        y += 24

    # Bottom status bar
    d.rectangle([0, 575, 800, 600], fill="#007ACC")
    d.text((15, 580), "Python 3.11.9 64-bit ('venv': conda) • CUDA 12.8 • UTF-8", fill="#FFFFFF", font=f_ui)

    out_path = SCREENSHOTS_DIR / "ui_vscode_python.png"
    img.save(out_path, "PNG")
    print(f"Saved: {out_path.name}")

def create_mumbai_map():
    img = Image.new("RGB", (700, 650), "#E8ECEF")
    d = ImageDraw.Draw(img)
    f_title = get_font(18, bold=True)
    f_bold = get_font(14, bold=True)
    f_reg = get_font(12)

    # Map Canvas styling
    d.rectangle([0, 0, 700, 60], fill="#1A73E8")
    d.text((25, 18), "Google Maps • Mumbai Local Transit Network Route", fill="#FFFFFF", font=f_title)

    # Train Lines
    # Western line (Red)
    d.line([(150, 100), (150, 580)], fill="#E53935", width=6)
    # Central line (Yellow/Green)
    d.line([(150, 300), (450, 580)], fill="#43A047", width=6)
    # Harbour line (Blue)
    d.line([(150, 420), (550, 480)], fill="#1E88E5", width=6)

    stations = [
        (150, 120, "Borivali Station (WR) - 0.0 km"),
        (150, 200, "Andheri Station (Interchange) - 12.4 km"),
        (150, 280, "Bandra Junction - 19.8 km"),
        (150, 360, "Dadar Central (Major Hub) - 24.1 km"),
        (150, 480, "Mumbai Central - 29.5 km"),
        (150, 560, "Churchgate Terminal - 34.0 km"),
        (300, 440, "Kurla Station (Central Hub) - 15.2 km"),
        (450, 560, "Thane Station - 33.8 km"),
        (530, 470, "Vashi Navi Mumbai - 28.0 km"),
    ]

    for x, y, name in stations:
        d.ellipse([x - 7, y - 7, x + 7, y + 7], fill="#FFFFFF", outline="#1A202C", width=2)
        d.text((x + 18, y - 8), name, fill="#1A202C", font=f_bold)

    # Route card overlay
    d.rectangle([400, 90, 670, 230], fill="#FFFFFF", outline="#CBD5E1", width=1)
    d.text((415, 105), "Fast Local Train #90124", fill="#1E88E5", font=f_bold)
    d.text((415, 130), "From: Churchgate Terminal", fill="#475569", font=f_reg)
    d.text((415, 150), "To: Borivali Fast", fill="#475569", font=f_reg)
    d.text((415, 175), "Duration: 38 mins (Distance: 34 km)", fill="#0F172A", font=f_bold)
    d.text((415, 198), "Frequency: Every 4 minutes", fill="#16A34A", font=f_reg)

    out_path = SCREENSHOTS_DIR / "map_mumbai_local.png"
    img.save(out_path, "PNG")
    print(f"Saved: {out_path.name}")

def create_pasta_recipe():
    img = Image.new("RGB", (650, 750), "#FFFDF9")
    d = ImageDraw.Draw(img)
    f_title = get_font(24, bold=True)
    f_bold = get_font(15, bold=True)
    f_reg = get_font(13)

    # Header Card
    d.rectangle([20, 20, 630, 110], fill="#8B4513")
    d.text((40, 35), "Authentic Pasta Carbonara", fill="#FFFFFF", font=f_title)
    d.text((40, 75), "Prep time: 10 mins • Cook time: 15 mins • Servings: 2 people", fill="#FDE8D7", font=f_reg)

    # Ingredients
    d.text((40, 140), "Ingredients List:", fill="#3E2723", font=f_bold)
    ingredients = [
        "• 200g Rigatoni or Spaghetti",
        "• 100g Guanciale or cured Pancetta (diced)",
        "• 2 large fresh egg yolks + 1 whole egg",
        "• 50g freshly grated Pecorino Romano cheese",
        "• 1 tablespoon freshly cracked black peppercorns",
        "• Reserved starchy pasta cooking water (1/2 cup)",
    ]
    y = 170
    for ing in ingredients:
        d.text((50, y), ing, fill="#4E342E", font=f_reg)
        y += 26

    # Cooking Steps
    y += 15
    d.text((40, y), "Step-by-Step Cooking Method:", fill="#3E2723", font=f_bold)
    y += 30
    steps = [
        "1. Boil pasta in generously salted water until al dente.",
        "2. Crisp diced guanciale in a dry pan on medium heat until golden.",
        "3. Whisk egg yolks, whole egg, grated Pecorino, and black pepper in a bowl.",
        "4. Remove pan from heat. Toss hot pasta with guanciale and rendering.",
        "5. Pour egg-cheese mixture with 2 tbsp pasta water, tossing rapidly to form a glossy emulsion.",
        "6. Serve immediately garnished with extra Pecorino and cracked pepper.",
    ]
    for step in steps:
        d.text((40, y), step[:68], fill="#3E2723", font=f_reg)
        if len(step) > 68:
            y += 20
            d.text((55, y), step[68:], fill="#3E2723", font=f_reg)
        y += 28

    out_path = SCREENSHOTS_DIR / "recipe_pasta_carbonara.png"
    img.save(out_path, "PNG")
    print(f"Saved: {out_path.name}")

def create_irctc_ticket():
    img = Image.new("RGB", (700, 600), "#F8FAFC")
    d = ImageDraw.Draw(img)
    f_title = get_font(20, bold=True)
    f_bold = get_font(14, bold=True)
    f_reg = get_font(13)
    f_small = get_font(11)

    # Header
    d.rectangle([20, 20, 680, 90], fill="#0A3871")
    d.text((40, 32), "IRCTC E-TICKETING RESERVATION", fill="#FFFFFF", font=f_title)
    d.text((40, 62), "Electronic Reservation Slip (ERS) • Indian Railways", fill="#93C5FD", font=f_small)

    d.rectangle([20, 100, 680, 580], fill="#FFFFFF", outline="#E2E8F0")

    # PNR & Train Details
    d.text((40, 120), "PNR: 821-4910283", fill="#0A3871", font=f_title)
    d.text((400, 125), "Train: 12951 / TEJAS RAJDHANI EXP", fill="#0F172A", font=f_bold)
    d.line([(40, 155), (660, 155)], fill="#E2E8F0", width=1)

    d.text((40, 170), "From: MUMBAI CENTRAL (MMCT)", fill="#334155", font=f_bold)
    d.text((40, 195), "Departure: 17:00 | 15-Aug-2026", fill="#64748B", font=f_reg)

    d.text((400, 170), "To: NEW DELHI (NDLS)", fill="#334155", font=f_bold)
    d.text((400, 195), "Arrival: 08:32 | 16-Aug-2026", fill="#64748B", font=f_reg)

    d.line([(40, 230), (660, 230)], fill="#E2E8F0", width=1)

    # Passenger Table
    d.rectangle([40, 250, 660, 285], fill="#F1F5F9")
    d.text((50, 260), "Passenger Name", fill="#0F172A", font=f_bold)
    d.text((280, 260), "Age / Gender", fill="#0F172A", font=f_bold)
    d.text((420, 260), "Booking Status", fill="#0F172A", font=f_bold)
    d.text((560, 260), "Coach / Berth", fill="#0F172A", font=f_bold)

    d.text((50, 305), "1. Prajwal K.", fill="#334155", font=f_reg)
    d.text((280, 305), "24 / Male", fill="#334155", font=f_reg)
    d.text((420, 305), "CNF (Confirmed)", fill="#16A34A", font=f_bold)
    d.text((560, 305), "B4 / 32 (Side Lower)", fill="#0F172A", font=f_bold)

    d.line([(40, 345), (660, 345)], fill="#E2E8F0", width=1)

    d.text((40, 365), "Class: AC 3 Tier (3A) • Quota: General (GN) • Total Fare: Rs. 2,450.00", fill="#0F172A", font=f_bold)
    d.text((40, 395), "Payment Mode: Net Banking / IRCTC iMudra • Transaction ID: #9821381290", fill="#64748B", font=f_small)

    out_path = SCREENSHOTS_DIR / "ticket_irctc_train.png"
    img.save(out_path, "PNG")
    print(f"Saved: {out_path.name}")

def create_github_issue():
    img = Image.new("RGB", (750, 600), "#0D1117")
    d = ImageDraw.Draw(img)
    f_title = get_font(18, bold=True)
    f_bold = get_font(13, bold=True)
    f_reg = get_font(13)
    f_code = get_font(12)

    # Top Header
    d.rectangle([0, 0, 750, 50], fill="#161B22")
    d.text((25, 15), "github.com / scryptic / aura-engine", fill="#E6EDF3", font=f_bold)

    # Issue Title
    d.text((25, 75), "Fix memory leak in embedding vector cache #142", fill="#E6EDF3", font=f_title)
    
    # State Badge
    d.rectangle([25, 115, 95, 140], fill="#238636", outline="#238636")
    d.text((38, 120), "Open", fill="#FFFFFF", font=f_bold)
    d.text((110, 122), "opened 3 hours ago by prajwalk • 4 comments", fill="#8B949E", font=f_reg)
    d.line([(25, 155), (725, 155)], fill="#30363D", width=1)

    # Issue Body Card
    d.rectangle([25, 175, 725, 560], fill="#161B22", outline="#30363D")
    d.text((45, 195), "### Problem Description", fill="#E6EDF3", font=f_bold)
    d.text((45, 225), "During batch ingestion of 500+ screenshots, GPU VRAM allocation increases linearly without releasing.", fill="#C9D1D9", font=f_reg)
    d.text((45, 250), "Profilers show `torch.cuda.empty_cache()` was not invoked after batch tensor normalization.", fill="#C9D1D9", font=f_reg)

    # Code block
    d.rectangle([45, 285, 705, 420], fill="#0D1117", outline="#30363D")
    code_snippet = [
        "# Proposed Patch in app/services/embeddings.py:",
        "@torch.no_grad()",
        "def compute_batch_embeddings(tensors):",
        "    with torch.cuda.amp.autocast():",
        "        embeddings = model(tensors.to(device))",
        "    torch.cuda.empty_cache()  # Fixes leak",
        "    return embeddings.cpu().numpy()",
    ]
    cy = 295
    for line in code_snippet:
        d.text((60, cy), line, fill="#79C0FF", font=f_code)
        cy += 18

    d.text((45, 440), "Assignees: @prajwalk • Labels: bug, performance, neural-engine", fill="#8B949E", font=f_reg)

    out_path = SCREENSHOTS_DIR / "ui_github_issue.png"
    img.save(out_path, "PNG")
    print(f"Saved: {out_path.name}")

def create_dashboard_analytics():
    img = Image.new("RGB", (750, 600), "#0F172A")
    d = ImageDraw.Draw(img)
    f_title = get_font(20, bold=True)
    f_bold = get_font(13, bold=True)
    f_reg = get_font(12)
    f_huge = get_font(24, bold=True)

    # Title
    d.text((30, 25), "AURA Telemetry & Neural Search Analytics", fill="#F8FAFC", font=f_title)
    d.text((30, 55), "Live cluster metric monitoring • 24h period", fill="#94A3B8", font=f_reg)

    # 3 Stat Metric Cards
    cards = [
        ("Total Queries", "14,892", "+18.4%", 30),
        ("P95 Retrieval Latency", "38.2 ms", "-12.1%", 270),
        ("Zero-Trust Shield Blocked", "482", "100% Protected", 510),
    ]
    for title, val, diff, x in cards:
        d.rectangle([x, 90, x + 210, 180], fill="#1E293B", outline="#334155")
        d.text((x + 15, 105), title, fill="#94A3B8", font=f_reg)
        d.text((x + 15, 130), val, fill="#F8FAFC", font=f_huge)
        d.text((x + 15, 160), diff, fill="#10B981", font=f_reg)

    # Chart Area
    d.rectangle([30, 200, 720, 430], fill="#1E293B", outline="#334155")
    d.text((50, 215), "Search Ingestion Throughput (req/sec)", fill="#F8FAFC", font=f_bold)

    # Draw simulated line graph
    pts = [
        (60, 380), (120, 340), (180, 350), (240, 290), (300, 310),
        (360, 260), (420, 280), (480, 240), (540, 250), (600, 220), (690, 210)
    ]
    for i in range(len(pts) - 1):
        d.line([pts[i], pts[i+1]], fill="#06B6D4", width=3)
        d.ellipse([pts[i][0]-3, pts[i][1]-3, pts[i][0]+3, pts[i][1]+3], fill="#38BDF8")

    # Table Area
    d.rectangle([30, 450, 720, 570], fill="#1E293B", outline="#334155")
    d.text((50, 465), "Top Query Clusters: 1. WiFi & Credentials (28%) | 2. Purchase Receipts (24%) | 3. ML Source Code (19%)", fill="#94A3B8", font=f_reg)
    d.text((50, 500), "Vector Index: 384-dimensional dense embeddings • Inverted token index: Active", fill="#64748B", font=f_reg)
    d.text((50, 530), "Graph Constellation Edges: 150 active relationships • Zero-Trust Mode: Strict", fill="#10B981", font=f_bold)

    out_path = SCREENSHOTS_DIR / "dashboard_analytics.png"
    img.save(out_path, "PNG")
    print(f"Saved: {out_path.name}")

def main():
    print("Generating 8 realistic programmatic screenshots...")
    create_swiggy_receipt()
    create_amazon_receipt()
    create_vscode_screenshot()
    create_mumbai_map()
    create_pasta_recipe()
    create_irctc_ticket()
    create_github_issue()
    create_dashboard_analytics()
    print("All 8 screenshots created successfully!")

if __name__ == "__main__":
    main()
