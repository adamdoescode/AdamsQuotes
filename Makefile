.PHONY: validate pages test

validate: pages test

pages:
	bundle exec jekyll build --safe --trace

test:
	uv run pytest
