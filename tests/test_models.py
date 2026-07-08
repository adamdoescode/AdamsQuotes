"""
Tests for the Quote dataclass in adamsquotes.models.
"""

from __future__ import annotations

from adamsquotes.models import Quote


class TestQuoteDataclass:
    def test_empty_quote_has_empty_title(self):
        q = Quote()
        q.generate_title()
        assert q.title == ""

    def test_short_quote_uses_full_text(self):
        q = Quote()
        q.quote = "Hello world"
        q.generate_title()
        assert q.title == "Hello world"

    def test_short_quote_exactly_seven_words(self):
        q = Quote()
        q.quote = "one two three four five six seven"
        q.generate_title()
        assert q.title == "one two three four five six seven"

    def test_short_quote_exactly_eight_words(self):
        q = Quote()
        q.quote = "one two three four five six seven eight"
        q.generate_title()
        assert q.title == "one two three four five six seven eight"

    def test_long_quote_truncates_to_eight_words(self):
        q = Quote()
        q.quote = "one two three four five six seven eight nine ten"
        q.generate_title()
        assert q.title == "one two three four five six seven eight..."

    def test_quote_has_random_id(self):
        q1 = Quote()
        q2 = Quote()
        assert q1.id_for_quote != q2.id_for_quote

    def test_default_fields_are_empty_strings(self):
        q = Quote()
        assert q.quote == ""
        assert q.source == ""
        assert q.note == ""
        assert q.link == ""
        assert q.author == ""
        assert q.title == ""

    def test_id_is_five_digit_integer(self):
        q = Quote()
        assert 10000 <= q.id_for_quote <= 99999
