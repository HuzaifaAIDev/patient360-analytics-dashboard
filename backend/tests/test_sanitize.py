"""Unit tests for the filename sanitization utility."""
from __future__ import annotations

from app.utils.sanitize import safe_filename


def test_normal_name_passes_through_with_underscores():
    assert safe_filename("Ali Saleem") == "Ali_Saleem"


def test_none_returns_fallback():
    assert safe_filename(None) == "export"
    assert safe_filename(None, fallback="dataset") == "dataset"


def test_empty_string_returns_fallback():
    assert safe_filename("") == "export"
    assert safe_filename("   ") == "export"


def test_strips_path_traversal_attempts():
    result = safe_filename("../../etc/passwd")
    assert "/" not in result
    assert ".." not in result


def test_strips_windows_path_traversal():
    result = safe_filename("..\\..\\windows\\system32")
    assert "\\" not in result
    assert ".." not in result


def test_strips_header_injection_characters():
    malicious = 'Ali"; filename*=UTF-8\'\'evil\r\nX-Injected: header'
    result = safe_filename(malicious)
    assert "\r" not in result
    assert "\n" not in result
    assert '"' not in result
    assert ";" not in result
    assert "'" not in result
    assert ":" not in result


def test_truncates_to_max_length():
    long_name = "A" * 500
    result = safe_filename(long_name, max_length=50)
    assert len(result) == 50


def test_preserves_legitimate_punctuation():
    # "Dr. Ahmed" style names with a period should survive (dots are safe
    # once slashes are stripped, since there's no separator left to combine
    # them into a traversal sequence).
    result = safe_filename("Dr. Ahmed")
    assert result == "Dr._Ahmed"
