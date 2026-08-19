"""
AURA — Comprehensive Multimodal Demo Dataset Generator
Generates 67 high-quality, visually distinct, rich synthetic screenshots across 11 cohesive clusters:
- Cluster A: Computer Vision & AI Research (YOLOv8, Vision Transformer, WandB curves, ISRO dataset)
- Cluster B: Audio & Headphone Shopping Journey (Photo, Specs, Rtings review, Price chart, Cart, Invoice)
- Cluster C: Laptop & Hardware Upgrade Journey (Silver laptop photo, Red laptop photo, Specs, Wishlist, Receipt, Monitor invoice)
- Cluster D: Bangalore to Goa Trip & Vacation (Flight ticket, Taj Exotica hotel, Maps route, Beach sunset, Rooftop bar, Cab receipt)
- Cluster E: Food & Culinary Story (Truffle pizza photo, Wild mushroom pasta, Japanese ramen, Recipe card, Bistro menu, Grocery receipt)
- Cluster F: Electronics & Engineering Study (RLC circuit diagram, 4-bit logic gates, Handwritten calculus notes, Neural net graph, AURA architecture)
- Cluster G: Software Engineering & DevOps (FastAPI auth code, GitHub issue #142, CUDA traceback, Git merge conflict, Grafana dashboard, DB schema, Swagger docs)
- Cluster H: Security & Credentials (Wi-Fi password, OpenAI API key, AWS IAM credentials, Stripe keys, WhatsApp address, Freelance invoice)
- Cluster I: Real-World Visual Photography (Himalayan mountain view, Red sports car, Chronograph watch, White sneakers, Office workspace, Whiteboard brainstorm, Night city skyline)
- Cluster J: Presentations & Documents (ISRO crater slides 1 & 4, Privacy policy, Semester timetable, Business card)
- Cluster K: UI & Digital Workspaces (Dark analytics dashboard, Figma design canvas, AURA search screen, Spotify music player)
"""

import math
import random
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
OUT_DIR = ROOT_DIR / "demo_data" / "screenshots"
OUT_DIR.mkdir(parents=True, exist_ok=True)

W, H = 1280, 800


def get_font(size=16, bold=False):
    font_names = ["segoeui.ttf", "arial.ttf", "calibri.ttf", "DejaVuSans.ttf"]
    if bold:
        font_names = ["segoeuib.ttf", "arialbd.ttf", "calibrib.ttf", "DejaVuSans-Bold.ttf"]
    for name in font_names:
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()


# ─── CLUSTER A: COMPUTER VISION & AI RESEARCH ─────────────────────────────────

def gen_research_yolo_paper():
    img = Image.new("RGB", (W, H), (248, 249, 250))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 45], fill=(30, 41, 59))
    d.text((25, 12), "arXiv:2401.08921v2 [cs.CV]  •  Computer Vision and Pattern Recognition", fill=(203, 213, 225), font=get_font(15))
    
    d.text((60, 75), "YOLOv8: Real-Time Object Detection and Instance Segmentation Architecture", fill=(15, 23, 42), font=get_font(22, bold=True))
    d.text((60, 110), "Prajwal Sharma, Glenn Jocher, Ultralytics AI Research Team", fill=(71, 85, 105), font=get_font(15))
    d.line([(60, 138), (W - 60, 138)], fill=(226, 232, 240), width=2)
    
    d.rectangle([60, 155, W - 60, 245], fill=(241, 245, 249), outline=(203, 213, 225), width=1)
    d.text((80, 168), "Abstract — We present YOLOv8, a cutting-edge, anchor-free object detector designed for real-time vision applications.", fill=(30, 41, 59), font=get_font(14, bold=True))
    d.text((80, 192), "By replacing decoupled head architectures with anchor-free split convolutional heads and integrating TaskAlignedAssigner,", fill=(51, 65, 85), font=get_font(14))
    d.text((80, 214), "YOLOv8 achieves 53.9% mAP50-95 on MS-COCO val2017 while running at 280 FPS on NVIDIA RTX 5060 GPUs.", fill=(51, 65, 85), font=get_font(14))
    
    d.text((60, 265), "1. Architecture & Loss Formulation", fill=(15, 23, 42), font=get_font(18, bold=True))
    d.text((60, 295), "The total optimization objective combines CIoU loss and Distribution Focal Loss (DFL):", fill=(51, 65, 85), font=get_font(14))
    d.rectangle([60, 325, 600, 375], fill=(255, 255, 255), outline=(203, 213, 225))
    d.text((80, 342), "L_total = λ_box · L_CIoU(b, b̂) + λ_cls · L_VFL(p, y) + λ_dfl · L_DFL(S)", fill=(30, 58, 138), font=get_font(16, bold=True))
    d.text((60, 390), "Where λ_box = 7.5, λ_cls = 0.5, and λ_dfl = 1.5 are the Pareto-optimal task weights.", fill=(71, 85, 105), font=get_font(14))
    
    d.rectangle([640, 265, W - 60, 550], fill=(255, 255, 255), outline=(203, 213, 225))
    d.text((660, 280), "Figure 1: YOLOv8 Backbone & Decoupled Head Structure", fill=(15, 23, 42), font=get_font(14, bold=True))
    blocks = [("Input 640x640x3", (224, 231, 255)), ("C2f Feature Extractor", (254, 243, 199)),
              ("SPPF Pooling Layer", (254, 226, 226)), ("PAN-FPN Neck", (220, 252, 231)), ("Decoupled Head", (243, 232, 255))]
    by = 315
    for bname, bcol in blocks:
        d.rectangle([680, by, W - 100, by + 34], fill=bcol, outline=(148, 163, 184))
        d.text((700, by + 8), bname, fill=(15, 23, 42), font=get_font(13, bold=True))
        by += 44
    d.text((660, 520), "Evaluated on MS COCO, Pascal VOC, and ISRO lunar terrain datasets.", fill=(100, 116, 139), font=get_font(12))

    d.rectangle([0, H - 35, W, H], fill=(241, 245, 249))
    d.text((25, H - 25), "Page 1 of 12  •  Computer Vision Project  •  AURA Verified Benchmark", fill=(100, 116, 139), font=get_font(13))
    img.save(OUT_DIR / "research_yolo_paper.png", "PNG")


def gen_chart_training_loss():
    img = Image.new("RGB", (W, H), (15, 23, 42))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 45], fill=(30, 41, 59))
    d.text((25, 12), "Weights & Biases  /  cv-project-yolov8  /  runs/train-exp-50-epochs", fill=(248, 250, 252), font=get_font(15, bold=True))
    d.rectangle([W - 140, 8, W - 25, 37], fill=(16, 185, 129))
    d.text((W - 125, 14), "● RUNNING", fill=(255, 255, 255), font=get_font(13, bold=True))

    d.rectangle([50, 70, 610, 420], fill=(24, 32, 47), outline=(51, 65, 85))
    d.text((70, 85), "train/box_loss (Convergence)", fill=(248, 250, 252), font=get_font(15, bold=True))
    d.line([(90, 380), (580, 380)], fill=(100, 116, 139), width=2)
    d.line([(90, 120), (90, 380)], fill=(100, 116, 139), width=2)
    points = []
    for step in range(50):
        x = 90 + (step / 50) * 490
        loss = 2.8 * math.exp(-step / 12) + 0.35 + (0.05 * math.sin(step))
        y = 380 - (loss / 3.5) * 250
        points.append((x, y))
    d.line(points, fill=(6, 182, 212), width=3)
    d.text((450, 160), "Final: 0.384", fill=(6, 182, 212), font=get_font(14, bold=True))

    d.rectangle([650, 70, W - 50, 420], fill=(24, 32, 47), outline=(51, 65, 85))
    d.text((670, 85), "metrics/mAP50-95 (Accuracy)", fill=(248, 250, 252), font=get_font(15, bold=True))
    d.line([(690, 380), (W - 80, 380)], fill=(100, 116, 139), width=2)
    d.line([(690, 120), (690, 380)], fill=(100, 116, 139), width=2)
    map_pts = []
    for step in range(50):
        x = 690 + (step / 50) * 490
        acc = 0.58 * (1 - math.exp(-step / 10)) + (0.02 * math.cos(step))
        y = 380 - (acc / 0.65) * 250
        map_pts.append((x, y))
    d.line(map_pts, fill=(245, 158, 11), width=3)
    d.text((W - 220, 160), "mAP50-95: 56.2%", fill=(245, 158, 11), font=get_font(14, bold=True))

    d.rectangle([50, 450, W - 50, 750], fill=(24, 32, 47), outline=(51, 65, 85))
    d.text((70, 470), "Telemetry & Hardware Utilization", fill=(248, 250, 252), font=get_font(15, bold=True))
    d.text((70, 505), "GPU: NVIDIA GeForce RTX 5060 Laptop (8GB GDDR7)  •  VRAM: 6.8 GB / 8.0 GB (85%)", fill=(148, 163, 184), font=get_font(14))
    d.text((70, 535), "Batch Size: 16  •  Workers: 8  •  AMP Precision: FP16  •  CUDA 12.8  •  PyTorch 2.11.0", fill=(148, 163, 184), font=get_font(14))
    img.save(OUT_DIR / "chart_training_loss.png", "PNG")


def gen_chart_confusion_matrix():
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 45], fill=(30, 41, 59))
    d.text((25, 12), "Evaluation Suite  /  Confusion Matrix (Normalized)  /  COCO-Val2017", fill=(248, 250, 252), font=get_font(15, bold=True))
    
    classes = ["person", "car", "chair", "laptop", "bottle", "dog", "background"]
    start_x, start_y = 320, 120
    cell_w, cell_h = 90, 80
    
    d.text((start_x + 180, 75), "Predicted Class", fill=(15, 23, 42), font=get_font(16, bold=True))
    d.text((120, start_y + 240), "True Class", fill=(15, 23, 42), font=get_font(16, bold=True))
    
    for i, c_true in enumerate(classes):
        d.text((start_x - 110, start_y + i * cell_h + 30), c_true, fill=(51, 65, 85), font=get_font(13, bold=True))
        d.text((start_x + i * cell_w + 15, start_y - 25), c_true, fill=(51, 65, 85), font=get_font(13, bold=True))
        for j, c_pred in enumerate(classes):
            val = 0.88 + 0.08 * math.sin(i * 3 + j) if i == j else 0.02 * (abs(i - j) % 3)
            val = min(max(val, 0.01), 0.96)
            intensity = int(val * 220)
            fill_col = (255 - intensity, 255 - int(intensity * 0.7), 255)
            d.rectangle([start_x + j * cell_w, start_y + i * cell_h, start_x + (j + 1) * cell_w, start_y + (i + 1) * cell_h], fill=fill_col, outline=(203, 213, 225))
            d.text((start_x + j * cell_w + 25, start_y + i * cell_h + 30), f"{val:.2f}", fill=(15, 23, 42) if val < 0.6 else (255, 255, 255), font=get_font(13, bold=True))
            
    img.save(OUT_DIR / "chart_confusion_matrix.png", "PNG")


def gen_code_yolo_training():
    img = Image.new("RGB", (W, H), (15, 23, 42))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 40], fill=(30, 41, 59))
    d.text((20, 10), "VS Code  —  cv-project / train_yolov8.py  ●", fill=(203, 213, 225), font=get_font(14))
    
    code = [
        ("import torch", (147, 197, 253)),
        ("from ultralytics import YOLO", (244, 114, 182)),
        ("from app.services.pipeline import log_metrics", (203, 213, 225)),
        ("", (255, 255, 255)),
        ("def main():", (251, 191, 36)),
        ("    # Load pretrained YOLOv8-X backbone", (100, 116, 139)),
        ("    model = YOLO('yolov8x.pt')", (52, 211, 153)),
        ("    device = 'cuda' if torch.cuda.is_available() else 'cpu'", (147, 197, 253)),
        ("    print(f'Training on {torch.cuda.get_device_name(0)}')", (251, 146, 60)),
        ("", (255, 255, 255)),
        ("    # Train for 50 epochs on MS COCO & ISRO crater dataset", (100, 116, 139)),
        ("    results = model.train(", (244, 114, 182)),
        ("        data='dataset_lunar_isro.yaml',", (52, 211, 153)),
        ("        epochs=50,", (251, 146, 60)),
        ("        imgsz=640,", (251, 146, 60)),
        ("        batch=16,", (251, 146, 60)),
        ("        device=0,", (251, 146, 60)),
        ("        amp=True,  # FP16 mixed precision", (100, 116, 139)),
        ("        workers=8,", (251, 146, 60)),
        ("        optimizer='AdamW',", (52, 211, 153)),
        ("        lr0=0.001,", (251, 146, 60)),
        ("    )", (244, 114, 182)),
        ("    metrics = model.val()", (52, 211, 153)),
        ("    print(f'mAP50-95: {metrics.box.map:.4f}')", (251, 146, 60)),
        ("", (255, 255, 255)),
        ("if __name__ == '__main__':", (251, 191, 36)),
        ("    main()", (52, 211, 153))
    ]
    
    y = 60
    for line, color in code:
        d.text((45, y), line, fill=color, font=get_font(15))
        y += 26
    img.save(OUT_DIR / "code_yolo_training.png", "PNG")


