BG_MAIN = "#F3F4F6"
BG_CARD = "#FFFFFF"
TEXT_MAIN = "#1F2937"
TEXT_MUTED = "#6B7280"
BORDER_COLOR = "#D1D5DB"

ACCENT_BLUE = "#1a3d6b"
ACCENT_HOVER = "#245090"

SUCCESS_FG = "#16A34A"
SUCCESS_FG_DARK = "#4ADE80"

WARNING_COLOR = "#DC2626"
VERY_STRONG_COLOR = "#8B5CF6"

DARK_BG_MAIN = "#111827"
DARK_BG_CARD = "#1F2937"
DARK_TEXT_MAIN = "#F9FAFB"
DARK_TEXT_MUTED = "#9CA3AF"
DARK_BORDER_COLOR = "#374151"

FONT_FAMILY = "Segoe UI"


class ThemeManager:
    def __init__(self, config_dir=None):
        self._config_dir = config_dir
        self.dark_mode = False
        self._load()

    def _config_path(self):
        if self._config_dir:
            return self._config_dir / "theme.json"
        return None

    def _load(self):
        path = self._config_path()
        if path and path.exists():
            try:
                import json
                data = json.loads(path.read_text())
                self.dark_mode = data.get("dark_mode", False)
            except Exception:
                self.dark_mode = False

    def _save(self):
        path = self._config_path()
        if path:
            try:
                import json
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps({"dark_mode": self.dark_mode}, indent=2))
            except Exception:
                pass

    def toggle(self):
        self.dark_mode = not self.dark_mode
        self._save()

    def get_bg_main(self):
        return DARK_BG_MAIN if self.dark_mode else BG_MAIN

    def get_bg_card(self):
        return DARK_BG_CARD if self.dark_mode else BG_CARD

    def get_text_main(self):
        return DARK_TEXT_MAIN if self.dark_mode else TEXT_MAIN

    def get_text_muted(self):
        return DARK_TEXT_MUTED if self.dark_mode else TEXT_MUTED

    def get_border_color(self):
        return DARK_BORDER_COLOR if self.dark_mode else BORDER_COLOR

    def get_accent_blue(self):
        return "#5b8fd4" if self.dark_mode else ACCENT_BLUE

    def get_accent_hover(self):
        return "#7aaee0" if self.dark_mode else ACCENT_HOVER

    def get_success_fg(self):
        return SUCCESS_FG_DARK if self.dark_mode else SUCCESS_FG

    def get_warning_color(self):
        return WARNING_COLOR

    def get_very_strong_color(self):
        return VERY_STRONG_COLOR

    def get_spin_bg(self):
        return DARK_BG_MAIN if self.dark_mode else BG_MAIN

    def get_separator_color(self):
        return DARK_BORDER_COLOR if self.dark_mode else "#E5E7EB"

    def get_chip_off(self):
        return "#1F2937" if self.dark_mode else "#E5E7EB"

    def get_chip_on(self):
        return "#374151" if self.dark_mode else "#E0E7FF"

    def get_chip_hov_off(self):
        return "#374151" if self.dark_mode else "#E5E7EB"

    def get_chip_hov_on(self):
        return "#4B5563" if self.dark_mode else "#D1D5DB"

    def get_shadow_color(self):
        return "#0A0F1A" if self.dark_mode else "#B0B8C4"

    def get_input_border_focus(self):
        return "#3d6fa8" if self.dark_mode else ACCENT_BLUE
