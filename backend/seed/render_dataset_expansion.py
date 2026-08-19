"""
AURA — Comprehensive 350-Image Multimodal Dataset Renderer & Manifest Generator
Generates realistic, high-contrast, OCR-readable, multimodal-parseable synthetic screenshots
across 12 core domains and outputs data/manifests/dataset_manifest_v2.json with 70/15/15 train/val/test splits.
"""
import sys
import os
import json
import random
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Set paths
root_dir = Path(__file__).resolve().parent.parent.parent
screenshots_dir = root_dir / "demo_data" / "screenshots"
screenshots_dir.mkdir(parents=True, exist_ok=True)
manifests_dir = root_dir / "data" / "manifests"
manifests_dir.mkdir(parents=True, exist_ok=True)

# Helper function to get default font
def get_font(size=14):
    try:
        # Try common windows fonts
        font_path = "C:/Windows/Fonts/segoeui.ttf"
        if os.path.exists(font_path):
            return ImageFont.truetype(font_path, size)
        font_path = "C:/Windows/Fonts/arial.ttf"
        if os.path.exists(font_path):
            return ImageFont.truetype(font_path, size)
        font_path = "C:/Windows/Fonts/consola.ttf"
        if os.path.exists(font_path):
            return ImageFont.truetype(font_path, size)
    except Exception:
        pass
    return ImageFont.load_default()

def get_code_font(size=13):
    try:
        font_path = "C:/Windows/Fonts/consola.ttf"
        if os.path.exists(font_path):
            return ImageFont.truetype(font_path, size)
    except Exception:
        pass
    return get_font(size)

# Visual Renderers for different screenshot types
def draw_window_frame(draw, width, height, title, bg_color=(30, 30, 30), text_color=(220, 220, 220)):
    draw.rectangle([0, 0, width, height], fill=bg_color)
    # Title bar
    draw.rectangle([0, 0, width, 32], fill=(45, 45, 45))
    # Window controls (close, min, max)
    draw.ellipse([width - 24, 10, width - 12, 22], fill=(239, 68, 68))
    draw.ellipse([width - 44, 10, width - 32, 22], fill=(245, 158, 11))
    draw.ellipse([width - 64, 10, width - 52, 22], fill=(16, 185, 129))
    font = get_font(12)
    draw.text((16, 8), title, fill=text_color, font=font)
    draw.line([(0, 32), (width, 32)], fill=(60, 60, 60), width=1)

def render_code_screenshot(filename, title, language, code_lines, theme="dark"):
    width, height = 900, 600
    img = Image.new("RGB", (width, height), color=(30, 30, 30) if theme == "dark" else (250, 250, 250))
    draw = ImageDraw.Draw(img)
    
    bg_col = (24, 24, 24) if theme == "dark" else (255, 255, 255)
    text_col = (230, 230, 230) if theme == "dark" else (30, 30, 30)
    line_num_col = (100, 100, 100) if theme == "dark" else (160, 160, 160)
    
    draw_window_frame(draw, width, height, f"{title} — Visual Studio Code", bg_color=bg_col, text_color=text_col)
    
    # Sidebar
    draw.rectangle([0, 32, 60, height], fill=(18, 18, 18) if theme == "dark" else (235, 235, 235))
    # File tab
    draw.rectangle([60, 32, 220, 62], fill=(30, 30, 30) if theme == "dark" else (240, 240, 240))
    tab_font = get_font(12)
    draw.text((76, 40), f"{title}", fill=(59, 130, 246), font=tab_font)
    draw.line([(60, 62), (width, 62)], fill=(50, 50, 50), width=1)
    
    code_font = get_code_font(14)
    y = 80
    for idx, line in enumerate(code_lines, start=1):
        draw.text((70, y), f"{idx:3d}", fill=line_num_col, font=code_font)
        # Simple syntax coloring simulation
        line_color = text_col
        if line.strip().startswith(("#", "//", "/*", "--")):
            line_color = (106, 153, 85) # Comment green
        elif any(k in line for k in ["def ", "fn ", "class ", "import ", "from ", "async ", "await ", "return ", "let ", "const ", "struct "]):
            line_color = (197, 134, 192) if theme == "dark" else (175, 0, 219) # Keyword purple
        elif any(k in line for k in ["True", "False", "None", "0", "1", "200", "404", "500"]):
            line_color = (181, 206, 168) if theme == "dark" else (9, 134, 88) # Number green
        elif '"' in line or "'" in line:
            line_color = (206, 145, 120) if theme == "dark" else (163, 21, 21) # String orange/red
            
        draw.text((115, y), line, fill=line_color, font=code_font)
        y += 24
        if y > height - 30:
            break
            
    # Status bar
    draw.rectangle([0, height - 24, width, height], fill=(0, 122, 204))
    draw.text((16, height - 19), f"UTF-8   {language.upper()}   LF   Ln 1, Col 1", fill=(255, 255, 255), font=get_font(11))
    
    out_path = screenshots_dir / filename
    img.save(out_path)
    return out_path