def gen_terminal_training_output():
    img = Image.new("RGB", (W, H), (10, 10, 15))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 35], fill=(30, 30, 40))
    d.text((15, 8), "Windows PowerShell (Admin) — Zenith / NVIDIA RTX 5060", fill=(200, 200, 210), font=get_font(13))
    
    lines = [
        ("PS C:\\Users\\prajw\\Desktop\\cv-project> python train_yolov8.py", (255, 255, 255)),
        ("Ultralytics YOLOv8.1.0  Python-3.11.9 torch-2.11.0+cu128 CUDA:0 (NVIDIA GeForce RTX 5060 Laptop, 8151MB)", (100, 200, 255)),
        ("engine/trainer: task=detect, mode=train, model=yolov8x.pt, data=dataset_lunar_isro.yaml, epochs=50", (150, 150, 160)),
        ("Free VRAM: 7.21 GB / 8.00 GB | CUDA stream initialized.", (120, 240, 120)),
        ("      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size", (200, 200, 200)),
        ("      45/50      6.42G     0.4120     0.2810     0.8920         64        640: 100%|██████████| 188/188 [01:14<00:00,  2.52it/s]", (255, 200, 100)),
        ("      46/50      6.44G     0.4050     0.2760     0.8870         64        640: 100%|██████████| 188/188 [01:13<00:00,  2.55it/s]", (255, 200, 100)),
        ("      47/50      6.43G     0.3980     0.2690     0.8810         64        640: 100%|██████████| 188/188 [01:14<00:00,  2.53it/s]", (255, 200, 100)),
        ("      48/50      6.45G     0.3920     0.2640     0.8750         64        640: 100%|██████████| 188/188 [01:13<00:00,  2.56it/s]", (255, 200, 100)),
        ("      49/50      6.44G     0.3870     0.2580     0.8690         64        640: 100%|██████████| 188/188 [01:13<00:00,  2.55it/s]", (255, 200, 100)),
        ("      50/50      6.45G     0.3840     0.2520     0.8640         64        640: 100%|██████████| 188/188 [01:14<00:00,  2.54it/s]", (255, 200, 100)),
        ("Validating runs/detect/train/weights/best.pt...", (120, 240, 120)),
        ("Class                 Images  Instances      Box(P          R      mAP50  mAP50-95)", (200, 200, 200)),
        ("all                     1200       4520      0.912      0.884      0.934     0.562", (100, 255, 100)),
        ("lunar_crater            1200       2140      0.924      0.895      0.948     0.584", (255, 255, 255)),
        ("boulder                 1200       2380      0.900      0.873      0.920     0.540", (255, 255, 255)),
        ("Results saved to runs/detect/train/weights/best.pt", (120, 240, 120)),
    ]
    
    y = 55
    for line, color in lines:
        d.text((25, y), line, fill=color, font=get_font(13))
        y += 24
    img.save(OUT_DIR / "terminal_training_output.png", "PNG")


def gen_research_vit_paper():
    img = Image.new("RGB", (W, H), (250, 250, 252))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 45], fill=(30, 41, 59))
    d.text((25, 12), "ICLR 2021  •  An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale", fill=(203, 213, 225), font=get_font(15))
    
    d.text((60, 75), "Vision Transformer (ViT): Patch Linear Projection & Multi-Head Self-Attention", fill=(15, 23, 42), font=get_font(20, bold=True))
    d.text((60, 105), "Alexey Dosovitskiy, Lucas Beyer, Neil Houlsby, Google Research, Brain Team", fill=(71, 85, 105), font=get_font(14))
    d.line([(60, 130), (W - 60, 130)], fill=(226, 232, 240), width=2)
    
    d.rectangle([60, 150, 560, 520], fill=(255, 255, 255), outline=(203, 213, 225))
    d.text((80, 170), "Equation (1): Patch Flattening & Linear Projection", fill=(15, 23, 42), font=get_font(14, bold=True))
    d.text((80, 210), "z_0 = [x_class; x_p^1 E; x_p^2 E; ...; x_p^N E] + E_pos", fill=(30, 58, 138), font=get_font(16, bold=True))
    d.text((80, 260), "Where E ∈ R^(P^2·C × D) is the linear projection matrix,", fill=(51, 65, 85), font=get_font(13))
    d.text((80, 285), "and E_pos ∈ R^((N+1) × D) is the 1D learnable position embedding.", fill=(51, 65, 85), font=get_font(13))
    
    d.rectangle([600, 150, W - 60, 520], fill=(248, 250, 252), outline=(203, 213, 225))
    d.text((620, 170), "Figure: ViT Multi-Head Self-Attention Flow", fill=(15, 23, 42), font=get_font(14, bold=True))
    
    # Draw Transformer Diagram blocks
    layers = ["Input Image (224x224x3)", "16x16 Patch Extraction (N=196)", "Linear Embedding + [CLS] Token", "Transformer Encoder Layer x12", "MLP Head Classification"]
    ly = 210
    for l in layers:
        d.rectangle([640, ly, W - 100, ly + 38], fill=(224, 231, 255), outline=(147, 197, 253))
        d.text((660, ly + 10), l, fill=(30, 58, 138), font=get_font(13, bold=True))
        ly += 50
    img.save(OUT_DIR / "research_vit_paper.png", "PNG")


def gen_research_transformer_diagram():
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 45], fill=(30, 41, 59))
    d.text((25, 12), "Architectural Blueprint  /  Attention Is All You Need  /  Transformer Architecture", fill=(248, 250, 252), font=get_font(15, bold=True))
    
    # Encoder Box
    d.rectangle([120, 100, 540, 680], fill=(248, 250, 252), outline=(203, 213, 225), width=2)
    d.text((240, 120), "ENCODER STACK (Nx)", fill=(30, 58, 138), font=get_font(16, bold=True))
    enc_blocks = [("Output Add & LayerNorm", (254, 243, 199)), ("Feed Forward Neural Net", (220, 252, 231)), ("Add & LayerNorm", (254, 243, 199)), ("Multi-Head Attention", (254, 226, 226)), ("Positional Encoding + Input", (224, 231, 255))]
    ey = 170
    for bname, bcol in enc_blocks:
        d.rectangle([160, ey, 500, ey + 60], fill=bcol, outline=(148, 163, 184), width=1)
        d.text((200, ey + 20), bname, fill=(15, 23, 42), font=get_font(14, bold=True))
        ey += 85
        
    # Decoder Box
    d.rectangle([640, 100, 1060, 680], fill=(248, 250, 252), outline=(203, 213, 225), width=2)
    d.text((760, 120), "DECODER STACK (Nx)", fill=(180, 83, 9), font=get_font(16, bold=True))
    dec_blocks = [("Linear & Softmax Output", (243, 232, 255)), ("Add & LayerNorm", (254, 243, 199)), ("Cross-Attention (Enc-Dec)", (254, 226, 226)), ("Masked Multi-Head Attention", (254, 202, 202)), ("Positional Encoding + Target", (224, 231, 255))]
    dy = 170
    for bname, bcol in dec_blocks:
        d.rectangle([680, dy, 1020, dy + 60], fill=bcol, outline=(148, 163, 184), width=1)
        d.text((710, dy + 20), bname, fill=(15, 23, 42), font=get_font(14, bold=True))
        dy += 85
        
    img.save(OUT_DIR / "research_transformer_diagram.png", "PNG")


def gen_research_dataset_info():
    img = Image.new("RGB", (W, H), (248, 249, 250))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 45], fill=(30, 41, 59))
    d.text((25, 12), "Dataset Dashboard  /  ISRO Lunar Terrain Crater Benchmark Dataset v2.4", fill=(248, 250, 252), font=get_font(15, bold=True))
    
    d.text((60, 80), "Dataset Class Distribution & Bounding Box Annotations", fill=(15, 23, 42), font=get_font(20, bold=True))
    d.text((60, 110), "Total Images: 12,450  •  Total Bounding Boxes: 48,920  •  Resolution: 1024x1024", fill=(71, 85, 105), font=get_font(14))
    
    categories = [("Simple Crater", 18400, (6, 182, 212)), ("Complex Crater", 12100, (59, 130, 246)), ("Degraded Crater", 8900, (245, 158, 11)), ("Boulder Field", 6400, (239, 68, 68)), ("Rille / Trench", 3120, (16, 185, 129))]
    by = 170
    for cat, cnt, col in categories:
        d.text((60, by), cat, fill=(30, 41, 59), font=get_font(14, bold=True))
        d.rectangle([240, by - 4, 240 + int(cnt / 25), by + 22], fill=col)
        d.text((250 + int(cnt / 25), by), f"{cnt:,} instances", fill=(71, 85, 105), font=get_font(13))
        by += 55
        
    img.save(OUT_DIR / "research_dataset_info.png", "PNG")


# ─── CLUSTER B: AUDIO & HEADPHONE SHOPPING JOURNEY ─────────────────────────────

def gen_product_photo_black_headphones():
    # Visual-only focus photo rendering
    img = Image.new("RGB", (W, H), (218, 208, 192)) # Warm wooden table tone
    d = ImageDraw.Draw(img)
    
    # Wooden desk texture slats
    for y in range(0, H, 40):
        d.line([(0, y), (W, y)], fill=(205, 195, 178), width=1)
        
    # Large headphone earcups (Sony WH-1000XM5 Matte Black visual rendering)
    # Headband arc
    d.arc([380, 160, 900, 600], start=180, end=360, fill=(35, 35, 38), width=32)
    # Left Ear Cup
    d.ellipse([340, 360, 480, 580], fill=(28, 28, 30), outline=(50, 50, 54), width=3)
    d.ellipse([360, 385, 460, 555], fill=(42, 42, 46))
    # Right Ear Cup
    d.ellipse([800, 360, 940, 580], fill=(28, 28, 30), outline=(50, 50, 54), width=3)
    d.ellipse([820, 385, 920, 555], fill=(42, 42, 46))
    
    # Subtle matte bronze Sony accent text on side
    d.text((400, 340), "SONY", fill=(184, 150, 110), font=get_font(12, bold=True))
    d.text((860, 340), "SONY", fill=(184, 150, 110), font=get_font(12, bold=True))
    
    img.save(OUT_DIR / "product_photo_black_headphones.png", "PNG")


def gen_product_comparison_headphones():
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 45], fill=(30, 41, 59))
    d.text((25, 12), "Product Comparison  /  Flagship Wireless ANC Headphones (2026)", fill=(248, 250, 252), font=get_font(15, bold=True))
    
    headers = ["Feature", "Sony WH-1000XM5", "Bose QC Ultra", "Apple AirPods Max"]
    rows = [
        ("Price", "₹26,990", "₹32,900", "₹54,900"),
        ("ANC Rating", "9.4 / 10 (Dual QN1)", "9.5 / 10 (CustomTune)", "9.2 / 10 (H1 Chip)"),
        ("Battery Life", "30 Hours (ANC ON)", "24 Hours (ANC ON)", "20 Hours (ANC ON)"),
        ("Weight", "250g (Ultra-Light)", "254g", "384g (Stainless Steel)"),
        ("Bluetooth Codecs", "LDAC, AAC, SBC", "aptX Adaptive, AAC", "AAC, SBC"),
        ("Microphones", "8 Mics + AI Beamforming", "6 Mics", "9 Mics (8 ANC)"),
        ("Verdict", "Best Value & Sound Quality", "Best Pure Comfort", "Best Apple Ecosystem"),
    ]
    
    col_x = [60, 300, 600, 900]
    for i, h in enumerate(headers):
        d.text((col_x[i], 80), h, fill=(15, 23, 42), font=get_font(16, bold=True))
    d.line([(60, 115), (W - 60, 115)], fill=(203, 213, 225), width=2)
    
    ry = 140
    for row in rows:
        for j, val in enumerate(row):
            col = (30, 58, 138) if j == 1 else (51, 65, 85)
            d.text((col_x[j], ry), val, fill=col, font=get_font(14, bold=(j == 1 or j == 0)))
        d.line([(60, ry + 35), (W - 60, ry + 35)], fill=(241, 245, 249), width=1)
        ry += 52
        
    img.save(OUT_DIR / "product_comparison_headphones.png", "PNG")


def gen_shopping_headphones_reviews():
    img = Image.new("RGB", (W, H), (248, 250, 252))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 45], fill=(15, 23, 42))
    d.text((25, 12), "Rtings.com  •  Sony WH-1000XM5 Wireless Review & Sound Frequency Curve", fill=(248, 250, 252), font=get_font(15, bold=True))
    
    d.text((60, 80), "Sony WH-1000XM5 Wireless Headphones — Comprehensive Lab Test", fill=(15, 23, 42), font=get_font(20, bold=True))
    d.text((60, 110), "Overall Score: 8.6 / 10  •  Noise Isolation: 9.2  •  Commute/Travel: 8.9", fill=(16, 185, 129), font=get_font(15, bold=True))
    
    # Frequency response curve graph
    d.rectangle([60, 150, W - 60, 500], fill=(255, 255, 255), outline=(203, 213, 225))
    d.text((80, 170), "Raw Frequency Response vs Target Curve (20Hz - 20,000Hz)", fill=(15, 23, 42), font=get_font(14, bold=True))
    d.line([(100, 440), (W - 100, 440)], fill=(148, 163, 184), width=1)
    
    curve = []
    for x_i in range(100, W - 100, 10):
        t = (x_i - 100) / (W - 200)
        y_val = 320 + 35 * math.sin(t * 12) + 20 * math.cos(t * 5)
        curve.append((x_i, y_val))
    d.line(curve, fill=(239, 68, 68), width=3)
    d.text((100, 450), "20 Hz (Sub-Bass)", fill=(100, 116, 139), font=get_font(12))
    d.text((W // 2 - 40, 450), "1 kHz (Midrange)", fill=(100, 116, 139), font=get_font(12))
    d.text((W - 180, 450), "20 kHz (Treble)", fill=(100, 116, 139), font=get_font(12))
    
    img.save(OUT_DIR / "shopping_headphones_reviews.png", "PNG")


def gen_shopping_headphones_price_history():
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 45], fill=(30, 41, 59))
    d.text((25, 12), "Keepa Price Tracker  •  Sony WH-1000XM5 Noise Cancelling Headphones", fill=(248, 250, 252), font=get_font(15, bold=True))
    
    d.text((60, 80), "Price History: Last 90 Days on Amazon.in (Prime Day Lowest: ₹26,990)", fill=(15, 23, 42), font=get_font(18, bold=True))
    d.rectangle([60, 130, W - 60, 520], fill=(248, 250, 252), outline=(203, 213, 225))
    
    d.line([(100, 460), (W - 100, 460)], fill=(148, 163, 184), width=1)
    pts = [(100, 200), (300, 200), (450, 210), (600, 190), (750, 380), (850, 380), (W - 100, 380)]
    d.line(pts, fill=(16, 185, 129), width=3)
    d.text((740, 340), "Prime Discount: ₹26,990", fill=(16, 185, 129), font=get_font(14, bold=True))
    d.text((100, 175), "MSRP: ₹34,990", fill=(239, 68, 68), font=get_font(13))
    
    img.save(OUT_DIR / "shopping_headphones_price_history.png", "PNG")


