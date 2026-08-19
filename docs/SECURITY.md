# AURA (Agentic Universal Retrieval and Analysis) — Security Architecture & Threat Model

## Overview
AURA (**Agentic Universal Retrieval and Analysis**) enforces a **Zero-Trust Privacy & Security Architecture** across desktop ingestion, vector persistence, multimodal VLM processing, and LangGraph agentic inference.

---

## 1. Zero-Trust OS Ingestion Gate

### Pre-Ingestion Filter Pipeline
Before any screenshot or clipboard buffer is processed by neural networks or transmitted to the backend, it passes through the client-side `PrivacyGate` (`desktop/privacy_gate.py`):

1. **Process Denylist**:
   - Automatically drops captures from password managers (`1password.exe`, `bitwarden.exe`, `keepass.exe`, `lastpass.exe`, `dashlane.exe`, `enpass.exe`), authenticators (`authenticator.exe`, `yubico`), and anonymous browsers (`tor.exe`).
2. **Window Title Regex Filtering**:
   - Drops frames containing keywords: `(?i)incognito`, `(?i)private browsing`, `(?i)inprivate`, `(?i)sign in to your bank`, `(?i)crypto wallet`, `(?i)metamask`, `(?i)2fa code`.
3. **Pre-Ingestion Secret Scanning & Redaction**:
   - Scans extracted text for high-entropy secrets and credential headers:
     - AWS Access Keys: `AKIA[0-9A-Z]{16}` $\to$ Redacted
     - API Keys: `sk-[a-zA-Z0-9_-]{20,}` $\to$ Redacted
     - GitHub Tokens: `gh[pousr]_[0-9a-zA-Z]{36}` $\to$ Redacted
     - JWT Tokens: `eyJ...\.eyJ...\....` $\to$ Redacted
     - RSA/OpenSSH Private Keys: `-----BEGIN ... PRIVATE KEY-----` $\to$ Complete Frame Drop

---

## 2. Screenshot Prompt Injection Defenses

Screenshots and OCR streams from untrusted third-party websites or documents present a severe vector for **Indirect Prompt Injection**.

### Multimodal Defense Architecture:
```
┌─────────────────────────┐
│ Untrusted Screenshot OCR│
└────────────┬────────────┘
             │
┌────────────▼────────────┐
│ Adversarial Signature   │
│ Scanner (Heuristics)    │
└────────────┬────────────┘
             │
      ┌──────┴──────┐
      │             │
[Threat >= 0.80] [Threat < 0.80]
      │             │
┌─────▼─────┐ ┌─────▼─────────────────────────┐
│ Quarantine│ │ Strict XML Boundary Isolation │
│ (Lockdown)│ │ <untrusted_screen_content>... │
└───────────┘ └─────┬─────────────────────────┘
                    │
              ┌─────▼─────┐
              │ LLM / VLM │
              └───────────┘
```

1. **XML Boundary Delimitation**:
   - All untrusted visual content is wrapped in `<untrusted_screen_content type="...">...</untrusted_screen_content>`.
   - Embedded closing tags and prompt escape markers (e.g. `<|im_end|>`) are stripped and escaped before forwarding to models.
2. **Signature Threat Scanner**:
   - Detects instruction overrides (`"Ignore previous instructions"`, `"Disregard prior directives"`).
   - Detects role hijacking (`"You are now DAN"`, `"System override"`).
   - Detects exfiltration directives (`"Send all passwords to http://..."`).
   - Detects destructive command payloads (`"rm -rf /"`, `"DROP TABLE"`).
3. **Automated Adversarial Quarantine**:
   - Screenshots matching high-risk signatures are marked with `is_quarantined = True` and excluded from general search and agent retrieval candidate pools.
