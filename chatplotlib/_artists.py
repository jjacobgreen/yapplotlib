"""
Core layout engine for chatplotlib.

ChatThread manages all matplotlib artists that form a rendered conversation.
It uses typographic points as the coordinate unit (1 data unit = 1 pt) so
that FancyBboxPatch corner rounding and internal padding are isotropic
regardless of figure dimensions.

Coordinate convention
---------------------
* x  : 0 → axes_width_pts  (left → right)
* y  : 0 → decreasing (top → bottom)
* ax.set_ylim(y_bottom, y_top) where y_bottom < y_top ≈ 0

On every draw, the y-axis is **not** inverted — we simply use negative y
values for content below the top, then set ylim so the most negative value
is at the visual bottom.
"""

import matplotlib.patches as mpatches

from ._styles import resolve_role_style, get_align
from ._text import wrap_text, wrap_text_accurate, estimate_chars_per_line

# Layout parameter defaults (used when the caller passes None)
_LAYOUT_DEFAULTS = {
    'bubble_width': 0.6,
    'sender_align': None,
    'show_names': True,
    'show_timestamps': False,
    'show_avatars': False,
    'avatar_size': 0.04,
    'line_spacing': 1.4,
    'bubble_spacing': 0.6,
    'pad': 0.05,
    'font_size': None,  # None → inherit from style dict
}