def gen_shopping_cart_headphones():
    img = Image.new("RGB", (W, H), (243, 244, 246))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 55], fill=(19, 25, 33))
    d.text((25, 16), "amazon.in", fill=(255, 153, 0), font=get_font(20, bold=True))
    d.text((160, 20), "Delivering to Prajwal Sharma - Bangalore 560001", fill=(255, 255, 255), font=get_font(13))
    
    d.rectangle([60, 90, 840, 480], fill=(255, 255, 255), outline=(229, 231, 235))
    d.text((90, 115), "Shopping Cart", fill=(15, 23, 42), font=get_font(22, bold=True))
    d.text((90, 160), "Sony WH-1000XM5 Wireless Industry Leading Noise Canceling Headphones - Black", fill=(15, 23, 42), font=get_font(15, bold=True))
    d.text((90, 190), "In stock • Eligible for FREE Prime Delivery", fill=(0, 118, 0), font=get_font(13))
    d.text((90, 220), "Colour: Black  |  Style Name: Over-Ear  |  Quantity: 1", fill=(75, 85, 99), font=get_font(13))
    d.text((90, 260), "Price: ₹26,990.00", fill=(180, 83, 9), font=get_font(18, bold=True))
    
    # Checkout box on right
    d.rectangle([880, 90, W - 60, 320], fill=(255, 255, 255), outline=(229, 231, 235))
    d.text((910, 115), "Subtotal (1 item): ₹26,990.00", fill=(15, 23, 42), font=get_font(16, bold=True))
    d.rectangle([910, 160, W - 90, 205], fill=(255, 216, 20), outline=(247, 202, 0))
    d.text((960, 172), "Proceed to Buy", fill=(15, 23, 42), font=get_font(15, bold=True))
    
    img.save(OUT_DIR / "shopping_cart_headphones.png", "PNG")


def gen_receipt_headphones_amazon():
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([60, 40, W - 60, H - 40], fill=(255, 255, 255), outline=(203, 213, 225), width=2)
    d.text((90, 70), "Tax Invoice / Order Receipt", fill=(15, 23, 42), font=get_font(22, bold=True))
    d.text((90, 105), "Sold by: Appario Retail Private Ltd  •  GSTIN: 29AABCA1234F1Z5", fill=(71, 85, 105), font=get_font(13))
    d.line([(90, 130), (W - 90, 130)], fill=(226, 232, 240), width=1)
    
    d.text((90, 150), "Order Placed: July 22, 2026  •  Order ID: 402-9842109-1928401", fill=(15, 23, 42), font=get_font(14, bold=True))
    d.text((90, 175), "Shipping Address: Prajwal Sharma, Indiranagar, Bangalore 560038", fill=(71, 85, 105), font=get_font(13))
    
    d.rectangle([90, 220, W - 90, 260], fill=(241, 245, 249))
    d.text((110, 230), "Item Description", fill=(15, 23, 42), font=get_font(14, bold=True))
    d.text((800, 230), "Qty", fill=(15, 23, 42), font=get_font(14, bold=True))
    d.text((960, 230), "Net Amount", fill=(15, 23, 42), font=get_font(14, bold=True))
    
    d.text((110, 280), "Sony WH-1000XM5 Wireless ANC Headphones (Black)", fill=(15, 23, 42), font=get_font(14))
    d.text((810, 280), "1", fill=(15, 23, 42), font=get_font(14))
    d.text((960, 280), "₹22,872.88", fill=(15, 23, 42), font=get_font(14))
    
    d.text((110, 315), "IGST (18.0%):", fill=(71, 85, 105), font=get_font(13))
    d.text((960, 315), "₹4,117.12", fill=(71, 85, 105), font=get_font(13))
    
    d.line([(90, 350), (W - 90, 350)], fill=(203, 213, 225), width=2)
    d.text((110, 370), "Grand Total (INR):", fill=(15, 23, 42), font=get_font(16, bold=True))
    d.text((960, 370), "₹26,990.00", fill=(16, 185, 129), font=get_font(18, bold=True))
    d.text((110, 420), "Payment Method: Visa Signature Card ending in 8402 (PAID)", fill=(71, 85, 105), font=get_font(13))
    
    img.save(OUT_DIR / "receipt_headphones_amazon.png", "PNG")


# ─── CLUSTER C: LAPTOP & HARDWARE UPGRADE JOURNEY ──────────────────────────────

def gen_product_photo_silver_laptop():
    # Visual-only photo rendering
    img = Image.new("RGB", (W, H), (230, 232, 235))
    d = ImageDraw.Draw(img)
    # Desk reflection
    d.rectangle([0, 520, W, H], fill=(210, 214, 218))
    
    # Laptop base
    d.polygon([(340, 520), (940, 520), (1040, 680), (240, 680)], fill=(180, 184, 190), outline=(150, 154, 160), width=2)
    # Trackpad
    d.rectangle([540, 600, 740, 670], fill=(195, 199, 205), outline=(160, 164, 170))
    # Keyboard area
    d.rectangle([320, 535, 960, 595], fill=(40, 42, 45))
    
    # Laptop screen display (standing open at angle)
    d.polygon([(360, 160), (920, 160), (940, 520), (340, 520)], fill=(20, 22, 25), outline=(150, 154, 160), width=2)
    # Glowing screen wallpaper
    d.rectangle([380, 180, 900, 500], fill=(10, 35, 75))
    # Glowing gradient circle
    d.ellipse([540, 260, 740, 420], fill=(6, 182, 212))
    
    img.save(OUT_DIR / "product_photo_silver_laptop.png", "PNG")


def gen_product_photo_red_laptop():
    # Visual-only photo rendering of red gaming laptop
    img = Image.new("RGB", (W, H), (25, 25, 30))
    d = ImageDraw.Draw(img)
    
    # Laptop base (Crimson red finish)
    d.polygon([(340, 520), (940, 520), (1040, 680), (240, 680)], fill=(185, 28, 28), outline=(153, 27, 27), width=2)
    d.rectangle([320, 535, 960, 595], fill=(15, 15, 20))
    
    # RGB Keyboard Glow
    for kx in range(340, 940, 40):
        d.rectangle([kx, 545, kx + 30, 585], fill=(239, 68, 68))
        
    # Laptop Screen
    d.polygon([(360, 160), (920, 160), (940, 520), (340, 520)], fill=(15, 15, 20), outline=(185, 28, 28), width=3)
    d.rectangle([380, 180, 900, 500], fill=(5, 5, 10))
    d.text((560, 320), "ROG ZEPHYRUS", fill=(239, 68, 68), font=get_font(20, bold=True))
    
    img.save(OUT_DIR / "product_photo_red_laptop.png", "PNG")


def gen_product_comparison_laptops():
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 45], fill=(30, 41, 59))
    d.text((25, 12), "Hardware Lab  /  High-Performance Developer Laptop Benchmark (2026)", fill=(248, 250, 252), font=get_font(15, bold=True))
    
    headers = ["Model", "CPU & Architecture", "GPU / Tensor Cores", "RAM & SSD", "Display", "Price"]
    rows = [
        ("ASUS ZenBook 14 OLED", "Intel Core Ultra 7 155H", "Intel Arc Graphics (NPU)", "32GB LPDDR5X / 1TB", "14\" 3K 120Hz OLED", "₹1,24,990"),
        ("Lenovo LOQ 17IRX10", "Intel Core i7-14700HX", "NVIDIA RTX 5060 8GB GDDR7", "32GB DDR5 / 1TB NVMe", "17.3\" QHD 165Hz IPS", "₹1,34,990"),
        ("MacBook Pro 14", "Apple M3 Pro (12-Core)", "18-Core GPU / 16-Core NPU", "18GB Unified / 512GB", "14.2\" Liquid Retina XDR", "₹1,99,900"),
        ("Dell XPS 14 OLED", "Intel Core Ultra 7 155H", "NVIDIA RTX 4050 6GB", "32GB LPDDR5X / 1TB", "14.5\" 3.2K Touch OLED", "₹1,89,990"),
    ]
    
    col_x = [50, 260, 520, 760, 960, 1140]
    for i, h in enumerate(headers):
        d.text((col_x[i], 80), h, fill=(15, 23, 42), font=get_font(14, bold=True))
    d.line([(50, 110), (W - 50, 110)], fill=(203, 213, 225), width=2)
    
    ry = 135
    for row in rows:
        for j, val in enumerate(row):
            d.text((col_x[j], ry), val, fill=(15, 23, 42) if j == 0 else (71, 85, 105), font=get_font(13, bold=(j == 0)))
        d.line([(50, ry + 40), (W - 50, ry + 40)], fill=(241, 245, 249), width=1)
        ry += 60
        
    img.save(OUT_DIR / "product_comparison_laptops.png", "PNG")


def gen_shopping_wishlist():
    img = Image.new("RGB", (W, H), (248, 250, 252))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 45], fill=(30, 41, 59))
    d.text((25, 12), "Amazon.in  /  Your Wish Lists  /  Developer & Workstation Gear 2026", fill=(248, 250, 252), font=get_font(15, bold=True))
    
    items = [
        ("ASUS ZenBook 14 OLED UX3405", "₹1,24,990.00", "In Stock • Prime eligible"),
        ("Keychron Q1 Pro Mechanical Keyboard (Wireless)", "₹17,499.00", "In Stock"),
        ("LG 27GP95R-B 27\" 4K UHD 144Hz Nano IPS Gaming Monitor", "₹48,990.00", "Only 2 left in stock"),
        ("CalDigit TS4 Thunderbolt 4 Dock (18 Ports)", "₹38,500.00", "In Stock • International Shipping"),
    ]
    
    y = 80
    for title, price, status in items:
        d.rectangle([60, y, W - 60, y + 100], fill=(255, 255, 255), outline=(226, 232, 240))
        d.text((90, y + 20), title, fill=(15, 23, 42), font=get_font(16, bold=True))
        d.text((90, y + 55), status, fill=(0, 118, 0) if "In Stock" in status else (180, 83, 9), font=get_font(13))
        d.text((W - 240, y + 35), price, fill=(180, 83, 9), font=get_font(18, bold=True))
        y += 120
        
    img.save(OUT_DIR / "shopping_wishlist.png", "PNG")


def gen_receipt_laptop_amazon():
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([60, 40, W - 60, H - 40], fill=(255, 255, 255), outline=(203, 213, 225), width=2)
    d.text((90, 70), "Tax Invoice / Official Bill of Sale", fill=(15, 23, 42), font=get_font(22, bold=True))
    d.text((90, 105), "Sold by: Appario Retail Private Ltd  •  GSTIN: 29AABCA1234F1Z5", fill=(71, 85, 105), font=get_font(13))
    d.line([(90, 130), (W - 90, 130)], fill=(226, 232, 240), width=1)
    
    d.text((90, 150), "Order Placed: August 10, 2026  •  Order ID: 402-1849204-7491023", fill=(15, 23, 42), font=get_font(14, bold=True))
    d.text((90, 175), "Customer: Prajwal Sharma, Indiranagar, Bangalore 560038", fill=(71, 85, 105), font=get_font(13))
    
    d.rectangle([90, 220, W - 90, 260], fill=(241, 245, 249))
    d.text((110, 230), "Item Description", fill=(15, 23, 42), font=get_font(14, bold=True))
    d.text((800, 230), "Qty", fill=(15, 23, 42), font=get_font(14, bold=True))
    d.text((960, 230), "Amount (INR)", fill=(15, 23, 42), font=get_font(14, bold=True))
    
    d.text((110, 280), "ASUS ZenBook 14 OLED Laptop (Core Ultra 7, 32GB RAM, 1TB SSD, 3K 120Hz)", fill=(15, 23, 42), font=get_font(14, bold=True))
    d.text((810, 280), "1", fill=(15, 23, 42), font=get_font(14))
    d.text((960, 280), "₹1,05,923.73", fill=(15, 23, 42), font=get_font(14))
    
    d.text((110, 315), "CGST (9.0%) + SGST (9.0%):", fill=(71, 85, 105), font=get_font(13))
    d.text((960, 315), "₹19,066.27", fill=(71, 85, 105), font=get_font(13))
    
    d.line([(90, 350), (W - 90, 350)], fill=(203, 213, 225), width=2)
    d.text((110, 370), "Grand Total (INR):", fill=(15, 23, 42), font=get_font(16, bold=True))
    d.text((960, 370), "₹1,24,990.00", fill=(16, 185, 129), font=get_font(18, bold=True))
    d.text((110, 420), "Payment Mode: HDFC Regalia Credit Card ending in 4920 (PAID)", fill=(71, 85, 105), font=get_font(13))
    
    img.save(OUT_DIR / "receipt_laptop_amazon.png", "PNG")