def render_receipt_screenshot(filename, merchant, order_id, date_str, items, total, tax, payment_method):
    width, height = 750, 650
    img = Image.new("RGB", (width, height), color=(250, 250, 250))
    draw = ImageDraw.Draw(img)
    
    draw_window_frame(draw, width, height, f"Tax Invoice — {merchant} — Order #{order_id}", bg_color=(255, 255, 255), text_color=(30, 30, 30))
    
    # Header
    header_font = get_font(20)
    draw.text((40, 55), f"{merchant.upper()}", fill=(15, 23, 42), font=header_font)
    draw.text((40, 85), f"Tax Invoice / Purchase Receipt", fill=(71, 85, 105), font=get_font(13))
    draw.text((width - 250, 55), f"Order Date: {date_str}", fill=(71, 85, 105), font=get_font(12))
    draw.text((width - 250, 75), f"Order ID: {order_id}", fill=(15, 23, 42), font=get_font(12))
    draw.text((width - 250, 95), f"Payment: {payment_method}", fill=(71, 85, 105), font=get_font(12))
    
    draw.line([(40, 125), (width - 40, 125)], fill=(203, 213, 225), width=2)
    
    # Table Header
    th_font = get_font(13)
    draw.rectangle([40, 135, width - 40, 165], fill=(241, 245, 249))
    draw.text((50, 142), "Item Description", fill=(30, 41, 59), font=th_font)
    draw.text((400, 142), "Qty", fill=(30, 41, 59), font=th_font)
    draw.text((480, 142), "Price", fill=(30, 41, 59), font=th_font)
    draw.text((width - 150, 142), "Subtotal", fill=(30, 41, 59), font=th_font)
    
    y = 180
    row_font = get_font(13)
    for itm, qty, price, sub in items:
        draw.text((50, y), itm, fill=(15, 23, 42), font=row_font)
        draw.text((405, y), str(qty), fill=(71, 85, 105), font=row_font)
        draw.text((480, y), f"INR {price}", fill=(71, 85, 105), font=row_font)
        draw.text((width - 150, y), f"INR {sub}", fill=(15, 23, 42), font=row_font)
        draw.line([(40, y + 26), (width - 40, y + 26)], fill=(241, 245, 249), width=1)
        y += 35
        
    y += 20
    draw.line([(40, y), (width - 40, y)], fill=(203, 213, 225), width=1)
    y += 15
    draw.text((width - 280, y), f"GST / Taxes (18%):", fill=(71, 85, 105), font=row_font)
    draw.text((width - 150, y), f"INR {tax}", fill=(71, 85, 105), font=row_font)
    y += 25
    tot_font = get_font(16)
    draw.text((width - 280, y), f"Grand Total:", fill=(15, 23, 42), font=tot_font)
    draw.text((width - 150, y), f"INR {total}", fill=(16, 185, 129), font=tot_font)
    
    # Footer verification badge
    draw.rectangle([40, height - 60, width - 40, height - 20], fill=(240, 253, 244))
    draw.text((55, height - 47), "✓ Digitally Signed & GST Verified Invoice — Thank you for your business!", fill=(22, 101, 52), font=get_font(12))
    
    out_path = screenshots_dir / filename
    img.save(out_path)
    return out_path