class ChatThread:
    """
    Renders a list of chat messages onto a matplotlib Axes.

    This is not an Artist subclass; it manages patches/texts added directly
    to the axes and re-layouts on figure resize.

    Parameters
    ----------
    messages : list[dict]
    style : dict
        Fully resolved style dict (from _styles.resolve_style).
    ax : matplotlib.axes.Axes
    layout_params : dict
        Layout parameters (see _LAYOUT_DEFAULTS for keys).
    """

    def __init__(self, messages, style, ax, layout_params):
        self._messages = messages
        self._style = style
        self._ax = ax
        self._p = {**_LAYOUT_DEFAULTS, **{k: v for k, v in layout_params.items() if v is not None}}
        self._handles = []        # patches / text artists added to axes
        self._cid_resize = None

        self._do_layout()

        fig = ax.get_figure()
        if fig.canvas is not None:
            self._cid_resize = fig.canvas.mpl_connect(
                'resize_event', self._on_resize
            )

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def disconnect(self):
        """Disconnect the resize callback. Call before discarding."""
        if self._cid_resize is not None:
            try:
                self._ax.get_figure().canvas.mpl_disconnect(self._cid_resize)
            except Exception:
                pass
            self._cid_resize = None

    def redraw(self):
        """Force a full re-layout (e.g. after changing messages or style)."""
        self._do_layout()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _on_resize(self, event):
        self._do_layout()
        try:
            self._ax.get_figure().canvas.draw_idle()
        except Exception:
            pass

    def _ax_width_pts(self):
        """Return the current axes width in typographic points."""
        fig = self._ax.get_figure()
        ax_pos = self._ax.get_position()   # bbox in figure fraction
        return ax_pos.width * fig.get_size_inches()[0] * 72.0

    def _clear(self):
        """Remove all previously added artists from the axes."""
        for h in self._handles:
            try:
                h.remove()
            except (ValueError, AttributeError):
                pass
        self._handles = []

    def _add(self, artist):
        """Add an artist to the axes and track it."""
        self._handles.append(artist)
        return artist

    def _do_layout(self):
        """Compute and draw the full conversation layout."""
        self._clear()

        ax = self._ax
        p = self._p
        s = self._style

        ax_width_pts = self._ax_width_pts()
        if ax_width_pts < 10:
            return  # axes not yet placed on the figure

        # ── Typography ────────────────────────────────────────────────
        font_size = float(p.get('font_size') or s.get('font_size', 10.0))
        font_family = s.get('font_family', 'sans-serif')
        line_spacing = float(p.get('line_spacing', 1.4))
        name_font_size = float(s.get('name_font_size', font_size * 0.8))
        ts_font_size = float(s.get('timestamp_font_size', font_size * 0.7))

        line_height = font_size * line_spacing       # pts per wrapped line
        name_line_h = name_font_size * 1.35          # pts for name label row
        ts_line_h = ts_font_size * 1.30

        # ── Layout geometry (pts) ─────────────────────────────────────
        bubble_spacing_pts = line_height * float(p.get('bubble_spacing', 0.6))
        pad_x = ax_width_pts * float(p.get('pad', 0.05))
        bubble_width_pts = ax_width_pts * float(p.get('bubble_width', 0.6))
        internal_pad_x = font_size * 0.75   # horizontal text inset
        internal_pad_y = font_size * 0.45   # vertical text inset
        round_size = font_size * 0.40       # FancyBboxPatch rounding radius

        # Text column width; try pixel-accurate measurement, fall back to estimate
        text_col_width = bubble_width_pts - 2 * internal_pad_x
        try:
            renderer = ax.get_figure().canvas.get_renderer()
            dpi = ax.get_figure().dpi
            _wrap = lambda content, col_w: wrap_text_accurate(
                content, col_w, font_size, font_family, renderer, dpi
            )
        except Exception:
            _wrap = lambda content, col_w: wrap_text(
                content, estimate_chars_per_line(col_w, font_size, font_family)
            )

        show_names = bool(p.get('show_names', True))
        show_timestamps = bool(p.get('show_timestamps', False))
        sender_align = p.get('sender_align', None)

        # ── Coordinate system ─────────────────────────────────────────
        # x: 0 … ax_width_pts
        # y: starts at 0 (top), decreases downward (values become negative)
        ax.set_xlim(0, ax_width_pts)

        y_cursor = 0.0  # top of next element to place

        # ── Place each message ────────────────────────────────────────
        for msg in self._messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            name_display = msg.get('name', role)
            timestamp = msg.get('timestamp', None)
            msg_style = msg.get('style', {})

            # Merge per-message style override
            effective_style = {**s, **msg_style}
            role_s = resolve_role_style(role, effective_style)
            align = get_align(role, sender_align)

            # ── Wrap text ─────────────────────────────────────────────
            # System / center messages get a wider text column
            if align == 'center':
                center_bw = min(bubble_width_pts * 0.85, ax_width_pts * 0.80)
                col_w = center_bw - 2 * internal_pad_x
            else:
                center_bw = None
                col_w = text_col_width

            lines = _wrap(content, col_w)
            n_lines = len(lines)

            text_block_h = n_lines * line_height
            bubble_h = text_block_h + 2 * internal_pad_y

            # ── X bounds ──────────────────────────────────────────────
            if align == 'right':
                bw = bubble_width_pts
                bx0 = ax_width_pts - pad_x - bw
                bx1 = ax_width_pts - pad_x
            elif align == 'left':
                bw = bubble_width_pts
                bx0 = pad_x
                bx1 = pad_x + bw
            else:  # center
                bw = center_bw
                bx0 = (ax_width_pts - bw) / 2
                bx1 = bx0 + bw

            # ── Name label (above bubble) ─────────────────────────────
            if show_names and align != 'center':
                name_x = bx1 if align == 'right' else bx0
                name_ha = 'right' if align == 'right' else 'left'
                nt = ax.text(
                    name_x, y_cursor, name_display,
                    fontsize=name_font_size,
                    fontfamily=font_family,
                    color=role_s['textcolor'],
                    alpha=s.get('name_alpha', 0.65),
                    ha=name_ha,
                    va='top',
                    clip_on=False,
                    zorder=3,
                )
                self._add(nt)
                y_cursor -= name_line_h  # full label height; bubble starts below

            # ── Bubble body ───────────────────────────────────────────
            bubble_top = y_cursor
            bubble_bot = y_cursor - bubble_h

            ec = role_s['edgecolor']
            lw = s.get('bubble_lw', 0.8) if ec != 'none' else 0

            patch = mpatches.FancyBboxPatch(
                (bx0, bubble_bot),
                bw,
                bubble_h,
                boxstyle=f'round,pad=0,rounding_size={round_size}',
                facecolor=role_s['facecolor'],
                edgecolor='none' if ec == 'none' else ec,
                linewidth=lw,
                clip_on=False,
                zorder=2,
            )
            ax.add_patch(patch)
            self._add(patch)

            # ── Tail triangle ─────────────────────────────────────────
            # A small nubbin pointing outward from the bottom corner.
            if align != 'center':
                tail_h = font_size * 0.55
                tail_w = font_size * 0.45
                # Anchor the tail at the bottom corner of the bubble
                tail_anchor_y = bubble_bot + round_size + tail_h * 0.15

                if align == 'right':
                    verts = [
                        (bx1 - round_size, tail_anchor_y + tail_h * 0.55),
                        (bx1 - round_size, tail_anchor_y - tail_h * 0.15),
                        (bx1 + tail_w,     tail_anchor_y + tail_h * 0.20),
                    ]
                else:
                    verts = [
                        (bx0 + round_size, tail_anchor_y + tail_h * 0.55),
                        (bx0 + round_size, tail_anchor_y - tail_h * 0.15),
                        (bx0 - tail_w,     tail_anchor_y + tail_h * 0.20),
                    ]

                tail = mpatches.Polygon(
                    verts,
                    closed=True,
                    facecolor=role_s['facecolor'],
                    edgecolor='none',
                    clip_on=False,
                    zorder=1,
                )
                ax.add_patch(tail)
                self._add(tail)

            # ── Message text ──────────────────────────────────────────
            text_x = bx0 + internal_pad_x
            text_y = bubble_top - internal_pad_y

            for line in lines:
                t = ax.text(
                    text_x, text_y, line,
                    fontsize=font_size,
                    fontfamily=font_family,
                    color=role_s['textcolor'],
                    ha='left',
                    va='top',
                    clip_on=False,
                    zorder=3,
                )
                self._add(t)
                text_y -= line_height

            y_cursor = bubble_bot

            # ── Timestamp ─────────────────────────────────────────────
            if show_timestamps and timestamp:
                y_cursor -= ts_line_h * 0.20
                ts_x = bx1 if align == 'right' else bx0
                ts_ha = 'right' if align == 'right' else 'left'
                ts = ax.text(
                    ts_x, y_cursor, timestamp,
                    fontsize=ts_font_size,
                    fontfamily=font_family,
                    color=role_s['textcolor'],
                    alpha=s.get('timestamp_alpha', 0.5),
                    ha=ts_ha,
                    va='top',
                    clip_on=False,
                    zorder=3,
                )
                self._add(ts)
                y_cursor -= ts_line_h

            # ── Gap between messages ──────────────────────────────────
            y_cursor -= bubble_spacing_pts

        # ── Set final ylim ────────────────────────────────────────────
        top_pad = internal_pad_y * 2.0
        bot_pad = bubble_spacing_pts * 1.5

        # y_cursor is now below all content (most negative value)
        ax.set_ylim(y_cursor - bot_pad, top_pad)

        # ── Axes cosmetics ────────────────────────────────────────────
        ax.set_axis_off()
        ax.set_facecolor(s.get('axes_facecolor', 'white'))
