from secu.ui.theme import ThemeManager


def test_toggle_theme():
    theme = ThemeManager()
    current = theme.dark_mode
    theme.toggle()
    assert theme.dark_mode != current
