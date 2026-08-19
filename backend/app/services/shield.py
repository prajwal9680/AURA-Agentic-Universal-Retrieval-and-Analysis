"""
AURA Shield — Sensitive Information Detection
Implements deterministic regex-first detection, then AI classification.
Never relies solely on LLM output for secret detection.
"""
import re
import json
import logging
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)

# Sensitivity levels
PUBLIC = "PUBLIC"
PERSONAL = "PERSONAL"
SENSITIVE = "SENSITIVE"
CRITICAL = "CRITICAL"

# ─── Deterministic Patterns ───────────────────────────────────────────────────

PATTERNS = {
    # CRITICAL — secrets & credentials
    "api_key": [
        r"\b[A-Za-z0-9_\-]{32,}\b",  # Generic long token
        r"(?i)(api[_\-\s]?key|api[_\-\s]?secret|access[_\-\s]?key|secret[_\-\s]?key|personal[_\-\s]?access[_\-\s]?token)\s*[:=]\s*[^\s]{6,}",
        r"(?i)(?:personal[_\-\s]access[_\-\s]token|github[_\-\s]personal[_\-\s]access[_\-\s]token|access[_\-\s]token|auth[_\-\s]token)",
        r"AIza[0-9A-Za-z\-_]{35}",   # Google API key
        r"AKIA[0-9A-Z]{16}",          # AWS access key
        r"gh[pousr]_[A-Za-z0-9]{36,}", # GitHub PAT
        r"sk-[A-Za-z0-9]{32,}",       # OpenAI key
        r"xox[baprs]-[A-Za-z0-9\-]+", # Slack token
        r"AQ\.[A-Za-z0-9_\-]{20,}",   # Google AI Studio key
    ],
    "jwt": [
        r"eyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+",
    ],
    "private_key": [
        r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
        r"-----BEGIN CERTIFICATE-----",
    ],
    "password": [
        r"(?i)(?:password|passwd|pwd|passphrase|secret|wifi[_\s\-]?password|network[_\s\-]?key|wpa[23]?[_\s\-]?(?:key|password|passphrase)|wireless\s*security|router\s*password)\s*[:=]\s*\S+",
        r"(?i)(?:wi[\-\.\s]?fi|ssid|network|router|wpa[23]?)[^\n]*(?:password|key|pass|psk|preshared|wpa)[^\n]*",
        r"(?i)(?:wpa[23]?[\-_]?(?:psk|personal|key)|wep)[\s\S]{0,60}?(?:key|password|securekey|[:=]\s*\S+)",
        r"(?i)(?:wireless\s*security\s*settings|primary\s*wireless\s*network)",
        r"(?i)(?:sensitive\s*credential\s*detected|aura\s*shield\s*zero[\-\s]?trust)",
    ],
    "cloud_credentials": [
        r"(?i)(aws_secret|aws_access|azure_client|gcp_key|service_account)\s*[:=]\s*\S+",
    ],
    # SENSITIVE — PII
    "credit_card": [
        r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b",
    ],
    "ssn": [
        r"\b\d{3}-\d{2}-\d{4}\b",      # US SSN
        r"\b\d{12}\b",                   # Aadhaar (12 digits)
    ],
    "bank_account": [
        r"(?i)(account[_\s]?no|account[_\s]?number|acct[_\s]?no)\s*[:=]?\s*\d{8,18}",
        r"(?i)(IFSC|routing[_\s]?number|sort[_\s]?code)\s*[:=]?\s*[A-Z0-9]{8,11}",
    ],
    # PERSONAL — contact info
    "email": [
        r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b",
    ],
    "phone": [
        r"\b(?:\+?91[-\s]?)?[6-9]\d{9}\b",
        r"\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b",
        r"\b\+\d{1,3}[-.\s]\d{4,14}\b",
    ],
    "address": [
        r"\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Lane|Ln|Drive|Dr|Court|Ct|Boulevard|Blvd)\b",
        r"(?i)(?:address|addr)\s*[:=]\s*[^\n]{10,}",
    ],
}

# Severity mapping per finding type
SEVERITY_MAP = {
    "api_key": CRITICAL,
    "jwt": CRITICAL,
    "private_key": CRITICAL,
    "password": CRITICAL,
    "cloud_credentials": CRITICAL,
    "credit_card": CRITICAL,
    "ssn": CRITICAL,
    "bank_account": SENSITIVE,
    "email": PERSONAL,
    "phone": PERSONAL,
    "address": PERSONAL,
}

SEVERITY_ORDER = [PUBLIC, PERSONAL, SENSITIVE, CRITICAL]