def render_chart_screenshot(filename, title, chart_type, x_labels, y_values, y_label, theme="dark"):
    width, height = 800, 520
    bg_col = (18, 24, 38) if theme == "dark" else (255, 255, 255)
    text_col = (241, 245, 249) if theme == "dark" else (15, 23, 42)
    grid_col = (40, 53, 76) if theme == "dark" else (226, 232, 240)
    
    img = Image.new("RGB", (width, height), color=bg_col)
    draw = ImageDraw.Draw(img)
    
    draw_window_frame(draw, width, height, f"{title} — Analytics & Visual Intelligence", bg_color=bg_col, text_color=text_col)
    
    draw.text((40, 50), title, fill=text_col, font=get_font(18))
    draw.text((40, 75), f"Metric: {y_label} | Chart Type: {chart_type.upper()}", fill=(148, 163, 184), font=get_font(12))
    
    # Plot bounds
    px0, py0, px1, py1 = 80, 110, width - 60, height - 80
    draw.rectangle([px0, py0, px1, py1], outline=grid_col, width=1)
    
    # Horizontal grid lines
    num_grids = 5
    for i in range(num_grids + 1):
        gy = py0 + (py1 - py0) * i / num_grids
        draw.line([(px0, gy), (px1, gy)], fill=grid_col, width=1)
        val = max(y_values) * (1 - i / num_grids)
        draw.text((25, gy - 8), f"{val:.1f}", fill=(148, 163, 184), font=get_font(10))
        
    n = len(x_labels)
    if chart_type == "bar":
        bar_w = (px1 - px0) / (n * 1.5)
        for i, (xl, yv) in enumerate(zip(x_labels, y_values)):
            bx = px0 + (i + 0.3) * ((px1 - px0) / n)
            bh = (yv / max(max(y_values), 1e-5)) * (py1 - py0)
            by = py1 - bh
            # Gradient blue bar
            draw.rectangle([bx, by, bx + bar_w, py1], fill=(59, 130, 246))
            draw.text((bx + 2, by - 16), f"{yv:.1f}", fill=(96, 165, 250), font=get_font(10))
            draw.text((bx - 5, py1 + 8), str(xl), fill=text_col, font=get_font(11))
    elif chart_type in ("line", "loss_curve"):
        pts = []
        for i, (xl, yv) in enumerate(zip(x_labels, y_values)):
            lx = px0 + i * ((px1 - px0) / max(n - 1, 1))
            ly = py1 - (yv / max(max(y_values), 1e-5)) * (py1 - py0)
            pts.append((lx, ly))
            draw.text((lx - 10, py1 + 8), str(xl), fill=text_col, font=get_font(11))
            
        for i in range(len(pts) - 1):
            draw.line([pts[i], pts[i+1]], fill=(16, 185, 129), width=3)
        for pt in pts:
            draw.ellipse([pt[0]-4, pt[1]-4, pt[0]+4, pt[1]+4], fill=(52, 211, 153), outline=(255,255,255))
            
    out_path = screenshots_dir / filename
    img.save(out_path)
    return out_path

