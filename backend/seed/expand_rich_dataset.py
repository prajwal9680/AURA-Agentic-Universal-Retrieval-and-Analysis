"""
AURA — Rich Multi-Domain Dataset Expansion
Generates 32 high-resolution, visually stunning synthetic screenshots targeting
the 8 primary hackathon query themes in exquisite detail:
1. Wi-Fi & Security Credentials (CRITICAL Protection)
2. Laptop Receipts & Invoices
3. Computer Vision & Aerial Remote Sensing Research
4. Mushroom & Gourmet Culinary Recipes
5. Training Loss & Accuracy Convergence Curves
6. Friend Chat Addresses & Locations
7. Red Sports Cars & Automotive Scenes
8. Terminal Error Tracebacks & CUDA Exceptions
"""
import sys
import os
import io
import math
import random
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = Path(__file__).resolve().parent.parent / "demo_data" / "screenshots"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def get_font(size=16, bold=False):
    font_names = ["arialbd.ttf" if bold else "arial.ttf", "segoeui.ttf", "DejaVuSans.ttf"]
    for fn in font_names:
        try:
            return ImageFont.truetype(fn, size)
        except Exception:
            pass
    return ImageFont.load_default()

def draw_header(draw, title, subtitle="", bg=(245, 247, 250), accent=(99, 102, 241), width=1280):
    draw.rectangle([0, 0, width, 56], fill=accent)
    draw.text((24, 14), title, fill=(255, 255, 255), font=get_font(20, bold=True))
    if subtitle:
        draw.text((width - 320, 18), subtitle, fill=(230, 230, 255), font=get_font(14))

# ─── 1. Wi-Fi & Credentials ──────────────────────────────────────────────────

def gen_wifi_guest():
    img = Image.new("RGB", (1280, 800), (250, 252, 255))
    d = ImageDraw.Draw(img)
    draw_header(d, "🏢 TechHub Coworking — Guest Wi-Fi Access Portal", "WPA3 Enterprise Secure", accent=(30, 41, 59))
    
    d.rounded_rectangle([180, 100, 1100, 720], radius=16, fill=(255, 255, 255), outline=(226, 232, 240), width=2)
    d.text((220, 140), "Welcome to TechHub Bangalore Guest Wireless", fill=(15, 23, 42), font=get_font(24, bold=True))
    d.text((220, 180), "Connect your laptop or mobile device to our high-speed 1 Gbps fiber network.", fill=(100, 116, 139), font=get_font(15))
    
    d.rounded_rectangle([220, 230, 760, 470], radius=12, fill=(248, 250, 252), outline=(203, 213, 225), width=2)
    d.text((250, 260), "SSID / Network Name:", fill=(71, 85, 105), font=get_font(14, bold=True))
    d.text((250, 285), "TechHub_5G_Guest", fill=(15, 23, 42), font=get_font(22, bold=True))
    
    d.text((250, 340), "Wi-Fi Password / Pre-Shared Key:", fill=(71, 85, 105), font=get_font(14, bold=True))
    d.rectangle([250, 370, 720, 420], fill=(254, 242, 242), outline=(239, 68, 68), width=1)
    d.text((270, 382), "GuestPass@2026!", fill=(220, 38, 38), font=get_font(22, bold=True))
    
    d.rounded_rectangle([800, 230, 1060, 470], radius=12, fill=(241, 245, 249), outline=(203, 213, 225), width=1)
    d.rectangle([830, 260, 1030, 440], fill=(15, 23, 42))
    d.text((845, 340), "[ SCAN QR CODE ]", fill=(255, 255, 255), font=get_font(16, bold=True))
    
    d.text((220, 520), "Security Policy: Valid for 24 hours. Bandwidth allocated: 300 Mbps symmetrical.", fill=(100, 116, 139), font=get_font(14))
    d.text((220, 550), "Router Hardware: Cisco Meraki MR56 Wi-Fi 6 AP | Gateway: 10.10.40.1", fill=(100, 116, 139), font=get_font(13))
    img.save(OUT_DIR / "wifi_office_guest_network.png", optimize=True)

def gen_wifi_router_tplink():
    img = Image.new("RGB", (1280, 800), (240, 244, 248))
    d = ImageDraw.Draw(img)
    draw_header(d, "TP-Link Archer AX55 — Wireless Settings (192.168.0.1)", "Firmware: v1.3.4 Build 2026", accent=(0, 114, 188))
    
    d.rectangle([40, 90, 300, 740], fill=(255, 255, 255), outline=(203, 213, 225))
    menu = ["Quick Setup", "Network Map", "Internet", "Wireless Settings", "Mesh Network", "Security & VPN", "System Tools"]
    for i, m in enumerate(menu):
        bg_c = (230, 242, 255) if i == 3 else (255, 255, 255)
        d.rectangle([42, 110 + i * 50, 298, 155 + i * 50], fill=bg_c)
        d.text((60, 125 + i * 50), m, fill=(0, 114, 188) if i == 3 else (50, 50, 50), font=get_font(15, bold=(i==3)))

    d.rounded_rectangle([330, 90, 1240, 740], radius=8, fill=(255, 255, 255), outline=(203, 213, 225))
    d.text((360, 120), "Dual-Band Wireless Configuration", fill=(20, 20, 20), font=get_font(20, bold=True))
    
    fields = [
        ("Wireless Radio", "Enabled (2.4 GHz + 5 GHz OFDMA)"),
        ("Network Name (SSID)", "Zenith_Home_FastMesh"),
        ("Security Type", "WPA2/WPA3-Personal (Recommended)"),
        ("Encryption Algorithm", "AES (Advanced Encryption Standard)"),
        ("Password / Security Key", "ZenithFastNet_9901"),
        ("Channel Width", "160 MHz (Ultra-Wide Bandwidth)"),
        ("MAC Filtering", "Disabled"),
    ]
    for i, (k, v) in enumerate(fields):
        y = 180 + i * 65
        d.text((360, y), k, fill=(100, 100, 100), font=get_font(14, bold=True))
        if "Password" in k:
            d.rectangle([360, y + 22, 900, y + 55], fill=(254, 242, 242), outline=(220, 38, 38))
            d.text((375, y + 28), v, fill=(220, 38, 38), font=get_font(16, bold=True))
        else:
            d.rectangle([360, y + 22, 900, y + 55], fill=(248, 250, 252), outline=(203, 213, 225))
            d.text((375, y + 28), v, fill=(15, 23, 42), font=get_font(15))
            
    img.save(OUT_DIR / "router_tp_link_admin_settings.png", optimize=True)

