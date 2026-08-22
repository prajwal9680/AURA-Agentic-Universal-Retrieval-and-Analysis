"""
AURA — Hybrid Search Service
Combines semantic similarity + BM25 text score + entity overlap + category + temporal.
"""
import math
import logging
import json
import re
from datetime import datetime, timezone
from typing import Optional
import numpy as np

from app.config import settings
from app.services.embeddings import (
    embed_text, hex_to_embedding, batch_cosine_similarities
)

logger = logging.getLogger(__name__)


# ─── Stop words & tokenization ────────────────────────────────────────────────
STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "as", "at", "be", "because", "been", "before", "being", "below",
    "between", "both", "but", "by", "can", "did", "do", "does", "doing", "don",
    "down", "during", "each", "few", "find", "for", "from", "further", "get", "had",
    "has", "have", "having", "he", "her", "here", "hers", "herself", "him", "himself",
    "his", "how", "i", "if", "in", "into", "is", "it", "its", "itself", "just", "me",
    "more", "most", "my", "myself", "no", "nor", "not", "now", "of", "off", "on",
    "once", "only", "or", "other", "our", "ours", "ourselves", "out", "over", "own",
    "same", "she", "should", "show", "so", "some", "such", "than", "that", "the",
    "their", "theirs", "them", "themselves", "then", "there", "these", "they",
    "this", "those", "through", "to", "too", "under", "until", "up", "very", "was",
    "we", "were", "what", "when", "where", "which", "while", "who", "whom", "why",
    "will", "with", "you", "your", "yours", "yourself", "yourselves"
}

from functools import lru_cache

@lru_cache(maxsize=2048)
def _tokenize_cached(text: str) -> tuple:
    clean = re.sub(r"[^a-zA-Z0-9]", " ", text.lower())
    return tuple(t for t in clean.split() if len(t) >= 2)


def _tokenize(text: str, remove_stopwords: bool = False) -> list:
    tokens = list(_tokenize_cached(text))
    if remove_stopwords:
        filtered = [t for t in tokens if t not in STOP_WORDS]
        return filtered if filtered else tokens
    return tokens


GENERIC_INTENT_WORDS = {
    "receipt", "invoice", "photo", "picture", "screenshot", "image",
    "file", "document", "doc", "page", "app", "screen"
}

def _bm25_score(query_tokens: list, doc_text: str, avg_doc_len: float = 200.0) -> float:
    """Lightweight BM25-inspired scoring with subject term weighting."""
    k1, b = 1.5, 0.75
    doc_tokens = _tokenize(doc_text)
    if not doc_tokens or not query_tokens:
        return 0.0
    doc_len = len(doc_tokens)
    freq = {}
    for tok in doc_tokens:
        freq[tok] = freq.get(tok, 0) + 1

    score = 0.0
    total_weight = 0.0
    for qt in query_tokens:
        token_weight = 0.5 if qt in GENERIC_INTENT_WORDS else 2.0
        total_weight += token_weight
        if qt in freq:
            tf = freq[qt]
            score += token_weight * ((tf * (k1 + 1)) / (tf + k1 * (1 - b + b * doc_len / avg_doc_len)))

    return min(score / max(total_weight, 1.0), 1.0)


# ─── Entity overlap ───────────────────────────────────────────────────────────

def _jaccard(a: list, b: list) -> float:
    if not a or not b:
        return 0.0
    sa = set(x.lower() for x in a)
    sb = set(x.lower() for x in b)
    inter = sa & sb
    union = sa | sb
    return len(inter) / len(union) if union else 0.0


# ─── Temporal score ───────────────────────────────────────────────────────────

def _temporal_score(created_at: datetime) -> float:
    """Recency bias: decays over 30 days."""
    if not created_at:
        return 0.5
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    age_days = max((now - created_at).total_seconds() / 86400, 0)
    return math.exp(-age_days / 30.0)


# ─── Main hybrid scoring ──────────────────────────────────────────────────────

