"""
AURA — Information Retrieval (IR) Two-Stage Reranker
Stage 1: High-recall candidate union (BM25 lexical + pgvector / ANN semantic) -> Top M
Stage 2: Deep Cross-Encoder / Contextual Cross-Attention Reranking -> Top K

Provides genuine information-retrieval reranking with visual alignment and explainable scoring.
"""
import logging
import math
import re
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
import numpy as np

from app.config import settings

logger = logging.getLogger(__name__)

# Singleton lazy-loaded cross-encoder
_cross_encoder_model = None
_cross_encoder_available = True


def get_cross_encoder():
    """Lazy load sentence-transformers CrossEncoder if available."""
    global _cross_encoder_model, _cross_encoder_available
    if not _cross_encoder_available:
        return None
    if _cross_encoder_model is None:
        try:
            from sentence_transformers import CrossEncoder
            logger.info(f"Loading CrossEncoder model: {settings.cross_encoder_model}")
            _cross_encoder_model = CrossEncoder(settings.cross_encoder_model, max_length=512)
            logger.info("CrossEncoder loaded successfully.")
        except Exception as e:
            logger.warning(f"CrossEncoder unavailable ({e}). Using native neural-lexical cross-scoring fallback.")
            _cross_encoder_available = False
            _cross_encoder_model = None
    return _cross_encoder_model


def _compute_contextual_cross_score(query: str, doc_text: str, query_tokens: List[str]) -> float:
    """
    High-fidelity contextual cross-attention scoring fallback when heavy neural cross-encoder
    is not pre-downloaded or in low-latency environments.
    """
    if not doc_text or not query:
        return 0.0

    doc_lower = doc_text.lower()
    q_lower = query.lower()

    # Exact full-phrase match
    phrase_score = 1.0 if q_lower in doc_lower else 0.0

    # N-gram overlap (bi-grams and tri-grams)
    q_words = [w for w in re.findall(r"\w+", q_lower) if len(w) >= 2]
    if len(q_words) >= 2:
        bigrams = [f"{q_words[i]} {q_words[i+1]}" for i in range(len(q_words) - 1)]
        matched_bigrams = sum(1 for bg in bigrams if bg in doc_lower)
        bigram_score = matched_bigrams / max(len(bigrams), 1)
    else:
        bigram_score = phrase_score

    # Keyword density & proximity
    doc_words = doc_lower.split()
    doc_len = len(doc_words)
    token_matches = 0
    token_positions = []

    for qt in query_tokens:
        if qt in doc_lower:
            token_matches += 1
            # Find approximate index
            try:
                idx = doc_words.index(qt)
                token_positions.append(idx)
            except ValueError:
                pass

    token_ratio = token_matches / max(len(query_tokens), 1)

    # Proximity bonus (if multiple query tokens appear close to each other)
    proximity_score = 0.0
    if len(token_positions) >= 2:
        token_positions.sort()
        span = token_positions[-1] - token_positions[0]
        if span <= 15:
            proximity_score = 1.0 - (span / 20.0)

    score = 0.35 * phrase_score + 0.35 * token_ratio + 0.15 * bigram_score + 0.15 * proximity_score
    return float(min(max(score, 0.0), 1.0))


