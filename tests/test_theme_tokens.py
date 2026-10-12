"""
Tests that style.css only uses colour tokens the shared theme defines.

theme.css is vendored from adamdoescode.github.io/assets/theme.css. Set
THEME_CSS to check a different copy (``make check-theme`` uses the live one).
"""

from __future__ import annotations

import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
THEME_CSS = Path(os.environ.get("THEME_CSS", ROOT / "theme.css"))
STYLE_CSS = ROOT / "style.css"

VAR_USE = re.compile(r"var\(\s*(--[\w-]+)")
VAR_DEFINITION = re.compile(r"(--[\w-]+)\s*:")


def _strip_comments(css: str) -> str:
    return re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)


def test_style_uses_only_defined_theme_tokens():
    style = _strip_comments(STYLE_CSS.read_text(encoding="utf-8"))
    theme = _strip_comments(THEME_CSS.read_text(encoding="utf-8"))
    defined = set(VAR_DEFINITION.findall(theme)) | set(VAR_DEFINITION.findall(style))
    used = set(VAR_USE.findall(style))
    assert used, "style.css should consume theme tokens"
    assert sorted(used - defined) == []


def test_theme_defines_dark_mode():
    theme = THEME_CSS.read_text(encoding="utf-8")
    assert "prefers-color-scheme: dark" in theme
