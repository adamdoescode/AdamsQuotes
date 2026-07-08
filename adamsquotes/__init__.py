"""
adamsquotes — a pipeline for processing and rendering a personal quote collection.

Stages:
    1. ``tagger``      — Raw quotes → semi-processed tagged markdown
    2. ``converter``   — New-format raw quotes → tagged markdown
    3. ``llm_cleaner`` — LLM cleanup of tagged markdown
    4. ``html_renderer`` — Tagged markdown → styled HTML page
"""