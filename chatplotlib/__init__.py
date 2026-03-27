"""
chatplotlib — matplotlib plugin for rendering chat interfaces.

Quick start
-----------
>>> import chatplotlib
>>> messages = [
...     {'role': 'user',      'content': 'What is 2 + 2?'},
...     {'role': 'assistant', 'content': 'It is 4.'},
... ]
>>> fig, ax = chatplotlib.chat_thread(messages, style='paper')
>>> fig.savefig('chat.pdf', bbox_inches='tight')

Or embedded in an existing figure::

    import matplotlib.pyplot as plt
    import chatplotlib          # import injects Axes.chat_thread

    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    axes[0].chat_thread(messages, style='paper')
    axes[1].plot([1, 2, 3], [4, 5, 6])
    plt.tight_layout()
"""

from matplotlib.axes import Axes

from ._api import _ax_chat_thread, chat_thread
from ._styles import THEMES, resolve_style

# ── Inject Axes.chat_thread ───────────────────────────────────────────────
# This is the standard matplotlib extension pattern used by mplcursors,
# matplotlib-scalebar, and others.
Axes.chat_thread = _ax_chat_thread

# ── Public API ────────────────────────────────────────────────────────────
#: Read-only copies of the built-in theme dicts, available for introspection
#: or as a base for custom styles::
#:
#:     my_style = {**chatplotlib.themes['paper'], 'font_size': 11}
themes = {name: dict(s) for name, s in THEMES.items()}

__all__ = [
    'chat_thread',
    'themes',
    'resolve_style',
]

__version__ = '0.1.0'
