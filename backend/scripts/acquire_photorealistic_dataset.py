"""
AURA — High-Fidelity Photorealistic & Visual Dataset Generator
Produces visually breathtaking, realistic screenshots & open-source CC0 photography
for all 11 clusters to ensure the highest competition-winning visual quality.
"""
import os
import sys
import json
import math
import random
import urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DEMO_DIR = ROOT_DIR / "demo_data" / "screenshots"
DEMO_DIR.mkdir(parents=True, exist_ok=True)

W, H = 1280, 800

# ─── Font Helper ─────────────────────────────────────────────────────────────

def get_font(size=16, bold=False, mono=False):
    if mono:
        font_names = ["consola.ttf", "cour.ttf", "lucon.ttf", "DejaVuSansMono.ttf"]
    elif bold:
        font_names = ["segoeuib.ttf", "arialbd.ttf", "calibrib.ttf", "DejaVuSans-Bold.ttf"]
    else:
        font_names = ["segoeui.ttf", "arial.ttf", "calibri.ttf", "DejaVuSans.ttf"]

    for name in font_names:
        for path in [
            Path(f"C:/Windows/Fonts/{name}"),
            Path(f"/usr/share/fonts/truetype/{name}"),
            Path(name),
        ]:
            if path.exists():
                try:
                    return ImageFont.truetype(str(path), size)
                except Exception:
                    pass
    return ImageFont.load_default()


# ─── Open-Source Image Downloader Helper ─────────────────────────────────────

def download_or_create(filename: str, urls: list, fallback_fn):
    """Attempt downloading high-res open-source photo from Wikimedia/CC0 sources; fallback to high-fidelity PIL generator."""
    dest = DEMO_DIR / filename
    headers = {
        "User-Agent": "AURA-VisualMemoryEngine/1.0 (https://github.com/scryptic-aura; contact@scryptic.ai) Python-urllib"
    }

    for url in urls:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=8) as response:
                if response.status == 200:
                    data = response.read()
                    if len(data) > 5000:
                        # Save and resize to 1280x800 if needed
                        from io import BytesIO
                        img = Image.open(BytesIO(data)).convert("RGB")
                        # Cover resize to (W, H)
                        img_ratio = img.width / img.height
                        target_ratio = W / H
                        if img_ratio > target_ratio:
                            new_height = H
                            new_width = int(H * img_ratio)
                        else:
                            new_width = W
                            new_height = int(W / img_ratio)
                        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                        # Center crop
                        left = (new_width - W) // 2
                        top = (new_height - H) // 2
                        img = img.crop((left, top, left + W, top + H))
                        img.save(dest, "PNG")
                        print(f"✅ Downloaded & cropped high-res photo: {filename}")
                        return
        except Exception as e:
            # Continue to next source
            pass

    # Fallback to high-fidelity PIL rendering
    fallback_fn(dest)
    print(f"🎨 Generated high-fidelity visual render: {filename}")


# ─── Photo Downloads & Fallbacks ─────────────────────────────────────────────