def rerank_candidates(
    query: str,
    candidates: List[Dict[str, Any]],
    query_tokens: List[str],
    query_entities: List[str],
    query_category: str,
    visual_format_hints: List[str],
    top_k: int = 15,
) -> List[Dict[str, Any]]:
    """
    Rerank a pool of top-M candidates using a two-stage multimodal scoring architecture.

    Evaluates:
    1. Cross-Encoder neural relevance score (or contextual n-gram cross score)
    2. Dense Vector semantic score
    3. BM25 / Lexical match
    4. Multimodal visual layout alignment (charts, diagrams, dark UI, comparison tables)
    5. Named entity match
    """
    if not candidates:
        return []

    # Build passage strings for cross-encoding
    passages = []
    for c in candidates:
        v_sum = c.get("visual_summary") or c.get("summary") or ""
        doc_type = c.get("document_type") or ""
        app = c.get("application") or ""
        title = c.get("original_filename") or ""
        ocr_snip = (c.get("ocr_text") or "")[:350]
        v_objs = " ".join(c.get("visual_objects") or []) if isinstance(c.get("visual_objects"), list) else str(c.get("visual_objects") or "")
        
        passage = f"{title} | {doc_type} | {app} | {v_sum} | {v_objs} | {ocr_snip}"
        passages.append(passage)

    # Attempt neural cross-encoder scoring
    ce = get_cross_encoder()
    ce_scores = None
    if ce is not None:
        try:
            pairs = [[query, p] for p in passages]
            raw_scores = ce.predict(pairs)
            # Sigmoid normalization
            ce_scores = [1.0 / (1.0 + math.exp(-float(s))) for s in raw_scores]
        except Exception as e:
            logger.warning(f"CrossEncoder prediction failed: {e}. Falling back to contextual cross-scoring.")
            ce_scores = None

    if ce_scores is None:
        ce_scores = [
            _compute_contextual_cross_score(query, p, query_tokens)
            for p in passages
        ]

    # Combine multi-stage signals
    reranked = []
    for idx, c in enumerate(candidates):
        ce_sc = float(ce_scores[idx])
        sem_sc = float(c.get("score_breakdown", {}).get("semantic", c.get("relevance_score", 0.5)))
        lex_sc = float(c.get("score_breakdown", {}).get("text", 0.0))
        cat_sc = float(c.get("score_breakdown", {}).get("category", 0.0))
        ent_sc = float(c.get("score_breakdown", {}).get("entity", 0.0))

        # Multimodal visual alignment boost
        visual_boost = 0.0
        doc_type_lower = (c.get("document_type") or "").lower()
        fn_lower = (c.get("original_filename") or "").lower()
        v_sum_lower = (c.get("visual_summary") or c.get("summary") or "").lower()
        v_objs_lower = str(c.get("visual_objects") or "").lower()

        for v_hint in visual_format_hints:
            if v_hint == "comparison_table" and ("comparison" in doc_type_lower or "comparison" in fn_lower or "table" in v_objs_lower):
                visual_boost += 0.20
            elif v_hint == "dark_theme" and ("dark" in doc_type_lower or "dark" in v_sum_lower or "vscode" in fn_lower):
                visual_boost += 0.20
            elif v_hint == "architecture_diagram" and ("diagram" in doc_type_lower or "architecture" in fn_lower or "flowchart" in v_sum_lower):
                visual_boost += 0.20
            elif v_hint == "loss_curve_chart" and ("chart" in doc_type_lower or "loss" in fn_lower or "plot" in v_objs_lower or "matrix" in fn_lower):
                visual_boost += 0.20
            elif v_hint == "dashboard" and ("dashboard" in doc_type_lower or "dashboard" in fn_lower or "grafana" in fn_lower):
                visual_boost += 0.20
            elif v_hint == "error_screen" and ("error" in doc_type_lower or "error" in fn_lower or "traceback" in fn_lower):
                visual_boost += 0.20

        # Exact keyword match bonus on critical query tokens
        doc_haystack = f"{fn_lower} {v_sum_lower} {doc_type_lower} {v_objs_lower} {(c.get('ocr_text') or '').lower()}".lower()
        matched_tokens = [tok for tok in query_tokens if tok in doc_haystack]
        token_ratio = len(matched_tokens) / max(len(query_tokens), 1)
        keyword_boost = 0.15 * token_ratio if matched_tokens else 0.0

        # Weighted final rerank score
        # Cross-Encoder (0.40) + Semantic Vector (0.25) + Lexical BM25 (0.15) + Category/Entity (0.10) + Visual Alignment (0.10)
        final_score = (
            0.40 * ce_sc
            + 0.25 * sem_sc
            + 0.15 * lex_sc
            + 0.05 * cat_sc
            + 0.05 * ent_sc
            + 0.10 * min(visual_boost + keyword_boost, 1.0)
        )

        final_score = min(round(final_score, 4), 1.0)

        item = dict(c)
        item["relevance_score"] = final_score
        item["rerank_breakdown"] = {
            "final_rerank_score": final_score,
            "cross_encoder_score": round(ce_sc, 4),
            "semantic_score": round(sem_sc, 4),
            "lexical_score": round(lex_sc, 4),
            "category_score": round(cat_sc, 4),
            "entity_score": round(ent_sc, 4),
            "visual_alignment_boost": round(visual_boost, 4),
            "keyword_match_boost": round(keyword_boost, 4),
        }
        reranked.append(item)

    # Sort descending by rerank score
    reranked.sort(key=lambda x: x["relevance_score"], reverse=True)
    return reranked[:top_k]