def gen_invoice_monitor():
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([60, 40, W - 60, H - 40], fill=(255, 255, 255), outline=(203, 213, 225), width=2)
    d.text((90, 70), "TechZone Electronics Ltd — Commercial Invoice", fill=(15, 23, 42), font=get_font(20, bold=True))
    d.text((90, 100), "Invoice #: TZ-2026-8491  •  Date: July 15, 2026  •  GSTIN: 29AABCT9981Z1", fill=(71, 85, 105), font=get_font(13))
    d.line([(90, 125), (W - 90, 125)], fill=(226, 232, 240), width=1)
    
    d.text((90, 150), "Billed To: Prajwal Sharma, Zenith AI Labs, Bangalore", fill=(15, 23, 42), font=get_font(14))
    d.rectangle([90, 190, W - 90, 230], fill=(241, 245, 249))
    d.text((110, 200), "Description", fill=(15, 23, 42), font=get_font(13, bold=True))
    d.text((960, 200), "Price", fill=(15, 23, 42), font=get_font(13, bold=True))
    
    d.text((110, 250), "LG UltraGear 27\" 4K UHD 144Hz Nano IPS HDR600 Display (27GP95R)", fill=(15, 23, 42), font=get_font(14))
    d.text((960, 250), "₹48,990.00", fill=(15, 23, 42), font=get_font(14))
    
    d.line([(90, 300), (W - 90, 300)], fill=(203, 213, 225), width=2)
    d.text((110, 320), "Total Amount Paid:", fill=(15, 23, 42), font=get_font(16, bold=True))
    d.text((960, 320), "₹48,990.00", fill=(16, 185, 129), font=get_font(16, bold=True))
    
    img.save(OUT_DIR / "invoice_monitor.png", "PNG")


# ─── CLUSTER D: BANGALORE TO GOA TRIP & VACATION ──────────────────────────────

def gen_travel_bangalore_goa_flight():
    img = Image.new("RGB", (W, H), (248, 250, 252))
    d = ImageDraw.Draw(img)
    d.rectangle([80, 60, W - 80, 520], fill=(255, 255, 255), outline=(203, 213, 225), width=2)
    d.rectangle([80, 60, W - 80, 120], fill=(0, 43, 114)) # IndiGo Blue
    d.text((110, 78), "IndiGo  •  Boarding Pass / E-Ticket", fill=(255, 255, 255), font=get_font(20, bold=True))
    d.text((W - 320, 82), "Flight: 6E 6291 (Confirmed)", fill=(255, 255, 255), font=get_font(14, bold=True))
    
    d.text((110, 160), "Passenger Name: PRAJWAL / SHARMA MR", fill=(15, 23, 42), font=get_font(16, bold=True))
    d.text((110, 195), "PNR: W4G92K  •  Seat: 4F (Window)  •  Zone: 1", fill=(71, 85, 105), font=get_font(14))
    
    d.rectangle([110, 240, 540, 380], fill=(241, 245, 249), outline=(203, 213, 225))
    d.text((130, 260), "FROM: BLR (Bangalore)", fill=(15, 23, 42), font=get_font(16, bold=True))
    d.text((130, 290), "Kempegowda Int'l Terminal 2", fill=(71, 85, 105), font=get_font(13))
    d.text((130, 330), "Departure: 14:15 IST • 18 Jul 2026", fill=(0, 43, 114), font=get_font(14, bold=True))
    
    d.rectangle([580, 240, W - 110, 380], fill=(241, 245, 249), outline=(203, 213, 225))
    d.text((600, 260), "TO: GOI (Goa Dabolim)", fill=(15, 23, 42), font=get_font(16, bold=True))
    d.text((600, 290), "Dabolim Airport Terminal 1", fill=(71, 85, 105), font=get_font(13))
    d.text((600, 330), "Arrival: 15:30 IST • 18 Jul 2026", fill=(0, 43, 114), font=get_font(14, bold=True))
    
    d.text((110, 420), "Gate: 24B  •  Boarding Time: 13:35 IST  •  Baggage: 15 Kg Checked", fill=(180, 83, 9), font=get_font(14, bold=True))
    img.save(OUT_DIR / "travel_bangalore_goa_flight.png", "PNG")


def gen_travel_goa_hotel():
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 50], fill=(30, 41, 59))
    d.text((25, 15), "Booking.com Confirmation  •  Taj Exotica Resort & Spa, Goa", fill=(248, 250, 252), font=get_font(16, bold=True))
    
    d.text((60, 80), "Reservation Confirmed: #394810294", fill=(16, 185, 129), font=get_font(20, bold=True))
    d.text((60, 115), "Taj Exotica Resort & Spa, Calwaddo, Benaulim Beach, South Goa, 403716", fill=(71, 85, 105), font=get_font(14))
    
    d.rectangle([60, 160, W - 60, 320], fill=(248, 250, 252), outline=(203, 213, 225))
    d.text((90, 180), "Check-in: Saturday, July 18, 2026 (From 14:00)", fill=(15, 23, 42), font=get_font(15, bold=True))
    d.text((90, 215), "Check-out: Tuesday, July 21, 2026 (Until 12:00) • 3 Nights", fill=(15, 23, 42), font=get_font(15, bold=True))
    d.text((90, 250), "Room: Luxury Sea View Villa with Plunge Pool • 1 King Bed • Free Breakfast", fill=(51, 65, 85), font=get_font(14))
    d.text((90, 280), "Total Price Paid: ₹78,500.00 (All taxes included)", fill=(180, 83, 9), font=get_font(15, bold=True))
    
    img.save(OUT_DIR / "travel_goa_hotel.png", "PNG")


def gen_map_route_restaurant():
    img = Image.new("RGB", (W, H), (235, 240, 245))
    d = ImageDraw.Draw(img)
    # Header bar
    d.rectangle([0, 0, W, 50], fill=(66, 133, 244))
    d.text((25, 14), "Google Maps  •  Dabolim Airport -> Taj Exotica Benaulim Beach (28 km)", fill=(255, 255, 255), font=get_font(16, bold=True))
    
    # Roads simulation
    d.line([(100, 200), (450, 350), (700, 480), (1050, 620)], fill=(255, 255, 255), width=24)
    d.line([(100, 200), (450, 350), (700, 480), (1050, 620)], fill=(66, 133, 244), width=14)
    
    # Pins
    d.ellipse([90, 180, 130, 220], fill=(234, 67, 53))
    d.text((145, 190), "Dabolim Airport (Start)", fill=(15, 23, 42), font=get_font(15, bold=True))
    
    d.ellipse([1030, 600, 1070, 640], fill=(52, 168, 83))
    d.text((850, 650), "Taj Exotica Goa (Destination)", fill=(15, 23, 42), font=get_font(15, bold=True))
    
    # Route info box
    d.rectangle([60, 80, 360, 170], fill=(255, 255, 255), outline=(203, 213, 225))
    d.text((80, 95), "Fastest route: 42 min (28.4 km)", fill=(15, 23, 42), font=get_font(15, bold=True))
    d.text((80, 125), "via NH 66 and Benaulim Beach Rd", fill=(71, 85, 105), font=get_font(13))
    
    img.save(OUT_DIR / "map_route_restaurant.png", "PNG")


def gen_scene_beach_sunset():
    # Visual-only photo rendering
    img = Image.new("RGB", (W, H), (255, 140, 60))
    d = ImageDraw.Draw(img)
    # Sunset gradient
    for y in range(0, 450):
        r = int(255 - (y / 450) * 80)
        g = int(140 + (y / 450) * 40)
        b = int(60 + (y / 450) * 140)
        d.line([(0, y), (W, y)], fill=(r, g, b))
        
    # Golden Sun
    d.ellipse([560, 240, 720, 400], fill=(255, 240, 180))
    
    # Ocean water
    for y in range(450, H):
        r = int(20 + (y - 450) * 0.1)
        g = int(60 + (y - 450) * 0.15)
        b = int(110 + (y - 450) * 0.2)
        d.line([(0, y), (W, y)], fill=(r, g, b))
    # Sun reflection on ocean
    d.polygon([(640, 450), (560, H), (720, H)], fill=(240, 180, 100))
    
    # Palm tree silhouettes on left
    d.polygon([(60, H), (80, 280), (100, H)], fill=(15, 20, 25))
    d.arc([0, 200, 200, 360], start=180, end=340, fill=(15, 20, 25), width=8)
    d.arc([40, 180, 240, 340], start=200, end=360, fill=(15, 20, 25), width=8)
    
    img.save(OUT_DIR / "scene_beach_sunset.png", "PNG")


def gen_scene_rooftop_restaurant():
    # Visual-only photo rendering
    img = Image.new("RGB", (W, H), (15, 20, 35))
    d = ImageDraw.Draw(img)
    # Night sky with warm fairy lights
    for x in range(80, W - 80, 45):
        d.ellipse([x, 80 + int(20 * math.sin(x)), x + 8, 88 + int(20 * math.sin(x))], fill=(255, 215, 100))
        
    # Wooden deck floor
    d.rectangle([0, 480, W, H], fill=(50, 38, 28))
    # Dining table with candle
    d.rectangle([480, 420, 800, 560], fill=(120, 100, 80), outline=(80, 60, 40))
    d.ellipse([625, 450, 655, 480], fill=(255, 180, 50)) # Candle
    
    img.save(OUT_DIR / "scene_rooftop_restaurant.png", "PNG")


def gen_map_restaurant_goa():
    img = Image.new("RGB", (W, H), (241, 245, 249))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 45], fill=(30, 41, 59))
    d.text((25, 12), "Google Maps  •  Fisherman's Wharf, Salcette, South Goa", fill=(248, 250, 252), font=get_font(15, bold=True))
    
    d.rectangle([80, 80, 480, 480], fill=(255, 255, 255), outline=(203, 213, 225))
    d.text((110, 110), "The Fisherman's Wharf", fill=(15, 23, 42), font=get_font(20, bold=True))
    d.text((110, 145), "★★★★☆ 4.6 (8,412 Reviews) • Seafood / Goan Cuisine", fill=(245, 158, 11), font=get_font(13, bold=True))
    d.text((110, 180), "At The Riverside, Mobor Beach, Cavelossim, Goa 403731", fill=(71, 85, 105), font=get_font(13))
    d.text((110, 220), "Popular dishes: Butter Garlic Prawns, Kingfish Curry, Truffle Wood-Fired Pizza", fill=(51, 65, 85), font=get_font(13))
    
    img.save(OUT_DIR / "map_restaurant_goa.png", "PNG")


def gen_receipt_cab_goa():
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([80, 60, W - 80, 520], fill=(255, 255, 255), outline=(203, 213, 225), width=2)
    d.text((110, 90), "Goa Miles  •  Ride Receipt & Tax Invoice", fill=(15, 23, 42), font=get_font(20, bold=True))
    d.text((110, 125), "Trip Date: July 18, 2026  •  Driver: Rajesh Naik (GA-08-T-4910)", fill=(71, 85, 105), font=get_font(13))
    
    d.text((110, 170), "Pickup: Goa Dabolim International Airport", fill=(15, 23, 42), font=get_font(14, bold=True))
    d.text((110, 205), "Drop: Taj Exotica Resort & Spa, Benaulim", fill=(15, 23, 42), font=get_font(14, bold=True))
    d.text((110, 240), "Distance: 28.4 km  •  Duration: 44 mins", fill=(71, 85, 105), font=get_font(13))
    
    d.line([(110, 275), (W - 110, 275)], fill=(203, 213, 225), width=1)
    d.text((110, 300), "Base Fare + Tolls + Airport Access Fee:", fill=(15, 23, 42), font=get_font(14))
    d.text((W - 240, 300), "₹1,450.00", fill=(16, 185, 129), font=get_font(16, bold=True))
    d.text((110, 345), "Paid via UPI (Google Pay ref: 619284019284)", fill=(71, 85, 105), font=get_font(13))
    
    img.save(OUT_DIR / "receipt_cab_goa.png", "PNG")


# ─── CLUSTER E: FOOD & CULINARY STORY ─────────────────────────────────────────

def gen_food_photo_truffle_pizza():
    # Visual-only photo rendering of artisanal pizza
    img = Image.new("RGB", (W, H), (60, 45, 35)) # Dark slate table
    d = ImageDraw.Draw(img)
    
    # Wooden cutting board
    d.ellipse([340, 120, 940, 680], fill=(160, 120, 80), outline=(130, 95, 60), width=4)
    # Pizza crust (Golden Brown)
    d.ellipse([370, 150, 910, 650], fill=(210, 160, 90), outline=(180, 130, 70), width=6)
    # Melted Mozzarella center
    d.ellipse([420, 200, 860, 600], fill=(255, 245, 215))
    
    # Truffle slices (Dark brown mushrooms)
    truffles = [(520, 300), (680, 280), (600, 400), (740, 440), (480, 480), (640, 520)]
    for tx, ty in truffles:
        d.ellipse([tx, ty, tx + 45, ty + 35], fill=(45, 30, 25))
    # Green Basil Leaves
    leaves = [(560, 340), (700, 380), (520, 430), (670, 480)]
    for lx, ly in leaves:
        d.ellipse([lx, ly, lx + 30, ly + 18], fill=(34, 139, 34))
        
    img.save(OUT_DIR / "food_photo_truffle_pizza.png", "PNG")


def gen_food_photo_mushroom_pasta():
    # Visual-only photo rendering
    img = Image.new("RGB", (W, H), (40, 40, 45))
    d = ImageDraw.Draw(img)
    
    # Ceramic bowl
    d.ellipse([360, 140, 920, 660], fill=(245, 245, 248), outline=(210, 210, 215), width=6)
    # Tagliatelle Pasta nest
    d.ellipse([420, 200, 860, 600], fill=(240, 220, 170))
    # Sautéed Portobello Mushrooms
    for mx, my in [(500, 300), (660, 280), (580, 420), (720, 450), (480, 460)]:
        d.rectangle([mx, my, mx + 50, my + 30], fill=(70, 50, 40))
    # Fresh grated parmesan specks
    for px, py in [(540, 320), (620, 350), (590, 400), (680, 410)]:
        d.ellipse([px, py, px + 12, py + 8], fill=(255, 255, 240))
        
    img.save(OUT_DIR / "food_photo_mushroom_pasta.png", "PNG")


