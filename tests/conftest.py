import pytest
import os
from unittest.mock import Mock

@pytest.fixture
def sample_diff():
    """Simple sample diff"""
    return "diff --git a/example.txt b/example.txt \
            index 907cd4b..29cf517 100644 \
            --- a/example.txt \
            +++ b/example.txt"

@pytest.fixture
def valid_ai_response():
    """Valid ReviewResult structure"""
    return {
        "summary": "Added password and print statement",
        "findings": [
            {
                "severity": "error",
                "message": "Hardcoded password detected",
                "file": "test.py"
            }
        ]
    }

@pytest.fixture
def mock_gemini_client():
    """Mock Gemini API client"""
    mock = Mock()
    mock.models.generate_content.return_value.text = '{"summary": "Test", "findings": []}'
    return mock

@pytest.fixture
def set_api_key(monkeypatch):
    """Set GEMINI_API_KEY for tests"""
    monkeypatch.setenv("GEMINI_API_KEY", "test-key-123")
