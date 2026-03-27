"""
Text wrapping and measurement utilities for chatplotlib.

Provides both a fast character-count fallback and pixel-accurate wrapping
via the matplotlib renderer's font metrics.
"""

import textwrap
from matplotlib.font_manager import FontProperties


def wrap_text(content, max_chars):
    """
    Wrap *content* so no line exceeds *max_chars* characters.

    Hard newlines in the source are preserved. Returns a list of strings
    (never empty — a blank content string returns ['']).
    """
    if not content:
        return ['']
    max_chars = max(1, int(max_chars))
    lines = []
    for para in content.split('\n'):
        if para.strip() == '':
            lines.append('')
        else:
            wrapped = textwrap.wrap(
                para,
                width=max_chars,
                break_long_words=True,
                break_on_hyphens=True,
                expand_tabs=True,
            )
            lines.extend(wrapped or [''])
    return lines


def wrap_text_accurate(content, max_width_pts, font_size, font_family, renderer, dpi):
    """
    Wrap *content* using actual font metrics from the matplotlib renderer.

    Performs a greedy word-wrap: adds words until the line would exceed
    *max_width_pts*, then starts a new line.  Hard newlines are preserved.

    Uses ``renderer.get_text_width_height_descent`` — a lightweight font
    metrics call, not a full render — so it's fast even for long messages.

    Parameters
    ----------
    content : str
    max_width_pts : float
        Available column width in typographic points.
    font_size : float
        Font size in points.
    font_family : str
    renderer : matplotlib renderer
        Obtained via ``fig.canvas.get_renderer()``.
    dpi : float
        Figure DPI, used to convert renderer pixels → points.

    Returns
    -------
    list[str]
    """
    if not content:
        return ['']

    prop = FontProperties(family=font_family, size=font_size)
    pts_per_px = 72.0 / dpi

    def measure_pts(s):
        w_px, _, _ = renderer.get_text_width_height_descent(s, prop, ismath=False)
        return w_px * pts_per_px

    lines = []
    for para in content.split('\n'):
        words = para.split()
        if not words:
            lines.append('')
            continue

        current = []
        for word in words:
            candidate = ' '.join(current + [word])
            if not current or measure_pts(candidate) <= max_width_pts:
                current.append(word)
            else:
                lines.append(' '.join(current))
                current = [word]
        if current:
            lines.append(' '.join(current))

    return lines or ['']


def estimate_chars_per_line(width_pts, font_size, font_family='sans-serif'):
    """
    Fallback character-count estimate used when no renderer is available.
    """
    if 'mono' in font_family.lower():
        char_factor = 0.60
    elif 'serif' in font_family.lower():
        char_factor = 0.50
    else:
        char_factor = 0.55
    return max(8, int(width_pts / (font_size * char_factor)))