def hybrid_score(
    semantic_score: float,
    query_tokens: list,
    memory_ocr: str,
    query_entities: list,
    memory_entities: list,
    query_category: str,
    memory_category: str,
    created_at: datetime,
) -> dict:
    """
    Compute the final hybrid relevance score.

    Weights:
      semantic  0.45
      text      0.25
      entity    0.15
      category  0.10
      temporal  0.05
    """
    w = settings
    text_sc = _bm25_score(query_tokens, memory_ocr or "")
    entity_sc = _jaccard(query_entities, memory_entities)
    
    # Category cluster matching
    cat_sc = 0.0
    if query_category and memory_category:
        if query_category == memory_category:
            cat_sc = 1.0
        elif {query_category, memory_category} <= {"receipt", "invoice", "finance", "shopping"}:
            cat_sc = 0.85
        elif {query_category, memory_category} <= {"code", "terminal", "ide"}:
            cat_sc = 0.85
        elif {query_category, memory_category} <= {"research", "presentation", "document", "education"}:
            cat_sc = 0.85
        elif {query_category, memory_category} <= {"credentials", "settings"}:
            cat_sc = 0.85

    temp_sc = _temporal_score(created_at)

    final = (
        w.weight_semantic * semantic_score
        + w.weight_text * text_sc
        + w.weight_entity * entity_sc
        + w.weight_category * cat_sc
        + w.weight_temporal * temp_sc
    )

    return {
        "final": round(min(final, 1.0), 4),
        "semantic": round(semantic_score, 4),
        "text": round(text_sc, 4),
        "entity": round(entity_sc, 4),
        "category": round(cat_sc, 4),
        "temporal": round(temp_sc, 4),
    }


# ─── Query parser ─────────────────────────────────────────────────────────────

def parse_query(query: str) -> dict:
    """
    Extract structured signals from a natural-language query.
    Returns tokens, category hint, visual format hint, potential entities.
    """
    q_lower = query.lower()
    tokens = _tokenize(query, remove_stopwords=True)

    # Category hint from query keywords
    category_hints = {
        "receipt": ["receipt", "order", "purchase", "bought", "buy", "paid", "bill", "swiggy", "amazon invoice"],
        "recipe": ["recipe", "cook", "ingredient", "dish", "food", "eat", "mushroom", "pasta", "risotto", "ramen"],
        "code": ["code", "script", "function", "debug", "python", "yolo", "pytorch", "editor", "vscode", "computer vision", "cv project", "training"],
        "research": ["research", "paper", "study", "arxiv", "abstract", "satellite", "isro", "transformer", "neural network"],
        "credentials": ["password", "wifi", "wi-fi", "ssid", "api key", "token", "credential", "secret", "wpa"],
        "travel": ["hotel", "flight", "trip", "travel", "booking", "transit"],
        "map": ["map", "location", "route", "navigation", "directions", "mumbai"],
        "conversation": ["address", "friend", "chat", "whatsapp", "slack", "message", "dinner"],
        "finance": ["invoice", "payment", "bank", "tax", "finance", "gst"],
        "terminal": ["terminal", "command", "traceback", "shell", "npm", "pip", "cuda", "out of memory", "error"],
        "chart": ["graph", "chart", "loss", "accuracy", "curve", "confusion matrix", "plot", "metrics", "performance", "tsne"],
        "diagram": ["diagram", "architecture", "flowchart", "schema", "neural network", "circuit", "aura"],
        "product": ["laptop", "headphones", "keyboard", "monitor", "gadget", "device", "car", "sports car", "vehicle", "comparison"],
        "shopping": ["shopping", "cart", "wishlist", "buy", "store"],
    }
    detected_category = ""
    for cat, keywords in category_hints.items():
        if any(kw in q_lower for kw in keywords):
            detected_category = cat
            break

    # Visual layout / format hints
    visual_format_hints = []
    if "comparison" in q_lower or "compare" in q_lower:
        visual_format_hints.append("comparison_table")
    if "dark" in q_lower or "dark-themed" in q_lower or "dark theme" in q_lower:
        visual_format_hints.append("dark_theme")
    if "diagram" in q_lower or "architecture" in q_lower or "flowchart" in q_lower:
        visual_format_hints.append("architecture_diagram")
    if "graph" in q_lower or "chart" in q_lower or "loss" in q_lower or "curve" in q_lower or "plot" in q_lower:
        visual_format_hints.append("loss_curve_chart")
    if "dashboard" in q_lower:
        visual_format_hints.append("dashboard")
    if "error" in q_lower or "traceback" in q_lower or "exception" in q_lower:
        visual_format_hints.append("error_screen")

    # Extract quoted phrases as entity hints
    quoted = re.findall(r'"([^"]+)"', query)
    # Extract capitalized words as potential entities
    caps = re.findall(r"\b[A-Z][a-zA-Z0-9_\-]{2,}\b", query)
    # Known project/entity keywords
    project_words = re.findall(r"\b(?:YOLO|ISRO|transformers?|ResNet|GPT|BERT|PyTorch|TensorFlow|AWS|Azure|GCP|AURA|ASUS|ZenBook|Swiggy|Amazon|OpenCV|Vision)\b", query, re.IGNORECASE)

    entities = list(set(quoted + caps + project_words))

    return {
        "original": query,
        "tokens": tokens,
        "category_hint": detected_category,
        "visual_format_hints": visual_format_hints,
        "entities": entities,
    }