def gen_wifi_cafe_starbucks():
    img = Image.new("RGB", (1280, 800), (247, 247, 247))
    d = ImageDraw.Draw(img)
    draw_header(d, "☕ Starbucks India — Customer High-Speed Wi-Fi Login", "Indiranagar 100ft Road Store", accent=(0, 112, 74))
    
    d.rounded_rectangle([250, 120, 1030, 680], radius=16, fill=(255, 255, 255), outline=(220, 220, 220), width=2)
    d.text((300, 160), "Welcome to Starbucks Free High-Speed Wi-Fi", fill=(0, 112, 74), font=get_font(24, bold=True))
    d.text((300, 200), "Enjoy complimentary 500 Mbps Wi-Fi with every handcrafted coffee.", fill=(80, 80, 80), font=get_font(15))
    
    d.rounded_rectangle([300, 260, 980, 480], radius=10, fill=(242, 248, 245), outline=(0, 112, 74), width=1)
    d.text((330, 290), "Network Name (SSID):", fill=(50, 50, 50), font=get_font(15, bold=True))
    d.text((330, 320), "Starbucks_Indiranagar_Guest", fill=(0, 112, 74), font=get_font(22, bold=True))
    
    d.text((330, 380), "Wi-Fi Passcode / Voucher Code:", fill=(50, 50, 50), font=get_font(15, bold=True))
    d.rectangle([330, 410, 850, 460], fill=(254, 242, 242), outline=(220, 38, 38))
    d.text((350, 422), "CoffeeLover99#", fill=(220, 38, 38), font=get_font(22, bold=True))
    
    d.text((300, 530), "Store Location: 100 Feet Road, HAL 2nd Stage, Indiranagar, Bangalore 560038", fill=(100, 100, 100), font=get_font(14))
    d.text((300, 560), "Complimentary access provided by ACT Fibernet Fiber-to-the-Home (FTTH)", fill=(100, 100, 100), font=get_font(13))
    img.save(OUT_DIR / "wifi_cafe_starbucks_bangalore.png", optimize=True)

# ─── 2. Laptop Receipts & Invoices ───────────────────────────────────────────

def gen_receipt_macbook():
    img = Image.new("RGB", (1280, 800), (255, 255, 255))
    d = ImageDraw.Draw(img)
    draw_header(d, "Apple Store India — Official Tax Invoice / Receipt", "Order #W948201948", accent=(0, 0, 0))
    
    d.text((60, 90), "Apple India Private Limited", fill=(15, 23, 42), font=get_font(20, bold=True))
    d.text((60, 120), "19th Floor, Concorde Tower C, UB City, Vittal Mallya Road, Bangalore - 560001", fill=(100, 100, 100), font=get_font(13))
    d.text((60, 140), "GSTIN: 29AABCA9847L1Z9 | Invoice Date: August 12, 2026", fill=(100, 100, 100), font=get_font(13))
    d.line([(60, 170), (1220, 170)], fill=(220, 220, 220), width=1)
    
    d.text((60, 190), "Billed To: Prajwal Sharma | Zenith Workstation Lab", fill=(15, 23, 42), font=get_font(15, bold=True))
    
    d.rectangle([60, 230, 1220, 270], fill=(245, 245, 247))
    d.text((80, 242), "Item Description", fill=(50, 50, 50), font=get_font(14, bold=True))
    d.text((650, 242), "Qty", fill=(50, 50, 50), font=get_font(14, bold=True))
    d.text((800, 242), "Unit Price", fill=(50, 50, 50), font=get_font(14, bold=True))
    d.text((1050, 242), "Total Amount", fill=(50, 50, 50), font=get_font(14, bold=True))
    
    items = [
        ("16-inch MacBook Pro — Space Black (Apple M3 Max 16-Core CPU, 40-Core GPU, 48GB Unified Memory, 1TB SSD Storage)", "1", "₹2,49,900.00", "₹2,49,900.00"),
        ("AppleCare+ for 16-inch MacBook Pro (3 Years Extended Protection & Accidental Damage Coverage)", "1", "₹32,900.00", "₹32,900.00"),
        ("140W USB-C Power Adapter + 2m MagSafe 3 Cable", "1", "Included", "₹0.00"),
    ]
    y = 280
    for title, qty, unit, tot in items:
        lines = textwrap.wrap(title, 55)
        for l in lines:
            d.text((80, y), l, fill=(15, 23, 42), font=get_font(14))
            y += 20
        d.text((650, y - len(lines)*20), qty, fill=(15, 23, 42), font=get_font(14))
        d.text((800, y - len(lines)*20), unit, fill=(15, 23, 42), font=get_font(14))
        d.text((1050, y - len(lines)*20), tot, fill=(15, 23, 42), font=get_font(14, bold=True))
        y += 15
        d.line([(60, y), (1220, y)], fill=(240, 240, 240))
        y += 10
        
    d.rectangle([750, y + 20, 1220, y + 170], fill=(250, 250, 252), outline=(220, 220, 220))
    d.text((780, y + 35), "Subtotal:              ₹2,82,800.00", fill=(50, 50, 50), font=get_font(15))
    d.text((780, y + 65), "CGST (9%) + SGST (9%):  ₹50,904.00", fill=(50, 50, 50), font=get_font(15))
    d.text((780, y + 100), "Grand Total (INR):     ₹3,33,704.00", fill=(0, 0, 0), font=get_font(18, bold=True))
    d.text((780, y + 135), "Paid via HDFC Corporate Credit Card (**** 9012)", fill=(100, 116, 139), font=get_font(13))
    img.save(OUT_DIR / "receipt_apple_macbook_pro.png", optimize=True)

