"""
Theme definitions and style resolution for yapplotlib.
"""

THEMES = {
    "default": {
        # Role colours
        "user_facecolor": "#DCF8C6",
        "user_edgecolor": "#A8D9A0",
        "user_textcolor": "#111111",
        "assistant_facecolor": "#FFFFFF",
        "assistant_edgecolor": "#E0E0E0",
        "assistant_textcolor": "#111111",
        "system_facecolor": "#F0F0F0",
        "system_edgecolor": "#CCCCCC",
        "system_textcolor": "#666666",
        "reasoning_facecolor": "#FFF7D6",
        "reasoning_edgecolor": "#E6C75E",
        "reasoning_textcolor": "#5A4A00",
        "tool_call_facecolor": "#E8F1FF",
        "tool_call_edgecolor": "#9DBCE8",
        "tool_call_textcolor": "#153A66",
        "tool_result_facecolor": "#F2EDFF",
        "tool_result_edgecolor": "#B6A5E6",
        "tool_result_textcolor": "#39236A",
        "other_facecolor": "#E8E8E8",
        "other_edgecolor": "#CCCCCC",
        "other_textcolor": "#111111",
        # Typography
        "font_family": "sans-serif",
        "font_size": 10.0,
        "name_font_size": 8.0,
        "timestamp_font_size": 7.0,
        "name_alpha": 0.65,
        "timestamp_alpha": 0.50,
        # Bubble geometry
        "bubble_lw": 0.8,
        # Code blocks
        "code_facecolor": "#C8C8C8",
        "code_edgecolor": "none",
        # Avatars (background circle colour per role)
        "user_avatar_color": "#128C7E",
        "assistant_avatar_color": "#888888",
        "other_avatar_color": "#999999",
        # Backgrounds
        "figure_facecolor": "#E5DDD5",
        "axes_facecolor": "#E5DDD5",
    },
    "paper": {
        # Greyscale — survives black-and-white printing
        "user_facecolor": "#D8D8D8",
        "user_edgecolor": "#888888",
        "user_textcolor": "#000000",
        "assistant_facecolor": "#FFFFFF",
        "assistant_edgecolor": "#888888",
        "assistant_textcolor": "#000000",
        "system_facecolor": "#F0F0F0",
        "system_edgecolor": "#AAAAAA",
        "system_textcolor": "#444444",
        "reasoning_facecolor": "#F8F8F8",
        "reasoning_edgecolor": "#999999",
        "reasoning_textcolor": "#333333",
        "tool_call_facecolor": "#EEEEEE",
        "tool_call_edgecolor": "#777777",
        "tool_call_textcolor": "#000000",
        "tool_result_facecolor": "#F7F7F7",
        "tool_result_edgecolor": "#999999",
        "tool_result_textcolor": "#222222",
        "other_facecolor": "#EBEBEB",
        "other_edgecolor": "#AAAAAA",
        "other_textcolor": "#000000",
        "font_family": "serif",
        "font_size": 9.0,
        "name_font_size": 7.0,
        "timestamp_font_size": 6.5,
        "name_alpha": 0.80,
        "timestamp_alpha": 0.65,
        "bubble_lw": 0.6,
        "code_facecolor": "#E4E4E4",
        "code_edgecolor": "#BBBBBB",
        "user_avatar_color": "#666666",
        "assistant_avatar_color": "#AAAAAA",
        "other_avatar_color": "#999999",
        "figure_facecolor": "#FFFFFF",
        "axes_facecolor": "#FFFFFF",
    },
    "dark": {
        "user_facecolor": "#005C4B",
        "user_edgecolor": "none",
        "user_textcolor": "#E8E8E8",
        "assistant_facecolor": "#1F2C34",
        "assistant_edgecolor": "#2A3942",
        "assistant_textcolor": "#E8E8E8",
        "system_facecolor": "#1B2428",
        "system_edgecolor": "#2A3942",
        "system_textcolor": "#8696A0",
        "reasoning_facecolor": "#2C2615",
        "reasoning_edgecolor": "#6B5B28",
        "reasoning_textcolor": "#F0D98A",
        "tool_call_facecolor": "#162536",
        "tool_call_edgecolor": "#2F5E91",
        "tool_call_textcolor": "#D7E8FF",
        "tool_result_facecolor": "#251C34",
        "tool_result_edgecolor": "#5B4483",
        "tool_result_textcolor": "#E5D8FF",
        "other_facecolor": "#1F2C34",
        "other_edgecolor": "#2A3942",
        "other_textcolor": "#E8E8E8",
        "font_family": "sans-serif",
        "font_size": 10.0,
        "name_font_size": 8.0,
        "timestamp_font_size": 7.0,
        "name_alpha": 0.70,
        "timestamp_alpha": 0.50,
        "bubble_lw": 0.5,
        "code_facecolor": "#0D1117",
        "code_edgecolor": "#30363D",
        "user_avatar_color": "#00A884",
        "assistant_avatar_color": "#2A3942",
        "other_avatar_color": "#374248",
        "figure_facecolor": "#0B141A",
        "axes_facecolor": "#0B141A",
    },
    "minimal": {
        "user_facecolor": "#F0F0F0",
        "user_edgecolor": "#666666",
        "user_textcolor": "#000000",
        "assistant_facecolor": "#FFFFFF",
        "assistant_edgecolor": "#666666",
        "assistant_textcolor": "#000000",
        "system_facecolor": "none",
        "system_edgecolor": "#AAAAAA",
        "system_textcolor": "#666666",
        "reasoning_facecolor": "none",
        "reasoning_edgecolor": "#999999",
        "reasoning_textcolor": "#333333",
        "tool_call_facecolor": "none",
        "tool_call_edgecolor": "#777777",
        "tool_call_textcolor": "#000000",
        "tool_result_facecolor": "none",
        "tool_result_edgecolor": "#999999",
        "tool_result_textcolor": "#222222",
        "other_facecolor": "none",
        "other_edgecolor": "#666666",
        "other_textcolor": "#000000",
        "font_family": "sans-serif",
        "font_size": 10.0,
        "name_font_size": 8.0,
        "timestamp_font_size": 7.0,
        "name_alpha": 0.70,
        "timestamp_alpha": 0.50,
        "bubble_lw": 1.0,
        "code_facecolor": "#F0F0F0",
        "code_edgecolor": "#CCCCCC",
        "user_avatar_color": "#555555",
        "assistant_avatar_color": "#999999",
        "other_avatar_color": "#AAAAAA",
        "figure_facecolor": "#FFFFFF",
        "axes_facecolor": "#FFFFFF",
    },
}

