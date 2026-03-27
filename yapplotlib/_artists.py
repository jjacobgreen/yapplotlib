"""
Core layout engine for yapplotlib.

Coordinate system
-----------------
1 data unit = 1 typographic point in both axes, so FancyBboxPatch corner
rounding is isotropic.  The axes x-range is always [0, axes_width_pts];
y starts at 0 (top of content) and decreases as messages stack downward.
ax.set_ylim(y_content_bottom, small_positive) keeps the view correct.

Tight-layout compatibility
--------------------------
A draw_event callback detects when tight_layout (or any other mechanism)
has changed the axes width and schedules a relayout via draw_idle().
"""

import matplotlib.patches as mpatches

from ._styles import resolve_role_style, get_align
from ._text import wrap_text, wrap_text_accurate, estimate_chars_per_line, split_content_segments

_LAYOUT_DEFAULTS = {
    'bubble_width': 0.6,
    'sender_align': None,
    'show_names': True,
    'show_timestamps': False,
    'show_avatars': False,
    'avatar_size': None,   # None → derived from font_size
    'line_spacing': 1.4,
    'bubble_spacing': 0.6,
    'pad': 0.05,
    'font_size': None,
}


def _initials(name):
    """Return up to two uppercase initials from a display name."""
    words = name.split()
    return ''.join(w[0].upper() for w in words if w)[:2] or '?'