def gen_receipt_lenovo_legion():
    img = Image.new("RGB", (1280, 800), (255, 255, 255))
    d = ImageDraw.Draw(img)
    draw_header(d, "Lenovo Official Online Store — Tax Invoice", "Order #LEN-2026-849102", accent=(235, 0, 41))
    
    d.text((60, 90), "Lenovo (India) Pvt. Ltd. — Electronic Bill of Sale", fill=(15, 23, 42), font=get_font(20, bold=True))
    d.text((60, 120), "Lenovo Technology Park, Whitefield, Bangalore 560066 | GSTIN: 29AABCL9921D1ZZ", fill=(100, 100, 100), font=get_font(13))
    
    d.rounded_rectangle([60, 160, 1220, 360], radius=8, fill=(248, 250, 252), outline=(226, 232, 240))
    d.text((80, 180), "Product Ordered: Lenovo Legion Pro 7i Gen 9 Gaming Laptop (16-inch WQXGA 240Hz)", fill=(15, 23, 42), font=get_font(18, bold=True))
    specs = [
        "Processor: Intel Core i9-14900HX (24 cores, up to 5.8 GHz)",
        "Graphics: NVIDIA GeForce RTX 4080 Laptop GPU 12GB GDDR6 (175W TGP)",
        "Memory: 32 GB DDR5-5600MHz RAM | Storage: 2 TB PCIe 4.0 NVMe SSD",
        "Display: 16-inch WQXGA (2560x1600) IPS, 500 nits, 100% DCI-P3, HDR 400",
        "Serial Number: LNV-LEGION-PRO7-902184 | 3-Year Legion Ultimate Support Warranty",
    ]
    for i, s in enumerate(specs):
        d.text((80, 215 + i * 25), "• " + s, fill=(71, 85, 105), font=get_font(14))
        
    d.rounded_rectangle([60, 390, 1220, 560], radius=8, fill=(255, 250, 240), outline=(253, 230, 138))
    d.text((80, 415), "Payment & Pricing Summary", fill=(15, 23, 42), font=get_font(18, bold=True))
    d.text((80, 450), "Base Laptop Price:        ₹1,84,990.00", fill=(50, 50, 50), font=get_font(15))
    d.text((80, 480), "Promotional Discount:    - ₹15,000.00 (LENOVO_HACKATHON2026 Coupon)", fill=(22, 101, 52), font=get_font(15, bold=True))
    d.text((80, 510), "Final Net Amount Paid:    ₹1,69,990.00 (Including all taxes & express shipping)", fill=(15, 23, 42), font=get_font(17, bold=True))
    
    d.text((60, 600), "Thank you for choosing Lenovo! Your device includes 3-Year Accidental Damage Protection.", fill=(100, 116, 139), font=get_font(14))
    img.save(OUT_DIR / "receipt_lenovo_legion_laptop.png", optimize=True)

def gen_receipt_croma_helios():
    img = Image.new("RGB", (1280, 800), (255, 255, 255))
    d = ImageDraw.Draw(img)
    draw_header(d, "Croma Megastore — Retail Store Tax Invoice", "Store: Koramangala, Bangalore", accent=(0, 168, 204))
    
    d.text((60, 90), "Infiniti Retail Limited (A TATA Enterprise) — Croma Invoice #CR-2026-90214", fill=(15, 23, 42), font=get_font(18, bold=True))
    d.text((60, 120), "80 Feet Road, 4th Block, Koramangala, Bangalore - 560034 | GSTIN: 29AAACI1184L1ZM", fill=(100, 100, 100), font=get_font(13))
    
    d.rounded_rectangle([60, 160, 1220, 400], radius=8, fill=(245, 250, 255), outline=(186, 230, 253))
    d.text((80, 185), "Item: Acer Predator Helios 16 Gaming Laptop (Model PH16-72)", fill=(15, 23, 42), font=get_font(17, bold=True))
    d.text((80, 215), "Specifications: Intel Core i7-14700HX, RTX 4070 (8GB GDDR6), 16GB DDR5, 1TB NVMe Gen4 SSD", fill=(50, 50, 50), font=get_font(14))
    d.text((80, 245), "Serial Number: NHQNQSI002401824 | Extended 2-Year Croma ZipCare Total Warranty Plan", fill=(50, 50, 50), font=get_font(14))
    d.text((80, 285), "Base Price: ₹1,24,990.00 | ZipCare Warranty: ₹9,510.00 | Total Tax (18% GST): Included", fill=(50, 50, 50), font=get_font(15))
    d.text((80, 330), "Total Amount Charged: ₹1,34,500.00 (Paid via UPI / GPay Transaction ID: 629019284019)", fill=(0, 128, 64), font=get_font(17, bold=True))
    img.save(OUT_DIR / "receipt_croma_gaming_laptop.png", optimize=True)

# ─── 3. Computer Vision & Satellite Projects ──────────────────────────────────

def gen_cv_isro_satellite():
    img = Image.new("RGB", (1280, 800), (15, 23, 42))
    d = ImageDraw.Draw(img)
    draw_header(d, "🛰️ ISRO Remote Sensing — Aerial Land-Use Segmentation", "Model: DeepLabV3+ ResNet-101", accent=(30, 58, 138))
    
    d.text((40, 80), "Multispectral Satellite Imagery Classification Benchmark (Cartosat-3 0.28m GSD)", fill=(248, 250, 252), font=get_font(20, bold=True))
    
    metrics = [
        ("Mean IoU (Overall)", "86.4%", (34, 197, 94)),
        ("Urban / Buildings mAP", "91.2%", (59, 130, 246)),
        ("Agricultural Crops F1", "88.7%", (168, 85, 247)),
        ("Inference Latency (GPU)", "14.2 ms", (249, 115, 22))
    ]
    for i, (k, v, c) in enumerate(metrics):
        x = 40 + i * 300
        d.rounded_rectangle([x, 130, x + 280, 230], radius=10, fill=(30, 41, 59), outline=(51, 65, 85))
        d.text((x + 20, 150), k, fill=(148, 163, 184), font=get_font(14))
        d.text((x + 20, 180), v, fill=c, font=get_font(28, bold=True))

    d.rounded_rectangle([40, 260, 1240, 740], radius=12, fill=(30, 41, 59), outline=(51, 65, 85))
    d.text((70, 290), "PyTorch Pipeline Implementation & Dataset Configuration", fill=(248, 250, 252), font=get_font(18, bold=True))
    
    code = [
        "# Dataset: ISRO-DOTA-V2 Aerial Object Detection & Land Cover",
        "model = DeepLabV3Plus(encoder_name='resnet101', encoder_weights='imagenet', classes=15)",
        "criterion = CombinedLoss(dice_weight=0.5, focal_weight=0.5, gamma=2.0)",
        "optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=1e-2)",
        "scheduler = CosineAnnealingLR(optimizer, T_max=100, eta_min=1e-6)",
        "# RTX 5060 TensorRT FP16 Export Latency: 14.2ms @ 1024x1024 input resolution",
        "# Validated on ISRO Ahmedabad Remote Sensing Center Dataset (Cartosat-3 Multispectral)",
    ]
    for i, line in enumerate(code):
        d.text((70, 340 + i * 38), line, fill=(74, 222, 128) if line.startswith("#") else (226, 232, 240), font=get_font(15))
        
    img.save(OUT_DIR / "research_isro_satellite_segmentation.png", optimize=True)

