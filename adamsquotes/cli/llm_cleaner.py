"""
CLI entry point for the LLM cleaner stage.

Usage::

    export OPENROUTER_API_KEY="sk-or-..."
    uv run python -m adamsquotes.cli.llm_cleaner
    uv run python -m adamsquotes.cli.llm_cleaner \\
        --input markdown_quotes/new_quotes_tagged.md \\
        --output markdown_quotes/new_quotes_llm_processed.md \\
        --model deepseek/deepseek-v4-flash
"""

from __future__ import annotations

import argparse

from adamsquotes.types import DEFAULT_NEW_INPUT
from adamsquotes.pipeline.llm_cleaner import DEFAULT_MODEL, DEFAULT_OUTPUT


def _build_parser() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Clean tagged markdown quotes using an LLM via OpenRouter.",
    )
    parser.add_argument(
        "--input",
        type=str,
        default=DEFAULT_NEW_INPUT,
        help=f"Path to the tagged markdown input file (default: {DEFAULT_NEW_INPUT}).",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=DEFAULT_OUTPUT,
        help=f"Path for the cleaned markdown output file (default: {DEFAULT_OUTPUT}).",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL,
        help=f"OpenRouter model identifier (default: {DEFAULT_MODEL}).",
    )
    parser.add_argument(
        "--chunk-quotes",
        type=int,
        default=10,
        help="Number of quotes to send per LLM request (default: 10).",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Number of retries per failed API call (default: 3).",
    )
    parser.add_argument(
        "--delay-seconds",
        type=int,
        default=1,
        help="Delay between API calls in seconds (default: 1).",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=5,
        help="Maximum concurrent API requests (default: 5).",
    )
    return parser


def main() -> None:
    """Parse CLI args and run the LLM cleaner pipeline."""
    from adamsquotes.pipeline.llm_cleaner import main as cleaner_main  # noqa: PLC0415

    cleaner_main()


if __name__ == "__main__":
    main()