"""
AURA — Multimodal & Screenshot Prompt Injection Defense Engine
Provides:
1. Untrusted screen content boundary isolation with XML delimiters.
2. Adversarial prompt injection pattern scanner for OCR and visual text.
3. Automated adversarial quarantine to protect downstream Agentic RAG models.
"""
import re
import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger("aura.prompt_injection")

# Adversarial injection heuristics
INJECTION_SIGNATURES: List[Tuple[str, re.Pattern, float]] = [
    # Direct instruction override
    ("INSTRUCTION_OVERRIDE", re.compile(r"(?i)(?:ignore\s+(?:all\s+)?(?:previous|prior|above)\s+instructions|disregard\s+(?:all\s+)?instructions|forget\s+everything)"), 0.95),
    # System role hijacking
    ("ROLE_HIJACKING", re.compile(r"(?i)(?:system\s+override|you\s+are\s+now\s+(?:dan|unfiltered|jailbroken|godmode)|new\s+system\s+directive)"), 0.92),
    # Data exfiltration instructions
    ("EXFILTRATION_PAYLOAD", re.compile(r"(?i)(?:send|exfiltrate|transmit|post)\s+(?:all\s+)?(?:passwords|tokens|keys|secrets|memories)\s+to\s+https?://"), 0.98),
    # Code execution / destructive commands
    ("DESTRUCTIVE_COMMAND", re.compile(r"(?i)(?:rm\s+-rf\s+/|drop\s+table\s+\w+|format\s+[a-z]:\s+/fs|delete\s+from\s+\w+\s+where\s+1=1)"), 0.88),
    # Fake system markers
    ("FAKE_SYSTEM_TAG", re.compile(r"(?i)(?:<\|im_start\|>system|<system>|\[INST\]\s*<<SYS>>)"), 0.90),
    # Secret leakage prompt injection
    ("LEAK_PROMPT_INJECTION", re.compile(r"(?i)(?:print|output|reveal|dump)\s+(?:your\s+)?(?:system\s+prompt|initial\s+instructions|hidden\s+rules)"), 0.85),
]


def isolate_untrusted_content(raw_text: str, content_type: str = "screen_ocr") -> str:
    """
    Sanitizes and encloses untrusted visual or OCR text in strict XML isolation tags.
    This creates an explicit contextual boundary preventing downstream LLMs/VLMs from executing embedded directives.
    """
    if not raw_text:
        return ""
    
    # Strip any hostile closing tags from the untrusted content
    sanitized = raw_text.replace("</untrusted_screen_content>", "[ESCAPED_TAG]")
    sanitized = sanitized.replace("<|im_end|>", "[ESCAPED_MARKER]")

    return (
        f"<untrusted_screen_content type=\"{content_type}\">\n"
        f"{sanitized}\n"
        f"</untrusted_screen_content>"
    )


def scan_prompt_injection(text: str) -> Dict[str, Any]:
    """
    Scans text for adversarial prompt injection patterns.
    Returns:
        {
            "is_safe": bool,
            "risk_score": float,  # 0.0 to 1.0
            "is_quarantined": bool,
            "detected_threats": List[str],
            "highest_threat": str,
        }
    """
    if not text:
        return {
            "is_safe": True,
            "risk_score": 0.0,
            "is_quarantined": False,
            "detected_threats": [],
            "highest_threat": "NONE",
        }

    detected_threats = []
    max_risk = 0.0
    highest_threat = "NONE"

    for threat_name, pattern, risk_weight in INJECTION_SIGNATURES:
        if pattern.search(text):
            detected_threats.append(threat_name)
            if risk_weight > max_risk:
                max_risk = risk_weight
                highest_threat = threat_name

    # Quarantine threshold: risk >= 0.80
    is_quarantined = max_risk >= 0.80
    is_safe = max_risk < 0.60

    if is_quarantined:
        logger.warning(
            f"Adversarial Prompt Injection Detected! Threats: {detected_threats}, Risk Score: {max_risk:.2f}"
        )

    return {
        "is_safe": is_safe,
        "risk_score": round(max_risk, 3),
        "is_quarantined": is_quarantined,
        "detected_threats": detected_threats,
        "highest_threat": highest_threat,
    }