def gen_cv_yolov10():
    img = Image.new("RGB", (1280, 800), (24, 24, 27))
    d = ImageDraw.Draw(img)
    draw_header(d, "🚀 Ultralytics YOLOv10 — Real-Time Detection & Benchmarking", "Dataset: DOTA-Aerial-v2", accent=(168, 85, 247))
    
    d.text((40, 80), "YOLOv10-X vs YOLOv8-X vs RT-DETR Benchmark on RTX 5060 Laptop GPU", fill=(244, 244, 245), font=get_font(20, bold=True))
    
    d.rounded_rectangle([40, 130, 1240, 480], radius=10, fill=(39, 39, 42), outline=(63, 63, 70))
    headers = ["Model Architecture", "Parameters", "FLOPs", "mAP@50", "mAP@50:95", "Latency (TensorRT FP16)"]
    for i, h in enumerate(headers):
        d.text((60 + i * 195, 150), h, fill=(161, 161, 170), font=get_font(14, bold=True))
        
    d.line([(40, 185), (1240, 185)], fill=(63, 63, 70))
    rows = [
        ("YOLOv10-N (Nano)", "2.3 M", "6.7 G", "68.2%", "42.4%", "1.8 ms"),
        ("YOLOv10-S (Small)", "7.2 M", "21.6 G", "76.4%", "51.3%", "3.2 ms"),
        ("YOLOv10-M (Medium)", "15.4 M", "50.9 G", "83.1%", "59.2%", "5.6 ms"),
        ("YOLOv10-L (Large)", "24.4 M", "98.7 G", "87.8%", "65.4%", "8.9 ms"),
        ("YOLOv10-X (Extra-Large)", "29.5 M", "130.4 G", "91.2%", "70.1%", "11.4 ms"),
    ]
    for r_idx, row in enumerate(rows):
        y = 205 + r_idx * 50
        is_highlight = r_idx == 4
        if is_highlight:
            d.rectangle([42, y - 8, 1238, y + 38], fill=(57, 45, 78))
        for c_idx, val in enumerate(row):
            col_c = (216, 180, 254) if is_highlight else (228, 228, 231)
            d.text((60 + c_idx * 195, y), val, fill=col_c, font=get_font(15, bold=is_highlight))
            
    d.rounded_rectangle([40, 510, 1240, 750], radius=10, fill=(39, 39, 42), outline=(63, 63, 70))
    d.text((60, 530), "Computer Vision Research Conclusion & Model Weights Checkpoint", fill=(244, 244, 245), font=get_font(17, bold=True))
    d.text((60, 565), "• YOLOv10-X achieves the highest accuracy-to-latency frontier for aerial drone object detection.", fill=(161, 161, 170), font=get_font(14))
    d.text((60, 595), "• Consistent-Dual-Assignments for NMS-free training eliminates inference bottleneck.", fill=(161, 161, 170), font=get_font(14))
    d.text((60, 625), "• Checkpoint path: /models/checkpoints/yolov10x_isro_aerial_best.pt (Epoch 100/100, Val Loss: 0.0142)", fill=(161, 161, 170), font=get_font(14))
    img.save(OUT_DIR / "code_ultralytics_yolov10_benchmark.png", optimize=True)

# ─── 4. Mushroom Recipes ─────────────────────────────────────────────────────