def gen_red_sports_car(dest):
    urls = [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/2018_Ferrari_Portofino%2C_front_11.11.18.jpg/1280px-2018_Ferrari_Portofino%2C_front_11.11.18.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/67/Porsche_911_GT3_RS_%28991%29_%E2%80%93_Frontansicht%2C_28._August_2015%2C_D%C3%BCsseldorf.jpg/1280px-Porsche_911_GT3_RS_%28991%29_%E2%80%93_Frontansicht%2C_28._August_2015%2C_D%C3%BCsseldorf.jpg",
        "https://images.unsplash.com/photo-1544829099-b9a0c07fad1a?auto=format&fit=crop&w=1280&q=80",
    ]
    def fallback(p):
        img = Image.new("RGB", (W, H), (18, 18, 22))
        d = ImageDraw.Draw(img)
        # Gradient backdrop
        for y in range(H):
            r = int(18 + (y / H) * 25)
            d.line([(0, y), (W, y)], fill=(r, r, r + 5))
        # Sleek sports car
        d.rectangle([100, 560, W - 100, H - 40], fill=(25, 25, 30))
        d.polygon([(240, 560), (380, 420), (880, 420), (1060, 520), (1080, 580), (200, 580)], fill=(210, 25, 45))
        d.polygon([(420, 420), (520, 310), (760, 310), (860, 420)], fill=(12, 16, 20))
        d.ellipse([300, 500, 450, 650], fill=(15, 15, 18), outline=(160, 160, 170), width=6)
        d.ellipse([820, 500, 970, 650], fill=(15, 15, 18), outline=(160, 160, 170), width=6)
        d.text((W // 2, 720), "Crimson Red Italian Sports Car • Automotive Studio Photography", fill=(140, 145, 155), font=get_font(18, bold=True), anchor="mm")
        img.save(p, "PNG")
    download_or_create("scene_red_sports_car.png", urls, fallback)


def gen_mountain_view(dest):
    urls = [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Everest_North_Face_toward_Base_Camp-1920px.jpg/1280px-Everest_North_Face_toward_Base_Camp-1920px.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Matterhorn_from_Domh%C3%BCtte_-_2.jpg/1280px-Matterhorn_from_Domh%C3%BCtte_-_2.jpg",
        "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1280&q=80",
    ]
    def fallback(p):
        img = Image.new("RGB", (W, H), (135, 206, 235))
        d = ImageDraw.Draw(img)
        d.polygon([(0, 450), (400, 180), (700, 480)], fill=(240, 245, 255))
        d.polygon([(350, 480), (750, 120), (1150, 520)], fill=(255, 255, 255))
        d.polygon([(700, 520), (1050, 220), (W, 500)], fill=(230, 235, 245))
        d.rectangle([0, 480, W, H], fill=(45, 95, 55))
        d.text((W // 2, 740), "Himalayan Snow-Capped Mountain Range • High Altitude Landscape", fill=(240, 245, 240), font=get_font(18, bold=True), anchor="mm")
        img.save(p, "PNG")
    download_or_create("scene_mountain_view.png", urls, fallback)


def gen_food_pizza(dest):
    urls = [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a3/Eq_it-na_pizza-margherita_sep2005_sml.jpg/1280px-Eq_it-na_pizza-margherita_sep2005_sml.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d1/Pepperoni_pizza.jpg/1280px-Pepperoni_pizza.jpg",
        "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=1280&q=80",
    ]
    def fallback(p):
        img = Image.new("RGB", (W, H), (45, 35, 30))
        d = ImageDraw.Draw(img)
        d.ellipse([340, 100, 940, 700], fill=(225, 175, 95), outline=(175, 120, 55), width=18)
        d.ellipse([370, 130, 910, 670], fill=(185, 45, 30))
        d.ellipse([450, 220, 560, 320], fill=(250, 245, 230))
        d.ellipse([680, 280, 790, 380], fill=(250, 245, 230))
        d.ellipse([520, 450, 640, 560], fill=(250, 245, 230))
        d.text((W // 2, 740), "Artisanal Wood-Fired Truffle & Burrata Pizza • Gourmet Cuisine", fill=(245, 235, 220), font=get_font(18, bold=True), anchor="mm")
        img.save(p, "PNG")
    download_or_create("food_photo_truffle_pizza.png", urls, fallback)


def gen_food_pasta(dest):
    urls = [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/Espaguetis_carbonara.jpg/1280px-Espaguetis_carbonara.jpg",
        "https://images.unsplash.com/photo-1546549032-9571cd6b27df?auto=format&fit=crop&w=1280&q=80",
    ]
    def fallback(p):
        img = Image.new("RGB", (W, H), (35, 30, 28))
        d = ImageDraw.Draw(img)
        d.ellipse([320, 80, 960, 720], fill=(245, 240, 235), outline=(200, 195, 190), width=14)
        d.ellipse([390, 150, 890, 650], fill=(245, 215, 140))
        d.text((W // 2, 750), "Creamy Wild Mushroom Tagliatelle with Shaved Truffle", fill=(240, 235, 225), font=get_font(18, bold=True), anchor="mm")
        img.save(p, "PNG")
    download_or_create("food_photo_mushroom_pasta.png", urls, fallback)


def gen_food_ramen(dest):
    urls = [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dc/Shoyu_Ramen.jpg/1280px-Shoyu_Ramen.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cb/Ramen_at_Ichiran%2C_Shinjuku.jpg/1280px-Ramen_at_Ichiran%2C_Shinjuku.jpg",
    ]
    def fallback(p):
        img = Image.new("RGB", (W, H), (32, 28, 25))
        d = ImageDraw.Draw(img)
        d.ellipse([330, 90, 950, 710], fill=(120, 30, 25), outline=(60, 15, 12), width=16)
        d.ellipse([380, 140, 900, 660], fill=(185, 115, 45))
        d.ellipse([450, 230, 560, 340], fill=(255, 255, 250))
        d.ellipse([480, 260, 530, 310], fill=(255, 140, 0))
        d.text((W // 2, 750), "Traditional Japanese Tonkotsu Ramen with Chashu & Soft Boiled Egg", fill=(240, 235, 225), font=get_font(18, bold=True), anchor="mm")
        img.save(p, "PNG")
    download_or_create("food_photo_japanese_ramen.png", urls, fallback)


def gen_photo_watch(dest):
    urls = [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Omega_Speedmaster_Professional_3570.50.00.jpg/1280px-Omega_Speedmaster_Professional_3570.50.00.jpg",
        "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=1280&q=80",
    ]
    def fallback(p):
        img = Image.new("RGB", (W, H), (240, 238, 235))
        d = ImageDraw.Draw(img)
        d.rectangle([540, 20, 740, H - 20], fill=(70, 45, 30), outline=(40, 25, 15), width=2)
        d.ellipse([430, 190, 850, 610], fill=(210, 215, 220), outline=(150, 155, 160), width=16)
        d.ellipse([460, 220, 820, 580], fill=(20, 28, 45))
        d.text((W // 2, 380), "CHRONOGRAPH", fill=(220, 225, 235), font=get_font(16, bold=True), anchor="mm")
        d.text((W // 2, 750), "Stainless Steel Luxury Chronograph Watch • Blue Sunburst Dial", fill=(50, 55, 65), font=get_font(18, bold=True), anchor="mm")
        img.save(p, "PNG")
    download_or_create("photo_watch_chronograph.png", urls, fallback)


def gen_photo_sneakers(dest):
    urls = [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/92/Adidas_Stan_Smith_Original.jpg/1280px-Adidas_Stan_Smith_Original.jpg",
        "https://images.unsplash.com/photo-1549298916-b41d501d3772?auto=format&fit=crop&w=1280&q=80",
    ]
    def fallback(p):
        img = Image.new("RGB", (W, H), (245, 245, 247))
        d = ImageDraw.Draw(img)
        d.rectangle([200, 520, 1080, 560], fill=(220, 220, 225))
        d.polygon([(260, 520), (320, 360), (620, 320), (960, 440), (1020, 520)], fill=(255, 255, 255), outline=(200, 200, 205), width=2)
        d.text((W // 2, 720), "Minimalist White Leather Low-Top Designer Sneakers", fill=(60, 65, 75), font=get_font(18, bold=True), anchor="mm")
        img.save(p, "PNG")
    download_or_create("photo_sneakers_white.png", urls, fallback)


def gen_photo_laptop_silver(dest):
    urls = [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Laptop_PC_open.jpg/1280px-Laptop_PC_open.jpg",
        "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=1280&q=80",
    ]
    def fallback(p):
        img = Image.new("RGB", (W, H), (235, 238, 242))
        d = ImageDraw.Draw(img)
        d.polygon([(340, 160), (940, 160), (970, 560), (310, 560)], fill=(30, 35, 45), outline=(180, 185, 195), width=6)
        d.polygon([(240, 560), (1040, 560), (1080, 620), (200, 620)], fill=(200, 205, 215), outline=(160, 165, 175), width=2)
        d.text((W // 2, 720), "Ultra-Thin Metallic Silver Ultrabook • 14-Inch OLED Display", fill=(50, 55, 65), font=get_font(18, bold=True), anchor="mm")
        img.save(p, "PNG")
    download_or_create("product_photo_silver_laptop.png", urls, fallback)


def gen_photo_headphones_black(dest):
    urls = [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Headphones_icon.jpg/1280px-Headphones_icon.jpg",
        "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=1280&q=80",
    ]
    def fallback(p):
        img = Image.new("RGB", (W, H), (240, 238, 232))
        d = ImageDraw.Draw(img)
        d.arc([360, 120, 920, 680], start=180, end=0, fill=(35, 35, 40), width=32)
        d.ellipse([340, 360, 480, 620], fill=(25, 25, 28), outline=(60, 60, 65), width=4)
        d.ellipse([800, 360, 940, 620], fill=(25, 25, 28), outline=(60, 60, 65), width=4)
        d.text((W // 2, 720), "Matte Black Wireless Active Noise-Cancelling Headphones", fill=(45, 45, 50), font=get_font(18, bold=True), anchor="mm")
        img.save(p, "PNG")
    download_or_create("product_photo_black_headphones.png", urls, fallback)


def gen_scene_beach_sunset(dest):
    urls = [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b2/Sunset_at_Candolim_Beach_Goa.jpg/1280px-Sunset_at_Candolim_Beach_Goa.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bf/Sunset_in_Goa.jpg/1280px-Sunset_in_Goa.jpg",
        "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1280&q=80",
    ]
    def fallback(p):
        img = Image.new("RGB", (W, H), (255, 140, 50))
        d = ImageDraw.Draw(img)
        d.ellipse([540, 280, 740, 480], fill=(255, 240, 150))
        d.rectangle([0, 440, W, H], fill=(40, 110, 140))
        d.text((W // 2, 740), "Golden Hour Sunset over Candolim Beach, South Goa", fill=(255, 245, 230), font=get_font(18, bold=True), anchor="mm")
        img.save(p, "PNG")
    download_or_create("scene_beach_sunset.png", urls, fallback)


def gen_scene_city_skyline(dest):
    urls = [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Singapore_Skyline_at_Night_3.jpg/1280px-Singapore_Skyline_at_Night_3.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Hong_Kong_Skyline_Restitch_-_Dec_2007.jpg/1280px-Hong_Kong_Skyline_Restitch_-_Dec_2007.jpg",
    ]
    def fallback(p):
        img = Image.new("RGB", (W, H), (10, 15, 30))
        d = ImageDraw.Draw(img)
        # Buildings
        rects = [(120, 250, 240, 680), (260, 180, 400, 680), (420, 320, 540, 680), (560, 140, 720, 680), (740, 220, 880, 680), (900, 300, 1060, 680)]
        for x1, y1, x2, y2 in rects:
            d.rectangle([x1, y1, x2, y2], fill=(22, 28, 48), outline=(60, 75, 115), width=2)
        d.rectangle([0, 680, W, H], fill=(8, 12, 24))
        d.text((W // 2, 740), "Metropolitan Skyline at Night • Long Exposure Cityscape", fill=(200, 215, 240), font=get_font(18, bold=True), anchor="mm")
        img.save(p, "PNG")
    download_or_create("scene_city_skyline.png", urls, fallback)


def gen_photo_office_workspace(dest):
    urls = [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Modern_office_desk_setup.jpg/1280px-Modern_office_desk_setup.jpg",
        "https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=1280&q=80",
    ]
    def fallback(p):
        img = Image.new("RGB", (W, H), (242, 240, 235))
        d = ImageDraw.Draw(img)
        d.rectangle([100, 480, W - 100, H - 60], fill=(185, 145, 105), outline=(140, 105, 75), width=4)
        d.rectangle([340, 180, 940, 480], fill=(25, 28, 35), outline=(120, 125, 135), width=6)
        d.text((W // 2, 740), "Minimalist Engineering Workspace with Dual 4K Displays", fill=(60, 65, 75), font=get_font(18, bold=True), anchor="mm")
        img.save(p, "PNG")
    download_or_create("photo_office_workspace.png", urls, fallback)


# ─── High-Fidelity UI & Vector Screenshots ───────────────────────────────────

def gen_amazon_laptop_receipt(dest):
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)

    # Amazon Header
    d.rectangle([0, 0, W, 70], fill=(35, 47, 62)) # Amazon Dark Navy
    d.text((40, 20), "amazon.in", fill=(255, 153, 0), font=get_font(28, bold=True))
    d.text((200, 26), "Tax Invoice / Official Bill of Sale", fill=(255, 255, 255), font=get_font(18, bold=True))
    d.text((W - 320, 28), "Original for Recipient", fill=(200, 210, 225), font=get_font(14))

    # Seller & Buyer Info Box
    d.rectangle([40, 90, 600, 240], fill=(248, 249, 250), outline=(220, 225, 230))
    d.text((60, 105), "Sold by:", fill=(100, 110, 120), font=get_font(13))
    d.text((60, 125), "Appario Retail Private Ltd", fill=(20, 30, 40), font=get_font(16, bold=True))
    d.text((60, 150), "Warehouse #14, Bidadi Industrial Area, Bangalore - 562109", fill=(60, 70, 80), font=get_font(13))
    d.text((60, 172), "GSTIN: 29AABCA1234F1ZS  •  PAN: AABCA1234F", fill=(30, 40, 50), font=get_font(13, bold=True))
    d.text((60, 195), "State: Karnataka (Code: 29)", fill=(100, 110, 120), font=get_font(13))

    d.rectangle([640, 90, W - 40, 240], fill=(248, 249, 250), outline=(220, 225, 230))
    d.text((660, 105), "Billing & Delivery Address:", fill=(100, 110, 120), font=get_font(13))
    d.text((660, 125), "Prajwal Sharma (Verified Customer)", fill=(20, 30, 40), font=get_font(16, bold=True))
    d.text((660, 150), "Flat 402, Prestige Palms, 12th Main Road, Indiranagar", fill=(60, 70, 80), font=get_font(13))
    d.text((660, 172), "Bangalore, Karnataka - 560038", fill=(60, 70, 80), font=get_font(13))
    d.text((660, 195), "Order Placed: August 10, 2026  •  Order ID: 402-1849204-7491023", fill=(30, 58, 138), font=get_font(13, bold=True))

    # Itemized Table Header
    d.rectangle([40, 260, W - 40, 300], fill=(235, 240, 248), outline=(200, 210, 225))
    d.text((60, 272), "Description", fill=(30, 41, 59), font=get_font(14, bold=True))
    d.text((620, 272), "HSN / SAC", fill=(30, 41, 59), font=get_font(14, bold=True))
    d.text((740, 272), "Qty", fill=(30, 41, 59), font=get_font(14, bold=True))
    d.text((840, 272), "Gross Amount", fill=(30, 41, 59), font=get_font(14, bold=True))
    d.text((1020, 272), "Tax Rate (GST)", fill=(30, 41, 59), font=get_font(14, bold=True))
    d.text((1160, 272), "Total", fill=(30, 41, 59), font=get_font(14, bold=True))

    # Line Item 1
    d.text((60, 320), "ASUS ZenBook 14 OLED (2026) Laptop Intel Core Ultra 7", fill=(15, 23, 42), font=get_font(15, bold=True))
    d.text((60, 345), "16GB LPDDR5X RAM, 1TB NVMe PCIe 4.0 SSD, 14\" 3K OLED 120Hz Display, Ponder Blue (UX3405MA)", fill=(71, 85, 105), font=get_font(13))
    d.text((620, 330), "84713010", fill=(71, 85, 105), font=get_font(13))
    d.text((740, 330), "1", fill=(15, 23, 42), font=get_font(14, bold=True))
    d.text((840, 330), "₹58,466.10", fill=(71, 85, 105), font=get_font(14))
    d.text((1020, 330), "18% (9% CGST + 9% SGST)", fill=(71, 85, 105), font=get_font(13))
    d.text((1140, 330), "₹68,990.00", fill=(15, 23, 42), font=get_font(16, bold=True))

    d.line([(40, 385), (W - 40, 385)], fill=(226, 232, 240), width=1)

    # Line Item 2 (Accessories)
    d.text((60, 400), "ASUS Sleeve Case & 65W USB-C GaN Fast Charger (Included in Box)", fill=(30, 41, 59), font=get_font(14))
    d.text((620, 400), "85044090", fill=(71, 85, 105), font=get_font(13))
    d.text((740, 400), "1", fill=(15, 23, 42), font=get_font(14))
    d.text((840, 400), "₹0.00", fill=(71, 85, 105), font=get_font(14))
    d.text((1020, 400), "0%", fill=(71, 85, 105), font=get_font(13))
    d.text((1160, 400), "₹0.00", fill=(15, 23, 42), font=get_font(14))

    d.line([(40, 440), (W - 40, 440)], fill=(203, 213, 225), width=2)

    # Totals Box
    d.rectangle([700, 460, W - 40, 640], fill=(248, 250, 252), outline=(203, 213, 225))
    d.text((720, 480), "Net Taxable Value:", fill=(71, 85, 105), font=get_font(14))
    d.text((1140, 480), "₹58,466.10", fill=(71, 85, 105), font=get_font(14))
    d.text((720, 510), "CGST (9.0%):", fill=(71, 85, 105), font=get_font(14))
    d.text((1140, 510), "₹5,261.95", fill=(71, 85, 105), font=get_font(14))
    d.text((720, 540), "SGST (9.0%):", fill=(71, 85, 105), font=get_font(14))
    d.text((1140, 540), "₹5,261.95", fill=(71, 85, 105), font=get_font(14))
    d.line([(720, 570), (W - 60, 570)], fill=(203, 213, 225), width=1)

    d.text((720, 595), "GRAND TOTAL AMOUNT:", fill=(15, 23, 42), font=get_font(18, bold=True))
    d.text((1120, 595), "₹68,990.00", fill=(180, 83, 9), font=get_font(22, bold=True))

    # Payment Badge & Barcode
    d.rectangle([40, 470, 600, 630], fill=(241, 245, 249), outline=(203, 213, 225))
    d.text((60, 490), "Payment Information: Paid in Full", fill=(22, 101, 52), font=get_font(15, bold=True))
    d.text((60, 515), "Method: HDFC Bank Credit Card (Masked: **** **** **** 4891)", fill=(51, 65, 85), font=get_font(13))
    d.text((60, 538), "Transaction Ref: TXN_981274910283 | Authorization: AUTH_749102", fill=(51, 65, 85), font=get_font(13))
    
    # Fake Barcode lines
    bx = 60
    for i in range(48):
        bw = 2 if (i % 3 == 0 or i % 7 == 0) else 4
        d.rectangle([bx, 570, bx + bw, 610], fill=(15, 23, 42))
        bx += bw + (3 if i % 2 == 0 else 2)
    d.text((bx + 15, 585), "|| 402-1849204-7491023 ||", fill=(71, 85, 105), font=get_font(12, mono=True))

    # Footer
    d.rectangle([0, H - 50, W, H], fill=(241, 245, 249))
    d.text((W // 2, H - 28), "This is a computer-generated tax invoice. Authorized Signatory: Appario Retail Pvt Ltd.", fill=(100, 116, 139), font=get_font(13), anchor="mm")

    img.save(dest, "PNG")
    print(f"📄 Generated high-fidelity Amazon invoice: {dest.name}")


def gen_wifi_settings(dest):
    img = Image.new("RGB", (W, H), (245, 247, 250))
    d = ImageDraw.Draw(img)

    # TP-Link / ASUS Router Header
    d.rectangle([0, 0, W, 65], fill=(30, 41, 59))
    d.text((35, 20), "TP-Link Archer AX73  •  Dual-Band Wi-Fi 6 Gigabit Router", fill=(255, 255, 255), font=get_font(18, bold=True))
    d.text((W - 240, 24), "Firmware: v1.4.2 Build 2026", fill=(148, 163, 184), font=get_font(13))

    # Left Navigation Sidebar
    d.rectangle([0, 65, 260, H], fill=(255, 255, 255), outline=(226, 232, 240))
    menu = ["Network Map", "Internet Settings", "Wireless (2.4G & 5G)", "Security & Firewall", "VPN Server", "Advanced System"]
    my = 95
    for idx, item in enumerate(menu):
        is_active = (idx == 2)
        if is_active:
            d.rectangle([10, my - 5, 250, my + 32], fill=(239, 246, 255), outline=(191, 219, 254))
            d.text((30, my + 4), item, fill=(29, 78, 216), font=get_font(14, bold=True))
        else:
            d.text((30, my + 4), item, fill=(71, 85, 105), font=get_font(14))
        my += 48

    # Main Wireless Settings Area
    d.text((300, 95), "Wireless Network Settings", fill=(15, 23, 42), font=get_font(22, bold=True))
    d.text((300, 130), "Configure SSID, encryption protocols, channel width, and Wi-Fi security keys.", fill=(100, 116, 139), font=get_font(14))

    # 5GHz High-Speed Band Card (CRITICAL SECURITY)
    d.rectangle([300, 165, W - 40, 450], fill=(255, 255, 255), outline=(226, 232, 240))
    d.rectangle([300, 165, W - 40, 215], fill=(241, 245, 249))
    d.text((325, 182), "5GHz Wireless Network (High-Throughput)", fill=(15, 23, 42), font=get_font(16, bold=True))
    d.text((W - 140, 182), "● ACTIVE", fill=(22, 101, 52), font=get_font(13, bold=True))

    # Fields
    fields = [
        ("Network Name (SSID):", "AURA-HyperNet-5G", False),
        ("Security Mode:", "WPA3-Personal (SAE) / WPA2-Enterprise", False),
        ("Encryption Algorithm:", "AES-256 GCM Hardware Accelerated", False),
        ("Wi-Fi Password / Pre-Shared Key:", "HyperSonic@2026!Secured", True),
        ("Gateway IP Address:", "192.168.1.1 (Subnet: 255.255.255.0)", False),
        ("Channel & Width:", "Channel 48 (160MHz Ultra-Wide Band)", False),
    ]

    fy = 235
    for label, val, is_secret in fields:
        d.text((330, fy), label, fill=(71, 85, 105), font=get_font(14, bold=True))
        if is_secret:
            d.rectangle([620, fy - 6, 1020, fy + 26], fill=(254, 242, 242), outline=(252, 165, 165))
            d.text((635, fy), val, fill=(185, 28, 28), font=get_font(15, bold=True, mono=True))
            d.text((1040, fy + 2), "[Confidential]", fill=(220, 38, 38), font=get_font(12, bold=True))
        else:
            d.text((620, fy), val, fill=(15, 23, 42), font=get_font(14))
        fy += 34

    # 2.4GHz Guest Network Card
    d.rectangle([300, 475, W - 40, 680], fill=(255, 255, 255), outline=(226, 232, 240))
    d.rectangle([300, 475, W - 40, 520], fill=(241, 245, 249))
    d.text((325, 490), "2.4GHz IoT & Guest Wireless Network", fill=(15, 23, 42), font=get_font(16, bold=True))

    gfields = [
        ("Guest Network SSID:", "AURA-Guest-IoT", False),
        ("Guest Password:", "GuestAccess#2026", True),
        ("Client Isolation:", "Enabled (Prevents LAN sniffing)", False),
    ]
    gy = 540
    for label, val, is_secret in gfields:
        d.text((330, gy), label, fill=(71, 85, 105), font=get_font(14, bold=True))
        if is_secret:
            d.rectangle([620, gy - 6, 920, gy + 26], fill=(254, 242, 242), outline=(252, 165, 165))
            d.text((635, gy), val, fill=(185, 28, 28), font=get_font(14, bold=True, mono=True))
        else:
            d.text((620, gy), val, fill=(15, 23, 42), font=get_font(14))
        gy += 38

    # Save Button
    d.rectangle([W - 180, 720, W - 40, 765], fill=(37, 99, 235), outline=(29, 78, 216))
    d.text((W - 110, 742), "Save Changes", fill=(255, 255, 255), font=get_font(14, bold=True), anchor="mm")

    img.save(dest, "PNG")
    print(f"🔒 Generated high-fidelity Wi-Fi Router Settings: {dest.name}")


def gen_vscode_code(dest):
    img = Image.new("RGB", (W, H), (30, 30, 30))
    d = ImageDraw.Draw(img)

    # VS Code Title Bar
    d.rectangle([0, 0, W, 40], fill=(60, 60, 60))
    d.text((20, 12), "● ● ●", fill=(200, 100, 100), font=get_font(13))
    d.text((W // 2, 20), "train_yolo.py — ultralytics-cv-engine — Visual Studio Code", fill=(200, 200, 200), font=get_font(13), anchor="mm")

    # Left Activity Bar
    d.rectangle([0, 40, 50, H], fill=(45, 45, 45))
    d.text((15, 60), "📁\n\n🔍\n\n🌿\n\n🐞\n\n📦", fill=(180, 180, 180), font=get_font(16))

    # Editor Tab
    d.rectangle([50, 40, 260, 75], fill=(30, 30, 30))
    d.text((70, 52), "🐍 train_yolo.py", fill=(255, 255, 255), font=get_font(13, bold=True))
    d.rectangle([260, 40, 440, 75], fill=(45, 45, 45))
    d.text((280, 52), "📄 dataset.yaml", fill=(150, 150, 150), font=get_font(13))

    # Code Lines
    lines = [
        ("import torch", (197, 134, 192)),
        ("import torch.nn as nn", (197, 134, 192)),
        ("from ultralytics import YOLO", (197, 134, 192)),
        ("from torchvision.transforms import v2 as T", (197, 134, 192)),
        ("", (255, 255, 255)),
        ("# Initialize Blackwell-optimized YOLOv8 model architecture", (106, 153, 85)),
        ("device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')", (220, 220, 220)),
        ("model = YOLO('yolov8x.pt').to(device)", (220, 220, 220)),
        ("", (255, 255, 255)),
        ("def train_computer_vision_pipeline():", (220, 220, 170)),
        ("    '''Train model on ISRO lunar crater dataset with mixed precision.'''", (206, 145, 120)),
        ("    results = model.train(", (220, 220, 220)),
        ("        data='configs/isro_lunar_craters.yaml',", (206, 145, 120)),
        ("        epochs=100,", (181, 206, 168)),
        ("        imgsz=640,", (181, 206, 168)),
        ("        batch=32,", (181, 206, 168)),
        ("        device=device,", (156, 220, 254)),
        ("        optimizer='AdamW',", (206, 145, 120)),
        ("        lr0=0.001,", (181, 206, 168)),
        ("        augment=True,", (86, 156, 214)),
        ("        val=True,", (86, 156, 214)),
        ("    )", (220, 220, 220)),
        ("    print(f'Training complete! Validation mAP50-95: {results.box.map:.4f}')", (220, 220, 220)),
    ]

    ly = 95
    for idx, (code_str, color) in enumerate(lines, 1):
        d.text((65, ly), f"{idx:2d}", fill=(100, 100, 100), font=get_font(13, mono=True))
        d.text((105, ly), code_str, fill=color, font=get_font(14, mono=True))
        ly += 22

    # Integrated Terminal Panel
    d.rectangle([50, 560, W, H], fill=(24, 24, 24), outline=(50, 50, 50))
    d.text((70, 575), "TERMINAL  |  1: python (NVIDIA GeForce RTX 5060 Laptop GPU - 8GB GDDR7)", fill=(200, 200, 200), font=get_font(12, bold=True))
    d.text((70, 605), "PS C:\\Users\\prajwal\\projects\\vision> python train_yolo.py", fill=(255, 255, 255), font=get_font(13, mono=True))
    d.text((70, 630), "Epoch 100/100: 100%|██████████| 120/120 [00:42<00:00, 2.84it/s, loss=0.0142, mAP=0.948]", fill=(78, 201, 176), font=get_font(12, mono=True))
    d.text((70, 655), "Validation Results: mAP@0.5 = 94.8%  |  mAP@0.5:0.95 = 78.4%  |  Precision = 96.2%  |  Recall = 93.1%", fill=(220, 220, 170), font=get_font(12, mono=True))
    d.text((70, 680), "Model weights successfully saved to 'runs/detect/train/weights/best.pt'", fill=(106, 153, 85), font=get_font(12, mono=True))

    img.save(dest, "PNG")
    print(f"💻 Generated high-fidelity VS Code Python IDE: {dest.name}")


def main():
    print("🚀 Starting Photorealistic Dataset Synthesis & Acquisition...")
    
    # 1. Real Photography & Products
    gen_red_sports_car(DEMO_DIR / "scene_red_sports_car.png")
    gen_mountain_view(DEMO_DIR / "scene_mountain_view.png")
    gen_food_pizza(DEMO_DIR / "food_photo_truffle_pizza.png")
    gen_food_pasta(DEMO_DIR / "food_photo_mushroom_pasta.png")
    gen_food_ramen(DEMO_DIR / "food_photo_japanese_ramen.png")
    gen_photo_watch(DEMO_DIR / "photo_watch_chronograph.png")
    gen_photo_sneakers(DEMO_DIR / "photo_sneakers_white.png")
    gen_photo_laptop_silver(DEMO_DIR / "product_photo_silver_laptop.png")
    gen_photo_headphones_black(DEMO_DIR / "product_photo_black_headphones.png")
    gen_scene_beach_sunset(DEMO_DIR / "scene_beach_sunset.png")
    gen_scene_city_skyline(DEMO_DIR / "scene_city_skyline.png")
    gen_photo_office_workspace(DEMO_DIR / "photo_office_workspace.png")

    # 2. Key Demo Structured Invoices & Screens
    gen_amazon_laptop_receipt(DEMO_DIR / "receipt_laptop_amazon.png")
    gen_wifi_settings(DEMO_DIR / "settings_wifi_password.png")
    gen_vscode_code(DEMO_DIR / "code_yolo_training.png")

    print(f"🎉 Acquisition complete! Total demo screenshots in {DEMO_DIR}")

if __name__ == "__main__":
    main()
