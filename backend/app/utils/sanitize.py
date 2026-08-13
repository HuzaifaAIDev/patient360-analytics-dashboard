"""
Filename sanitization.

Used anywhere a user-influenced value (a patient name from a query
parameter, for example) ends up in a `Content-Disposition` header or a
server-generated file path. Without this, a value like

    Ali"; filename*=UTF-8''evil\r\nX-Injected: header

interpolated directly into a header string is a header-injection risk, and
values like `../../etc/passwd` interpolated into a file path are a path
traversal risk. This allow-lists safe characters instead of trying to
block-list dangerous ones.
"""
from __future__ import annotations

import re

_UNSAFE_CHARS = re.compile(r"[^A-Za-z0-9 _.\-]")
_WHITESPACE = re.compile(r"\s+")


def safe_filename(value: str | None, fallback: str = "export", max_length: int = 100) -> str:
    """
    Return a filesystem-and-header-safe version of `value`.

    - Strips anything that isn't a letter, digit, space, underscore, hyphen,
      or dot (this alone rules out `/`, `\\`, `..`, quotes, and CR/LF —
      there is no way to smuggle a path separator or a newline through).
    - Collapses whitespace and trims leading/trailing dots/spaces (Windows
      treats trailing dots/spaces specially).
    - Falls back to a safe default if the result would otherwise be empty.
    - Truncates to `max_length` characters.
    """
    if not value:
        return fallback

    cleaned = _UNSAFE_CHARS.sub("", value)
    cleaned = _WHITESPACE.sub(" ", cleaned).strip(" .")
    cleaned = cleaned.replace(" ", "_")

    if not cleaned:
        return fallback

    return cleaned[:max_length]