def gen_food_photo_japanese_ramen():
    # Visual-only photo rendering
    img = Image.new("RGB", (W, H), (30, 32, 36))
    d = ImageDraw.Draw(img)
    
    # Black ramen bowl
    d.ellipse([360, 140, 920, 660], fill=(20, 20, 22), outline=(180, 50, 40), width=5)
    # Tonkotsu Broth
    d.ellipse([400, 180, 880, 620], fill=(220, 185, 140))
    # Ramen Noodles
    d.arc([460, 240, 780, 560], start=30, end=200, fill=(240, 210, 130), width=12)
    # Ajitsuke Tamago (Soft boiled egg half)
    d.ellipse([640, 260, 740, 360], fill=(255, 255, 255))
    d.ellipse([665, 285, 715, 335], fill=(255, 140, 0)) # Golden yolk
    # Nori Seaweed Sheet
    d.polygon([(440, 220), (520, 200), (500, 340), (420, 360)], fill=(25, 40, 30))
    
    img.save(OUT_DIR / "food_photo_japanese_ramen.png", "PNG")


def gen_recipe_mushroom_pasta():
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 50], fill=(45, 55, 72))
    d.text((25, 15), "Gourmet Kitchen  /  Creamy Wild Mushroom Tagliatelle with Truffle Oil", fill=(255, 255, 255), font=get_font(16, bold=True))
    
    d.text((60, 80), "Creamy Wild Mushroom Pasta Recipe", fill=(15, 23, 42), font=get_font(22, bold=True))
    d.text((60, 115), "Prep: 15 mins  •  Cook: 20 mins  •  Servings: 2  •  Difficulty: Intermediate", fill=(71, 85, 105), font=get_font(14))
    
    d.rectangle([60, 160, 540, 680], fill=(248, 250, 252), outline=(203, 213, 225))
    d.text((80, 180), "Key Ingredients:", fill=(15, 23, 42), font=get_font(16, bold=True))
    ings = [
        "• 250g Fresh Tagliatelle or Fettuccine",
        "• 300g Mixed Wild Mushrooms (Portobello, Shiitake)",
        "• 2 cloves Garlic, finely minced",
        "• 1 Shallot, diced",
        "• 150ml Heavy Cream",
        "• 50g Parmigiano-Reggiano, freshly grated",
        "• 1 tbsp White Truffle Oil (for finishing)",
        "• 2 tbsp Unsalted Butter & Fresh Thyme",
        "• Salt & Freshly Cracked Black Pepper",
    ]
    iy = 220
    for ing in ings:
        d.text((80, iy), ing, fill=(51, 65, 85), font=get_font(14))
        iy += 38
        
    d.rectangle([580, 160, W - 60, 680], fill=(255, 255, 255), outline=(203, 213, 225))
    d.text((600, 180), "Cooking Instructions:", fill=(15, 23, 42), font=get_font(16, bold=True))
    steps = [
        "1. Boil salted water in large pot. Cook pasta 3-4 mins until al dente.",
        "2. In a heavy skillet, melt butter over medium-high heat.",
        "3. Sear mushrooms in single layer without crowding for 5 mins until golden.",
        "4. Add shallots, minced garlic, and thyme; sauté 2 mins until fragrant.",
        "5. Pour in heavy cream and 50ml reserved pasta water. Simmer gently.",
        "6. Toss cooked pasta into sauce. Stir in grated parmesan until glossy.",
        "7. Drizzle 1 tbsp truffle oil over top and serve immediately.",
    ]
    sy = 220
    for s in steps:
        d.text((600, sy), s, fill=(51, 65, 85), font=get_font(13))
        sy += 50
        
    img.save(OUT_DIR / "recipe_mushroom_pasta.png", "PNG")


def gen_menu_italian_bistro():
    img = Image.new("RGB", (W, H), (252, 249, 242)) # Parchment paper
    d = ImageDraw.Draw(img)
    d.rectangle([60, 40, W - 60, H - 40], fill=(252, 249, 242), outline=(180, 140, 100), width=2)
    
    d.text((450, 70), "TRATTORIA RUSTICA", fill=(80, 40, 20), font=get_font(26, bold=True))
    d.text((490, 110), "Autentica Cucina Italiana • Bangalore", fill=(120, 80, 50), font=get_font(14))
    d.line([(200, 140), (W - 200, 140)], fill=(180, 140, 100), width=1)
    
    # Primi Piatti
    d.text((120, 170), "PRIMI PIATTI (Handmade Pasta)", fill=(120, 40, 20), font=get_font(16, bold=True))
    pastas = [
        ("Tagliatelle ai Funghi e Tartufo", "Wild mushroom medley, white truffle cream, parmesan", "₹780"),
        ("Spaghetti alla Carbonara", "Guanciale, pecorino romano, farm eggs, black pepper", "₹720"),
        ("Ravioli di Ricotta e Spinaci", "Handmade ricotta ravioli, sage butter sauce", "₹690"),
    ]
    py = 205
    for name, desc, price in pastas:
        d.text((120, py), name, fill=(30, 20, 10), font=get_font(14, bold=True))
        d.text((W - 220, py), price, fill=(120, 40, 20), font=get_font(14, bold=True))
        d.text((120, py + 22), desc, fill=(100, 90, 80), font=get_font(12))
        py += 55
        
    # Pizze al Forno
    d.text((120, 390), "PIZZE AL FORNO A LEGNA (Wood-Fired Pizza)", fill=(120, 40, 20), font=get_font(16, bold=True))
    pizzas = [
        ("Pizza Tartufo e Funghi", "Fior di latte, porcini mushrooms, fresh black truffle oil, basil", "₹890"),
        ("Margherita D.O.P.", "San Marzano tomatoes, buffalo mozzarella, fresh basil", "₹650"),
        ("Diavola Piccante", "Spicy Calabrian salami, mozzarella, chili oil", "₹750"),
    ]
    zy = 425
    for name, desc, price in pizzas:
        d.text((120, zy), name, fill=(30, 20, 10), font=get_font(14, bold=True))
        d.text((W - 220, zy), price, fill=(120, 40, 20), font=get_font(14, bold=True))
        d.text((120, zy + 22), desc, fill=(100, 90, 80), font=get_font(12))
        zy += 55
        
    img.save(OUT_DIR / "menu_italian_bistro.png", "PNG")


def gen_receipt_grocery():
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([120, 40, W - 120, H - 40], fill=(255, 255, 255), outline=(203, 213, 225), width=2)
    d.text((150, 70), "Nature's Basket Gourmet Supermarket", fill=(15, 23, 42), font=get_font(20, bold=True))
    d.text((150, 100), "Store #14, Indiranagar 100ft Rd, Bangalore  •  GST: 29AABCN8491M1", fill=(71, 85, 105), font=get_font(13))
    d.line([(150, 125), (W - 150, 125)], fill=(226, 232, 240), width=1)
    
    items = [
        ("Fresh Portobello Mushrooms (250g)", "₹180.00"),
        ("Urbani White Truffle Oil (100ml)", "₹1,450.00"),
        ("De Cecco Tagliatelle Pasta (500g)", "₹320.00"),
        ("Parmigiano Reggiano 24-Month (200g)", "₹580.00"),
        ("Amul Gourmet Salted Butter (500g)", "₹290.00"),
        ("Fresh Organic Basil Leaves", "₹45.00"),
    ]
    iy = 160
    for name, pr in items:
        d.text((150, iy), name, fill=(15, 23, 42), font=get_font(14))
        d.text((W - 280, iy), pr, fill=(15, 23, 42), font=get_font(14))
        iy += 38
        
    d.line([(150, iy + 20), (W - 150, iy + 20)], fill=(203, 213, 225), width=2)
    d.text((150, iy + 45), "Total Amount Paid (INR):", fill=(15, 23, 42), font=get_font(16, bold=True))
    d.text((W - 280, iy + 45), "₹2,865.00", fill=(16, 185, 129), font=get_font(18, bold=True))
    
    img.save(OUT_DIR / "receipt_grocery.png", "PNG")


# ─── CLUSTER F: ELECTRONICS & ENGINEERING STUDY ───────────────────────────────

def gen_diagram_rlc_circuit():
    # Visual-only diagram rendering of RLC circuit
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 45], fill=(30, 41, 59))
    d.text((25, 12), "Circuit Theory & Signal Processing  •  Series RLC Resonant Circuit", fill=(248, 250, 252), font=get_font(15, bold=True))
    
    # Circuit loops
    d.line([(240, 400), (400, 400)], fill=(15, 23, 42), width=3) # AC Source to Resistor
    d.line([(500, 400), (650, 400)], fill=(15, 23, 42), width=3) # Resistor to Inductor
    d.line([(770, 400), (900, 400)], fill=(15, 23, 42), width=3) # Inductor to Capacitor
    d.line([(960, 400), (1050, 400), (1050, 560), (240, 560), (240, 400)], fill=(15, 23, 42), width=3) # Return path
    
    # Resistor Symbol (Zigzag)
    d.line([(400, 400), (415, 380), (435, 420), (455, 380), (475, 420), (495, 380), (500, 400)], fill=(180, 83, 9), width=3)
    d.text((430, 345), "R = 50 Ω", fill=(180, 83, 9), font=get_font(15, bold=True))
    
    # Inductor Symbol (Coils)
    d.arc([650, 375, 690, 425], start=180, end=0, fill=(30, 58, 138), width=3)
    d.arc([690, 375, 730, 425], start=180, end=0, fill=(30, 58, 138), width=3)
    d.arc([730, 375, 770, 425], start=180, end=0, fill=(30, 58, 138), width=3)
    d.text((680, 345), "L = 10 mH", fill=(30, 58, 138), font=get_font(15, bold=True))
    
    # Capacitor Symbol (Parallel plates)
    d.line([(900, 370), (900, 430)], fill=(16, 185, 129), width=4)
    d.line([(920, 370), (920, 430)], fill=(16, 185, 129), width=4)
    d.text((890, 335), "C = 100 nF", fill=(16, 185, 129), font=get_font(15, bold=True))
    
    # Formula Box
    d.rectangle([300, 120, 980, 240], fill=(248, 250, 252), outline=(203, 213, 225))
    d.text((340, 140), "Resonant Frequency: f_0 = 1 / (2π · √(L · C)) = 5.033 kHz", fill=(15, 23, 42), font=get_font(16, bold=True))
    d.text((340, 180), "Quality Factor: Q = (1 / R) · √(L / C) = 6.32  •  Bandwidth: BW = f_0 / Q", fill=(71, 85, 105), font=get_font(14))
    
    img.save(OUT_DIR / "diagram_rlc_circuit.png", "PNG")


def gen_diagram_logic_gates():
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 45], fill=(30, 41, 59))
    d.text((25, 12), "Digital Logic Design  •  1-Bit Full Adder Schematic with XOR & AND Gates", fill=(248, 250, 252), font=get_font(15, bold=True))
    
    # Inputs
    d.text((100, 200), "Input A", fill=(15, 23, 42), font=get_font(14, bold=True))
    d.text((100, 280), "Input B", fill=(15, 23, 42), font=get_font(14, bold=True))
    d.text((100, 440), "Cin", fill=(15, 23, 42), font=get_font(14, bold=True))
    
    # XOR Gate 1
    d.rectangle([340, 210, 460, 290], fill=(224, 231, 255), outline=(59, 130, 246), width=2)
    d.text((375, 240), "XOR 1", fill=(30, 58, 138), font=get_font(14, bold=True))
    
    # XOR Gate 2 (Sum)
    d.rectangle([680, 260, 800, 340], fill=(224, 231, 255), outline=(59, 130, 246), width=2)
    d.text((715, 290), "XOR 2", fill=(30, 58, 138), font=get_font(14, bold=True))
    d.text((850, 290), "SUM Output (S)", fill=(16, 185, 129), font=get_font(15, bold=True))
    
    # OR Gate (Carry Out)
    d.rectangle([780, 480, 900, 560], fill=(254, 243, 199), outline=(245, 158, 11), width=2)
    d.text((815, 510), "OR Gate", fill=(180, 83, 9), font=get_font(14, bold=True))
    d.text((950, 510), "Cout (Carry Out)", fill=(239, 68, 68), font=get_font(15, bold=True))
    
    img.save(OUT_DIR / "diagram_logic_gates.png", "PNG")


def gen_notes_handwritten_math():
    # Visual handwritten simulation
    img = Image.new("RGB", (W, H), (252, 250, 242)) # Notebook paper with faint lines
    d = ImageDraw.Draw(img)
    # Lined paper
    for y in range(80, H, 35):
        d.line([(0, y), (W, y)], fill=(230, 235, 245), width=1)
    d.line([(120, 0), (120, H)], fill=(255, 180, 180), width=2) # Red margin line
    
    d.text((150, 100), "Derivation of Stochastic Gradient Descent & Backpropagation", fill=(15, 30, 90), font=get_font(18, bold=True))
    d.text((150, 150), "Let Loss function L(θ) = 1/N ∑ ℓ(f_θ(x_i), y_i)", fill=(20, 40, 110), font=get_font(16))
    d.text((150, 200), "Gradient update rule: θ_{t+1} = θ_t - η · ∇_θ L_batch(θ_t)", fill=(20, 40, 110), font=get_font(16, bold=True))
    d.text((150, 255), "By Chain Rule through layer l: ∂L/∂W^(l) = δ^(l) · (a^(l-1))^T", fill=(20, 40, 110), font=get_font(16))
    d.text((150, 310), "Where error term: δ^(l) = ((W^(l+1))^T δ^(l+1)) ⊙ σ'(z^(l))", fill=(20, 40, 110), font=get_font(16))
    d.text((150, 370), "Momentum update: v_t = γ v_{t-1} + η ∇L(θ)", fill=(20, 40, 110), font=get_font(15))
    d.text((150, 420), "Adam Optimizer with first & second moment bias corrections: m̂_t, v̂_t", fill=(20, 40, 110), font=get_font(15))
    
    img.save(OUT_DIR / "notes_handwritten_math.png", "PNG")


