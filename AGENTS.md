# Repository Guidelines

## Project Structure & Module Organization

`adamsquotes/` contains the installable Python package. CLI entry points live in `adamsquotes/cli/`, while reusable pipeline logic lives in `adamsquotes/pipeline/`; shared models, path constants, and text helpers are in `models.py`, `types.py`, and `text_utils.py`. Tests are in `tests/` and mirror the package concerns with files such as `test_html_renderer.py` and `test_tagger.py`. Quote inputs and curated markdown live in `markdown_quotes/`. Root-level `Header.html`, `style.css`, `index.js`, and generated `index.html` make up the rendered site. `scripts/` keeps backward-compatible legacy wrappers; prefer adding new logic to the package.

## Build, Test, and Development Commands

Use `uv` for all local Python workflows.

- `uv sync` installs project and dev dependencies from `pyproject.toml` and `uv.lock`.
- `uv run pytest` runs the full test suite configured under `tests/`.
- `uv run adamsquotes-tag` tags raw quote markdown into semi-processed markdown.
- `uv run adamsquotes-convert` converts newer raw quote formats into tagged markdown.
- `uv run adamsquotes-clean` runs the OpenRouter-backed cleanup pipeline.
- `uv run adamsquotes-render` renders processed markdown to `index.html`.

## Coding Style & Naming Conventions

Target Python 3.14. Use 4-space indentation, type hints where practical, and `from __future__ import annotations` in new modules to match the current package style. Keep CLI modules thin: parse command-line concerns in `adamsquotes/cli/` and place testable behavior in `adamsquotes/pipeline/`. Use snake_case for functions, modules, and variables; use PascalCase for classes.

## Testing Guidelines

The project uses `pytest`. Add focused tests in `tests/test_<feature>.py`, with test functions named `test_<expected_behavior>`. Prefer small fixtures or constants in `tests/conftest.py` over duplicating markdown or HTML samples. Run `uv run pytest` before submitting changes, especially when touching parsing, rendering, or path defaults.

## Commit & Pull Request Guidelines

Recent commits use short, descriptive subjects, often prefixed with an issue reference such as `#11 move legacy scripts to a scripts folder` or a phase label for larger refactors. Keep commits scoped and explain user-visible behavior changes. Pull requests should include a concise summary, linked issue when applicable, test results, and screenshots or generated `index.html` notes when the rendered site changes.

## Security & Configuration Tips

Do not commit `.env`, API keys, or local virtual environments. The LLM cleanup stage expects `OPENROUTER_API_KEY` in the environment. Generated caches such as `__pycache__/`, `.pytest_cache/`, and build metadata should remain out of review unless intentionally changing packaging behavior.