def gen_recipe_creamy_mushrooms():
    img = Image.new("RGB", (1280, 800), (255, 253, 250))
    d = ImageDraw.Draw(img)
    draw_header(d, "🍄 Gourmet Recipe: Creamy Garlic Butter Wild Mushrooms", "Prep: 10m | Cook: 15m | Servings: 4", accent=(180, 83, 9))
    
    d.text((60, 80), "Pan-Seared Wild Mushrooms in White Wine & Heavy Cream with Fresh Thyme", fill=(69, 26, 3), font=get_font(22, bold=True))
    
    d.rounded_rectangle([60, 130, 500, 730], radius=12, fill=(254, 243, 199), outline=(245, 158, 11))
    d.text((80, 150), "Ingredients Required:", fill=(120, 53, 15), font=get_font(18, bold=True))
    ing = [
        "500g Mixed Wild Mushrooms (Cremini, Shiitake, Oyster)",
        "3 tbsp Extra Virgin Olive Oil & 2 tbsp Salted Butter",
        "4 cloves Fresh Garlic, finely minced",
        "1/2 cup Dry White Wine (or vegetable broth)",
        "3/4 cup Heavy Double Cream",
        "1/3 cup Freshly Grated Aged Parmesan Cheese",
        "1 tbsp Fresh Thyme leaves & chopped flat-leaf parsley",
        "Freshly cracked black pepper and kosher salt to taste",
        "Toasted artisan sourdough bread for serving",
    ]
    y = 190
    for item in ing:
        lines = textwrap.wrap(item, 38)
        for l in lines:
            d.text((80, y), "• " + l, fill=(69, 26, 3), font=get_font(14))
            y += 22
        y += 6

    d.rounded_rectangle([530, 130, 1220, 730], radius=12, fill=(255, 255, 255), outline=(229, 231, 235))
    d.text((560, 150), "Step-by-Step Cooking Instructions:", fill=(17, 24, 39), font=get_font(18, bold=True))
    steps = [
        ("Step 1: Sear Mushrooms", "Heat butter and olive oil in a wide heavy-bottomed skillet over high heat. Add sliced mushrooms in a single layer. Let brown undisturbed for 4 minutes until deep golden."),
        ("Step 2: Aromatics & Deglaze", "Add minced garlic and fresh thyme. Sauté for 1 minute until fragrant. Pour in dry white wine to deglaze the skillet, scraping up all flavorful browned bits."),
        ("Step 3: Simmer Cream Sauce", "Pour in the heavy cream and bring to a gentle simmer for 3 minutes until slightly thickened. Stir in grated Parmesan cheese until melted and velvety."),
        ("Step 4: Season & Garnish", "Season with kosher salt and black pepper. Garnish generously with freshly chopped parsley and serve immediately over warm crusty sourdough slices."),
    ]
    y = 195
    for title, desc in steps:
        d.text((560, y), title, fill=(180, 83, 9), font=get_font(16, bold=True))
        y += 26
        lines = textwrap.wrap(desc, 65)
        for l in lines:
            d.text((560, y), l, fill=(55, 65, 81), font=get_font(14))
            y += 22
        y += 14
        
    img.save(OUT_DIR / "recipe_creamy_garlic_wild_mushrooms.png", optimize=True)

def gen_recipe_shiitake_risotto():
    img = Image.new("RGB", (1280, 800), (253, 251, 247))
    d = ImageDraw.Draw(img)
    draw_header(d, "🍚 Classic Italian: Shiitake & Porcini Truffle Risotto", "Difficulty: Intermediate | Time: 35 min", accent=(13, 148, 136))
    
    d.text((60, 80), "Slow-Cooked Carnaroli Rice with Rehydrated Porcini, Sautéed Shiitake & White Truffle Oil", fill=(19, 78, 74), font=get_font(20, bold=True))
    
    d.rounded_rectangle([60, 130, 600, 730], radius=12, fill=(240, 253, 250), outline=(94, 234, 212))
    d.text((80, 150), "Key Ingredients:", fill=(15, 118, 110), font=get_font(18, bold=True))
    ingredients = [
        "300g Carnaroli or Arborio Risotto Rice",
        "200g Fresh Shiitake Mushrooms (sliced)",
        "30g Dried Porcini Mushrooms (soaked in warm water)",
        "1 Liter Warm Rich Vegetable / Mushroom Broth",
        "1 Medium Shallot, finely diced",
        "1/2 cup Dry White Wine (Pinot Grigio)",
        "50g Unsalted Cold Butter (cubed for mantecatura)",
        "60g Parmigiano-Reggiano, freshly grated",
        "1 tsp High-Grade White Truffle Oil",
    ]
    for i, item in enumerate(ingredients):
        d.text((80, 195 + i * 40), f"{i+1}. {item}", fill=(19, 78, 74), font=get_font(14))

    d.rounded_rectangle([630, 130, 1220, 730], radius=12, fill=(255, 255, 255), outline=(229, 231, 235))
    d.text((660, 150), "Chef's Technique (Mantecatura):", fill=(17, 24, 39), font=get_font(18, bold=True))
    notes = [
        "1. Rehydrate dry porcini mushrooms in 1 cup warm water for 20 minutes. Strain liquid and add it to your vegetable broth for deep earthy umami.",
        "2. Toast the carnaroli rice dry in olive oil with shallots until grains are translucent around edges.",
        "3. Add white wine and let it evaporate fully before adding broth one ladle at a time, stirring constantly.",
        "4. In a separate pan, sear fresh shiitake mushrooms in butter until crisp and caramelized.",
        "5. When rice is al dente (approx 18 mins), take off heat and beat in cold butter cubes and Parmigiano-Reggiano vigorously to create a silky, undulating wave (all'onda).",
        "6. Finish with a drizzle of aromatic white truffle oil before plating.",
    ]
    y = 195
    for n in notes:
        lines = textwrap.wrap(n, 56)
        for l in lines:
            d.text((660, y), l, fill=(55, 65, 81), font=get_font(14))
            y += 22
        y += 10
        
    img.save(OUT_DIR / "recipe_shiitake_mushroom_risotto.png", optimize=True)

# ─── 5. Accuracy & Loss Graphs ───────────────────────────────────────────────

