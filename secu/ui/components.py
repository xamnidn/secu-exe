import tkinter as tk
from secu.ui.theme import FONT_FAMILY


class Tooltip:
    def __init__(self, widget, text, theme=None):
        self.widget = widget
        self.text = text
        self.tip = None
        self.theme = theme
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, event=None):
        bg = self.theme.get_bg_card() if self.theme else "#1F2937"
        fg = self.theme.get_text_main() if self.theme else "white"
        self.tip = tk.Toplevel(self.widget)
        self.tip.overrideredirect(True)
        self.tip.configure(bg=bg)
        tk.Label(
            self.tip,
            text=self.text,
            bg=bg,
            fg=fg,
            font=(FONT_FAMILY, 8),
            padx=8,
            pady=5,
        ).pack()
        self.tip.update_idletasks()
        sw = self.widget.winfo_screenwidth()
        sh = self.widget.winfo_screenheight()
        tw = self.tip.winfo_reqwidth()
        th = self.tip.winfo_reqheight()
        x = min(self.widget.winfo_pointerx(), sw - tw - 10)
        y = min(self.widget.winfo_pointery() + 22, sh - th - 10)
        self.tip.geometry(f"+{x}+{y}")

    def hide(self, event=None):
        if self.tip:
            self.tip.destroy()
            self.tip = None
