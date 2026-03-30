# yapplotlib

A matplotlib plugin for rendering chat interfaces.

## Installation

```bash
pip install yapplotlib
# or with uv:
uv add yapplotlib
```

## Quick start

```python
import yapplotlib

messages = [
    {'role': 'system',    'content': 'You are a helpful assistant.'},
    {'role': 'user',      'content': 'What is the capital of France?'},
    {'role': 'assistant', 'content': 'The capital of France is Paris.'},
]

fig, ax = yapplotlib.chat_thread(messages, style='paper')
fig.savefig('chat.pdf', bbox_inches='tight')
```

## Embedding in an existing figure

```python
import matplotlib.pyplot as plt
import yapplotlib  # patches Axes.chat_thread on import

fig, axes = plt.subplots(1, 2, figsize=(12, 6))
axes[0].chat_thread(messages, style='paper')
axes[1].plot([1, 2, 3], [4, 5, 6])
plt.tight_layout()
```

## Message format

Each message is a plain dict with at least `role` and `content`:

```python
{
    'role':      'user',            # required
    'content':   'Hello!',          # required
    'name':      'Alice',           # optional — display name override
    'timestamp': '10:04 AM',        # optional — shown when show_timestamps=True
    'style':     {'user_facecolor': '#FFD700'},  # optional — per-message override
}
```

## Themes

| Theme | Description |
|-------|-------------|
| `'default'` | WhatsApp-style green/white, sans-serif |
| `'paper'`   | Greyscale, serif — survives black-and-white printing |
| `'dark'`    | Dark background for slides and web |
| `'minimal'` | Outline only, no fill |

```python
fig, ax = yapplotlib.chat_thread(messages, style='paper')
```

## mplstyle integration

```python
import matplotlib.pyplot as plt
with plt.style.context('yapplotlib.paper'):
    fig, ax = yapplotlib.chat_thread(messages, style='paper')
```

Available styles: `yapplotlib.paper`, `yapplotlib.dark`.

## rcParams defaults

Import-time defaults can be overridden globally via `matplotlib.rcParams`:

```python
import matplotlib
matplotlib.rcParams['yapplotlib.style']        = 'paper'
matplotlib.rcParams['yapplotlib.bubble_width'] = 0.65
matplotlib.rcParams['yapplotlib.show_names']   = False
```

Available keys: `yapplotlib.style`, `yapplotlib.bubble_width`,
`yapplotlib.show_names`, `yapplotlib.show_timestamps`,
`yapplotlib.show_avatars`, `yapplotlib.font_size`,
`yapplotlib.bubble_spacing`, `yapplotlib.line_spacing`, `yapplotlib.pad`.

## Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `style` | `'default'` | Theme name or partial style dict |
| `bubble_width` | `0.6` | Max bubble width as fraction of axes width |
| `show_names` | `True` | Show sender name labels |
| `show_timestamps` | `False` | Show timestamp strings |
| `show_avatars` | `False` | Show circular avatar badges with initials |
| `sender_align` | `None` | Dict mapping role → `'left'`/`'right'`/`'center'` |
| `line_spacing` | `1.4` | Line spacing multiplier |
| `bubble_spacing` | `0.6` | Gap between bubbles (in line-heights) |
| `pad` | `0.05` | Left/right edge padding (fraction of axes width) |
| `font_size` | theme | Font size in points |

## Style customisation

```python
# Partial override — merges with a named base theme
my_style = {**yapplotlib.themes['paper'], 'font_size': 11, 'user_facecolor': '#D0E8FF'}
fig, ax = yapplotlib.chat_thread(messages, style=my_style)

# Per-message highlight
messages[2]['style'] = {'user_facecolor': '#FFD700'}
```

## ChatThread object

`ax.chat_thread()` returns a `ChatThread` object:

```python
thread = ax.chat_thread(messages)

thread.get_children()  # list of all managed matplotlib artists
thread.redraw()        # force re-layout (e.g. after changing messages)
thread.disconnect()    # remove canvas event callbacks
```

## Development

```bash
uv run pytest          # run tests
uv run python smoke_test.py  # render all styles to smoke_output/
```

---

## Planned features

- **Thinking / reasoning messages** — collapsible or visually distinct bubbles
  for model reasoning traces (e.g. `<thinking>` blocks in chain-of-thought
  outputs). Proposed role name: `'thinking'`.

- **Tool call / tool result messages** — structured display for function-call
  messages (`role: 'tool'` or `role: 'tool_result'`), showing the tool name,
  inputs, and output in a monospace code-block style distinct from regular
  assistant prose.

- **Plotly support**
