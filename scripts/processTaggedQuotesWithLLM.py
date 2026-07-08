"""
Backward-compatible wrapper.  Delegates to ``adamsquotes.pipeline.llm_cleaner``.

Usage::

    export OPENROUTER_API_KEY="sk-or-..."
    uv run python processTaggedQuotesWithLLM.py
"""

from __future__ import annotations

from adamsquotes.pipeline.llm_cleaner import main as main  # noqa: F401
from adamsquotes.pipeline.llm_cleaner import (
    DEFAULT_MODEL as DEFAULT_MODEL,  # noqa: F401
    DEFAULT_OUTPUT as DEFAULT_OUTPUT,  # noqa: F401
    SYSTEM_PROMPT as SYSTEM_PROMPT,  # noqa: F401
)

if __name__ == "__main__":
    main()