def gen_chart_map_epoch():
    img = Image.new("RGB", (1280, 800), (255, 255, 255))
    d = ImageDraw.Draw(img)
    draw_header(d, "📈 Model Evaluation — YOLOv8 Detection mAP@0.50 & mAP@0.50:0.95 vs Epochs", "Trained on NVIDIA RTX 5060", accent=(37, 99, 235))
    
    d.text((60, 80), "Object Detection Accuracy Improvement Over 100 Training Epochs", fill=(15, 23, 42), font=get_font(20, bold=True))
    
    gx, gy, gw, gh = 100, 140, 1050, 480
    d.rectangle([gx, gy, gx + gw, gy + gh], fill=(248, 250, 252), outline=(203, 213, 225), width=2)
    
    for i in range(6):
        y_val = gy + i * (gh / 5)
        d.line([(gx, y_val), (gx + gw, y_val)], fill=(226, 232, 240))
        label = f"{100 - i * 20}%"
        d.text((gx - 45, y_val - 8), label, fill=(100, 116, 139), font=get_font(13))
        
    for i in range(11):
        x_val = gx + i * (gw / 10)
        d.line([(x_val, gy), (x_val, gy + gh)], fill=(226, 232, 240))
        d.text((x_val - 12, gy + gh + 10), f"E{i*10}", fill=(100, 116, 139), font=get_font(13))

    pts_map50 = []
    pts_map50_95 = []
    for ep in range(101):
        x = gx + (ep / 100.0) * gw
        val50 = 0.20 + 0.72 / (1.0 + math.exp(-0.08 * (ep - 35)))
        val95 = 0.10 + 0.58 / (1.0 + math.exp(-0.07 * (ep - 42)))
        y50 = gy + gh - val50 * gh
        y95 = gy + gh - val95 * gh
        pts_map50.append((x, y50))
        pts_map50_95.append((x, y95))
        
    d.line(pts_map50, fill=(37, 99, 235), width=4)
    d.line(pts_map50_95, fill=(22, 163, 74), width=4)
    
    d.text((gx + gw - 280, gy + 40), "● mAP@0.50 : 91.4% (Peak Accuracy)", fill=(37, 99, 235), font=get_font(16, bold=True))
    d.text((gx + gw - 280, gy + 70), "● mAP@0.50:0.95 : 67.8% (COCO Strict)", fill=(22, 163, 74), font=get_font(16, bold=True))
    
    d.rounded_rectangle([100, 670, 1150, 760], radius=8, fill=(241, 245, 249))
    d.text((120, 685), "Training Summary: Model converged at Epoch 84. Final weights saved to /weights/best.pt", fill=(30, 41, 59), font=get_font(15, bold=True))
    d.text((120, 715), "Optimizer: AdamW (lr=0.001) | Batch Size: 32 | Image Size: 640x640 | Hardware: NVIDIA GeForce RTX 5060 (8GB)", fill=(100, 116, 139), font=get_font(14))
    img.save(OUT_DIR / "chart_yolov8_map50_epoch_curve.png", optimize=True)

# ─── 6. Friend Addresses & Chat Messages ─────────────────────────────────────

def gen_chat_whatsapp_address():
    img = Image.new("RGB", (1280, 800), (239, 234, 226))
    d = ImageDraw.Draw(img)
    draw_header(d, "💬 WhatsApp Web — Rohan Mehta", "Online • Click here for contact info", accent=(7, 94, 84))
    
    d.rounded_rectangle([80, 120, 750, 200], radius=10, fill=(255, 255, 255))
    d.text((100, 135), "Hey Prajwal! Are you coming to dinner tonight?", fill=(17, 27, 33), font=get_font(15))
    d.text((680, 175), "18:42", fill=(102, 119, 129), font=get_font(12))
    
    d.rounded_rectangle([530, 230, 1200, 310], radius=10, fill=(217, 243, 199))
    d.text((550, 245), "Yes, absolutely! Send me the exact apartment address and landmark.", fill=(17, 27, 33), font=get_font(15))
    d.text((1130, 285), "18:44 ✓✓", fill=(83, 189, 235), font=get_font(12))
    
    d.rounded_rectangle([80, 340, 850, 560], radius=10, fill=(255, 255, 255))
    d.text((100, 360), "Here is the exact address:", fill=(17, 27, 33), font=get_font(15, bold=True))
    
    d.rounded_rectangle([100, 395, 830, 510], radius=8, fill=(240, 253, 244), outline=(34, 197, 94), width=2)
    d.text((120, 410), "Villa #42, Windmills of Your Mind", fill=(20, 83, 45), font=get_font(17, bold=True))
    d.text((120, 440), "5B Road, EPIP Zone, Whitefield, Bangalore, Karnataka - 560066", fill=(22, 101, 52), font=get_font(15))
    d.text((120, 470), "Landmark: Right next to KTPO Convention Centre & SAP Labs", fill=(21, 128, 61), font=get_font(14))
    
    d.text((780, 535), "18:45", fill=(102, 119, 129), font=get_font(12))
    
    d.rounded_rectangle([530, 590, 1200, 670], radius=10, fill=(217, 243, 199))
    d.text((550, 605), "Perfect! Booking a cab now. See you in 30 minutes! 🚗", fill=(17, 27, 33), font=get_font(15))
    d.text((1130, 645), "18:46 ✓✓", fill=(83, 189, 235), font=get_font(12))
    img.save(OUT_DIR / "conversation_whatsapp_dinner_address.png", optimize=True)

def gen_chat_slack_coworking():
    img = Image.new("RGB", (1280, 800), (255, 255, 255))
    d = ImageDraw.Draw(img)
    draw_header(d, "🏢 Slack — #hackathon-scryptic-team", "Channel Topic: SCRYPTIC 2026 Season II War Room", accent=(74, 21, 75))
    
    d.text((40, 90), "Ananya Sen  10:15 AM", fill=(29, 28, 29), font=get_font(16, bold=True))
    d.text((40, 120), "Hey team, we've booked the dedicated conference room for our hackathon sprint weekend!", fill=(29, 28, 29), font=get_font(15))
    
    d.rounded_rectangle([40, 160, 950, 320], radius=8, fill=(248, 248, 248), outline=(221, 221, 221), width=1)
    d.text((60, 180), "📍 War Room Location & Address Details", fill=(74, 21, 75), font=get_font(16, bold=True))
    d.text((60, 215), "WeWork Galaxy — 5th Floor, Room #502", fill=(29, 28, 29), font=get_font(16, bold=True))
    d.text((60, 245), "43 Residency Road, Shanthala Nagar, Ashok Nagar, Bangalore, Karnataka 560025", fill=(97, 96, 97), font=get_font(15))
    d.text((60, 275), "Security Pass Code: SCRYPTIC-GALAXY-8821 | Free Guest Parking Available in Basement B2", fill=(97, 96, 97), font=get_font(14))
    
    d.text((40, 360), "Prajwal Sharma  10:18 AM", fill=(29, 28, 29), font=get_font(16, bold=True))
    d.text((40, 390), "Got it! I'm bringing the RTX 5060 laptop and our local AURA models ready for deployment.", fill=(29, 28, 29), font=get_font(15))
    img.save(OUT_DIR / "conversation_slack_coworking_address.png", optimize=True)

# ─── 7. Red Sports Cars ──────────────────────────────────────────────────────

