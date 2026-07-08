"""
Send chunks of a tagged quotes markdown file to an LLM for cleanup, then stitch
responses back into a single markdown file.

The intended use is to fix residual formatting issues in files like
``markdown_quotes/new_quotes_tagged.md`` that were produced by earlier,
heuristic-based stages of the pipeline. The LLM is asked to return the same
quotes, cleaned up and consistently formatted, without inventing new content.

Usage::

    export OPENROUTER_API_KEY="sk-or-..."
    uv run python processTaggedQuotesWithLLM.py
    uv run python processTaggedQuotesWithLLM.py \
        --input markdown_quotes/new_quotes_tagged.md \
        --output markdown_quotes/new_quotes_llm_processed.md \
        --model deepseek/deepseek-v4-flash \
        --chunk-quotes 10

The API key is read from the ``OPENROUTER_API_KEY`` environment variable, or
from a ``.env`` file in the repository root (``OPENROUTER_API_KEY=sk-or-...``).
The ``.env`` file is ignored by git so secrets are never committed.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path
from typing import List

import aiohttp
from dotenv import load_dotenv


DEFAULT_MODEL = "deepseek/deepseek-v4-flash"
DEFAULT_CHUNK_QUOTES = 10
DEFAULT_CONCURRENCY = 5
DEFAULT_INPUT = "markdown_quotes/new_quotes_tagged.md"
DEFAULT_OUTPUT = "markdown_quotes/new_quotes_llm_processed.md"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM_PROMPT = """You are a careful text-processing assistant.

Your task is to clean up a chunk of a markdown quotes file. The file uses a
strict tagged format. Each quote has exactly these fields in this order:

*quote:*	<the quote text, may span multiple paragraphs>
*source:*	<book, article, website, or other source>
*author:*	<person who said or wrote the quote, if known>
*link:*	<URL, if any>
*note:*	<personal note or commentary, may span multiple lines>

Rules:
1. Preserve every quote from the input. Do not add new quotes.
2. Preserve the original wording of each quote as closely as possible.
3. Fix obvious formatting problems:
   - Merge lines that were incorrectly hard-wrapped mid-sentence.
   - Keep intentional paragraph breaks (blank lines) within a quote.
   - Move stray attribution text that ended up in the wrong field to the
     correct field (e.g. an author name in *source:* should usually move to
     *author:*, a URL should move to *link:*).
   - If a *source:* field contains both a title and an author, put the author
     in *author:* and the title in *source:* when you can do so confidently.
   - Remove spurious backslash escapes like \" or \\--.
4. Output only the cleaned tagged markdown. Do not add explanations, markdown
   code fences, or any text outside the quote blocks.
5. Keep the exact field tags ``*quote:*\t``, ``*source:*\t``,
   ``*author:*\t``, ``*link:*\t``, ``*note:*\t`` (tab-separated).
