"""
AURA — Production Adaptive OCR Pipeline
Implements:
1. EXIF orientation correction.
2. Adaptive multi-scale image preprocessing (dark/light UI detection, contrast enhancement, sharpening).
3. Structured OCR extraction with bounding boxes, line indexes, block groupings, and confidence scores.
4. Conservative deterministic OCR dictionary cleaning preserving technical strings (URLs, code, API keys, hashes, paths).
5. Fast, robust fallback mechanisms.
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional

logger = logging.getLogger(__name__)

_reader = None


def _get_reader():
    """Lazy-load EasyOCR reader with GPU acceleration when available."""
    global _reader
    if _reader is None:
        try:
            import torch
            try:
                torch.set_num_threads(8)
            except Exception:
                pass
            import easyocr
            has_cuda = torch.cuda.is_available()
            _reader = easyocr.Reader(["en"], gpu=has_cuda, verbose=False)
            logger.info(f"EasyOCR initialized (GPU={has_cuda}, threads=8)")
        except Exception as e:
            logger.error(f"EasyOCR init failed: {e}")
            _reader = None
    return _reader


# ─── 1. Adaptive Image Preprocessing ──────────────────────────────────────────

def preprocess_for_ocr(image_path: str) -> Tuple[Any, float]:
    """
    Preprocess image for OCR without altering original file.
    Returns:
        (numpy_array_for_ocr, scale_factor)
    """
    from PIL import Image, ImageOps, ImageEnhance, ImageFilter, ImageStat
    import numpy as np

    img = Image.open(image_path)
    
    # 1. Correct EXIF orientation
    try:
        img = ImageOps.exif_transpose(img)
    except Exception:
        pass

    # Ensure RGB
    if img.mode != "RGB":
        img = img.convert("RGB")

    orig_w, orig_h = img.size
    scale = 1.0

    # 2. Adaptive scaling for small/large fonts
    # Small screenshots (< 1100px) benefit from high-quality upscaling
    if orig_w < 1100:
        scale = 1.4
        new_w = int(orig_w * scale)
        new_h = int(orig_h * scale)
        img_proc = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    elif orig_w > 1600:
        scale = 1600.0 / orig_w
        new_w = 1600
        new_h = int(orig_h * scale)
        img_proc = img.resize((new_w, new_h), Image.Resampling.BILINEAR)
    else:
        img_proc = img.copy()

    # 3. Analyze brightness & contrast
    grayscale = img_proc.convert("L")
    stat = ImageStat.Stat(grayscale)
    mean_brightness = stat.mean[0]  # 0 (dark) to 255 (bright)
    stddev_contrast = stat.stddev[0]

    # 4. Enhance contrast if washed out
    if stddev_contrast < 45:
        enhancer = ImageEnhance.Contrast(img_proc)
        img_proc = enhancer.enhance(1.35)
    elif mean_brightness > 220:
        # Very bright document/receipt: slightly deepen blacks
        enhancer = ImageEnhance.Contrast(img_proc)
        img_proc = enhancer.enhance(1.2)

    # 5. Mild sharpening to crisp up text edges
    img_proc = img_proc.filter(ImageFilter.UnsharpMask(radius=1, percent=120, threshold=3))

    return np.array(img_proc), scale


# ─── 2. Structured OCR Extraction ─────────────────────────────────────────────

def extract_text(image_path: str) -> dict:
    """
    Extract structured, cleaned text from an image with bounding boxes and line confidences.
    Returns:
        {
            "raw": str,
            "cleaned": str,
            "confidence": float,
            "blocks": list of {text, confidence, bbox, line_index, block_index},
            "entities": dict of {emails, urls, phones, prices, dates, api_keys, passwords, credit_cards}
        }
    """
    reader = _get_reader()
    if reader is None:
        return _fallback_extraction(image_path)

    try:
        img_arr, scale = preprocess_for_ocr(image_path)
        
        # Run EasyOCR with detail=1 for bounding boxes and confidence scores
        raw_results = reader.readtext(
            img_arr,
            detail=1,
            paragraph=False,
            batch_size=8,
            min_size=8,
            text_threshold=0.25,
            low_text=0.25,
            link_threshold=0.35,
        )

        if not raw_results:
            return {
                "raw": "",
                "cleaned": "",
                "confidence": 0.0,
                "blocks": [],
                "entities": _extract_entities(""),
            }

        # Structure OCR entries with scaled coordinates
        structured_blocks = []
        raw_lines = []
        confidences = []

        # Sort blocks by vertical position (reading order: top to bottom, left to right)
        def get_top_left(item):
            bbox = item[0]  # [[x1,y1], [x2,y1], [x2,y2], [x1,y2]]
            y_top = min(p[1] for p in bbox)
            x_left = min(p[0] for p in bbox)
            return (y_top, x_left)

        sorted_results = sorted(raw_results, key=get_top_left)

        current_block = 0
        last_y = -100

        for line_idx, (bbox, text, conf) in enumerate(sorted_results):
            text_str = str(text).strip()
            if not text_str or conf < 0.2:
                continue

            # Scale bounding box back to original image space
            inv_scale = 1.0 / (scale if scale > 0 else 1.0)
            xs = [p[0] * inv_scale for p in bbox]
            ys = [p[1] * inv_scale for p in bbox]
            x1, y1, x2, y2 = min(xs), min(ys), max(xs), max(ys)

            # Block grouping heuristic
            if last_y > 0 and abs(y1 - last_y) > 40:
                current_block += 1
            last_y = y2

            structured_blocks.append({
                "text": text_str,
                "confidence": round(float(conf), 3),
                "bbox": [round(x1, 1), round(y1, 1), round(x2, 1), round(y2, 1)],
                "line_index": line_idx,
                "block_index": current_block,
            })
            raw_lines.append(text_str)
            confidences.append(float(conf))

        raw_text = "\n".join(raw_lines)
        cleaned_text = clean_ocr_text(raw_text)
        avg_confidence = round(sum(confidences) / len(confidences), 3) if confidences else 0.0
        entities = _extract_entities(cleaned_text)

        return {
            "raw": raw_text,
            "cleaned": cleaned_text,
            "confidence": avg_confidence,
            "blocks": structured_blocks,
            "entities": entities,
        }

    except Exception as e:
        logger.error(f"Production OCR failed for {image_path}: {e}", exc_info=True)
        return _fallback_extraction(image_path)


# ─── 3. Deterministic OCR Text Cleaning ───────────────────────────────────────

# Conservative dictionary of common OCR scan misrecognitions
OCR_CORRECTIONS = {
    # System & Architecture terms
    "syslem": "System",
    "archileclure": "Architecture",
    "upoad": "Upload",
    "extracton": "Extraction",
    "enbty": "Entity",
    "sensitivty": "Sensitivity",
    "classifcation": "Classification",
    "uncerstanding": "Understanding",
    "temporai": "temporal",
    "solite": "SQLite",
    "sqlite3": "SQLite",
    
    # UI / Security / Hardware terms
    "sennty": "Security",
    "mede": "Mode",
    "ercrypted": "Encrypted",
    "netwvork": "Network",
    "mame": "Name",
    "zcnith": "Zenith",
    "psk": "PSK",
    "wpa2-psk": "WPA2-PSK",
    "wpa3-psk": "WPA3-PSK",
    "redential": "Credential",
    "passwrd": "Password",
    "pattem": "Pattern",
    "recogntion": "Recognition",
    "unversity": "University",
    "restuarant": "Restaurant",
    "congnitive": "Cognitive",
    "reciept": "Receipt",
    "invoce": "Invoice",
}

TECHNICAL_TOKEN_RE = re.compile(
    r"^(?:https?://|[a-z0-9_\-\.]+\.[a-z]{2,}|/[a-z0-9_\-/]+|\\[a-z0-9_\-\\]+|[0-9a-f]{16,}|[0-9]+\.[0-9]+|[A-Za-z0-9_]+=[^\s]+|[a-z0-9_\-\+]+@[a-z0-9_\-\.]+)$",
    re.IGNORECASE,
)


def clean_ocr_text(text: str) -> str:
    """
    Conservative deterministic OCR cleaner.
    Corrects frequent OCR artifacts while strictly preserving technical strings,
    URLs, file paths, code identifiers, API keys, and hashes.
    """
    if not text:
        return ""

    lines = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        # Split words while preserving punctuation boundaries
        tokens = line.split(" ")
        cleaned_tokens = []

        for token in tokens:
            stripped = token.strip(".,;:()[]{}\"'`")
            lower_token = stripped.lower()

            # Preserve technical tokens unchanged
            if TECHNICAL_TOKEN_RE.match(stripped) or any(c in stripped for c in ["_", "/", "\\", ":", "=", "@"]):
                cleaned_tokens.append(token)
                continue

            # Check conservative dictionary
            if lower_token in OCR_CORRECTIONS:
                replacement = OCR_CORRECTIONS[lower_token]
                # Preserve original capitalization if titlecased or uppercased
                if stripped.isupper():
                    replacement = replacement.upper()
                elif stripped.istitle():
                    replacement = replacement.title()
                
                # Replace token while keeping original boundary punctuation
                fixed_token = token.replace(stripped, replacement)
                cleaned_tokens.append(fixed_token)
            else:
                cleaned_tokens.append(token)

        lines.append(" ".join(cleaned_tokens))

    return "\n".join(lines)


# ─── 4. Structured Entity Extraction ──────────────────────────────────────────

def _extract_entities(text: str) -> dict:
    """
    Deterministic entity extraction from OCR text for AURA Shield and Search index.
    """
    entities = {
        "emails": [],
        "urls": [],
        "phones": [],
        "prices": [],
        "dates": [],
        "api_keys": [],
        "passwords": [],
        "credit_cards": [],
    }

    if not text:
        return entities

    # Emails
    entities["emails"] = list(set(re.findall(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", text
    )))

    # URLs
    entities["urls"] = list(set(re.findall(
        r"https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)",
        text,
    )))

    # Phones (Indian + International)
    entities["phones"] = list(set(re.findall(
        r"(?:\+91[\-\s]?)?[6-9]\d{9}|\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b", text
    )))

    # Prices / Currency amounts
    entities["prices"] = list(set(re.findall(
        r"(?:₹|Rs\.?|\$|€|£)\s*[\d,]+(?:\.\d{2})?|\b[\d,]+(?:\.\d{2})?\s*(?:INR|USD|EUR|GBP)\b",
        text,
        re.IGNORECASE,
    )))

    # Dates
    entities["dates"] = list(set(re.findall(
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b",
        text,
        re.IGNORECASE,
    )))

    # API Keys / Tokens
    entities["api_keys"] = list(set(re.findall(
        r"\b(?:AIza[0-9A-Za-z\-_]{35}|AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{36,}|sk-[A-Za-z0-9]{32,}|AQ\.[A-Za-z0-9_\-]{20,})\b",
        text,
    )))

    return entities


def _fallback_extraction(image_path: str) -> dict:
    """Safe fallback when EasyOCR is unavailable."""
    try:
        from PIL import Image
        with Image.open(image_path) as img:
            w, h = img.size
        return {
            "raw": f"[Image dimensions: {w}x{h}]",
            "cleaned": f"[Image dimensions: {w}x{h}]",
            "confidence": 0.0,
            "blocks": [],
            "entities": _extract_entities(""),
        }
    except Exception:
        return {"raw": "", "cleaned": "", "confidence": 0.0, "blocks": [], "entities": _extract_entities("")}
