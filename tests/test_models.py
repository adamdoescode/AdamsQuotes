"""
Tests for the Quote dataclass in adamsquotes.models.
"""

from __future__ import annotations

from adamsquotes.models import Quote, assign_stable_ids


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

    def test_content_id_is_deterministic(self):
        q1 = Quote(quote="Same", source="Book", author="Writer")
        q2 = Quote(quote="Same", source="Book", author="Writer")
        assert q1.content_id() == q2.content_id()

    def test_content_id_depends_on_source_and_author(self):
        base = Quote(quote="Same", source="Book", author="Writer")
        assert base.content_id() != Quote(quote="Same", source="Other", author="Writer").content_id()
        assert base.content_id() != Quote(quote="Same", source="Book", author="Other").content_id()

    def test_content_id_is_valid_html_anchor(self):
        anchor = Quote(quote="x").content_id()
        assert anchor.startswith("q") and anchor[1:].isalnum()

    def test_default_fields_are_empty_strings(self):
        q = Quote()
        assert q.quote == ""
        assert q.source == ""
        assert q.note == ""
        assert q.link == ""
        assert q.author == ""
        assert q.tags == []
        assert q.title == ""


class TestAssignStableIds:
    def test_duplicate_quotes_get_unique_suffixed_ids(self):
        quotes = [Quote(quote="dup"), Quote(quote="other"), Quote(quote="dup")]
        assign_stable_ids(quotes)
        ids = [q.id_for_quote for q in quotes]
        assert len(set(ids)) == 3
        assert ids[2] == f"{ids[0]}-2"

    def test_ids_do_not_depend_on_neighbours(self):
        first = [Quote(quote="a"), Quote(quote="b")]
        second = [Quote(quote="b")]
        assign_stable_ids(first)
        assign_stable_ids(second)
        assert first[1].id_for_quote == second[0].id_for_quote