# Canonical role names for colour lookup (aliases map to these)
_ROLE_ALIASES = {
    "human": "user",
    "ai": "assistant",
    "bot": "assistant",
    "model": "assistant",
}

# Automatic colour palette for unknown roles (deterministic via hash)
_ROLE_COLOR_PALETTE = [
    "#AED6F1",
    "#A9DFBF",
    "#F9E79F",
    "#F1948A",
    "#C39BD3",
    "#85C1E9",
    "#7DCEA0",
    "#FAD7A0",
    "#A3E4D7",
    "#FDEBD0",
    "#D2B4DE",
    "#A9CCE3",
]

# Default horizontal alignment per role
DEFAULT_ALIGN = {
    "user": "right",
    "human": "right",
    "assistant": "left",
    "ai": "left",
    "bot": "left",
    "model": "left",
    "reasoning": "left",
    "tool_call": "left",
    "tool_result": "left",
    "system": "center",
}


def _build_auto_theme():
    """
    Build the 'default' theme by inheriting background and text colors from
    matplotlib's currently active style (rcParams).

    The bubble color palette is chosen based on the luminance of the active
    axes background: dark backgrounds get the 'dark' bubble palette, light
    backgrounds keep the standard 'default' palette.
    """
    import matplotlib
    from matplotlib.colors import to_rgb

    fig_fc = matplotlib.rcParams.get("figure.facecolor", "#E5DDD5")
    axes_fc = matplotlib.rcParams.get("axes.facecolor", "#E5DDD5")
    text_color = matplotlib.rcParams.get("text.color", "#111111")

    r, g, b = to_rgb(axes_fc)
    luminance = 0.299 * r + 0.587 * g + 0.114 * b

    base = dict(THEMES["dark" if luminance <= 0.5 else "default"])
    base["figure_facecolor"] = fig_fc
    base["axes_facecolor"] = axes_fc
    for role in ("user", "assistant", "system", "reasoning", "tool_call", "tool_result", "other"):
        base[f"{role}_textcolor"] = text_color
    return base


def resolve_style(style):
    """
    Resolve a style name or partial dict to a complete style dict.

    Parameters
    ----------
    style : str or dict or None
        A theme name ('default', 'paper', 'dark', 'minimal'), a partial
        style dict (merged on top of 'default'), or None (uses 'default').

        The ``'default'`` theme is adaptive: it inherits background and text
        colors from matplotlib's currently active style (rcParams), and
        selects light or dark bubble colors based on background luminance.

    Returns
    -------
    dict
        A fully resolved style dict containing all known keys.
    """
    if style is None or style == "default":
        return _build_auto_theme()
    if isinstance(style, str):
        if style not in THEMES:
            raise ValueError(f"Unknown style {style!r}. Available themes: {sorted(THEMES)}")
        return dict(THEMES[style])
    if isinstance(style, dict):
        base_name = style.get("_base", "default")
        if base_name == "default":
            base = _build_auto_theme()
        else:
            base = dict(THEMES.get(base_name, THEMES["default"]))
        base.update({k: v for k, v in style.items() if k != "_base"})
        return base
    raise TypeError(f"style must be a str or dict, got {type(style).__name__!r}")


def resolve_role_style(role, style_dict):
    """
    Return the facecolor, edgecolor, and textcolor for a given role.

    Parameters
    ----------
    role : str
    style_dict : dict
        A fully resolved style dict (from resolve_style).

    Returns
    -------
    dict with keys 'facecolor', 'edgecolor', 'textcolor'
    """
    canon = _ROLE_ALIASES.get(role, role)
    if canon in ("user", "assistant", "system", "reasoning", "tool_call", "tool_result"):
        return {
            "facecolor": style_dict.get(f"{canon}_facecolor", style_dict["other_facecolor"]),
            "edgecolor": style_dict.get(f"{canon}_edgecolor", style_dict["other_edgecolor"]),
            "textcolor": style_dict.get(f"{canon}_textcolor", style_dict["other_textcolor"]),
        }
    # Unknown role: derive from palette deterministically
    idx = hash(role) % len(_ROLE_COLOR_PALETTE)
    return {
        "facecolor": _ROLE_COLOR_PALETTE[idx],
        "edgecolor": style_dict["other_edgecolor"],
        "textcolor": style_dict["other_textcolor"],
    }


def get_align(role, sender_align=None):
    """
    Return the horizontal alignment string for a role.

    Parameters
    ----------
    role : str
    sender_align : dict or None
        User-supplied overrides, e.g. {'user': 'left', 'assistant': 'right'}.

    Returns
    -------
    str : 'left', 'right', or 'center'
    """
    if sender_align and role in sender_align:
        return sender_align[role]
    return DEFAULT_ALIGN.get(role, "left")
