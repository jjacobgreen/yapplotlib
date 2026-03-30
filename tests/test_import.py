"""
Tests for package import, rcParams registration, and mplstyle availability.
"""

import matplotlib
import matplotlib.pyplot as plt
import pytest


def test_import():
    import yapplotlib

    assert yapplotlib.__version__ == "0.1.0"


def test_axes_method_injected():
    """Importing yapplotlib patches Axes.chatplot."""
    from matplotlib.axes import Axes

    import yapplotlib  # noqa: F401 — import for side-effect

    assert hasattr(Axes, "chatplot")
    assert callable(Axes.chatplot)


def test_themes_exposed():
    import yapplotlib

    assert set(yapplotlib.themes) == {"default", "paper", "dark", "minimal"}


def test_resolve_style_exported():
    import yapplotlib

    result = yapplotlib.resolve_style("paper")
    assert isinstance(result, dict)
    assert "user_facecolor" in result


def test_rcparams_registered():
    import yapplotlib  # noqa: F401

    expected = [
        "yapplotlib.style",
        "yapplotlib.bubble_width",
        "yapplotlib.show_names",
        "yapplotlib.show_timestamps",
        "yapplotlib.show_avatars",
        "yapplotlib.font_size",
        "yapplotlib.bubble_spacing",
        "yapplotlib.line_spacing",
        "yapplotlib.pad",
    ]
    for key in expected:
        assert key in matplotlib.rcParams, f"Missing rcParam: {key}"


def test_rcparam_defaults():
    import yapplotlib  # noqa: F401

    assert matplotlib.rcParams["yapplotlib.style"] == "default"
    assert matplotlib.rcParams["yapplotlib.bubble_width"] == pytest.approx(0.6)
    assert matplotlib.rcParams["yapplotlib.show_names"] is True
    assert matplotlib.rcParams["yapplotlib.show_timestamps"] is False


def test_mplstyle_paper_available():
    import yapplotlib  # noqa: F401

    # Should not raise
    with plt.style.context("yapplotlib.paper"):
        pass


def test_mplstyle_dark_available():
    import yapplotlib  # noqa: F401

    with plt.style.context("yapplotlib.dark"):
        pass


def test_mplstyle_paper_sets_yapplotlib_style():
    import matplotlib

    import yapplotlib  # noqa: F401

    with plt.style.context("yapplotlib.paper"):
        assert matplotlib.rcParams["yapplotlib.style"] == "paper"


def test_mplstyle_dark_sets_yapplotlib_style():
    import matplotlib

    import yapplotlib  # noqa: F401

    with plt.style.context("yapplotlib.dark"):
        assert matplotlib.rcParams["yapplotlib.style"] == "dark"
