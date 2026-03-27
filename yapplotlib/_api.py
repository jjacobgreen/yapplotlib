"""
Public API functions and the Axes.chat_thread method for yapplotlib.
"""

import matplotlib
import matplotlib.pyplot as plt

from ._styles import resolve_style
from ._artists import ChatThread

# Keys that can be passed from chat_thread() kwargs to ax.chat_thread()
_LAYOUT_KEYS = (
    'bubble_width', 'sender_align', 'show_names', 'show_timestamps',
    'show_avatars', 'avatar_size', 'line_spacing', 'bubble_spacing',
    'pad', 'font_size',
)


def _rc(key, fallback):
    """Read a yapplotlib rcParam, falling back to *fallback* if not set."""
    try:
        return matplotlib.rcParams[f'yapplotlib.{key}']
    except KeyError:
        return fallback


def _ax_chat_thread(
    self,
    messages,
    *,
    style=None,
    bubble_width=None,
    sender_align=None,
    show_names=None,
    show_timestamps=None,
    show_avatars=None,
    avatar_size=None,
    line_spacing=None,
    bubble_spacing=None,
    pad=None,
    font_size=None,
):
    """
    Render a chat thread on this Axes.

    This method is injected onto ``matplotlib.axes.Axes`` when yapplotlib
    is imported, so you can call it as ``ax.chat_thread(messages, ...)``.

    Parameters
    ----------
    messages : list[dict]
        Conversation messages. Each dict must have at least::

            {'role': 'user', 'content': 'Hello!'}

        Optional keys: ``'name'`` (display name override), ``'timestamp'``
        (shown when *show_timestamps* is True), ``'style'`` (per-message
        style dict that merges with the active theme).

    style : str or dict, optional
        Theme name (``'default'``, ``'paper'``, ``'dark'``, ``'minimal'``)
        or a partial style dict. Partial dicts are merged on top of
        ``'default'``. Default: rcParam ``yapplotlib.style`` (initially
        ``'default'``).

    bubble_width : float, optional
        Maximum bubble width as a fraction of axes width.
        Default: rcParam ``yapplotlib.bubble_width`` (0.6).

    sender_align : dict, optional
        Maps role names to ``'left'``, ``'right'``, or ``'center'``.
        By default: user → right, assistant → left, system → center.

    show_names : bool, optional
        Show sender name labels above each bubble.
        Default: rcParam ``yapplotlib.show_names`` (True).

    show_timestamps : bool, optional
        Show timestamp strings (requires ``'timestamp'`` key in messages).
        Default: rcParam ``yapplotlib.show_timestamps`` (False).

    show_avatars : bool, optional
        Show circular avatar badges with role initials.
        Default: rcParam ``yapplotlib.show_avatars`` (False).

    line_spacing : float, optional
        Line spacing multiplier.
        Default: rcParam ``yapplotlib.line_spacing`` (1.4).

    bubble_spacing : float, optional
        Gap between consecutive bubbles, expressed in line-heights.
        Default: rcParam ``yapplotlib.bubble_spacing`` (0.6).

    pad : float, optional
        Left/right edge padding as a fraction of axes width.
        Default: rcParam ``yapplotlib.pad`` (0.05).

    font_size : float, optional
        Font size in points. ``None`` inherits from the active style.

    Returns
    -------
    ChatThread
        The thread object, which exposes ``redraw()`` and ``disconnect()``.
    """
    # Apply rcParam defaults for any argument left as None
    if style is None:
        style = _rc('style', 'default')

    resolved_style = resolve_style(style)

    layout_params = {
        k: v for k, v in {
            'bubble_width':    bubble_width    if bubble_width    is not None else _rc('bubble_width',    0.6),
            'sender_align':    sender_align,
            'show_names':      show_names      if show_names      is not None else _rc('show_names',      True),
            'show_timestamps': show_timestamps if show_timestamps is not None else _rc('show_timestamps', False),
            'show_avatars':    show_avatars    if show_avatars    is not None else _rc('show_avatars',    False),
            'avatar_size':     avatar_size,
            'line_spacing':    line_spacing    if line_spacing    is not None else _rc('line_spacing',    1.4),
            'bubble_spacing':  bubble_spacing  if bubble_spacing  is not None else _rc('bubble_spacing',  0.6),
            'pad':             pad             if pad             is not None else _rc('pad',             0.05),
            'font_size':       font_size       if font_size       is not None else _rc('font_size',       None),
        }.items()
        if v is not None
    }

    # Apply figure/axes background colours from style
    fig = self.get_figure()
    fig.patch.set_facecolor(resolved_style.get('figure_facecolor', 'white'))
    self.set_facecolor(resolved_style.get('axes_facecolor', 'white'))

    return ChatThread(messages, resolved_style, self, layout_params)


def chat_thread(
    messages,
    *,
    figsize=None,
    dpi=150,
    style=None,
    **kwargs,
):
    """
    Render a chat thread as a standalone figure.

    Creates a new matplotlib Figure and Axes, renders the conversation,
    and optionally auto-sizes the figure height to fit the content.

    Parameters
    ----------
    messages : list[dict]
        Conversation messages (see ``ax.chat_thread`` for format).

    figsize : (float, float), optional
        Figure ``(width, height)`` in inches. If *None*, width defaults to
        5 inches and height is automatically computed from the content.

    dpi : int, optional
        Figure resolution in dots per inch. Default: 150.

    style : str or dict, optional
        Theme name or style dict. Default: ``'default'``.

    **kwargs
        All keyword arguments accepted by ``ax.chat_thread()``
        (``bubble_width``, ``show_names``, ``style``, etc.).

    Returns
    -------
    fig : matplotlib.figure.Figure
    ax  : matplotlib.axes.Axes
    """
    fig_w = figsize[0] if figsize is not None else 5.0
    fig_h = figsize[1] if figsize is not None else 9.0

    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=dpi)
    # Maximise axes area; chat display needs no tick labels or titles
    fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02)

    thread = ax.chat_thread(messages, style=style, **kwargs)

    if figsize is None:
        _autosize_figure(fig, thread)

    return fig, ax


def _autosize_figure(fig, thread):
    """
    Resize the figure height so it exactly fits the laid-out content.

    Reads the current ylim (which ChatThread sets to the content extent),
    converts to inches at the figure's DPI, then sets the new figure height
    and re-runs the layout at the correct size.
    """
    # Need a renderer to trigger layout; draw_idle may not be enough
    fig.canvas.draw()

    ax = thread._ax
    ymin, ymax = ax.get_ylim()
    content_pts = abs(ymax - ymin)   # ylim is in pt units

    # Convert content height from pts to inches, add a small margin
    margin_pts = 14
    new_h = (content_pts + 2 * margin_pts) / 72.0

    # Clamp to a sane range
    new_h = max(1.5, min(new_h, 40.0))

    fig_w = fig.get_size_inches()[0]
    fig.set_size_inches(fig_w, new_h)

    # Re-layout at the new size so text positions are correct
    thread._do_layout()
