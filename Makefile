.PHONY: validate pages test check-theme

THEME_URL := https://adamdoescode.github.io/assets/theme.css

validate: pages test

pages:
	bundle exec jekyll build --safe --trace

test:
	uv run pytest

# Needs network: checks style.css against the live homepage theme, not the vendored copy.
check-theme:
	@tmp=$$(mktemp); trap 'rm -f "$$tmp"' EXIT; \
	curl -fsSL $(THEME_URL) -o "$$tmp" && \
	THEME_CSS="$$tmp" uv run pytest -q tests/test_theme_tokens.py