def scan_text(text: str) -> dict:
    """
    Run deterministic shield scan on extracted text.
    Returns:
        {
            "sensitivity_level": "PUBLIC" | "PERSONAL" | "SENSITIVE" | "CRITICAL",
            "findings": [{"type": str, "match": str, "severity": str}],
            "confidence": float,
            "summary": str
        }
    """
    if not text or len(text.strip()) < 3:
        return {
            "sensitivity_level": PUBLIC,
            "findings": [],
            "confidence": 0.95,
            "summary": "No text content to scan.",
        }

    findings = []
    max_severity = PUBLIC

    for finding_type, pattern_list in PATTERNS.items():
        for pattern in pattern_list:
            try:
                matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    if isinstance(match, tuple):
                        match = " ".join(m for m in match if m)
                    match_str = str(match).strip()
                    if len(match_str) < 4:  # Skip trivial matches
                        continue

                    severity = SEVERITY_MAP.get(finding_type, PERSONAL)
                    findings.append({
                        "type": finding_type,
                        "match": _redact_match(match_str, finding_type),
                        "severity": severity,
                    })

                    # Update max severity
                    if SEVERITY_ORDER.index(severity) > SEVERITY_ORDER.index(max_severity):
                        max_severity = severity
            except re.error:
                continue

    # Deduplicate findings
    seen = set()
    unique_findings = []
    for f in findings:
        key = f"{f['type']}:{f['match']}"
        if key not in seen:
            seen.add(key)
            unique_findings.append(f)

    confidence = 0.95 if unique_findings else 0.80
    summary = _build_summary(unique_findings, max_severity)

    return {
        "sensitivity_level": max_severity,
        "findings": unique_findings[:20],  # cap
        "confidence": confidence,
        "summary": summary,
    }


def scan_with_ai(text: str, image_path: str, ocr_findings: dict) -> dict:
    """
    AI-enhanced sensitivity classification using Gemini.
    Supplements (never replaces) deterministic detection.
    """
    # Start with deterministic results
    base = scan_text(text)

    if not settings.gemini_api_key or base["sensitivity_level"] == CRITICAL:
        # If already CRITICAL, deterministic is sufficient
        return base

    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel(settings.gemini_model)

        existing = json.dumps(base["findings"][:5], indent=2)
        prompt = f"""You are a security classification system. Rate the sensitivity of this screenshot content.

Existing detected findings: {existing}

Text content (first 1000 chars):
{text[:1000]}

Return JSON:
{{
  "sensitivity_level": "PUBLIC|PERSONAL|SENSITIVE|CRITICAL",
  "additional_findings": ["description of any sensitive content not already detected"],
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation"
}}

Be conservative — if unsure, use the lower sensitivity level."""

        response = model.generate_content(prompt)
        resp_text = response.text.strip()
        if resp_text.startswith("```"):
            resp_text = resp_text.split("```")[1]
            if resp_text.startswith("json"):
                resp_text = resp_text[4:]

        ai_result = json.loads(resp_text.strip())
        ai_level = ai_result.get("sensitivity_level", PUBLIC)

        # Only upgrade sensitivity, never downgrade from deterministic finding
        if SEVERITY_ORDER.index(ai_level) > SEVERITY_ORDER.index(base["sensitivity_level"]):
            base["sensitivity_level"] = ai_level
            base["confidence"] = ai_result.get("confidence", 0.7)

        # Add any AI-discovered findings
        for extra in ai_result.get("additional_findings", []):
            if extra and len(extra) > 3:
                base["findings"].append({
                    "type": "ai_detected",
                    "match": extra[:100],
                    "severity": ai_level,
                })

        base["summary"] = _build_summary(base["findings"], base["sensitivity_level"])
        return base

    except Exception as e:
        logger.warning(f"AI shield scan failed, using deterministic only: {e}")
        return base


def _redact_match(match: str, finding_type: str) -> str:
    """Partially redact a sensitive match for safe logging/display."""
    if finding_type in ("api_key", "jwt", "private_key", "password", "cloud_credentials"):
        # Show first 4 chars + redact rest
        if len(match) > 8:
            return match[:4] + "****" + match[-2:]
        return "****"
    elif finding_type == "credit_card":
        # Show last 4 digits
        digits = re.sub(r"\D", "", match)
        return f"****-****-****-{digits[-4:]}" if len(digits) >= 4 else "****"
    elif finding_type == "email":
        parts = match.split("@")
        if len(parts) == 2:
            return f"{parts[0][:2]}***@{parts[1]}"
        return match
    elif finding_type == "phone":
        digits = re.sub(r"\D", "", match)
        return f"{'*' * (len(digits)-4)}{digits[-4:]}" if len(digits) > 4 else "****"
    else:
        return match[:20] + ("..." if len(match) > 20 else "")


def _build_summary(findings: list, level: str) -> str:
    """Human-readable summary of shield findings."""
    if not findings:
        return "No sensitive content detected."

    types = list(set(f["type"] for f in findings))
    readable = {
        "api_key": "API key",
        "jwt": "authentication token",
        "private_key": "private key",
        "password": "password",
        "cloud_credentials": "cloud credentials",
        "credit_card": "credit card number",
        "ssn": "national identifier",
        "bank_account": "bank account details",
        "email": "email address",
        "phone": "phone number",
        "address": "physical address",
        "ai_detected": "sensitive content",
    }
    type_names = [readable.get(t, t) for t in types[:4]]
    count = len(findings)
    return f"{count} finding(s): {', '.join(type_names)}."
