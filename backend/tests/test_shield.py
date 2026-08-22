"""
AURA — Shield Unit Tests
Tests deterministic regex detection for all sensitive types.
Run: pytest tests/test_shield.py -v
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from app.services.shield import scan_text, CRITICAL, SENSITIVE, PERSONAL, PUBLIC


class TestAPIKeyDetection:
    def test_github_pat(self):
        text = "Token: ghp_Kx9mRTq7YvN3pL2wQeZ1AbC8dFjHuI4oG5sX"
        result = scan_text(text)
        assert result["sensitivity_level"] == CRITICAL
        assert any(f["type"] == "api_key" for f in result["findings"])

    def test_google_api_key(self):
        text = "api_key = AIzaSyDummyKey12345678901234567890"
        result = scan_text(text)
        assert result["sensitivity_level"] == CRITICAL

    def test_aws_access_key(self):
        text = "AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE"
        result = scan_text(text)
        assert result["sensitivity_level"] == CRITICAL

    def test_openai_key(self):
        text = "OPENAI_API_KEY=sk-proj-AbcDefGhiJklMnoPqrStuVwxYz1234567890"
        result = scan_text(text)
        assert result["sensitivity_level"] == CRITICAL

    def test_google_aistudio_key(self):
        text = "AI_STUDIO_KEY=AIzaSyA1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q"
        result = scan_text(text)
        assert result["sensitivity_level"] == CRITICAL


class TestJWTDetection:
    def test_jwt_token(self):
        text = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
        result = scan_text(text)
        assert result["sensitivity_level"] == CRITICAL
        assert any(f["type"] == "jwt" for f in result["findings"])


class TestPasswordDetection:
    def test_wifi_password(self):
        text = "Wi-Fi Password: Aura@2026#SecureNetwork!"
        result = scan_text(text)
        assert result["sensitivity_level"] == CRITICAL
        assert any(f["type"] == "password" for f in result["findings"])

    def test_password_field(self):
        text = "password: hunter2"
        result = scan_text(text)
        assert result["sensitivity_level"] == CRITICAL

    def test_ssid_password(self):
        text = "SSID: MyNetwork\nWPA Key: S3cur3P@ssw0rd!"
        result = scan_text(text)
        assert result["sensitivity_level"] == CRITICAL


class TestPIIDetection:
    def test_email(self):
        text = "Contact: user@example.com for support"
        result = scan_text(text)
        assert result["sensitivity_level"] in (PERSONAL, SENSITIVE, CRITICAL)
        assert any(f["type"] == "email" for f in result["findings"])

    def test_indian_phone(self):
        text = "Call me at 9876543210 anytime"
        result = scan_text(text)
        assert result["sensitivity_level"] in (PERSONAL, SENSITIVE, CRITICAL)
        assert any(f["type"] == "phone" for f in result["findings"])

    def test_credit_card(self):
        text = "Card Number: 4532015112830366"
        result = scan_text(text)
        assert result["sensitivity_level"] == CRITICAL
        assert any(f["type"] == "credit_card" for f in result["findings"])


class TestSafeContent:
    def test_public_code(self):
        text = "def hello_world():\n    print('Hello, World!')\n    return True"
        result = scan_text(text)
        assert result["sensitivity_level"] == PUBLIC

    def test_recipe(self):
        text = "Mix 2 cups flour, 1 tsp salt, 3 tbsp butter. Bake at 180°C for 25 minutes."
        result = scan_text(text)
        assert result["sensitivity_level"] == PUBLIC

    def test_research_abstract(self):
        text = "Abstract: We propose a novel attention mechanism for object detection achieving 94.2% mAP on COCO."
        result = scan_text(text)
        assert result["sensitivity_level"] == PUBLIC


class TestRedaction:
    def test_api_key_redacted_in_findings(self):
        text = "API_KEY=ghp_Kx9mRTq7YvN3pL2wQeZ1AbC8dFjHuI4oG5sX"
        result = scan_text(text)
        # Verify sensitive match is redacted in findings display
        for f in result["findings"]:
            if f["type"] == "api_key":
                # Should not expose full key in findings
                assert len(f["match"]) <= 12  # at most redacted form

    def test_credit_card_redacted(self):
        text = "Credit Card: 4532015112830366 expiry 12/28"
        result = scan_text(text)
        for f in result["findings"]:
            if f["type"] == "credit_card":
                assert "****" in f["match"]


if __name__ == "__main__":
    import subprocess
    subprocess.run(["pytest", __file__, "-v"])
