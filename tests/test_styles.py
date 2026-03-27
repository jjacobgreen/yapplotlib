"""
Tests for style resolution and per-role colour lookup.
"""

import pytest
from yapplotlib._styles import resolve_style, resolve_role_style, get_align, THEMES


class TestResolveStyle:
    def test_none_returns_default(self):
        result = resolve_style(None)
        assert result == dict(THEMES['default'])

    def test_string_theme_name(self):
        for name in ('default', 'paper', 'dark', 'minimal'):
            result = resolve_style(name)
            assert result == dict(THEMES[name])

    def test_unknown_string_raises(self):
        with pytest.raises(ValueError, match="Unknown style"):
            resolve_style('nonexistent')

    def test_dict_merges_over_default(self):
        result = resolve_style({'user_facecolor': '#FF0000'})
        assert result['user_facecolor'] == '#FF0000'
        # Other keys still come from default
        assert result['font_family'] == THEMES['default']['font_family']

    def test_dict_with_base(self):
        result = resolve_style({'_base': 'paper', 'font_size': 12.0})
        assert result['font_size'] == 12.0
        assert result['font_family'] == THEMES['paper']['font_family']

    def test_wrong_type_raises(self):
        with pytest.raises(TypeError):
            resolve_style(42)

    def test_returns_copy(self):
        result1 = resolve_style('default')
        result2 = resolve_style('default')
        result1['user_facecolor'] = 'red'
        assert result2['user_facecolor'] != 'red'


class TestResolveRoleStyle:
    def test_user_role(self):
        s = resolve_style('default')
        rs = resolve_role_style('user', s)
        assert rs['facecolor'] == s['user_facecolor']
        assert rs['edgecolor'] == s['user_edgecolor']
        assert rs['textcolor'] == s['user_textcolor']

    def test_assistant_role(self):
        s = resolve_style('paper')
        rs = resolve_role_style('assistant', s)
        assert rs['facecolor'] == s['assistant_facecolor']

    def test_system_role(self):
        s = resolve_style('default')
        rs = resolve_role_style('system', s)
        assert rs['facecolor'] == s['system_facecolor']

    def test_alias_human_maps_to_user(self):
        s = resolve_style('default')
        rs_user  = resolve_role_style('user', s)
        rs_human = resolve_role_style('human', s)
        assert rs_human['facecolor'] == rs_user['facecolor']

    def test_alias_ai_maps_to_assistant(self):
        s = resolve_style('default')
        rs_asst = resolve_role_style('assistant', s)
        rs_ai   = resolve_role_style('ai', s)
        assert rs_ai['facecolor'] == rs_asst['facecolor']

    def test_unknown_role_deterministic(self):
        s = resolve_style('default')
        rs1 = resolve_role_style('oracle', s)
        rs2 = resolve_role_style('oracle', s)
        assert rs1['facecolor'] == rs2['facecolor']

    def test_unknown_role_returns_dict(self):
        s = resolve_style('default')
        rs = resolve_role_style('mystery_role', s)
        assert set(rs) == {'facecolor', 'edgecolor', 'textcolor'}


class TestGetAlign:
    def test_defaults(self):
        assert get_align('user')      == 'right'
        assert get_align('assistant') == 'left'
        assert get_align('system')    == 'center'

    def test_aliases(self):
        assert get_align('human') == 'right'
        assert get_align('ai')    == 'left'
        assert get_align('bot')   == 'left'

    def test_unknown_role_defaults_left(self):
        assert get_align('oracle') == 'left'

    def test_sender_align_override(self):
        overrides = {'user': 'left', 'assistant': 'right'}
        assert get_align('user',      overrides) == 'left'
        assert get_align('assistant', overrides) == 'right'
        # System not overridden → default
        assert get_align('system', overrides) == 'center'