class ChatThread:
    """
    Renders a list of chat messages onto a matplotlib Axes.

    Not an Artist subclass — manages patches/texts added directly to the
    axes and re-layouts whenever the axes width changes.
    """

    def __init__(self, messages, style, ax, layout_params):
        self._messages = messages
        self._style = style
        self._ax = ax
        self._p = {
            **_LAYOUT_DEFAULTS,
            **{k: v for k, v in layout_params.items() if v is not None},
        }
        self._handles = []
        self._last_ax_width = None
        self._relayout_pending = False
        self._cid_resize = None
        self._cid_draw = None

        self._do_layout()

        fig = ax.get_figure()
        if fig.canvas is not None:
            self._cid_resize = fig.canvas.mpl_connect(
                'resize_event', self._on_resize
            )
            self._cid_draw = fig.canvas.mpl_connect(
                'draw_event', self._on_draw
            )

    # ── Public ────────────────────────────────────────────────────────

    def disconnect(self):
        """Disconnect all event callbacks."""
        fig = self._ax.get_figure()
        if fig.canvas is not None:
            for cid in (self._cid_resize, self._cid_draw):
                if cid is not None:
                    try:
                        fig.canvas.mpl_disconnect(cid)
                    except Exception:
                        pass
        self._cid_resize = self._cid_draw = None

    def redraw(self):
        """Force a full re-layout (call after changing messages or style)."""
        self._do_layout()

    def get_children(self):
        """
        Return all matplotlib artists managed by this ChatThread.

        Useful for artist introspection, hit-testing, and save/restore
        workflows. The list is rebuilt on every layout pass, so call this
        after any ``redraw()`` to get the current set.

        Returns
        -------
        list
            Shallow copy of the internal handle list (patches and Text
            objects currently added to the axes).
        """
        return list(self._handles)

    # ── Event callbacks ───────────────────────────────────────────────

    def _on_resize(self, event):
        self._do_layout()
        try:
            self._ax.get_figure().canvas.draw_idle()
        except Exception:
            pass

    def _on_draw(self, event):
        """
        Detect axes-width changes caused by tight_layout / constrained_layout.
        We update the artist graph here but do NOT call draw() or draw_idle()
        inside the callback to avoid re-entrant rendering.  The relayout takes
        effect on the next draw triggered by the caller (interactive redraw,
        subsequent savefig, etc.).
        """
        if self._relayout_pending:
            return
        new_w = self._ax_width_pts()
        if self._last_ax_width is not None and abs(new_w - self._last_ax_width) > 1.0:
            self._relayout_pending = True
            self._do_layout()
            self._relayout_pending = False
            try:
                event.canvas.draw_idle()
            except Exception:
                pass

    # ── Geometry helpers ──────────────────────────────────────────────

    def _ax_width_pts(self):
        fig = self._ax.get_figure()
        pos = self._ax.get_position()
        return pos.width * fig.get_size_inches()[0] * 72.0

    def _clear(self):
        for h in self._handles:
            try:
                h.remove()
            except (ValueError, AttributeError):
                pass
        self._handles = []

    def _add(self, artist):
        self._handles.append(artist)
        return artist

    # ── Content helpers ───────────────────────────────────────────────

    def _make_wrap_fn(self, ax, font_size, font_family):
        """Return a wrapping callable, using renderer when available."""
        try:
            renderer = ax.get_figure().canvas.get_renderer()
            dpi = ax.get_figure().dpi
            return lambda text, width_pts: wrap_text_accurate(
                text, width_pts, font_size, font_family, renderer, dpi
            )
        except Exception:
            return lambda text, width_pts: wrap_text(
                text, estimate_chars_per_line(width_pts, font_size, font_family)
            )

    def _measure_segments(self, segments, col_w, line_h, code_line_h,
                          code_inner_pad, code_gap, wrap_fn):
        """Return total content height in pts (excludes bubble top/bottom padding)."""
        total = 0.0
        for i, (kind, text) in enumerate(segments):
            if kind == 'code':
                n = max(1, len(text.split('\n')))
                total += 2 * code_inner_pad + n * code_line_h
                if i > 0:
                    total += code_gap
                if i < len(segments) - 1:
                    total += code_gap
            else:
                stripped = text.strip()
                lines = wrap_fn(stripped, col_w) if stripped else []
                total += len(lines) * line_h
        return total

    def _render_segments(self, segments, ax, bx0, bw, text_x, y_top, col_w,
                         font_size, font_family, text_color,
                         code_facecolor, code_edgecolor, code_lw,
                         line_h, code_line_h, code_inner_pad, code_gap,
                         internal_pad_x, wrap_fn):
        """Draw all content segments; returns height consumed."""
        y = y_top
        for i, (kind, text) in enumerate(segments):
            if kind == 'code':
                if i > 0:
                    y -= code_gap
                code_lines = text.split('\n') or ['']
                n = len(code_lines)
                block_h = 2 * code_inner_pad + n * code_line_h
                rx0 = bx0 + internal_pad_x * 0.4
                rw = bw - internal_pad_x * 0.8
                bg = mpatches.FancyBboxPatch(
                    (rx0, y - block_h), rw, block_h,
                    boxstyle=f'round,pad=0,rounding_size={font_size * 0.15}',
                    facecolor=code_facecolor,
                    edgecolor='none' if code_edgecolor == 'none' else code_edgecolor,
                    linewidth=0 if code_edgecolor == 'none' else code_lw,
                    clip_on=False, zorder=2.5,
                )
                ax.add_patch(bg)
                self._add(bg)
                cy = y - code_inner_pad
                for line in code_lines:
                    t = ax.text(
                        rx0 + font_size * 0.4, cy, line,
                        fontsize=font_size * 0.88,
                        fontfamily='monospace',
                        color=text_color,
                        ha='left', va='top',
                        clip_on=False, zorder=3,
                    )
                    self._add(t)
                    cy -= code_line_h
                y -= block_h
                if i < len(segments) - 1:
                    y -= code_gap
            else:
                stripped = text.strip()
                lines = wrap_fn(stripped, col_w) if stripped else []
                for line in lines:
                    t = ax.text(
                        text_x, y, line,
                        fontsize=font_size,
                        fontfamily=font_family,
                        color=text_color,
                        ha='left', va='top',
                        clip_on=False, zorder=3,
                    )
                    self._add(t)
                    y -= line_h
        return y_top - y

    # ── Main layout ───────────────────────────────────────────────────

    def _do_layout(self):
        self._clear()

        ax = self._ax
        p = self._p
        s = self._style

        ax_width_pts = self._ax_width_pts()
        if ax_width_pts < 10:
            return
        self._last_ax_width = ax_width_pts

        # ── Typography ────────────────────────────────────────────────
        font_size    = float(p.get('font_size') or s.get('font_size', 10.0))
        font_family  = s.get('font_family', 'sans-serif')
        line_spacing = float(p.get('line_spacing', 1.4))

        line_h        = font_size * line_spacing
        name_font     = float(s.get('name_font_size',      font_size * 0.80))
        ts_font       = float(s.get('timestamp_font_size', font_size * 0.70))
        name_line_h   = name_font * 1.35
        ts_line_h     = ts_font   * 1.30
        code_font     = font_size * 0.88
        code_line_h   = code_font * line_spacing
        code_inner_pad = font_size * 0.35   # top/bottom padding inside code bg
        code_gap       = font_size * 0.30   # gap above/below a code block within prose

        # ── Layout geometry ───────────────────────────────────────────
        bubble_spacing_pts = line_h * float(p.get('bubble_spacing', 0.6))
        pad_x              = ax_width_pts * float(p.get('pad', 0.05))
        bubble_width_pts   = ax_width_pts * float(p.get('bubble_width', 0.6))
        internal_pad_x     = font_size * 0.75
        internal_pad_y     = font_size * 0.45
        round_size         = font_size * 0.40

        show_names      = bool(p.get('show_names', True))
        show_timestamps = bool(p.get('show_timestamps', False))
        show_avatars    = bool(p.get('show_avatars', False))
        sender_align    = p.get('sender_align', None)

        # Avatar geometry (used only when show_avatars=True)
        avatar_r   = float(p.get('avatar_size') or font_size * 1.1)
        avatar_gap = font_size * 0.35         # gap between avatar edge and bubble

        # When avatars are shown, bubble edges move inward to leave room
        if show_avatars:
            bx1_right  = ax_width_pts - pad_x - 2 * avatar_r - avatar_gap
            bx0_left   = pad_x + 2 * avatar_r + avatar_gap
            avatar_cx_right = ax_width_pts - pad_x - avatar_r
            avatar_cx_left  = pad_x + avatar_r
        else:
            bx1_right  = ax_width_pts - pad_x
            bx0_left   = pad_x
            avatar_cx_right = avatar_cx_left = 0.0  # unused

        # Wrapping function (pixel-accurate when renderer is available)
        wrap_fn = self._make_wrap_fn(ax, font_size, font_family)

        # ── Coordinate system ─────────────────────────────────────────
        ax.set_xlim(0, ax_width_pts)
        y_cursor = 0.0   # y=0 is top; decreases as content stacks down

        # ── Per-message loop ──────────────────────────────────────────
        for msg in self._messages:
            role        = msg.get('role', 'user')
            content     = msg.get('content', '')
            name_str    = msg.get('name', role)
            timestamp   = msg.get('timestamp', None)
            msg_style   = msg.get('style', {})

            role_s = resolve_role_style(role, {**s, **msg_style})
            align  = get_align(role, sender_align)

            # ── X bounds ──────────────────────────────────────────────
            if align == 'right':
                bx1 = bx1_right
                bx0 = bx1 - bubble_width_pts
                bw  = bubble_width_pts
            elif align == 'left':
                bx0 = bx0_left
                bx1 = bx0 + bubble_width_pts
                bw  = bubble_width_pts
            else:  # center (system)
                bw  = min(bubble_width_pts * 0.85, ax_width_pts * 0.80)
                bx0 = (ax_width_pts - bw) / 2
                bx1 = bx0 + bw

            col_w    = bw - 2 * internal_pad_x
            text_x   = bx0 + internal_pad_x

            # ── Name label ────────────────────────────────────────────
            if show_names and align != 'center':
                name_x  = bx1 if align == 'right' else bx0
                name_ha = 'right' if align == 'right' else 'left'
                self._add(ax.text(
                    name_x, y_cursor, name_str,
                    fontsize=name_font, fontfamily=font_family,
                    color=role_s['textcolor'],
                    alpha=s.get('name_alpha', 0.65),
                    ha=name_ha, va='top',
                    clip_on=False, zorder=3,
                ))
                y_cursor -= name_line_h

            # ── Measure content height ─────────────────────────────────
            segments   = split_content_segments(content)
            content_h  = self._measure_segments(
                segments, col_w, line_h, code_line_h,
                code_inner_pad, code_gap, wrap_fn
            )
            bubble_h = content_h + 2 * internal_pad_y

            bubble_top = y_cursor
            bubble_bot = y_cursor - bubble_h

            # ── Bubble body ───────────────────────────────────────────
            ec = role_s['edgecolor']
            lw = s.get('bubble_lw', 0.8) if ec != 'none' else 0
            self._add(ax.add_patch(mpatches.FancyBboxPatch(
                (bx0, bubble_bot), bw, bubble_h,
                boxstyle=f'round,pad=0,rounding_size={round_size}',
                facecolor=role_s['facecolor'],
                edgecolor='none' if ec == 'none' else ec,
                linewidth=lw,
                clip_on=False, zorder=2,
            )))

            # ── Tail ──────────────────────────────────────────────────
            if align != 'center':
                tail_h = font_size * 0.55
                tail_w = font_size * 0.45
                anchor_y = bubble_bot + round_size + tail_h * 0.15
                if align == 'right':
                    verts = [
                        (bx1 - round_size, anchor_y + tail_h * 0.55),
                        (bx1 - round_size, anchor_y - tail_h * 0.15),
                        (bx1 + tail_w,     anchor_y + tail_h * 0.20),
                    ]
                else:
                    verts = [
                        (bx0 + round_size, anchor_y + tail_h * 0.55),
                        (bx0 + round_size, anchor_y - tail_h * 0.15),
                        (bx0 - tail_w,     anchor_y + tail_h * 0.20),
                    ]
                self._add(ax.add_patch(mpatches.Polygon(
                    verts, closed=True,
                    facecolor=role_s['facecolor'],
                    edgecolor='none',
                    clip_on=False, zorder=1,
                )))

            # ── Avatar ────────────────────────────────────────────────
            if show_avatars and align != 'center':
                canon  = {'human': 'user', 'ai': 'assistant',
                          'bot': 'assistant', 'model': 'assistant'}.get(role, role)
                av_key = f'{canon}_avatar_color' if canon in ('user', 'assistant') \
                         else 'other_avatar_color'
                av_color = s.get(av_key, s.get('other_avatar_color', '#888888'))

                avatar_cx = avatar_cx_right if align == 'right' else avatar_cx_left
                avatar_cy = (bubble_top + bubble_bot) / 2
                side = 2 * avatar_r
                self._add(ax.add_patch(mpatches.FancyBboxPatch(
                    (avatar_cx - avatar_r, avatar_cy - avatar_r),
                    side, side,
                    boxstyle=f'round,pad=0,rounding_size={avatar_r}',
                    facecolor=av_color,
                    edgecolor='none',
                    clip_on=False, zorder=3,
                )))
                self._add(ax.text(
                    avatar_cx, avatar_cy, _initials(name_str),
                    fontsize=font_size * 0.75,
                    fontfamily=font_family,
                    color='white',
                    ha='center', va='center',
                    clip_on=False, zorder=4,
                ))

            # ── Content ───────────────────────────────────────────────
            self._render_segments(
                segments, ax, bx0, bw, text_x,
                bubble_top - internal_pad_y,
                col_w, font_size, font_family, role_s['textcolor'],
                s.get('code_facecolor', '#E0E0E0'),
                s.get('code_edgecolor', 'none'),
                s.get('bubble_lw', 0.8),
                line_h, code_line_h, code_inner_pad, code_gap,
                internal_pad_x, wrap_fn,
            )

            y_cursor = bubble_bot

            # ── Timestamp ─────────────────────────────────────────────
            if show_timestamps and timestamp:
                y_cursor -= ts_line_h * 0.20
                ts_x  = bx1 if align == 'right' else bx0
                ts_ha = 'right' if align == 'right' else 'left'
                self._add(ax.text(
                    ts_x, y_cursor, timestamp,
                    fontsize=ts_font, fontfamily=font_family,
                    color=role_s['textcolor'],
                    alpha=s.get('timestamp_alpha', 0.5),
                    ha=ts_ha, va='top',
                    clip_on=False, zorder=3,
                ))
                y_cursor -= ts_line_h

            y_cursor -= bubble_spacing_pts

        # ── Finalise axes ─────────────────────────────────────────────
        top_pad = internal_pad_y * 2.0
        bot_pad = bubble_spacing_pts * 1.5
        ax.set_ylim(y_cursor - bot_pad, top_pad)
        ax.set_axis_off()
        ax.set_facecolor(s.get('axes_facecolor', 'white'))