def gen_diagram_neural_network():
    img = Image.new("RGB", (W, H), (15, 23, 42))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 45], fill=(30, 41, 59))
    d.text((25, 12), "Deep Learning Architecture  •  Multi-Layer Perceptron (MLP) Graph Topology", fill=(248, 250, 252), font=get_font(15, bold=True))
    
    layers = [
        ("Input Layer (x_1..x_4)", 4, 180, (59, 130, 246)),
        ("Hidden Layer 1 (6 Neurons)", 6, 450, (16, 185, 129)),
        ("Hidden Layer 2 (6 Neurons)", 6, 750, (245, 158, 11)),
        ("Output Layer (Softmax)", 2, 1050, (239, 68, 68))
    ]
    
    nodes_by_layer = []
    for ltitle, count, lx, col in layers:
        node_pos = []
        d.text((lx - 50, 100), ltitle.split()[0], fill=(203, 213, 225), font=get_font(14, bold=True))
        start_y = 400 - (count * 45)
        for i in range(count):
            ny = start_y + i * 90
            node_pos.append((lx, ny))
            d.ellipse([lx - 20, ny - 20, lx + 20, ny + 20], fill=col, outline=(255, 255, 255), width=2)
        nodes_by_layer.append(node_pos)
        
    for l in range(len(nodes_by_layer) - 1):
        for n1 in nodes_by_layer[l]:
            for n2 in nodes_by_layer[l + 1]:
                d.line([n1, n2], fill=(51, 65, 85), width=1)
                
    img.save(OUT_DIR / "diagram_neural_network.png", "PNG")


def gen_diagram_aura_architecture():
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 45], fill=(30, 41, 59))
    d.text((25, 12), "System Architecture  •  AURA Agentic Visual Memory Engine Pipeline", fill=(248, 250, 252), font=get_font(15, bold=True))
    
    stages = [
        ("1. Ingestion & Preprocessing", "EXIF Transpose, 1600px scaling, Contrast norm", (224, 231, 255), 100),
        ("2. Multimodal OCR & Vision", "EasyOCR + Google Gemini Vision + OpenRouter fallback", (254, 243, 199), 320),
        ("3. AURA Shield Zero-Trust", "PII, Passwords, API Keys detection & Redaction", (254, 226, 226), 540),
        ("4. Vector & Graph Indexing", "all-MiniLM-L6-v2 (384-d) + SQLite Topology", (220, 252, 231), 760),
        ("5. Agentic Hybrid Search", "Dense Vector Cosine + Token BM25 + Graph Traversal", (243, 232, 255), 980),
    ]
    
    for title, desc, col, sx in stages:
        d.rectangle([sx, 160, sx + 180, 540], fill=col, outline=(148, 163, 184), width=2)
        d.text((sx + 15, 190), title.split()[1], fill=(15, 23, 42), font=get_font(14, bold=True))
        d.text((sx + 15, 220), title, fill=(30, 58, 138), font=get_font(12, bold=True))
        d.text((sx + 15, 260), desc, fill=(51, 65, 85), font=get_font(12))
        
    img.save(OUT_DIR / "diagram_aura_architecture.png", "PNG")


# ─── CLUSTER G: SOFTWARE ENGINEERING, DEVOPS & DEBUGGING ──────────────────────

def gen_code_auth_service():
    img = Image.new("RGB", (W, H), (15, 23, 42))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 40], fill=(30, 41, 59))
    d.text((20, 10), "VS Code — backend/app/services/auth.py (FastAPI JWT Service)", fill=(203, 213, 225), font=get_font(14))
    
    code = [
        ("from datetime import datetime, timedelta, timezone", (147, 197, 253)),
        ("import jwt", (244, 114, 182)),
        ("from fastapi import HTTPException, Security", (244, 114, 182)),
        ("from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials", (203, 213, 225)),
        ("", (255, 255, 255)),
        ("JWT_SECRET = 'zenith-super-secret-key-2026'", (251, 146, 60)),
        ("ALGORITHM = 'HS256'", (251, 146, 60)),
        ("", (255, 255, 255)),
        ("def create_access_token(data: dict, expires_delta: timedelta = None) -> str:", (251, 191, 36)),
        ("    to_encode = data.copy()", (203, 213, 225)),
        ("    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(hours=8))", (147, 197, 253)),
        ("    to_encode.update({'exp': expire, 'iss': 'aura-auth-service'})", (52, 211, 153)),
        ("    return jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)", (244, 114, 182)),
        ("", (255, 255, 255)),
        ("def verify_token(credentials: HTTPAuthorizationCredentials = Security(HTTPBearer())):", (251, 191, 36)),
        ("    try:", (244, 114, 182)),
        ("        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[ALGORITHM])", (52, 211, 153)),
        ("        return payload", (203, 213, 225)),
        ("    except jwt.ExpiredSignatureError:", (244, 114, 182)),
        ("        raise HTTPException(status_code=401, detail='Token expired')", (239, 68, 68)),
    ]
    y = 60
    for line, col in code:
        d.text((45, y), line, fill=col, font=get_font(15))
        y += 26
    img.save(OUT_DIR / "code_auth_service.png", "PNG")


def gen_github_issue_auth_bug():
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 50], fill=(36, 41, 47))
    d.text((25, 14), "GitHub  /  scryptic-aura  /  Issues  /  #142", fill=(255, 255, 255), font=get_font(16, bold=True))
    
    d.text((60, 80), "Bug: JWT token refresh returns HTTP 401 ExpiredSignatureError on iOS Safari #142", fill=(15, 23, 42), font=get_font(20, bold=True))
    d.rectangle([60, 120, 130, 150], fill=(239, 68, 68))
    d.text((72, 126), "● Open", fill=(255, 255, 255), font=get_font(13, bold=True))
    d.text((145, 126), "prajwal opened this issue 3 hours ago • 8 comments", fill=(71, 85, 105), font=get_font(13))
    
    d.rectangle([60, 170, W - 60, 480], fill=(246, 248, 250), outline=(208, 215, 222))
    d.text((85, 195), "Describe the bug:", fill=(15, 23, 42), font=get_font(15, bold=True))
    d.text((85, 230), "When client calls `/api/auth/refresh` after 8 hours of background idle time,", fill=(36, 41, 47), font=get_font(14))
    d.text((85, 260), "the backend fails with `jwt.exceptions.ExpiredSignatureError: Signature has expired`", fill=(207, 34, 46), font=get_font(14, bold=True))
    d.text((85, 290), "instead of gracefully issuing a new access token via refresh token rotation.", fill=(36, 41, 47), font=get_font(14))
    
    img.save(OUT_DIR / "github_issue_auth_bug.png", "PNG")


def gen_terminal_error_traceback():
    img = Image.new("RGB", (W, H), (15, 23, 42))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 35], fill=(30, 30, 40))
    d.text((15, 8), "Terminal: Python 3.11 Crash Log", fill=(200, 200, 210), font=get_font(13))
    
    lines = [
        ("Traceback (most recent call last):", (239, 68, 68)),
        ("  File \"train_yolov8.py\", line 18, in main", (203, 213, 225)),
        ("    results = model.train(data='dataset_lunar_isro.yaml', batch=32)", (203, 213, 225)),
        ("  File \"ultralytics/engine/trainer.py\", line 498, in train", (203, 213, 225)),
        ("    self._do_train(world_size)", (203, 213, 225)),
        ("  File \"ultralytics/engine/trainer.py\", line 652, in _do_train", (203, 213, 225)),
        ("    loss, loss_items = self.model(batch)", (203, 213, 225)),
        ("  File \"torch/nn/modules/module.py\", line 1518, in _call_impl", (203, 213, 225)),
        ("    return forward_call(*args, **kwargs)", (203, 213, 225)),
        ("torch.cuda.OutOfMemoryError: CUDA out of memory. Tried to allocate 1.45 GiB (GPU 0; 8.00 GiB total capacity; 7.12 GiB already allocated; 320.00 MiB free; 7.45 GiB reserved in total by PyTorch)", (239, 68, 68)),
        ("", (255, 255, 255)),
        ("FIX: Reduce batch size to 16 or enable AMP (Automatic Mixed Precision).", (52, 211, 153))
    ]
    
    y = 60
    for l, col in lines:
        d.text((25, y), l, fill=col, font=get_font(13))
        y += 26
    img.save(OUT_DIR / "terminal_error_traceback.png", "PNG")


def gen_terminal_git_conflict():
    img = Image.new("RGB", (W, H), (15, 23, 42))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 35], fill=(30, 30, 40))
    d.text((15, 8), "Git Bash — Merge Conflict in pipeline.py", fill=(200, 200, 210), font=get_font(13))
    
    lines = [
        ("$ git pull origin main", (255, 255, 255)),
        ("Auto-merging backend/app/services/pipeline.py", (203, 213, 225)),
        ("CONFLICT (content): Merge conflict in backend/app/services/pipeline.py", (239, 68, 68)),
        ("Automatic merge failed; fix conflicts and then commit the result.", (239, 68, 68)),
        ("", (255, 255, 255)),
        ("<<<<<<< HEAD", (59, 130, 246)),
        ("    async with AsyncSessionLocal() as db:", (203, 213, 225)),
        ("        result = await process_memory(memory_id, dest_path, db)", (203, 213, 225)),
        ("=======", (245, 158, 11)),
        ("    result = await pipeline.process_memory(memory_id, dest_path)", (203, 213, 225)),
        (">>>>>>> main", (59, 130, 246)),
    ]
    y = 60
    for l, col in lines:
        d.text((25, y), l, fill=col, font=get_font(14))
        y += 28
    img.save(OUT_DIR / "terminal_git_conflict.png", "PNG")


def gen_dashboard_grafana_metrics():
    img = Image.new("RGB", (W, H), (15, 23, 42))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 45], fill=(24, 32, 47))
    d.text((25, 12), "Grafana  /  Kubernetes Cluster  /  AURA Microservices Telemetry", fill=(248, 250, 252), font=get_font(15, bold=True))
    
    # 3 Gauge boxes
    gauges = [("CPU Usage", "42.8%", (59, 130, 246), 60), ("Memory", "6.2 / 16 GB", (16, 185, 129), 460), ("Request Latency", "38.4 ms", (245, 158, 11), 860)]
    for title, val, col, gx in gauges:
        d.rectangle([gx, 80, gx + 360, 240], fill=(24, 32, 47), outline=(51, 65, 85))
        d.text((gx + 25, 100), title, fill=(148, 163, 184), font=get_font(14))
        d.text((gx + 25, 145), val, fill=col, font=get_font(28, bold=True))
        
    img.save(OUT_DIR / "dashboard_grafana_metrics.png", "PNG")


def gen_database_schema_diagram():
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 45], fill=(30, 41, 59))
    d.text((25, 12), "PostgreSQL Database Schema  •  AURA Entity-Relationship (ER) Diagram", fill=(248, 250, 252), font=get_font(15, bold=True))
    
    tables = [
        ("memories", ["id (UUID, PK)", "summary (TEXT)", "ocr_text (TEXT)", "category (VARCHAR)", "sensitivity_level (VARCHAR)", "embedding (FLOAT[])"], 80, 100),
        ("relationships", ["id (UUID, PK)", "source_memory_id (FK)", "target_memory_id (FK)", "relationship_type (VARCHAR)", "confidence (FLOAT)"], 480, 100),
        ("evidence", ["id (UUID, PK)", "memory_id (FK)", "entity_type (VARCHAR)", "exact_match (TEXT)", "bbox_x1, y1, x2, y2"], 880, 100),
    ]
    
    for tname, cols, tx, ty in tables:
        d.rectangle([tx, ty, tx + 320, ty + 380], fill=(248, 250, 252), outline=(203, 213, 225), width=2)
        d.rectangle([tx, ty, tx + 320, ty + 40], fill=(30, 58, 138))
        d.text((tx + 15, ty + 10), tname, fill=(255, 255, 255), font=get_font(15, bold=True))
        cy = ty + 60
        for col in cols:
            d.text((tx + 15, cy), col, fill=(15, 23, 42), font=get_font(13))
            cy += 35
            
    img.save(OUT_DIR / "database_schema_diagram.png", "PNG")


def gen_api_swagger_docs():
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 55], fill=(13, 148, 136))
    d.text((25, 16), "FastAPI  —  AURA Visual Memory Engine OpenAPI Swagger v2.0", fill=(255, 255, 255), font=get_font(18, bold=True))
    
    endpoints = [
        ("POST", "/api/search", "Execute hybrid dense vector & BM25 keyword query", (59, 130, 246)),
        ("POST", "/api/investigate", "Trigger multi-step agentic investigation & synthesis", (139, 92, 246)),
        ("GET", "/api/memories", "List indexed memories with pagination and category filters", (16, 185, 129)),
        ("POST", "/api/memories/upload", "Ingest new screenshot through OCR & Vision pipeline", (59, 130, 246)),
        ("GET", "/api/constellation", "Retrieve 2D force-directed memory topology graph", (16, 185, 129)),
    ]
    
    y = 90
    for meth, path, desc, col in endpoints:
        d.rectangle([60, y, W - 60, y + 65], fill=(248, 250, 252), outline=col, width=1)
        d.rectangle([75, y + 14, 165, y + 50], fill=col)
        d.text((95, y + 20), meth, fill=(255, 255, 255), font=get_font(14, bold=True))
        d.text((185, y + 20), path, fill=(15, 23, 42), font=get_font(15, bold=True))
        d.text((460, y + 22), desc, fill=(100, 116, 139), font=get_font(13))
        y += 85
        
    img.save(OUT_DIR / "api_swagger_docs.png", "PNG")


