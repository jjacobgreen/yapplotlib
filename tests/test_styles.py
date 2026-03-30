"""
Tests for style resolution and per-role colour lookup.
"""

import pytest

from yapplotlib._styles import THEMES, get_align, resolve_role_style, resolve_style

_REQUIRED_KEYS = {
    "user_facecolor",
    "user_edgecolor",
    "user_textcolor",
    "assistant_facecolor",
    "assistant_edgecolor",
    "assistant_textcolor",
    "system_facecolor",
    "system_edgecolor",
    "system_textcolor",
    "figure_facecolor",
    "axes_facecolor",
    "font_family",
    "font_size",
}


class TestResolveStyle:
    def test_none_returns_complete_style(self):
        result = resolve_style(None)
        assert _REQUIRED_KEYS.issubset(result)

    def test_default_returns_complete_style(self):
        result = resolve_style("default")
        assert _REQUIRED_KEYS.issubset(result)

    def test_explicit_themes_unchanged(self):
        for name in ("paper", "dark", "minimal"):
            result = resolve_style(name)
            assert result == dict(THEMES[name])

    def test_default_inherits_mpl_backgrounds(self):
        import matplotlib

        original_fc = matplotlib.rcParams["figure.facecolor"]
        original_ac = matplotlib.rcParams["axes.facecolor"]
        try:
            matplotlib.rcParams["figure.facecolor"] = "#AABBCC"
            matplotlib.rcParams["axes.facecolor"] = "#AABBCC"
            result = resolve_style("default")
            assert result["figure_facecolor"] == "#AABBCC"
            assert result["axes_facecolor"] == "#AABBCC"
        finally:
            matplotlib.rcParams["figure.facecolor"] = original_fc
            matplotlib.rcParams["axes.facecolor"] = original_ac

    def test_default_dark_background_uses_dark_palette(self):
        import matplotlib

        original = matplotlib.rcParams["axes.facecolor"]
        try:
            matplotlib.rcParams["axes.facecolor"] = "#0B141A"
            result = resolve_style("default")
            assert result["user_facecolor"] == THEMES["dark"]["user_facecolor"]
        finally:
            matplotlib.rcParams["axes.facecolor"] = original

    def test_default_light_background_uses_light_palette(self):
        import matplotlib

        original = matplotlib.rcParams["axes.facecolor"]
        try:
            matplotlib.rcParams["axes.facecolor"] = "white"
            result = resolve_style("default")
            assert result["user_facecolor"] == THEMES["default"]["user_facecolor"]
        finally:
            matplotlib.rcParams["axes.facecolor"] = original

    def test_unknown_string_raises(self):
        with pytest.raises(ValueError, match="Unknown style"):
            resolve_style("nonexistent")

    def test_dict_merges_over_default(self):
        result = resolve_style({"user_facecolor": "#FF0000"})
        assert result["user_facecolor"] == "#FF0000"
        assert isinstance(result["font_family"], str)

    def test_dict_with_base(self):
        result = resolve_style({"_base": "paper", "font_size": 12.0})
        assert result["font_size"] == 12.0
        assert result["font_family"] == THEMES["paper"]["font_family"]

    def test_wrong_type_raises(self):
        with pytest.raises(TypeError):
            resolve_style(42)

    def test_returns_copy(self):
        result1 = resolve_style("default")
        result2 = resolve_style("default")
        result1["user_facecolor"] = "red"
        assert result2["user_facecolor"] != "red"


class TestResolveRoleStyle:
    def test_user_role(self):
        s = resolve_style("default")
        rs = resolve_role_style("user", s)
        assert rs["facecolor"] == s["user_facecolor"]
        assert rs["edgecolor"] == s["user_edgecolor"]
        assert rs["textcolor"] == s["user_textcolor"]

    def test_assistant_role(self):
        s = resolve_style("paper")
        rs = resolve_role_style("assistant", s)
        assert rs["facecolor"] == s["assistant_facecolor"]

    def test_system_role(self):
        s = resolve_style("default")
        rs = resolve_role_style("system", s)
        assert rs["facecolor"] == s["system_facecolor"]

    def test_alias_human_maps_to_user(self):
        s = resolve_style("default")
        rs_user = resolve_role_style("user", s)
        rs_human = resolve_role_style("human", s)
        assert rs_human["facecolor"] == rs_user["facecolor"]

    def test_alias_ai_maps_to_assistant(self):
        s = resolve_style("default")
        rs_asst = resolve_role_style("assistant", s)
        rs_ai = resolve_role_style("ai", s)
        assert rs_ai["facecolor"] == rs_asst["facecolor"]

    def test_unknown_role_deterministic(self):
        s = resolve_style("default")
        rs1 = resolve_role_style("oracle", s)
        rs2 = resolve_role_style("oracle", s)
        assert rs1["facecolor"] == rs2["facecolor"]

    def test_unknown_role_returns_dict(self):
        s = resolve_style("default")
        rs = resolve_role_style("mystery_role", s)
        assert set(rs) == {"facecolor", "edgecolor", "textcolor"}


class TestGetAlign:
    def test_defaults(self):
        assert get_align("user") == "right"
        assert get_align("assistant") == "left"
        assert get_align("system") == "center"

    def test_aliases(self):
        assert get_align("human") == "right"
        assert get_align("ai") == "left"
        assert get_align("bot") == "left"

    def test_unknown_role_defaults_left(self):
        assert get_align("oracle") == "left"

    def test_sender_align_override(self):
        overrides = {"user": "left", "assistant": "right"}
        assert get_align("user", overrides) == "left"
        assert get_align("assistant", overrides) == "right"
        # System not overridden → default
        assert get_align("system", overrides) == "center"