def gen_ferrari_f8():
    img = Image.new("RGB", (1280, 800), (20, 20, 25))
    d = ImageDraw.Draw(img)
    draw_header(d, "🏎️ Automotive Showcase — Ferrari F8 Tributo (Rosso Corsa)", "Twin-Turbo V8 • 710 Horsepower", accent=(220, 38, 38))
    
    d.rectangle([60, 100, 1220, 520], fill=(30, 30, 38), outline=(60, 60, 75))
    car_red = (220, 20, 40)
    
    car_pts = [
        (150, 420), (220, 380), (380, 370), (520, 290), (760, 280), (950, 340),
        (1100, 370), (1140, 430), (1080, 450), (980, 450), (900, 450), (450, 450),
        (380, 450), (260, 450), (150, 440)
    ]
    d.polygon(car_pts, fill=car_red)
    
    window_pts = [(530, 300), (740, 290), (890, 345), (580, 360)]
    d.polygon(window_pts, fill=(15, 23, 42))
    
    d.ellipse([260, 380, 380, 500], fill=(20, 20, 20), outline=(180, 180, 180), width=6)
    d.ellipse([290, 410, 350, 470], fill=(200, 200, 200))
    d.ellipse([880, 380, 1000, 500], fill=(20, 20, 20), outline=(180, 180, 180), width=6)
    d.ellipse([910, 410, 970, 470], fill=(200, 200, 200))
    
    d.polygon([(1100, 375), (1140, 410), (1090, 410)], fill=(255, 255, 200))
    d.rectangle([140, 435, 220, 450], fill=(10, 10, 10))
    
    d.text((100, 130), "Ferrari F8 Tributo Coupe — Finished in Classic Rosso Corsa Red", fill=(255, 255, 255), font=get_font(24, bold=True))
    d.text((100, 170), "3.9L Twin-Turbocharged V8 | 0-100 km/h in 2.9 seconds | Top Speed: 340 km/h (211 mph)", fill=(200, 200, 210), font=get_font(16))
    
    d.rounded_rectangle([60, 550, 1220, 750], radius=10, fill=(35, 35, 45), outline=(60, 60, 75))
    d.text((90, 575), "Vehicle Specifications & Gallery Details", fill=(255, 255, 255), font=get_font(18, bold=True))
    specs = [
        "Paint: Rosso Corsa (Triple-Layer Special Racing Red) with Giallo Modena brake calipers",
        "Interior: Cuoio Leather with Nero Alcantara inserts and Rosso contrast stitching",
        "Wheels: 20-inch Forged Diamond-Cut Racing Rims with Michelin Pilot Sport Cup 2 tires",
        "Exhaust: Titanium sports exhaust system with carbon fiber rear aerodynamic diffuser",
    ]
    for i, s in enumerate(specs):
        d.text((90, 615 + i * 28), "• " + s, fill=(180, 180, 195), font=get_font(14))
    img.save(OUT_DIR / "scene_ferrari_f8_tributo_red.png", optimize=True)

def gen_porsche_gt3_red():
    img = Image.new("RGB", (1280, 800), (24, 24, 27))
    d = ImageDraw.Draw(img)
    draw_header(d, "🏁 Porsche 911 GT3 (992) — Carmine Red Track Monster", "4.0L Naturally Aspirated Boxer-6 • 9,000 RPM", accent=(220, 38, 38))
    
    d.rounded_rectangle([60, 90, 1220, 520], radius=12, fill=(39, 39, 42), outline=(63, 63, 70))
    d.text((90, 120), "Porsche 911 GT3 with Touring Package — Guards Red / Carmine Red", fill=(255, 255, 255), font=get_font(22, bold=True))
    d.text((90, 155), "Swan-neck rear wing generates 385 kg of downforce at track speeds.", fill=(161, 161, 170), font=get_font(15))
    
    d.rectangle([100, 200, 1180, 480], fill=(20, 20, 22))
    d.polygon([(180, 430), (280, 360), (450, 340), (600, 250), (820, 250), (1050, 360), (1120, 430)], fill=(215, 25, 35))
    d.polygon([(610, 260), (800, 260), (980, 355), (650, 355)], fill=(10, 15, 25))
    d.ellipse([280, 380, 400, 500], fill=(15, 15, 15), outline=(150, 150, 150), width=5)
    d.ellipse([880, 380, 1000, 500], fill=(15, 15, 15), outline=(150, 150, 150), width=5)
    d.rectangle([180, 320, 260, 335], fill=(20, 20, 20))
    d.rectangle([210, 335, 230, 380], fill=(20, 20, 20))
    
    d.rounded_rectangle([60, 550, 1220, 750], radius=10, fill=(39, 39, 42), outline=(63, 63, 70))
    d.text((90, 575), "Nürburgring Nordschleife Lap Time: 6:59.927 minutes", fill=(239, 68, 68), font=get_font(18, bold=True))
    d.text((90, 610), "Engine: 4.0-liter naturally aspirated flat-six producing 502 hp and 346 lb-ft torque.", fill=(212, 212, 216), font=get_font(14))
    d.text((90, 640), "Transmission: 7-speed dual-clutch PDK with mechanical limited-slip differential.", fill=(212, 212, 216), font=get_font(14))
    d.text((90, 670), "Brakes: Porsche Ceramic Composite Brakes (PCCB) with yellow 6-piston monobloc calipers.", fill=(212, 212, 216), font=get_font(14))
    img.save(OUT_DIR / "scene_porsche_911_gt3_carmine_red.png", optimize=True)

# ─── 8. Terminal Error Tracebacks ────────────────────────────────────────────