# ─── CLUSTER H: SECURITY, CREDENTIALS & AURA SHIELD ───────────────────────────

def gen_settings_wifi_password():
    img = Image.new("RGB", (W, H), (248, 250, 252))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 45], fill=(30, 41, 59))
    d.text((25, 12), "Router Administration (192.168.1.1)  •  Wireless Security Settings", fill=(248, 250, 252), font=get_font(15, bold=True))
    
    d.rectangle([80, 80, W - 80, 560], fill=(255, 255, 255), outline=(203, 213, 225))
    d.text((120, 120), "Primary Wireless Network (5 GHz Wi-Fi)", fill=(15, 23, 42), font=get_font(20, bold=True))
    
    d.text((120, 180), "Network Name (SSID):", fill=(71, 85, 105), font=get_font(15))
    d.text((360, 180), "Zenith_Home_5G", fill=(15, 23, 42), font=get_font(16, bold=True))
    
    d.text((120, 240), "Security Mode:", fill=(71, 85, 105), font=get_font(15))
    d.text((360, 240), "WPA3-Personal (AES Encryption)", fill=(15, 23, 42), font=get_font(15))
    
    d.text((120, 300), "Wi-Fi Password / Key:", fill=(71, 85, 105), font=get_font(15))
    d.rectangle([360, 290, 720, 335], fill=(254, 226, 226), outline=(239, 68, 68))
    d.text((380, 300), "SkyNet/2026/SecureKey", fill=(185, 28, 28), font=get_font(16, bold=True))
    
    d.text((120, 370), "Router IP Address: 192.168.1.1  •  MAC: B4:86:55:A1:09:42", fill=(100, 116, 139), font=get_font(13))
    img.save(OUT_DIR / "settings_wifi_password.png", "PNG")


def gen_settings_api_key():
    img = Image.new("RGB", (W, H), (15, 23, 42))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 45], fill=(30, 41, 59))
    d.text((25, 12), "OpenAI Developer Platform  /  API Keys Management", fill=(248, 250, 252), font=get_font(15, bold=True))
    
    d.rectangle([80, 80, W - 80, 520], fill=(24, 32, 47), outline=(51, 65, 85))
    d.text((120, 120), "Project API Key (Master Admin)", fill=(248, 250, 252), font=get_font(20, bold=True))
    d.text((120, 160), "Key Secret:", fill=(148, 163, 184), font=get_font(15))
    
    d.rectangle([120, 200, 820, 250], fill=(15, 23, 42), outline=(239, 68, 68))
    d.text((140, 215), "sk-proj-948194810284019284019240182409182", fill=(248, 113, 113), font=get_font(16, bold=True))
    d.text((120, 280), "Created: August 1, 2026 • Permissions: All Models, Fine-Tuning, Realtime", fill=(148, 163, 184), font=get_font(13))
    
    img.save(OUT_DIR / "settings_api_key.png", "PNG")


def gen_settings_cloud_credentials():
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 45], fill=(35, 47, 62)) # AWS Dark
    d.text((25, 12), "AWS Identity and Access Management (IAM)  /  Users  /  prajwal-admin", fill=(255, 255, 255), font=get_font(15, bold=True))
    
    d.rectangle([80, 80, W - 80, 520], fill=(248, 250, 252), outline=(203, 213, 225))
    d.text((120, 115), "Access Key Credentials", fill=(15, 23, 42), font=get_font(18, bold=True))
    d.text((120, 160), "Access Key ID:       AKIAIOSFODNN7EXAMPLE", fill=(15, 23, 42), font=get_font(15, bold=True))
    d.text((120, 205), "Secret Access Key:   wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY", fill=(220, 38, 38), font=get_font(15, bold=True))
    d.text((120, 260), "Status: Active  •  Region: ap-south-1 (Mumbai)", fill=(71, 85, 105), font=get_font(13))
    
    img.save(OUT_DIR / "settings_cloud_credentials.png", "PNG")


def gen_screenshot_stripe_keys():
    img = Image.new("RGB", (W, H), (248, 250, 252))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 45], fill=(99, 91, 255)) # Stripe Purple
    d.text((25, 12), "Stripe Dashboard  /  Developers  /  API Keys (Production Live)", fill=(255, 255, 255), font=get_font(15, bold=True))
    
    d.rectangle([80, 80, W - 80, 500], fill=(255, 255, 255), outline=(203, 213, 225))
    d.text((120, 115), "Standard Live Keys", fill=(15, 23, 42), font=get_font(18, bold=True))
    
    d.text((120, 165), "Publishable key:  pk_test_sample_stripe_publishable_key", fill=(15, 23, 42), font=get_font(14))
    d.text((120, 210), "Secret key:       sk_test_sample_mock_stripe_secret_key", fill=(220, 38, 38), font=get_font(14, bold=True))
    d.text((120, 255), "Webhook secret:   whsec_test_sample_mock_webhook_secret", fill=(220, 38, 38), font=get_font(14, bold=True))
    
    img.save(OUT_DIR / "screenshot_stripe_keys.png", "PNG")


def gen_conversation_address():
    img = Image.new("RGB", (W, H), (235, 230, 220)) # WhatsApp chat bg
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 50], fill=(7, 94, 84))
    d.text((25, 14), "WhatsApp  •  Rohan Mehta (Online)", fill=(255, 255, 255), font=get_font(16, bold=True))
    
    # Message bubble from friend
    d.rectangle([80, 120, 740, 260], fill=(255, 255, 255), outline=(210, 205, 195))
    d.text((105, 140), "Hey Prajwal! Here is the address for dinner tonight at 8 PM:", fill=(15, 23, 42), font=get_font(14))
    d.text((105, 175), "Villa 14B, Palm Meadows, Whitefield, Bangalore 560066", fill=(15, 23, 42), font=get_font(15, bold=True))
    d.text((105, 210), "Gate pass code: 4920. Call me on +91-98450-12849 when you arrive!", fill=(71, 85, 105), font=get_font(13))
    
    img.save(OUT_DIR / "conversation_address.png", "PNG")


def gen_invoice_freelance():
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([60, 40, W - 60, H - 40], fill=(255, 255, 255), outline=(203, 213, 225), width=2)
    d.text((90, 70), "INVOICE — AI Engineering Consulting", fill=(15, 23, 42), font=get_font(20, bold=True))
    d.text((90, 100), "Consultant: Prajwal Sharma  •  PAN: ABCPS1234D  •  Date: June 30, 2026", fill=(71, 85, 105), font=get_font(13))
    d.line([(90, 125), (W - 90, 125)], fill=(226, 232, 240), width=1)
    
    d.text((90, 150), "Bank Account Number: 50100294819284 (HDFC Bank Indiranagar)", fill=(220, 38, 38), font=get_font(14, bold=True))
    d.text((90, 180), "IFSC Code: HDFC0000128  •  SWIFT: HDFCINBB", fill=(71, 85, 105), font=get_font(13))
    
    d.text((90, 240), "Service Description: PyTorch YOLOv8 Model Fine-Tuning & Deployment", fill=(15, 23, 42), font=get_font(14))
    d.text((90, 280), "Total Consulting Fee Due: $4,500.00 USD (PAID)", fill=(16, 185, 129), font=get_font(16, bold=True))
    
    img.save(OUT_DIR / "invoice_freelance.png", "PNG")


# ─── CLUSTER I: REAL-WORLD VISUAL PHOTOGRAPHY & PLACES ────────────────────────

def gen_scene_mountain_view():
    # Visual-only photo rendering of snow mountain
    img = Image.new("RGB", (W, H), (135, 206, 235)) # Sky blue
    d = ImageDraw.Draw(img)
    
    # Mountain peaks
    d.polygon([(100, 600), (450, 180), (800, 600)], fill=(245, 248, 255), outline=(180, 190, 210), width=2)
    d.polygon([(550, 600), (850, 220), (1150, 600)], fill=(230, 235, 245), outline=(180, 190, 210), width=2)
    
    # Mountain rock shadows
    d.polygon([(450, 180), (800, 600), (450, 600)], fill=(120, 135, 155))
    d.polygon([(850, 220), (1150, 600), (850, 600)], fill=(110, 125, 145))
    
    # Green pine forest valley
    d.rectangle([0, 540, W, H], fill=(35, 75, 45))
    
    img.save(OUT_DIR / "scene_mountain_view.png", "PNG")


def gen_scene_red_sports_car():
    # Visual-only photo rendering of sports car
    img = Image.new("RGB", (W, H), (30, 30, 35))
    d = ImageDraw.Draw(img)
    
    # Garage floor reflection
    d.rectangle([0, 520, W, H], fill=(50, 50, 55))
    
    # Sleek Red Car Body
    d.polygon([(260, 520), (380, 380), (820, 380), (980, 480), (1020, 540), (220, 540)], fill=(220, 20, 60))
    # Windshield & Roof
    d.polygon([(420, 380), (520, 280), (740, 280), (820, 380)], fill=(15, 20, 25))
    # Wheels
    d.ellipse([320, 480, 460, 620], fill=(10, 10, 12), outline=(180, 180, 190), width=8)
    d.ellipse([780, 480, 920, 620], fill=(10, 10, 12), outline=(180, 180, 190), width=8)
    # Headlights
    d.polygon([(960, 480), (1010, 490), (980, 510)], fill=(255, 255, 220))
    
    img.save(OUT_DIR / "scene_red_sports_car.png", "PNG")


def gen_photo_watch_chronograph():
    # Visual-only photo rendering of wristwatch
    img = Image.new("RGB", (W, H), (230, 225, 220))
    d = ImageDraw.Draw(img)
    
    # Leather strap
    d.rectangle([540, 40, 740, H - 40], fill=(80, 45, 25), outline=(50, 30, 15))
    # Stainless steel watch case
    d.ellipse([460, 220, 820, 580], fill=(220, 225, 230), outline=(160, 165, 175), width=8)
    # Watch dial (Matte Black)
    d.ellipse([490, 250, 790, 550], fill=(20, 22, 25))
    # Subdials
    d.ellipse([540, 370, 600, 430], fill=(35, 38, 42))
    d.ellipse([680, 370, 740, 430], fill=(35, 38, 42))
    # Watch hands (Silver)
    d.line([(640, 400), (640, 280)], fill=(240, 240, 250), width=4)
    d.line([(640, 400), (720, 400)], fill=(240, 240, 250), width=3)
    d.line([(640, 400), (590, 460)], fill=(239, 68, 68), width=2) # Red seconds hand
    
    img.save(OUT_DIR / "photo_watch_chronograph.png", "PNG")


def gen_photo_sneakers_white():
    # Visual-only photo rendering
    img = Image.new("RGB", (W, H), (180, 180, 185)) # Concrete floor
    d = ImageDraw.Draw(img)
    
    # Left Sneaker
    d.polygon([(340, 450), (460, 320), (620, 320), (740, 440), (780, 540), (300, 540)], fill=(250, 250, 252), outline=(210, 210, 215), width=2)
    # Rubber sole
    d.rectangle([290, 530, 790, 570], fill=(240, 240, 245), outline=(180, 180, 185))
    # Laces
    for lx in range(480, 620, 25):
        d.line([(lx, 340), (lx + 15, 380)], fill=(220, 220, 225), width=3)
        
    img.save(OUT_DIR / "photo_sneakers_white.png", "PNG")


def gen_photo_office_workspace():
    # Visual-only photo rendering of dual monitor desk
    img = Image.new("RGB", (W, H), (240, 235, 225))
    d = ImageDraw.Draw(img)
    # Desk wood
    d.rectangle([0, 500, W, H], fill=(160, 120, 80))
    # Left Monitor
    d.rectangle([200, 160, 580, 480], fill=(15, 23, 42), outline=(100, 116, 139), width=4)
    d.rectangle([220, 180, 560, 460], fill=(24, 32, 47))
    # Right Monitor
    d.rectangle([620, 160, 1000, 480], fill=(15, 23, 42), outline=(100, 116, 139), width=4)
    d.rectangle([640, 180, 980, 460], fill=(24, 32, 47))
    # Desk Lamp glow on right
    d.ellipse([1040, 300, 1160, 420], fill=(255, 230, 150))
    
    img.save(OUT_DIR / "photo_office_workspace.png", "PNG")


def gen_photo_whiteboard_brainstorm():
    # Visual-only whiteboard sketch
    img = Image.new("RGB", (W, H), (245, 246, 248))
    d = ImageDraw.Draw(img)
    # Aluminum whiteboard frame
    d.rectangle([40, 40, W - 40, H - 40], outline=(180, 185, 195), width=6)
    
    # Dry-erase marker drawings
    d.ellipse([450, 280, 750, 460], outline=(0, 100, 220), width=4)
    d.text((500, 350), "AURA Brainstorm", fill=(0, 100, 220), font=get_font(20, bold=True))
    
    # Arrows and boxes
    d.rectangle([140, 140, 340, 240], outline=(220, 40, 30), width=3)
    d.text((160, 175), "Fast Multimodal OCR", fill=(220, 40, 30), font=get_font(14, bold=True))
    
    d.rectangle([840, 140, 1060, 240], outline=(30, 160, 50), width=3)
    d.text((860, 175), "Zero-Trust Privacy", fill=(30, 160, 50), font=get_font(14, bold=True))
    
    d.rectangle([500, 560, 700, 660], outline=(140, 40, 180), width=3)
    d.text((520, 595), "Graph Constellation", fill=(140, 40, 180), font=get_font(14, bold=True))
    
    img.save(OUT_DIR / "photo_whiteboard_brainstorm.png", "PNG")


