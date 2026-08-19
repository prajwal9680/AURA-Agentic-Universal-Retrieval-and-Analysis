"""
AURA — OS-Level Zero-Trust Privacy Gate
Evaluates screen frames, active applications, and window titles BEFORE ingestion.
Deterministic pre-ingestion security policies:
1. Blocked Process Verification (Password managers, authenticators, Tor)
2. Blocked Window Patterns (Incognito, Banking, Metamask, 2FA)
3. Pre-Ingestion Secret Scanning & Redaction (AWS keys, OpenAI/API keys, GitHub tokens, RSA private keys)
"""
import re
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

logger = logging.getLogger("aura.privacy_gate")

DEFAULT_RULES_PATH = Path(__file__).resolve().parent.parent / "config" / "privacy_rules.json"


class PrivacyGate:
    def __init__(self, rules_path: Optional[Path] = None):
        self.rules_path = rules_path or DEFAULT_RULES_PATH
        self.blocked_processes: List[str] = []
        self.blocked_window_patterns: List[re.Pattern] = []
        self.secret_patterns: List[Tuple[str, re.Pattern, str]] = []
        self._load_rules()

    def _load_rules(self):
        """Loads and compiles privacy gate rules from JSON."""
        if not self.rules_path.exists():
            # Fallback default rules
            self.blocked_processes = [
                "1password.exe", "bitwarden.exe", "keepass.exe", "lastpass.exe",
                "dashlane.exe", "enpass.exe", "tor.exe", "authenticator.exe"
            ]
            self.blocked_window_patterns = [
                re.compile(r"(?i)incognito"),
                re.compile(r"(?i)private browsing"),
                re.compile(r"(?i)inprivate"),
                re.compile(r"(?i)password manager"),
                re.compile(r"(?i)sign in to your bank"),
                re.compile(r"(?i)crypto wallet"),
            ]
            self.secret_patterns = [
                ("AWS Access Key", re.compile(r"AKIA[0-9A-Z]{16}"), "REDACT_OR_BLOCK"),
                ("API Key", re.compile(r"sk-(?:live|proj|ant)?[a-zA-Z0-9_-]{20,}"), "REDACT_OR_BLOCK"),
                ("GitHub Token", re.compile(r"gh[pousr]_[0-9a-zA-Z]{36}"), "REDACT_OR_BLOCK"),
                ("Private Key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"), "BLOCK"),
            ]
            return

        try:
            with open(self.rules_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.blocked_processes = [p.lower().strip() for p in data.get("blocked_processes", [])]
            self.blocked_window_patterns = [
                re.compile(pat) for pat in data.get("blocked_window_patterns", [])
            ]
            self.secret_patterns = [
                (s["name"], re.compile(s["regex"]), s.get("action", "REDACT"))
                for s in data.get("secret_patterns", [])
            ]
            logger.info(f"Loaded {len(self.blocked_processes)} blocked apps, {len(self.blocked_window_patterns)} window rules, {len(self.secret_patterns)} secret patterns.")
        except Exception as e:
            logger.error(f"Failed to load privacy rules from {self.rules_path}: {e}")

    def evaluate_capture(
        self,
        app_name: str,
        window_title: str,
        extracted_text: str = "",
    ) -> Dict[str, Any]:
        """
        Determines whether a captured screenshot is safe for ingestion.
        Returns:
            {
                "allowed": bool,
                "action": "ALLOW" | "DROP" | "REDACT",
                "reason": str,
                "detected_secrets": List[str],
                "redacted_text": str,
            }
        """
        clean_app = app_name.lower().strip()
        clean_title = window_title.strip()

        # 1. Check blocked processes
        for bp in self.blocked_processes:
            if clean_app == bp or clean_app.endswith(bp):
                return {
                    "allowed": False,
                    "action": "DROP",
                    "reason": f"Blocked application: '{app_name}' is in the zero-trust exclusion list.",
                    "detected_secrets": [],
                    "redacted_text": "",
                }

        # 2. Check blocked window title regexes
        for wp in self.blocked_window_patterns:
            if wp.search(clean_title):
                return {
                    "allowed": False,
                    "action": "DROP",
                    "reason": f"Blocked window title pattern matched: '{clean_title}'.",
                    "detected_secrets": [],
                    "redacted_text": "",
                }

        # 3. Pre-ingestion secret scanning
        detected = []
        should_block = False
        redacted = extracted_text

        if extracted_text:
            for name, pattern, action in self.secret_patterns:
                matches = pattern.findall(extracted_text)
                if matches:
                    detected.append(name)
                    if action == "BLOCK":
                        should_block = True
                    # Redact matched patterns in text
                    redacted = pattern.sub(f"[REDACTED_{name.upper().replace(' ', '_')}]", redacted)

        if should_block:
            return {
                "allowed": False,
                "action": "DROP",
                "reason": f"High-risk secrets detected in frame: {', '.join(detected)}.",
                "detected_secrets": detected,
                "redacted_text": "",
            }

        action = "REDACT" if detected else "ALLOW"
        return {
            "allowed": True,
            "action": action,
            "reason": f"Secrets redacted: {', '.join(detected)}" if detected else "Passed zero-trust privacy checks.",
            "detected_secrets": detected,
            "redacted_text": redacted,
        }


# Global default instance
privacy_gate = PrivacyGate()