def render_dashboard_screenshot(filename, app_name, kpis, tables):
    width, height = 900, 580
    img = Image.new("RGB", (width, height), color=(15, 23, 42))
    draw = ImageDraw.Draw(img)
    
    draw_window_frame(draw, width, height, f"{app_name} — Enterprise Cloud Console", bg_color=(15, 23, 42), text_color=(248, 250, 252))
    
    # Top navbar
    draw.rectangle([0, 32, width, 75], fill=(30, 41, 59))
    draw.text((25, 45), f"⚡ {app_name.upper()} INFRASTRUCTURE HUB", fill=(56, 189, 248), font=get_font(15))
    draw.text((width - 220, 47), "Region: ap-south-1 (Mumbai)", fill=(148, 163, 184), font=get_font(12))
    
    # KPI Metric Cards
    card_w = (width - 80) / len(kpis)
    for i, (kpi_title, kpi_val, kpi_change, status_col) in enumerate(kpis):
        cx0 = 30 + i * (card_w + 10)
        cx1 = cx0 + card_w
        draw.rectangle([cx0, 90, cx1, 175], fill=(30, 41, 59), outline=(51, 65, 85), width=1)
        draw.text((cx0 + 15, 102), kpi_title, fill=(148, 163, 184), font=get_font(12))
        draw.text((cx0 + 15, 122), str(kpi_val), fill=(248, 250, 252), font=get_font(18))
        draw.text((cx0 + 15, 150), kpi_change, fill=status_col, font=get_font(11))
        
    # Table panel
    draw.rectangle([30, 195, width - 30, height - 30], fill=(30, 41, 59), outline=(51, 65, 85), width=1)
    draw.text((45, 208), tables["title"], fill=(248, 250, 252), font=get_font(14))
    
    # Table rows
    ty = 240
    th_cols = tables["headers"]
    col_w = (width - 120) / len(th_cols)
    for c_idx, head in enumerate(th_cols):
        draw.text((45 + c_idx * col_w, ty), head, fill=(148, 163, 184), font=get_font(12))
    draw.line([(45, ty + 20), (width - 45, ty + 20)], fill=(51, 65, 85), width=1)
    
    ty += 30
    for row in tables["rows"]:
        for c_idx, cell in enumerate(row):
            draw.text((45 + c_idx * col_w, ty), str(cell), fill=(226, 232, 240), font=get_font(12))
        draw.line([(45, ty + 22), (width - 45, ty + 22)], fill=(40, 53, 76), width=1)
        ty += 28
        if ty > height - 40:
            break
            
    out_path = screenshots_dir / filename
    img.save(out_path)
    return out_path

def render_chat_screenshot(filename, sender_name, channel, messages):
    width, height = 750, 550
    img = Image.new("RGB", (width, height), color=(17, 24, 39))
    draw = ImageDraw.Draw(img)
    
    draw_window_frame(draw, width, height, f"{sender_name} ({channel}) — Communications Hub", bg_color=(17, 24, 39), text_color=(243, 244, 246))
    
    # Chat header
    draw.rectangle([0, 32, width, 80], fill=(31, 41, 55))
    draw.ellipse([20, 42, 54, 76], fill=(59, 130, 246))
    draw.text((28, 48), sender_name[0], fill=(255, 255, 255), font=get_font(16))
    draw.text((65, 45), sender_name, fill=(243, 244, 246), font=get_font(14))
    draw.text((65, 63), f"Channel: #{channel} | Online", fill=(16, 185, 129), font=get_font(11))
    
    y = 100
    for msg in messages:
        sender, text, timestamp, is_me = msg
        msg_w = min(len(text) * 8 + 40, width - 200)
        msg_h = 45
        if is_me:
            bx0 = width - msg_w - 30
            bx1 = width - 30
            b_col = (37, 99, 235)
        else:
            bx0 = 30
            bx1 = 30 + msg_w
            b_col = (55, 65, 81)
            
        draw.rectangle([bx0, y, bx1, y + msg_h], fill=b_col, outline=(75, 85, 99), width=1)
        draw.text((bx0 + 12, y + 6), text, fill=(255, 255, 255), font=get_font(12))
        draw.text((bx0 + 12, y + 26), f"{sender} • {timestamp}", fill=(209, 213, 219), font=get_font(10))
        y += 58
        if y > height - 70:
            break
            
    out_path = screenshots_dir / filename
    img.save(out_path)
    return out_path

