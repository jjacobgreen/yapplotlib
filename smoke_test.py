"""
Smoke test for yapplotlib.
Renders output images into smoke_output/ (git-ignored).
"""

import matplotlib

matplotlib.use("Agg")  # headless backend for testing

from pathlib import Path

import matplotlib.pyplot as plt

import yapplotlib

OUT = Path(__file__).parent / "smoke_output"
OUT.mkdir(exist_ok=True)


def save(fig, name):
    path = OUT / name
    fig.savefig(path, bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"  → {path.relative_to(Path(__file__).parent)}")


MESSAGES = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is the capital of France?"},
    {"role": "assistant", "content": "The capital of France is Paris."},
    {"role": "user", "content": "And Germany?"},
    {"role": "assistant", "content": "The capital of Germany is Berlin."},
    {
        "role": "user",
        "content": (
            "Can you explain why these are the capitals? "
            "I would love to understand the historical context behind "
            "these choices and whether they changed at any point."
        ),
    },
    {
        "role": "assistant",
        "content": (
            "Paris has been the capital of France since the late 10th century. "
            "Berlin became the capital of a unified Germany in 1871 under Bismarck, "
            "though Bonn served as West Germany's capital from 1949–1990."
        ),
    },
]

# ── Test 1: standalone paper style ───────────────────────────────────────
print("Test 1: standalone paper style...")
save(yapplotlib.chatplot(MESSAGES, style="paper")[0], "paper.png")

# ── Test 2: standalone default style ─────────────────────────────────────
print("Test 2: standalone default style...")
save(yapplotlib.chatplot(MESSAGES, style="default")[0], "default.png")

# ── Test 3: dark style ────────────────────────────────────────────────────
print("Test 3: dark style...")
save(yapplotlib.chatplot(MESSAGES, style="dark")[0], "dark.png")

# ── Test 4: minimal style ─────────────────────────────────────────────────
print("Test 4: minimal style...")
save(yapplotlib.chatplot(MESSAGES, style="minimal")[0], "minimal.png")

# ── Test 5: embedded in subplot grid ─────────────────────────────────────
print("Test 5: embedded in subplot grid...")
fig, axes = plt.subplots(1, 2, figsize=(11, 7))
axes[0].chatplot(MESSAGES[:5], style="paper", show_names=True)
axes[1].plot([1, 2, 3, 4], [1, 4, 2, 3], marker="o")
axes[1].set_title("Model accuracy")
plt.tight_layout()
save(fig, "embedded.png")

# ── Test 6: timestamps + no names ────────────────────────────────────────
print("Test 6: timestamps, no names...")
ts_msgs = [
    {"role": "user", "content": "Hey!", "timestamp": "10:00 AM"},
    {"role": "assistant", "content": "Hi there!", "timestamp": "10:00 AM"},
    {"role": "user", "content": "How are you?", "timestamp": "10:01 AM"},
    {"role": "assistant", "content": "Doing well, thanks for asking!", "timestamp": "10:01 AM"},
]
save(
    yapplotlib.chatplot(ts_msgs, style="default", show_names=False, show_timestamps=True)[0],
    "timestamps.png",
)

# ── Test 7: per-message style override ────────────────────────────────────
print("Test 7: per-message style override...")
override_msgs = list(MESSAGES)
override_msgs[1] = {
    **override_msgs[1],
    "style": {"user_facecolor": "#FFD700", "user_edgecolor": "#FFA500"},
}
save(yapplotlib.chatplot(override_msgs, style="default")[0], "override.png")

# ── Test 8: avatars ───────────────────────────────────────────────────────
print("Test 8: avatars...")
save(yapplotlib.chatplot(MESSAGES[:5], style="default", show_avatars=True)[0], "avatars.png")

# ── Test 9: code blocks ───────────────────────────────────────────────────
print("Test 9: code blocks...")
code_msgs = [
    {"role": "user", "content": "How do I reverse a list in Python?"},
    {
        "role": "assistant",
        "content": (
            "You can reverse a list in several ways:\n\n"
            "**Using slicing:**\n"
            "```python\nmy_list = [1, 2, 3]\nreversed_list = my_list[::-1]\n```\n"
            "**Using reverse():**\n"
            "```\nmy_list.reverse()  # in-place\n```\n"
            "The slice approach returns a new list; `reverse()` modifies in place."
        ),
    },
    {"role": "user", "content": "Which is faster?"},
    {
        "role": "assistant",
        "content": "`list.reverse()` is slightly faster as it avoids allocating a new list. For large lists, prefer it when you don't need the original.",
    },
]
save(yapplotlib.chatplot(code_msgs, style="default")[0], "code.png")

# ── Test 10: code blocks + paper style ───────────────────────────────────
print("Test 10: code blocks + paper style...")
save(yapplotlib.chatplot(code_msgs, style="paper")[0], "code_paper.png")

# ── Test 11: avatars + dark style ────────────────────────────────────────
print("Test 11: avatars + dark style...")
save(
    yapplotlib.chatplot(MESSAGES[:5], style="dark", show_avatars=True, show_names=False)[0],
    "avatars_dark.png",
)

# ── Test 12: mplstyle registration ───────────────────────────────────────
print("Test 12: plt.style.use('yapplotlib.paper')...")
with plt.style.context("yapplotlib.paper"):
    save(yapplotlib.chatplot(MESSAGES[:3], style="paper")[0], "mplstyle.png")

print("\nAll tests passed! Output in smoke_output/")
