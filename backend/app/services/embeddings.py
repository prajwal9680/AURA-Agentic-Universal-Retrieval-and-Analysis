"""
AURA — Embedding Service
Uses sentence-transformers (all-MiniLM-L6-v2) for local semantic embeddings.
No API key required. GPU-accelerated when available.
"""
import logging
import struct
import numpy as np
from typing import Optional, Any, List, Union, Dict

from app.config import settings

logger = logging.getLogger(__name__)

_model = None


def _get_model():
    """Lazy-load the embedding model."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer(settings.embedding_model)
            logger.info(f"Embedding model loaded: {settings.embedding_model}")
        except Exception as e:
            logger.error(f"Embedding model load failed: {e}")
            _model = None
    return _model


def build_memory_text(
    summary: str = "",
    ocr_text: str = "",
    entities: list = None,
    topics: list = None,
    category: str = "other",
    application: str = "",
    window_title: str = "",
    clipboard_context: str = "",
    visual_summary: str = "",
    visual_objects: list = None,
    document_type: str = "",
    visual_details: dict = None,
) -> str:
    """
    Construct canonical multimodal semantic representation for embedding.
    Explicitly balances true visual layout/understanding and supporting OCR text.
    """
    entities = entities or []
    topics = topics or []
    visual_objects = visual_objects or []
    visual_details = visual_details or {}

    parts = []

    # 1. Category and Document Format
    if category and category != "other":
        parts.append(f"Category: {category}")
    if document_type:
        parts.append(f"Type: {document_type.replace('_', ' ')}")

    # 2. True Multimodal Visual Understanding
    v_sum = visual_summary or summary
    if v_sum:
        parts.append(f"Visual Scene: {v_sum}")

    if visual_objects:
        parts.append(f"Visible Objects: {', '.join(visual_objects[:8])}")

    # Visual Theme / Structure
    if isinstance(visual_details, dict):
        layout = visual_details.get("layout_structure")
        theme = visual_details.get("theme")
        if layout:
            parts.append(f"Layout: {layout}")
        if theme and theme != "light":
            parts.append(f"Theme: {theme} mode")

    # 3. Context & Topics
    if topics:
        parts.append(f"Topics: {', '.join(topics[:8])}")
    if entities:
        parts.append(f"Entities: {', '.join(entities[:10])}")

    # 4. OS & Environment Context
    if application:
        parts.append(f"Application: {application}")
    if window_title:
        parts.append(f"Window: {window_title}")
    if clipboard_context:
        parts.append(f"Clipboard: {clipboard_context[:150]}")

    # 5. Supporting OCR Text (Capped to prevent noise from dominating diagrams/visuals)
    if ocr_text:
        cleaned_ocr = " ".join(ocr_text.split())[:350]
        if cleaned_ocr:
            parts.append(f"Text: {cleaned_ocr}")

    return " | ".join(parts)


def embed_text(text: str) -> Optional[np.ndarray]:
    """
    Embed a single text string. Returns float32 numpy array (384-dim).
    Returns None if model unavailable.
    """
    model = _get_model()
    if model is None or not text:
        return None
    try:
        vec = model.encode(text, normalize_embeddings=True, convert_to_numpy=True)
        return vec.astype(np.float32)
    except Exception as e:
        logger.error(f"Embedding failed: {e}")
        return None


def embed_memory(
    summary: str = "",
    ocr_text: str = "",
    entities: list = None,
    topics: list = None,
    category: str = "other",
    application: str = "",
    window_title: str = "",
    clipboard_context: str = "",
    visual_summary: str = "",
    visual_objects: list = None,
    document_type: str = "",
    visual_details: dict = None,
) -> Optional[np.ndarray]:
    """Embed a full multimodal memory object into the dense vector space."""
    text = build_memory_text(
        summary=summary,
        ocr_text=ocr_text,
        entities=entities,
        topics=topics,
        category=category,
        application=application,
        window_title=window_title,
        clipboard_context=clipboard_context,
        visual_summary=visual_summary,
        visual_objects=visual_objects,
        document_type=document_type,
        visual_details=visual_details,
    )
    return embed_text(text)


def embedding_to_hex(vec: np.ndarray) -> str:
    """Serialize float32 numpy array to hex string for SQLite TEXT storage."""
    return vec.astype(np.float32).tobytes().hex()


import json
from functools import lru_cache

@lru_cache(maxsize=8192)
def hex_to_embedding(val: Any) -> Optional[np.ndarray]:
    """
    Robust embedding deserializer with LRU vector caching.
    Supports JSON list strings (e.g. '[0.1, -0.2, ...]'), binary hex strings,
    raw float arrays, and lists.
    """
    if not val:
        return None
    if isinstance(val, np.ndarray):
        arr = val.astype(np.float32)
        arr.flags.writeable = False
        return arr
    if isinstance(val, (list, tuple)):
        arr = np.array(val, dtype=np.float32)
        arr.flags.writeable = False
        return arr
    if isinstance(val, str):
        val_str = val.strip()
        if val_str.startswith("[") and val_str.endswith("]"):
            try:
                arr = np.array(json.loads(val_str), dtype=np.float32)
                arr.flags.writeable = False
                return arr
            except Exception:
                pass
        try:
            raw = bytes.fromhex(val_str)
            arr = np.frombuffer(raw, dtype=np.float32)
            arr.flags.writeable = False
            return arr
        except Exception:
            pass
    return None


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two normalized vectors."""
    if a is None or b is None:
        return 0.0
    try:
        dot = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(dot / (norm_a * norm_b))
    except Exception:
        return 0.0


def batch_cosine_similarities(query_vec: np.ndarray, memory_vecs: list) -> np.ndarray:
    """
    Vectorized cosine similarity of query vs many memories.
    memory_vecs: list of (memory_id, np.ndarray) tuples
    Returns parallel array of float scores.
    """
    if not memory_vecs or query_vec is None:
        return np.zeros(len(memory_vecs))

    try:
        valid_vecs = [v for _, v in memory_vecs if v is not None and isinstance(v, np.ndarray)]
        if len(valid_vecs) != len(memory_vecs):
            # Fallback if any vector in the list is invalid
            scores = []
            for _, v in memory_vecs:
                scores.append(cosine_similarity(query_vec, v) if v is not None else 0.0)
            return np.array(scores, dtype=float)

        matrix = np.stack(valid_vecs, axis=0)  # (N, dim)
        query_norm = query_vec / (np.linalg.norm(query_vec) + 1e-10)
        matrix_norm = matrix / (np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-10)
        scores = matrix_norm @ query_norm  # (N,)
        return scores.astype(float)
    except Exception as e:
        logger.error(f"Batch similarity failed: {e}")
        return np.zeros(len(memory_vecs))

