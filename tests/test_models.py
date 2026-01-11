import pytest
from pydantic import ValidationError
from diffaid.models import Finding, ReviewResult

def test_finding_valid():
    """Test valid Finding creation"""
    finding = Finding(
        severity="error",
        message="Test error",
        file="test.py"
    )
    assert finding.severity == "error"
    assert finding.message == "Test error"

def test_finding_invalid_severity():
    """Test invalid severity raises error"""
    with pytest.raises(ValidationError):
        Finding(severity="critical", message="Test")

def test_review_result_empty_findings():
    """Test ReviewResults with no findings"""
    result = ReviewResult(summary="No issues", findings=[])
    assert result.summary == "No issues"
    assert len(result.findings) == 0

def test_review_result_multiple_findings():
    """Test ReviewResults with multiple findings"""
    result = ReviewResult(
        summary="Found issues",
        findings=[
            Finding(severity="error", message="Error 1"),
            Finding(severity="warning", message="Warning 1"),
            Finding(severity="note", message="Note 1")
        ]
    )
    assert len(result.findings) == 3