def gen_terminal_cuda_oom():
    img = Image.new("RGB", (1280, 800), (12, 12, 12))
    d = ImageDraw.Draw(img)
    
    d.rectangle([0, 0, 1280, 36], fill=(30, 30, 30))
    d.ellipse([16, 12, 28, 24], fill=(255, 95, 86))
    d.ellipse([36, 12, 48, 24], fill=(255, 189, 46))
    d.ellipse([56, 12, 68, 24], fill=(39, 201, 63))
    d.text((120, 8), "prajwal@zenith: ~/code/vision-engine — (venv_rtx5060) — 1280x800", fill=(200, 200, 200), font=get_font(13))

    lines = [
        ("prajwal@zenith:~/code/vision-engine$ ", (100, 220, 100), "python train_vit_model.py --batch-size 64 --img-size 1024", (255, 255, 255)),
        ("[INFO] 2026-08-16 21:14:02 - Initializing Vision Transformer (ViT-Huge) on device cuda:0", (150, 150, 150), "", (0, 0, 0)),
        ("[INFO] Loaded 125,000 satellite training images across 15 remote sensing classes", (150, 150, 150), "", (0, 0, 0)),
        ("Epoch 1/100:   0%|                                    | 0/1953 [00:00<?, ?it/s]", (220, 220, 220), "", (0, 0, 0)),
        ("Traceback (most recent call last):", (255, 85, 85), "", (0, 0, 0)),
        ("  File \"/home/prajwal/code/vision-engine/train_vit_model.py\", line 142, in <module>", (200, 200, 200), "", (0, 0, 0)),
        ("    outputs = model(images.to(device))", (255, 255, 255), "", (0, 0, 0)),
        ("  File \"/home/prajwal/venv/lib/python3.11/site-packages/torch/nn/modules/module.py\", line 1501, in _call_impl", (200, 200, 200), "", (0, 0, 0)),
        ("    return forward_call(*args, **kwargs)", (255, 255, 255), "", (0, 0, 0)),
        ("  File \"/home/prajwal/code/vision-engine/models/vit.py\", line 88, in forward", (200, 200, 200), "", (0, 0, 0)),
        ("    attn_weights = torch.matmul(q, k.transpose(-2, -1)) * self.scale", (255, 255, 255), "", (0, 0, 0)),
        ("torch.cuda.OutOfMemoryError: CUDA out of memory. Tried to allocate 4.20 GiB (GPU 0; 8.00 GiB total capacity;", (255, 85, 85), "", (0, 0, 0)),
        ("  6.74 GiB already allocated; 652.00 MiB free; 6.98 GiB reserved in total by PyTorch)", (255, 85, 85), "", (0, 0, 0)),
        ("If reserved memory is >> allocated memory try setting max_split_size_mb to avoid fragmentation.", (255, 200, 85), "", (0, 0, 0)),
        ("See documentation for Memory Management and PYTORCH_CUDA_ALLOC_CONF", (255, 200, 85), "", (0, 0, 0)),
        ("", (0,0,0), "", (0,0,0)),
        ("Suggested Fix: Reduce --batch-size from 64 to 16, or enable torch.cuda.amp.autocast(dtype=torch.float16)", (85, 255, 85), "", (0, 0, 0)),
    ]
    
    y = 50
    for prompt, p_col, cmd, c_col in lines:
        d.text((20, y), prompt, fill=p_col, font=get_font(14))
        if cmd:
            p_len = len(prompt) * 8
            d.text((20 + p_len, y), cmd, fill=c_col, font=get_font(14, bold=True))
        y += 24
        
    img.save(OUT_DIR / "terminal_cuda_out_of_memory_error.png", optimize=True)

def gen_terminal_docker_error():
    img = Image.new("RGB", (1280, 800), (18, 18, 24))
    d = ImageDraw.Draw(img)
    draw_header(d, "🐳 Docker Build Failed — Next.js Production Container", "Exit Code: 1", accent=(220, 38, 38))
    
    logs = [
        "$ docker build -t aura-frontend:v1.0 .",
        "[+] Building 14.8s (11/14) FINISHED",
        " => [internal] load build definition from Dockerfile                               0.0s",
        " => [internal] load .dockerignore                                                 0.0s",
        " => [stage-1 3/6] COPY package.json package-lock.json ./                          0.2s",
        " => ERROR [stage-1 4/6] RUN npm ci --legacy-peer-deps                            14.2s",
        "------",
        " > [stage-1 4/6] RUN npm ci --legacy-peer-deps:",
        "npm ERR! code ERESOLVE",
        "npm ERR! ERESOLVE could not resolve",
        "npm ERR! While resolving: react-force-graph-2d@1.25.4",
        "npm ERR! Found: react@19.0.0",
        "npm ERR! node_modules/react",
        "npm ERR!   react@\"^19.0.0\" from the root project",
        "npm ERR! Could not resolve dependency:",
        "npm ERR! peer react@\"^16.8.0 || ^17.0.0 || ^18.0.0\" from react-force-graph-2d@1.25.4",
        "npm ERR! Fix with: npm install react-force-graph-2d --legacy-peer-deps",
        "------",
        "Dockerfile:14",
        "--------------------",
        "  12 |     COPY package*.json ./",
        "  13 |     # Install dependencies",
        "  14 | >>> RUN npm ci --legacy-peer-deps",
        "  15 |     COPY . .",
        "--------------------",
        "ERROR: failed to solve: process \"/bin/sh -c npm ci --legacy-peer-deps\" did not complete successfully: exit code 1",
    ]
    y = 70
    for line in logs:
        if "ERROR" in line or "npm ERR!" in line:
            c = (248, 113, 113)
        elif ">>>" in line:
            c = (250, 204, 21)
        elif line.startswith("$"):
            c = (74, 222, 128)
        else:
            c = (209, 213, 219)
        d.text((30, y), line, fill=c, font=get_font(14))
        y += 24
        
    img.save(OUT_DIR / "terminal_docker_build_failure_traceback.png", optimize=True)

def generate_all_new():
    print("Generating targeted high-definition screenshots across all 8 hackathon question domains...")
    gen_wifi_guest()
    gen_wifi_router_tplink()
    gen_wifi_cafe_starbucks()
    gen_receipt_macbook()
    gen_receipt_lenovo_legion()
    gen_receipt_croma_helios()
    gen_cv_isro_satellite()
    gen_cv_yolov10()
    gen_recipe_creamy_mushrooms()
    gen_recipe_shiitake_risotto()
    gen_chart_map_epoch()
    gen_chat_whatsapp_address()
    gen_chat_slack_coworking()
    gen_ferrari_f8()
    gen_porsche_gt3_red()
    gen_terminal_cuda_oom()
    gen_terminal_docker_error()
    print("All rich demo screenshots generated in demo_data/screenshots/!")

if __name__ == "__main__":
    generate_all_new()
