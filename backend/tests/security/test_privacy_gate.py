"""
AURA Security Test Suite — OS-Level Privacy Gate
Tests deterministic blocking of password managers, private browsing, and secrets.
"""
import sys
from pathlib import Path
import pytest

root_dir = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(root_dir))

from desktop.privacy_gate import PrivacyGate


@pytest.fixture
def gate():
    return PrivacyGate()


def test_block_password_managers(gate):
    # Test 1Password
    res1 = gate.evaluate_capture("1password.exe", "1Password — Vault", "")
    assert res1["allowed"] is False
    assert res1["action"] == "DROP"
    assert "Blocked application" in res1["reason"]

    # Test Bitwarden
    res2 = gate.evaluate_capture("bitwarden.exe", "Bitwarden", "")
    assert res2["allowed"] is False
    assert res2["action"] == "DROP"


def test_block_incognito_and_sensitive_windows(gate):
    # Test Chrome Incognito
    res1 = gate.evaluate_capture("chrome.exe", "New Incognito Tab - Google Chrome", "")
    assert res1["allowed"] is False
    assert res1["action"] == "DROP"

    # Test Net Banking
    res2 = gate.evaluate_capture("msedge.exe", "HDFC Bank - Sign in to Net Banking", "")
    assert res2["allowed"] is False
    assert res2["action"] == "DROP"


def test_secret_redaction_and_key_blocking(gate):
    # Test AWS Key Redaction
    sample_text = "Deploying with key AKIAIOSFODNN7EXAMPLE to us-east-1"
    res1 = gate.evaluate_capture("code.exe", "deploy.py - Visual Studio Code", sample_text)
    assert res1["allowed"] is True
    assert res1["action"] == "REDACT"
    assert "AWS Access Key" in res1["detected_secrets"]
    assert "AKIAIOSFODNN7EXAMPLE" not in res1["redacted_text"]
    assert "[REDACTED_AWS_ACCESS_KEY]" in res1["redacted_text"]

    # Test Private Key Drop
    key_text = "-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA0...\n-----END RSA PRIVATE KEY-----"
    res2 = gate.evaluate_capture("code.exe", "id_rsa - Visual Studio Code", key_text)
    assert res2["allowed"] is False
    assert res2["action"] == "DROP"


def test_allow_clean_developer_workflow(gate):
    res = gate.evaluate_capture("code.exe", "train_yolo.py — PyTorch Project", "import torch\nmodel = YOLO('yolov8n.pt')")
    assert res["allowed"] is True
    assert res["action"] == "ALLOW"
    assert len(res["detected_secrets"]) == 0