# ─── Full search pipeline ────────────────────────────────────────────────────

async def search_memories(query: str, memories: list, top_k: int = 20) -> list:
    """
    Run hybrid search over a list of memory dicts.
    Evaluates semantic vector similarity, BM25 text score, visual entity overlap,
    and first-class multimodal fields (visual_summary, visual_objects, document_type).
    """
    q_parsed = parse_query(query)
    q_tokens = q_parsed["tokens"]
    q_entities = q_parsed["entities"]
    q_category = q_parsed["category_hint"]
    q_v_hints = q_parsed["visual_format_hints"]

    # Embed query
    import asyncio
    q_vec = await asyncio.to_thread(embed_text, query)

    # Load all valid embeddings
    mem_vecs = []
    for m in memories:
        if m.get("is_deleted") or m.get("is_locked"):
            continue
        emb = m.get("embedding")
        if emb:
            vec = hex_to_embedding(emb)
            if vec is not None:
                mem_vecs.append((m["id"], vec))

    # Batch cosine similarities
    if q_vec is not None and mem_vecs:
        sem_scores_arr = batch_cosine_similarities(q_vec, mem_vecs)
        sem_scores = {mid: float(score) for (mid, _), score in zip(mem_vecs, sem_scores_arr)}
    else:
        sem_scores = {}

    # Score each memory
    scored = []
    for m in memories:
        if m.get("is_deleted") or m.get("is_locked"):
            continue

        mid = m["id"]
        sem_score = sem_scores.get(mid, 0.0)

        try:
            m_entities = m.get("entities") or []
            if isinstance(m_entities, str):
                m_entities = json.loads(m_entities)
        except Exception:
            m_entities = []

        try:
            m_v_objects = m.get("visual_objects") or []
            if isinstance(m_v_objects, str):
                m_v_objects = json.loads(m_v_objects)
        except Exception:
            m_v_objects = []

        app_lower = (m.get("application") or "").lower()
        win_lower = (m.get("window_title") or "").lower()
        clip_lower = (m.get("clipboard_context") or "").lower()
        v_sum_lower = (m.get("visual_summary") or "").lower()
        sum_lower = (m.get("summary") or "").lower()
        doc_type_lower = (m.get("document_type") or "").lower()
        v_objs_str = " ".join(m_v_objects).lower()
        
        m_topics = m.get("topics") or []
        if isinstance(m_topics, str):
            try:
                m_topics = json.loads(m_topics)
            except Exception:
                m_topics = [m_topics]
        topics_str = " ".join(m_topics).lower()

        combined_text = f"{m.get('original_filename', '')} {app_lower} {win_lower} {clip_lower} {v_sum_lower} {sum_lower} {doc_type_lower} {v_objs_str} {topics_str} {m.get('ocr_text', '')} {' '.join(m_entities)}"
        scores = hybrid_score(
            semantic_score=sem_score,
            query_tokens=q_tokens,
            memory_ocr=combined_text,
            query_entities=q_entities,
            memory_entities=m_entities,
            query_category=q_category,
            memory_category=m.get("category", ""),
            created_at=m.get("created_at"),
        )

        # Boost relevance score based on literal matches in visual summary, objects, OCR text, application, and clipboard
        raw_final = scores["final"]
        boost = 0.0

        ocr_lower = (m.get("ocr_text") or "").lower()
        fn_lower = (m.get("original_filename") or "").lower()

        # Meaningful tokens (excluding generic intent words)
        meaningful_tokens = [t for t in q_tokens if t not in GENERIC_INTENT_WORDS and len(t) >= 3]
        if not meaningful_tokens:
            meaningful_tokens = q_tokens

        # Count how many distinct meaningful query tokens match across all fields
        doc_haystack = f"{fn_lower} {ocr_lower} {v_sum_lower} {sum_lower} {doc_type_lower} {v_objs_str} {app_lower} {win_lower} {clip_lower} {topics_str} {' '.join(m_entities)}".lower()
        matched_tokens = [tok for tok in meaningful_tokens if tok in doc_haystack]
        match_ratio = len(matched_tokens) / max(len(meaningful_tokens), 1)

        # Proportional token match boost (up to +0.30 for matching all keywords)
        if matched_tokens:
            boost += 0.15 + 0.15 * match_ratio

        # Exact filename token boost (up to +0.20 when distinct query tokens appear in filename)
        fn_matches = [tok for tok in meaningful_tokens if tok in fn_lower]
        if fn_matches:
            boost += 0.20 * (len(fn_matches) / max(len(meaningful_tokens), 1))

        # Exact category match boost (+0.10)
        if q_category and m.get("category") == q_category:
            boost += 0.10

        # Visual layout / format match boost (+0.15)
        for v_hint in q_v_hints:
            if v_hint == "comparison_table" and ("comparison" in doc_type_lower or "comparison" in fn_lower or "comparison" in v_objs_str):
                boost += 0.20
            elif v_hint == "dark_theme" and ("dark" in doc_type_lower or "dark" in v_sum_lower or "dark" in fn_lower or "vscode" in fn_lower):
                boost += 0.20
            elif v_hint == "architecture_diagram" and ("diagram" in doc_type_lower or "architecture" in fn_lower or "architecture" in v_sum_lower):
                boost += 0.20
            elif v_hint == "loss_curve_chart" and ("chart" in doc_type_lower or "loss" in fn_lower or "plot" in v_objs_str or "matrix" in fn_lower):
                boost += 0.20
            elif v_hint == "dashboard" and ("dashboard" in doc_type_lower or "dashboard" in fn_lower or "grafana" in fn_lower):
                boost += 0.20
            elif v_hint == "error_screen" and ("error" in doc_type_lower or "error" in fn_lower or "traceback" in fn_lower or "bug" in fn_lower):
                boost += 0.20

        boosted_score = min(raw_final + boost, 1.0)
        boosted_score = round(boosted_score, 4)

        scores["final"] = boosted_score
        scores["boost"] = round(boost, 4)

        scored.append({
            **m,
            "relevance_score": boosted_score,
            "score_breakdown": scores,
        })

    # Sort descending by initial first-stage relevance score
    scored.sort(key=lambda x: x["relevance_score"], reverse=True)

    # First-stage candidate pool (top M)
    candidate_pool_size = max(top_k * 2, settings.rerank_candidate_pool)
    candidate_pool = scored[:candidate_pool_size]

    # Stage 2: Deep Cross-Encoder / Multimodal Reranking
    from app.services.reranker import rerank_candidates
    reranked = rerank_candidates(
        query=query,
        candidates=candidate_pool,
        query_tokens=q_tokens,
        query_entities=q_entities,
        query_category=q_category,
        visual_format_hints=q_v_hints,
        top_k=top_k,
    )

    # Filter out noise below 0.25 threshold (keep at least top 3 if available)
    filtered = [x for x in reranked if x["relevance_score"] >= 0.25]
    if not filtered and reranked:
        filtered = reranked[:3]

    return filtered[:top_k]