def render_travel_ticket(filename, airline_or_transit, pnr, passenger, route, date_str, seat, gate):
    width, height = 750, 480
    img = Image.new("RGB", (width, height), color=(248, 250, 252))
    draw = ImageDraw.Draw(img)
    
    draw_window_frame(draw, width, height, f"Boarding Pass — {airline_or_transit} — PNR: {pnr}", bg_color=(255, 255, 255), text_color=(15, 23, 42))
    
    # Boarding card container
    draw.rectangle([30, 55, width - 30, height - 30], fill=(255, 255, 255), outline=(203, 213, 225), width=2)
    # Header banner
    draw.rectangle([30, 55, width - 30, 115], fill=(30, 58, 138))
    draw.text((50, 72), f"✈️ {airline_or_transit.upper()} BOARDING PASS", fill=(255, 255, 255), font=get_font(16))
    draw.text((width - 200, 75), f"PNR: {pnr}", fill=(254, 240, 138), font=get_font(14))
    
    # Flight Route
    draw.text((50, 135), route["from_city"], fill=(15, 23, 42), font=get_font(22))
    draw.text((50, 165), route["from_code"], fill=(100, 116, 139), font=get_font(14))
    draw.text((width // 2 - 40, 145), "──────►", fill=(59, 130, 246), font=get_font(16))
    draw.text((width - 220, 135), route["to_city"], fill=(15, 23, 42), font=get_font(22))
    draw.text((width - 220, 165), route["to_code"], fill=(100, 116, 139), font=get_font(14))
    
    draw.line([(50, 205), (width - 50, 205)], fill=(226, 232, 240), width=1)
    
    # Details Grid
    draw.text((50, 225), "Passenger Name", fill=(100, 116, 139), font=get_font(12))
    draw.text((50, 245), passenger, fill=(15, 23, 42), font=get_font(15))
    
    draw.text((250, 225), "Date / Time", fill=(100, 116, 139), font=get_font(12))
    draw.text((250, 245), date_str, fill=(15, 23, 42), font=get_font(15))
    
    draw.text((450, 225), "Seat", fill=(100, 116, 139), font=get_font(12))
    draw.text((450, 245), seat, fill=(225, 29, 72), font=get_font(18))
    
    draw.text((580, 225), "Gate", fill=(100, 116, 139), font=get_font(12))
    draw.text((580, 245), gate, fill=(16, 185, 129), font=get_font(18))
    
    # Simulated Barcode
    for bx in range(50, width - 50, 6):
        bw = random.choice([2, 4])
        draw.rectangle([bx, 300, bx + bw, 370], fill=(15, 23, 42))
    draw.text((width // 2 - 80, 380), f"*{pnr}-{passenger[:4].upper()}*", fill=(100, 116, 139), font=get_font(11))
    
    out_path = screenshots_dir / filename
    img.save(out_path)
    return out_path

def render_credentials_screenshot(filename, service_name, cred_fields):
    width, height = 750, 450
    img = Image.new("RGB", (width, height), color=(24, 24, 27))
    draw = ImageDraw.Draw(img)
    
    draw_window_frame(draw, width, height, f"{service_name} — Security & API Keys Console", bg_color=(24, 24, 27), text_color=(244, 244, 245))
    
    draw.text((40, 50), f"🔒 {service_name} Access & API Credentials", fill=(244, 244, 245), font=get_font(16))
    draw.text((40, 75), "Confidential Settings — Protected by AURA Zero-Trust Shield", fill=(239, 68, 68), font=get_font(12))
    
    y = 115
    for label, val in cred_fields:
        draw.text((40, y), label, fill=(161, 161, 170), font=get_font(13))
        draw.rectangle([40, y + 22, width - 40, y + 58], fill=(39, 39, 42), outline=(63, 63, 70), width=1)
        draw.text((55, y + 32), val, fill=(244, 244, 245), font=get_code_font(13))
        y += 70
        
    out_path = screenshots_dir / filename
    img.save(out_path)
    return out_path

def render_adversarial_screenshot(filename, attack_name, injection_text):
    width, height = 750, 420
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    draw_window_frame(draw, width, height, f"Adversarial Evaluation Note — {attack_name}", bg_color=(255, 255, 255), text_color=(15, 23, 42))
    
    draw.text((30, 50), f"Security Test Payload: {attack_name}", fill=(220, 38, 38), font=get_font(15))
    draw.rectangle([30, 80, width - 30, height - 40], fill=(254, 242, 242), outline=(248, 113, 113), width=1)
    
    lines = injection_text.split("\n")
    y = 95
    for l in lines:
        draw.text((45, y), l, fill=(153, 27, 27), font=get_code_font(13))
        y += 24
        
    out_path = screenshots_dir / filename
    img.save(out_path)
    return out_path

print("Starting Expanded Synthetic Dataset Generation (240+ High-Quality New Artifacts)...")