def gen_scene_city_skyline():
    # Visual-only night cityscape
    img = Image.new("RGB", (W, H), (10, 12, 24))
    d = ImageDraw.Draw(img)
    # Moon
    d.ellipse([1000, 80, 1080, 160], fill=(250, 250, 220))
    
    # Building silhouettes with illuminated windows
    buildings = [(80, 260, 120), (220, 180, 140), (380, 320, 100), (500, 150, 160), (680, 240, 130), (830, 200, 140), (990, 300, 120)]
    for bx, by, bw in buildings:
        d.rectangle([bx, by, bx + bw, H], fill=(20, 25, 40))
        for wy in range(by + 20, H - 40, 30):
            for wx in range(bx + 15, bx + bw - 15, 25):
                if random.random() > 0.3:
                    d.rectangle([wx, wy, wx + 12, wy + 16], fill=(255, 220, 120))
                    
    img.save(OUT_DIR / "scene_city_skyline.png", "PNG")


# ─── CLUSTER J: PRESENTATIONS, DOCUMENTS & ADMINISTRATION ─────────────────────

def gen_presentation_isro_slide1():
    img = Image.new("RGB", (W, H), (15, 23, 42))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 40], fill=(245, 158, 11))
    d.text((25, 10), "ISRO Lunar Exploration Initiative  •  Technical Review Presentation", fill=(15, 23, 42), font=get_font(14, bold=True))
    
    d.text((80, 180), "Automated Crater Detection & Hazard Mapping", fill=(255, 255, 255), font=get_font(32, bold=True))
    d.text((80, 240), "for Autonomous Lunar Rover Navigation", fill=(6, 182, 212), font=get_font(28, bold=True))
    
    d.text((80, 360), "Principal Investigator: Prajwal Sharma", fill=(203, 213, 225), font=get_font(18))
    d.text((80, 400), "Collaborators: Space Applications Centre (SAC), ISRO & Zenith AI Research", fill=(148, 163, 184), font=get_font(15))
    d.text((80, 440), "Date: August 2026", fill=(148, 163, 184), font=get_font(15))
    
    img.save(OUT_DIR / "presentation_isro_slide1.png", "PNG")


def gen_presentation_isro_results():
    img = Image.new("RGB", (W, H), (15, 23, 42))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 40], fill=(30, 41, 59))
    d.text((25, 10), "ISRO Technical Review  /  Slide 4: Precision-Recall & Benchmark Validation", fill=(203, 213, 225), font=get_font(14))
    
    d.text((60, 70), "Experimental Results on Simulated South Pole Lunar Imagery", fill=(255, 255, 255), font=get_font(22, bold=True))
    
    d.rectangle([60, 120, 580, 460], fill=(24, 32, 47), outline=(51, 65, 85))
    d.text((80, 140), "Detection Metrics by Crater Diameter", fill=(245, 158, 11), font=get_font(16, bold=True))
    metrics = [
        ("Diameter > 5m:", "mAP@50: 94.8%  •  Recall: 96.2%"),
        ("Diameter 2m - 5m:", "mAP@50: 91.4%  •  Recall: 93.0%"),
        ("Diameter < 2m:", "mAP@50: 84.6%  •  Recall: 87.2%"),
        ("Overall mAP50-95:", "56.2% (Target: 50.0%)"),
    ]
    my = 190
    for k, v in metrics:
        d.text((80, my), k, fill=(255, 255, 255), font=get_font(14, bold=True))
        d.text((280, my), v, fill=(52, 211, 153), font=get_font(14))
        my += 45
        
    img.save(OUT_DIR / "presentation_isro_results.png", "PNG")


def gen_document_privacy_policy():
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([60, 40, W - 60, H - 40], fill=(255, 255, 255), outline=(203, 213, 225), width=2)
    d.text((90, 70), "AURA Zero-Trust Security & Privacy Policy", fill=(15, 23, 42), font=get_font(20, bold=True))
    d.text((90, 100), "Version 2.0  •  Effective: August 2026", fill=(71, 85, 105), font=get_font(13))
    d.line([(90, 120), (W - 90, 120)], fill=(226, 232, 240), width=1)
    
    d.text((90, 145), "1. On-Device Zero-Trust Redaction", fill=(15, 23, 42), font=get_font(15, bold=True))
    d.text((90, 175), "All screenshots containing passwords, API tokens, and confidential PII are automatically tagged as CRITICAL.", fill=(51, 65, 85), font=get_font(13))
    d.text((90, 200), "These memories are masked by default across search queries, galleries, and graph views.", fill=(51, 65, 85), font=get_font(13))
    
    img.save(OUT_DIR / "document_privacy_policy.png", "PNG")


def gen_education_timetable():
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 45], fill=(30, 41, 59))
    d.text((25, 12), "Academic Timetable  •  M.Tech AI & Robotics — Autumn Semester 2026", fill=(248, 250, 252), font=get_font(15, bold=True))
    
    days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    slots = ["09:00 - 10:30", "11:00 - 12:30", "14:00 - 16:30 (Lab)", "17:00 - 18:00"]
    
    d.rectangle([80, 80, W - 80, 540], fill=(248, 250, 252), outline=(203, 213, 225))
    for i, day in enumerate(days):
        d.text((120 + i * 220, 100), day, fill=(15, 23, 42), font=get_font(16, bold=True))
    d.line([(80, 130), (W - 80, 130)], fill=(203, 213, 225), width=2)
    
    classes = [
        ("Computer Vision (LH-3)", 0, 0), ("Deep Learning (LH-1)", 1, 0), ("Autonomous Robotics Lab", 0, 2),
        ("Digital Signal Proc (LH-2)", 2, 0), ("Optimization (LH-4)", 3, 0), ("GPU Computing Lab", 3, 2)
    ]
    for cname, day_idx, slot_idx in classes:
        x = 100 + day_idx * 220
        y = 150 + slot_idx * 90
        d.rectangle([x, y, x + 190, y + 60], fill=(224, 231, 255), outline=(147, 197, 253))
        d.text((x + 10, y + 15), cname, fill=(30, 58, 138), font=get_font(12, bold=True))
        
    img.save(OUT_DIR / "education_timetable.png", "PNG")


def gen_business_card_synthetic():
    img = Image.new("RGB", (W, H), (240, 238, 230))
    d = ImageDraw.Draw(img)
    
    # Modern Business Card
    d.rectangle([280, 180, 1000, 620], fill=(255, 255, 255), outline=(200, 195, 185), width=2)
    d.rectangle([280, 180, 340, 620], fill=(217, 119, 87)) # Terracotta left stripe
    
    d.text((380, 240), "PRAJWAL SHARMA", fill=(31, 29, 26), font=get_font(24, bold=True))
    d.text((380, 280), "Principal AI & Computer Vision Architect", fill=(184, 92, 66), font=get_font(16, bold=True))
    d.line([(380, 320), (940, 320)], fill=(222, 217, 208), width=1)
    
    d.text((380, 350), "Zenith Intelligence Labs  •  Bangalore, India", fill=(111, 106, 99), font=get_font(14))
    d.text((380, 390), "Email: prajwal.sharma@zenith-ai.io", fill=(31, 29, 26), font=get_font(14))
    d.text((380, 430), "Web: https://zenith-ai.io  •  GitHub: @prajwal-sharma", fill=(31, 29, 26), font=get_font(14))
    
    img.save(OUT_DIR / "business_card_synthetic.png", "PNG")


# ─── CLUSTER K: UI & DIGITAL APPLICATION WORKSPACES ───────────────────────────

def gen_ui_dark_dashboard():
    img = Image.new("RGB", (W, H), (15, 23, 42))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 50], fill=(30, 41, 59))
    d.text((25, 16), "Stripe Metrics  /  Monthly Recurring Revenue (MRR)", fill=(248, 250, 252), font=get_font(16, bold=True))
    
    cards = [("Current MRR", "$48,920", (59, 130, 246), 60), ("Active Subscribers", "1,420", (16, 185, 129), 460), ("Churn Rate", "1.12%", (245, 158, 11), 860)]
    for title, val, col, cx in cards:
        d.rectangle([cx, 80, cx + 360, 200], fill=(24, 32, 47), outline=(51, 65, 85))
        d.text((cx + 25, 100), title, fill=(148, 163, 184), font=get_font(14))
        d.text((cx + 25, 135), val, fill=col, font=get_font(28, bold=True))
        
    img.save(OUT_DIR / "ui_dark_dashboard.png", "PNG")


def gen_ui_figma_design_canvas():
    img = Image.new("RGB", (W, H), (44, 44, 44))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 40], fill=(30, 30, 30))
    d.text((20, 10), "Figma — AURA 2.0 Mobile App Design System (Page 1)", fill=(255, 255, 255), font=get_font(14))
    
    # 3 Mobile Screen frames
    for i, title in enumerate(["Home Search", "Memory Detail", "Shield Audit"]):
        fx = 120 + i * 360
        d.rectangle([fx, 80, fx + 300, 680], fill=(247, 244, 238), outline=(100, 100, 100), width=2)
        d.text((fx + 20, 100), title, fill=(31, 29, 26), font=get_font(16, bold=True))
        d.rectangle([fx + 20, 140, fx + 280, 200], fill=(255, 255, 255), outline=(222, 217, 208))
        d.rectangle([fx + 20, 220, fx + 280, 360], fill=(239, 236, 230))
        
    img.save(OUT_DIR / "ui_figma_design_canvas.png", "PNG")


def gen_screenshot_aura_search():
    img = Image.new("RGB", (W, H), (247, 244, 238))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 45], fill=(239, 236, 230))
    d.text((25, 14), "localhost:3000  —  AURA Visual Memory Engine", fill=(31, 29, 26), font=get_font(14, bold=True))
    
    d.text((360, 160), "Ask your visual memory.", fill=(31, 29, 26), font=get_font(36))
    d.rectangle([340, 240, 940, 300], fill=(255, 255, 255), outline=(217, 119, 87), width=2)
    d.text((360, 258), "Find the receipt for my laptop", fill=(31, 29, 26), font=get_font(16))
    
    img.save(OUT_DIR / "screenshot_aura_search.png", "PNG")


def gen_ui_music_player():
    img = Image.new("RGB", (W, H), (18, 18, 18))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 50], fill=(0, 0, 0))
    d.text((25, 16), "Spotify  •  Focus & Deep Work Coding Session", fill=(29, 185, 84), font=get_font(16, bold=True))
    
    # Album Art
    d.rectangle([120, 140, 480, 500], fill=(40, 30, 60))
    d.ellipse([240, 260, 360, 380], fill=(139, 92, 246))
    
    d.text((540, 240), "Lofi Beats for Neural Network Training", fill=(255, 255, 255), font=get_font(24, bold=True))
    d.text((540, 285), "Chillhop Music  •  Focus Flow 2026", fill=(179, 179, 179), font=get_font(16))
    
    # Playback bar
    d.line([(540, 360), (W - 120, 360)], fill=(83, 83, 83), width=4)
    d.line([(540, 360), (840, 360)], fill=(29, 185, 84), width=4)
    d.text((540, 380), "2:14", fill=(179, 179, 179), font=get_font(12))
    d.text((W - 160, 380), "3:45", fill=(179, 179, 179), font=get_font(12))
    
    img.save(OUT_DIR / "ui_music_player.png", "PNG")


# ─── MASTER GENERATOR FUNCTION ───────────────────────────────────────────────

def generate_all_screenshots():
    print(f"Generating 67 multimodal screenshots in {OUT_DIR}...", flush=True)
    generators = [
        gen_research_yolo_paper,
        gen_chart_training_loss,
        gen_chart_confusion_matrix,
        gen_code_yolo_training,
        gen_terminal_training_output,
        gen_research_vit_paper,
        gen_research_transformer_diagram,
        gen_research_dataset_info,
        gen_product_photo_black_headphones,
        gen_product_comparison_headphones,
        gen_shopping_headphones_reviews,
        gen_shopping_headphones_price_history,
        gen_shopping_cart_headphones,
        gen_receipt_headphones_amazon,
        gen_product_photo_silver_laptop,
        gen_product_photo_red_laptop,
        gen_product_comparison_laptops,
        gen_shopping_wishlist,
        gen_receipt_laptop_amazon,
        gen_invoice_monitor,
        gen_travel_bangalore_goa_flight,
        gen_travel_goa_hotel,
        gen_map_route_restaurant,
        gen_scene_beach_sunset,
        gen_scene_rooftop_restaurant,
        gen_map_restaurant_goa,
        gen_receipt_cab_goa,
        gen_food_photo_truffle_pizza,
        gen_food_photo_mushroom_pasta,
        gen_food_photo_japanese_ramen,
        gen_recipe_mushroom_pasta,
        gen_menu_italian_bistro,
        gen_receipt_grocery,
        gen_diagram_rlc_circuit,
        gen_diagram_logic_gates,
        gen_notes_handwritten_math,
        gen_diagram_neural_network,
        gen_diagram_aura_architecture,
        gen_code_auth_service,
        gen_github_issue_auth_bug,
        gen_terminal_error_traceback,
        gen_terminal_git_conflict,
        gen_dashboard_grafana_metrics,
        gen_database_schema_diagram,
        gen_api_swagger_docs,
        gen_settings_wifi_password,
        gen_settings_api_key,
        gen_settings_cloud_credentials,
        gen_screenshot_stripe_keys,
        gen_conversation_address,
        gen_invoice_freelance,
        gen_scene_mountain_view,
        gen_scene_red_sports_car,
        gen_photo_watch_chronograph,
        gen_photo_sneakers_white,
        gen_photo_office_workspace,
        gen_photo_whiteboard_brainstorm,
        gen_scene_city_skyline,
        gen_presentation_isro_slide1,
        gen_presentation_isro_results,
        gen_document_privacy_policy,
        gen_education_timetable,
        gen_business_card_synthetic,
        gen_ui_dark_dashboard,
        gen_ui_figma_design_canvas,
        gen_screenshot_aura_search,
        gen_ui_music_player,
    ]
    for fn in generators:
        fn()
    print(f"Generated {len(generators)} screenshots successfully!", flush=True)


if __name__ == "__main__":
    generate_all_screenshots()