6. Leave a blank line between consecutive quotes.
7. If a field is empty, keep the tag and a tab but leave the value blank.
"""


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Clean tagged markdown quotes using an LLM via OpenRouter.",
    )
    parser.add_argument(
        "--input",
        type=str,
        default=DEFAULT_INPUT,
        help=f"Path to the tagged markdown input file (default: {DEFAULT_INPUT}).",
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
        default=DEFAULT_CHUNK_QUOTES,
        help=f"Number of quotes to send per LLM request (default: {DEFAULT_CHUNK_QUOTES}).",
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
        default=DEFAULT_CONCURRENCY,
        help=f"Maximum concurrent API requests (default: {DEFAULT_CONCURRENCY}).",
    )
    return parser


def _read_chunks(input_path: Path, chunk_quotes: int) -> List[str]:
    """Split the input file into chunks of ``chunk_quotes`` quotes each.

    Chunks are aligned to quote boundaries so that no quote is split across two
    chunks. A quote is assumed to start with a line beginning with ``*quote:*``.
    """
    text = input_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    # Find the starting line of each quote block.
    quote_indices = [
        i for i, line in enumerate(lines) if line.strip().startswith("*quote:*")
    ]
    if not quote_indices:
        raise ValueError(f"No *quote:* tags found in {input_path}")

    # Append a sentinel representing the end of the file.
    quote_indices.append(len(lines))

    chunks: List[str] = []
    for i in range(0, len(quote_indices) - 1, chunk_quotes):
        start_line = quote_indices[i]
        # End right before the next quote after this chunk, or the end of file.
        end_index = min(i + chunk_quotes, len(quote_indices) - 1)
        end_line = quote_indices[end_index]
        chunk_lines_subset = lines[start_line:end_line]
        chunks.append("\n".join(chunk_lines_subset).rstrip() + "\n")

    return chunks


async def _call_openrouter(
    session: aiohttp.ClientSession,
    api_key: str,
    model: str,
    user_content: str,
    max_retries: int,
) -> str:
    """Send a single chunk to the OpenRouter chat completions endpoint."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
    }

    last_error: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            async with session.post(
                OPENROUTER_URL,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=120),
            ) as response:
                response.raise_for_status()
                data = await response.json()
                choices = data.get("choices", [])
                if not choices:
                    raise RuntimeError(f"OpenRouter returned no choices: {data}")
                content = choices[0].get("message", {}).get("content", "")
                if content is None:
                    raise RuntimeError("OpenRouter returned empty content")
                return content
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt < max_retries:
                wait = 2 ** (attempt - 1)
                await asyncio.sleep(wait)

    raise RuntimeError(
        f"OpenRouter request failed after {max_retries} attempts: {last_error}"
    ) from last_error


def _strip_code_fences(text: str) -> str:
    """Remove leading/trailing markdown code fences if the LLM added them."""
    stripped = text.strip()
    if stripped.startswith("```"):
        # Drop the opening fence line.
        lines = stripped.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        # Drop the closing fence line if present.
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        elif lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()
    return stripped


def _validate_stitched_output(output_text: str) -> None:
    """Warn if the stitched output does not look like tagged quotes."""
    quote_count = output_text.count("*quote:*")
    source_count = output_text.count("*source:*")
    if quote_count == 0:
        raise ValueError("Stitched output contains no *quote:* tags")
    if abs(quote_count - source_count) > 1:
        print(
            f"Warning: mismatch between *quote:* ({quote_count}) and *source:* ({source_count}) counts",
            file=sys.stderr,
        )


def main() -> None:
    # Load OPENROUTER_API_KEY from a local .env file if present.
    load_dotenv()

    parser = _build_parser()
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if input_path.suffix != ".md":
        parser.error(f"Input file must have a .md suffix, got '{input_path.suffix}'")
    if args.chunk_quotes < 1:
        parser.error("--chunk-quotes must be at least 1")
    if args.concurrency < 1:
        parser.error("--concurrency must be at least 1")

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        parser.error(
            "OPENROUTER_API_KEY is required. Set it as an environment variable "
            "or add it to a .env file in the repository root."
        )

    chunks = _read_chunks(input_path, args.chunk_quotes)
    print(f"Split {input_path} into {len(chunks)} chunk(s)")

    async def _process_chunks() -> List[str]:
        cleaned_parts: List[str] = [""] * len(chunks)
        semaphore = asyncio.Semaphore(args.concurrency)

        async def _process_one(idx: int, chunk: str) -> None:
            async with semaphore:
                print(f"Processing chunk {idx}/{len(chunks)}...")
                cleaned = await _call_openrouter(
                    session=session,
                    api_key=api_key,
                    model=args.model,
                    user_content=chunk,
                    max_retries=args.max_retries,
                )
                cleaned_parts[idx - 1] = _strip_code_fences(cleaned)
                if args.delay_seconds > 0:
                    await asyncio.sleep(args.delay_seconds)

        async with aiohttp.ClientSession() as session:
            await asyncio.gather(
                *(_process_one(idx, chunk) for idx, chunk in enumerate(chunks, start=1))
            )
        return cleaned_parts

    cleaned_parts = asyncio.run(_process_chunks())

    stitched = "\n\n".join(part.strip() for part in cleaned_parts) + "\n"
    _validate_stitched_output(stitched)

    output_path.write_text(stitched, encoding="utf-8")
    print(f"Wrote cleaned quotes to {output_path}")


if __name__ == "__main__":
    main()
