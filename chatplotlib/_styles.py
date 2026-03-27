"""
Theme definitions and style resolution for chatplotlib.
"""

THEMES = {
    'default': {
        # Role colours
        'user_facecolor': '#DCF8C6',
        'user_edgecolor': 'none',
        'user_textcolor': '#111111',
        'assistant_facecolor': '#FFFFFF',
        'assistant_edgecolor': '#E0E0E0',
        'assistant_textcolor': '#111111',
        'system_facecolor': '#F0F0F0',
        'system_edgecolor': '#CCCCCC',
        'system_textcolor': '#666666',
        'other_facecolor': '#E8E8E8',
        'other_edgecolor': '#CCCCCC',
        'other_textcolor': '#111111',
        # Typography
        'font_family': 'sans-serif',
        'font_size': 10.0,
        'name_font_size': 8.0,
        'timestamp_font_size': 7.0,
        'name_alpha': 0.65,
        'timestamp_alpha': 0.50,
        # Bubble geometry
        'bubble_lw': 0.8,
        # Backgrounds
        'figure_facecolor': '#E5DDD5',
        'axes_facecolor': '#E5DDD5',
    },
    'paper': {
        # Greyscale — survives black-and-white printing
        'user_facecolor': '#D8D8D8',
        'user_edgecolor': '#888888',
        'user_textcolor': '#000000',
        'assistant_facecolor': '#FFFFFF',
        'assistant_edgecolor': '#888888',
        'assistant_textcolor': '#000000',
        'system_facecolor': '#F0F0F0',
        'system_edgecolor': '#AAAAAA',
        'system_textcolor': '#444444',
        'other_facecolor': '#EBEBEB',
        'other_edgecolor': '#AAAAAA',
        'other_textcolor': '#000000',
        'font_family': 'serif',
        'font_size': 9.0,
        'name_font_size': 7.0,
        'timestamp_font_size': 6.5,
        'name_alpha': 0.80,
        'timestamp_alpha': 0.65,
        'bubble_lw': 0.6,
        'figure_facecolor': '#FFFFFF',
        'axes_facecolor': '#FFFFFF',
    },
    'dark': {
        'user_facecolor': '#005C4B',
        'user_edgecolor': 'none',
        'user_textcolor': '#E8E8E8',
        'assistant_facecolor': '#1F2C34',
        'assistant_edgecolor': '#2A3942',
        'assistant_textcolor': '#E8E8E8',
        'system_facecolor': '#1B2428',
        'system_edgecolor': '#2A3942',
        'system_textcolor': '#8696A0',
        'other_facecolor': '#1F2C34',
        'other_edgecolor': '#2A3942',
        'other_textcolor': '#E8E8E8',
        'font_family': 'sans-serif',
        'font_size': 10.0,
        'name_font_size': 8.0,
        'timestamp_font_size': 7.0,
        'name_alpha': 0.70,
        'timestamp_alpha': 0.50,
        'bubble_lw': 0.5,
        'figure_facecolor': '#0B141A',
        'axes_facecolor': '#0B141A',
    },
    'minimal': {
        'user_facecolor': '#F0F0F0',
        'user_edgecolor': '#666666',
        'user_textcolor': '#000000',
        'assistant_facecolor': '#FFFFFF',
        'assistant_edgecolor': '#666666',
        'assistant_textcolor': '#000000',
        'system_facecolor': 'none',
        'system_edgecolor': '#AAAAAA',
        'system_textcolor': '#666666',
        'other_facecolor': 'none',
        'other_edgecolor': '#666666',
        'other_textcolor': '#000000',
        'font_family': 'sans-serif',
        'font_size': 10.0,
        'name_font_size': 8.0,
        'timestamp_font_size': 7.0,
        'name_alpha': 0.70,
        'timestamp_alpha': 0.50,
        'bubble_lw': 1.0,
        'figure_facecolor': '#FFFFFF',
        'axes_facecolor': '#FFFFFF',
    },
}

# Canonical role names for colour lookup (aliases map to these)
_ROLE_ALIASES = {
    'human': 'user',
    'ai': 'assistant',
    'bot': 'assistant',
    'model': 'assistant',
}

# Automatic colour palette for unknown roles (deterministic via hash)
_ROLE_COLOR_PALETTE = [
    '#AED6F1', '#A9DFBF', '#F9E79F', '#F1948A',
    '#C39BD3', '#85C1E9', '#7DCEA0', '#FAD7A0',
    '#A3E4D7', '#FDEBD0', '#D2B4DE', '#A9CCE3',
]

# Default horizontal alignment per role
DEFAULT_ALIGN = {
    'user': 'right',
    'human': 'right',
    'assistant': 'left',
    'ai': 'left',
    'bot': 'left',
    'model': 'left',
    'system': 'center',
}


def resolve_style(style):
    """
    Resolve a style name or partial dict to a complete style dict.

    Parameters
    ----------
    style : str or dict or None
        A theme name ('default', 'paper', 'dark', 'minimal'), a partial
        style dict (merged on top of 'default'), or None (uses 'default').

    Returns
    -------
    dict
        A fully resolved style dict containing all known keys.
    """
    if style is None:
        return dict(THEMES['default'])
    if isinstance(style, str):
        if style not in THEMES:
            raise ValueError(
                f"Unknown style {style!r}. Available themes: {sorted(THEMES)}"
            )
        return dict(THEMES[style])
    if isinstance(style, dict):
        base_name = style.get('_base', 'default')
        base = dict(THEMES.get(base_name, THEMES['default']))
        base.update({k: v for k, v in style.items() if k != '_base'})
        return base
    raise TypeError(
        f"style must be a str or dict, got {type(style).__name__!r}"
    )


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
    if canon in ('user', 'assistant', 'system'):
        return {
            'facecolor': style_dict.get(
                f'{canon}_facecolor', style_dict['other_facecolor']
            ),
            'edgecolor': style_dict.get(
                f'{canon}_edgecolor', style_dict['other_edgecolor']
            ),
            'textcolor': style_dict.get(
                f'{canon}_textcolor', style_dict['other_textcolor']
            ),
        }
    # Unknown role: derive from palette deterministically
    idx = hash(role) % len(_ROLE_COLOR_PALETTE)
    return {
        'facecolor': _ROLE_COLOR_PALETTE[idx],
        'edgecolor': style_dict['other_edgecolor'],
        'textcolor': style_dict['other_textcolor'],
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
    return DEFAULT_ALIGN.get(role, 'left')
