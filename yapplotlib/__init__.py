"""
yapplotlib — matplotlib plugin for rendering chat interfaces.

Quick start
-----------
>>> import yapplotlib
>>> messages = [
...     {'role': 'user',      'content': 'What is 2 + 2?'},
...     {'role': 'assistant', 'content': 'It is 4.'},
... ]
>>> fig, ax = yapplotlib.chatplot(messages, style='paper')
>>> fig.savefig('chat.pdf', bbox_inches='tight')

Or embedded in an existing figure::

    import matplotlib.pyplot as plt
    import yapplotlib          # import injects Axes.chatplot

    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    axes[0].chatplot(messages, style='paper')
    axes[1].plot([1, 2, 3], [4, 5, 6])
    plt.tight_layout()
"""

from pathlib import Path

import matplotlib
import matplotlib.style
from matplotlib.axes import Axes

from ._api import _ax_chatplot, chatplot
from ._artists import ChatPlot
from ._styles import THEMES, resolve_style

# ── Register custom rcParams ──────────────────────────────────────────────
# Inject yapplotlib.* keys into matplotlib.rcParams using dict.__setitem__
# to bypass matplotlib's key-validation (standard third-party extension
# pattern for keys not in matplotlib's built-in schema).
#
# IMPORTANT: this must happen before reload_library() below so that the
# yapplotlib.* keys are known to the validator when mplstyle files are parsed.
#
# Users can then set defaults via:
#   import matplotlib
#   matplotlib.rcParams['yapplotlib.style'] = 'paper'
try:
    from matplotlib import rcsetup as _rcsetup

    _RC_DEFAULTS = {
        "yapplotlib.style": ("default", _rcsetup.validate_string),
        "yapplotlib.bubble_width": (0.6, _rcsetup.validate_float),
        "yapplotlib.show_names": (True, _rcsetup.validate_bool),
        "yapplotlib.show_timestamps": (False, _rcsetup.validate_bool),
        "yapplotlib.show_avatars": (False, _rcsetup.validate_bool),
        "yapplotlib.font_size": (10.0, _rcsetup.validate_float),
        "yapplotlib.bubble_spacing": (0.6, _rcsetup.validate_float),
        "yapplotlib.line_spacing": (1.4, _rcsetup.validate_float),
        "yapplotlib.pad": (0.05, _rcsetup.validate_float),
    }

    for _key, (_default, _validator) in _RC_DEFAULTS.items():
        # Register the validator so normal rcParams[key] = value writes work.
        # matplotlib.rcParams.validate is the dict that __setitem__ checks.
        if _key not in matplotlib.rcParams.validate:
            matplotlib.rcParams.validate[_key] = _validator
        # Seed the default value, bypassing validation (key wasn't in schema
        # until the line above, so the normal setter would have rejected it).
        if _key not in matplotlib.rcParams:
            dict.__setitem__(matplotlib.rcParams, _key, _default)
except Exception:
    pass

# ── Register bundled .mplstyle files ─────────────────────────────────────
# Enables:  plt.style.use('yapplotlib.paper')
# Must come after rcParams registration so yapplotlib.* keys are valid when
# the style files are parsed by reload_library().
_styles_dir = Path(__file__).parent / "styles"
if _styles_dir not in matplotlib.style.core.USER_LIBRARY_PATHS:
    matplotlib.style.core.USER_LIBRARY_PATHS.append(_styles_dir)  # type: ignore[arg-type]
matplotlib.style.reload_library()

# ── Inject Axes.chatplot ──────────────────────────────────────────────────
# This is the standard matplotlib extension pattern used by mplcursors,
# matplotlib-scalebar, and others.
Axes.chatplot = _ax_chatplot  # type: ignore[attr-defined]

# ── Public API ────────────────────────────────────────────────────────────
#: Read-only copies of the built-in theme dicts, available for introspection
#: or as a base for custom styles::
#:
#:     my_style = {**yapplotlib.themes['paper'], 'font_size': 11}
themes = {name: dict(s) for name, s in THEMES.items()}

__all__ = [
    "ChatPlot",
    "chatplot",
    "themes",
    "resolve_style",
]

__version__ = "0.1.0"
