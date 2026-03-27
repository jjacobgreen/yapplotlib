"""
Tests for text wrapping and segment splitting utilities.
"""

import pytest
from yapplotlib._text import (
    wrap_text,
    estimate_chars_per_line,
    split_content_segments,
)


class TestWrapText:
    def test_empty_string(self):
        assert wrap_text('', 40) == ['']

    def test_short_string_no_wrap(self):
        result = wrap_text('Hello world', 40)
        assert result == ['Hello world']

    def test_long_string_wraps(self):
        long = 'word ' * 20
        result = wrap_text(long.strip(), 20)
        assert len(result) > 1
        for line in result:
            assert len(line) <= 20

    def test_hard_newlines_preserved(self):
        result = wrap_text('Line one\nLine two', 80)
        assert 'Line one' in result
        assert 'Line two' in result

    def test_blank_lines_preserved(self):
        result = wrap_text('Para one\n\nPara two', 80)
        assert '' in result

    def test_max_chars_one(self):
        # Should not crash with very small max_chars
        result = wrap_text('hello', 1)
        assert all(isinstance(l, str) for l in result)

    def test_returns_list_of_strings(self):
        result = wrap_text('Some text here', 30)
        assert isinstance(result, list)
        assert all(isinstance(l, str) for l in result)


class TestEstimateCharsPerLine:
    def test_returns_positive_int(self):
        result = estimate_chars_per_line(200, 10)
        assert isinstance(result, int)
        assert result > 0

    def test_monospace_narrower(self):
        mono  = estimate_chars_per_line(200, 10, 'monospace')
        sans  = estimate_chars_per_line(200, 10, 'sans-serif')
        # monospace chars are wider → fewer fit
        assert mono <= sans

    def test_minimum_chars(self):
        # Even tiny widths return at least 8
        result = estimate_chars_per_line(1, 100)
        assert result >= 8

    def test_wider_means_more_chars(self):
        narrow = estimate_chars_per_line(100, 10)
        wide   = estimate_chars_per_line(400, 10)
        assert wide > narrow


class TestSplitContentSegments:
    def test_plain_text_no_code(self):
        result = split_content_segments('Hello world')
        assert result == [('text', 'Hello world')]

    def test_single_code_block(self):
        content = 'Before\n```python\nx = 1\n```\nAfter'
        segs = split_content_segments(content)
        kinds = [k for k, _ in segs]
        assert 'code' in kinds
        assert 'text' in kinds

    def test_code_block_inner_text(self):
        content = '```\nprint("hello")\n```'
        segs = split_content_segments(content)
        assert len(segs) == 1
        assert segs[0][0] == 'code'
        assert 'print("hello")' in segs[0][1]

    def test_language_tag_stripped(self):
        content = '```python\nx = 1\n```'
        segs = split_content_segments(content)
        assert segs[0][0] == 'code'
        assert 'python' not in segs[0][1]

    def test_multiple_code_blocks(self):
        content = 'A\n```\ncode1\n```\nB\n```\ncode2\n```\nC'
        segs = split_content_segments(content)
        codes = [t for k, t in segs if k == 'code']
        assert len(codes) == 2
        assert 'code1' in codes[0]
        assert 'code2' in codes[1]

    def test_empty_string(self):
        result = split_content_segments('')
        assert result == [('text', '')]

    def test_returns_list_of_tuples(self):
        result = split_content_segments('plain')
        assert isinstance(result, list)
        assert all(isinstance(t, tuple) and len(t) == 2 for t in result)
