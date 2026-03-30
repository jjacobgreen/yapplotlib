"""
Tests for the public API: chatplot() and ax.chatplot().
"""

import matplotlib
import matplotlib.pyplot as plt
import pytest

import yapplotlib
from yapplotlib._artists import ChatThread

# ── Fixtures ─────────────────────────────────────────────────────────────


@pytest.fixture
def msgs():
    return [
        {"role": "user", "content": "Hello!"},
        {"role": "assistant", "content": "Hi there!"},
    ]


# ── chatplot() ─────────────────────────────────────────────────────────


class TestChatThread:
    def test_returns_fig_and_ax(self, msgs):
        fig, ax = yapplotlib.chatplot(msgs)
        assert isinstance(fig, matplotlib.figure.Figure)
        assert isinstance(ax, matplotlib.axes.Axes)

    def test_all_styles(self, msgs):
        for style in ("default", "paper", "dark", "minimal"):
            fig, ax = yapplotlib.chatplot(msgs, style=style)
            assert fig is not None

    def test_unknown_style_raises(self, msgs):
        with pytest.raises(ValueError, match="Unknown style"):
            yapplotlib.chatplot(msgs, style="nope")

    def test_custom_figsize(self, msgs):
        fig, ax = yapplotlib.chatplot(msgs, figsize=(8, 6))
        w, h = fig.get_size_inches()
        assert w == pytest.approx(8.0)
        assert h == pytest.approx(6.0)

    def test_auto_figsize_adjusts_height(self, msgs):
        # Auto-sized figure should not be the placeholder 9.0
        fig, ax = yapplotlib.chatplot(msgs, figsize=None)
        _, h = fig.get_size_inches()
        # A 2-message thread should be much shorter than 9 inches
        assert h < 8.0

    def test_custom_dpi(self, msgs):
        fig, ax = yapplotlib.chatplot(msgs, dpi=72)
        assert fig.dpi == pytest.approx(72.0)

    def test_empty_messages(self):
        # Should not raise
        fig, ax = yapplotlib.chatplot([])
        assert fig is not None

    def test_system_message_centered(self, full_messages):
        fig, ax = yapplotlib.chatplot(full_messages)
        assert fig is not None

    def test_dict_style_override(self, msgs):
        fig, ax = yapplotlib.chatplot(msgs, style={"user_facecolor": "#FF0000"})
        assert fig is not None


# ── ax.chatplot() ─────────────────────────────────────────────────────


class TestAxChatThread:
    def test_returns_chatplot_object(self, msgs):
        fig, ax = plt.subplots()
        thread = ax.chatplot(msgs)
        assert isinstance(thread, ChatThread)

    def test_embedded_in_subplot(self, msgs):
        fig, axes = plt.subplots(1, 2, figsize=(10, 5))
        thread = axes[0].chatplot(msgs, style="paper")
        axes[1].plot([1, 2, 3], [1, 4, 2])
        assert isinstance(thread, ChatThread)

    def test_show_names_false(self, msgs):
        fig, ax = plt.subplots()
        thread = ax.chatplot(msgs, show_names=False)
        assert isinstance(thread, ChatThread)

    def test_show_timestamps(self):
        msgs = [
            {"role": "user", "content": "Hey", "timestamp": "10:00"},
            {"role": "assistant", "content": "Hello!", "timestamp": "10:01"},
        ]
        fig, ax = plt.subplots()
        thread = ax.chatplot(msgs, show_timestamps=True)
        assert isinstance(thread, ChatThread)

    def test_show_avatars(self, msgs):
        fig, ax = plt.subplots()
        thread = ax.chatplot(msgs, show_avatars=True)
        assert isinstance(thread, ChatThread)

    def test_per_message_style(self, msgs):
        msgs[0] = {**msgs[0], "style": {"user_facecolor": "#FFD700"}}
        fig, ax = plt.subplots()
        thread = ax.chatplot(msgs)
        assert isinstance(thread, ChatThread)

    def test_sender_align_override(self, msgs):
        fig, ax = plt.subplots()
        thread = ax.chatplot(
            msgs,
            sender_align={"user": "left", "assistant": "right"},
        )
        assert isinstance(thread, ChatThread)

    def test_bubble_width(self, msgs):
        fig, ax = plt.subplots()
        thread = ax.chatplot(msgs, bubble_width=0.8)
        assert isinstance(thread, ChatThread)


# ── ChatThread introspection ──────────────────────────────────────────────


class TestChatThreadIntrospection:
    def test_get_children_returns_list(self, msgs):
        fig, ax = plt.subplots()
        thread = ax.chatplot(msgs)
        children = thread.get_children()
        assert isinstance(children, list)

    def test_get_children_nonempty(self, msgs):
        fig, ax = plt.subplots()
        thread = ax.chatplot(msgs)
        assert len(thread.get_children()) > 0

    def test_get_children_returns_copy(self, msgs):
        fig, ax = plt.subplots()
        thread = ax.chatplot(msgs)
        c1 = thread.get_children()
        c2 = thread.get_children()
        assert c1 is not c2

    def test_disconnect_does_not_raise(self, msgs):
        fig, ax = plt.subplots()
        thread = ax.chatplot(msgs)
        thread.disconnect()  # should not raise

    def test_redraw_does_not_raise(self, msgs):
        fig, ax = plt.subplots()
        thread = ax.chatplot(msgs)
        thread.redraw()


# ── rcParams integration ──────────────────────────────────────────────────


class TestRcParams:
    def test_rcparam_style_respected(self, msgs):
        original = matplotlib.rcParams.get("yapplotlib.style", "default")
        try:
            matplotlib.rcParams["yapplotlib.style"] = "paper"
            fig, ax = plt.subplots()
            # Should use 'paper' style from rcParams (no explicit style arg)
            thread = ax.chatplot(msgs)
            assert isinstance(thread, ChatThread)
        finally:
            matplotlib.rcParams["yapplotlib.style"] = original
