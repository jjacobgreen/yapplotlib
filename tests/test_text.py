"""
Tests for text wrapping utilities.
"""

from yapplotlib._text import estimate_chars_per_line, wrap_text


class TestWrapText:
    def test_empty_string(self):
        assert wrap_text("", 40) == [""]

    def test_short_string_no_wrap(self):
        result = wrap_text("Hello world", 40)
        assert result == ["Hello world"]

    def test_long_string_wraps(self):
        long = "word " * 20
        result = wrap_text(long.strip(), 20)
        assert len(result) > 1
        for line in result:
            assert len(line) <= 20

    def test_hard_newlines_preserved(self):
        result = wrap_text("Line one\nLine two", 80)
        assert "Line one" in result
        assert "Line two" in result

    def test_blank_lines_preserved(self):
        result = wrap_text("Para one\n\nPara two", 80)
        assert "" in result

    def test_max_chars_one(self):
        # Should not crash with very small max_chars
        result = wrap_text("hello", 1)
        assert all(isinstance(line, str) for line in result)

    def test_returns_list_of_strings(self):
        result = wrap_text("Some text here", 30)
        assert isinstance(result, list)
        assert all(isinstance(line, str) for line in result)


class TestEstimateCharsPerLine:
    def test_returns_positive_int(self):
        result = estimate_chars_per_line(200, 10)
        assert isinstance(result, int)
        assert result > 0

    def test_monospace_narrower(self):
        mono = estimate_chars_per_line(200, 10, "monospace")
        sans = estimate_chars_per_line(200, 10, "sans-serif")
        # monospace chars are wider → fewer fit
        assert mono <= sans

    def test_minimum_chars(self):
        # Even tiny widths return at least 8
        result = estimate_chars_per_line(1, 100)
        assert result >= 8

    def test_wider_means_more_chars(self):
        narrow = estimate_chars_per_line(100, 10)
        wide = estimate_chars_per_line(400, 10)
        assert wide > narrow
