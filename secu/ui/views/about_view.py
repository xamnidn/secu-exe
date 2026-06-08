import tkinter as tk
from secu.ui.theme import FONT_FAMILY
from .base_view import BaseView


class AboutView(BaseView):
    VERSION = "v1.3.0"
    ABOUT_DETAILS = """Key Derivation
Argon2id · time cost 3 · memory 64 MB · parallelism 4
Output length 32 bytes · OWASP Interactive Login recommendation

Runtime
Python 3 · Tkinter · argon2-cffi · pyperclip (optional)

License
MIT License · Free for personal and commercial use

More information:
• secu.my.id

© SECU Project 2026"""

    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.build()
        self.apply_theme()

    def build(self):
        self._back_btn = tk.Button(
            self,
            text="\u2190 Back",
            bg=self.app.theme.get_bg_card(),
            fg=self.app.theme.get_accent_blue(),
            font=(FONT_FAMILY, 9, "bold"),
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.app.go_back,
        )
        self._back_btn.pack(anchor="w", pady=(0, 12))
        self._back_btn.bind(
            "<Enter>", lambda e: self._back_btn.config(fg=self.app.theme.get_accent_hover())
        )
        self._back_btn.bind(
            "<Leave>", lambda e: self._back_btn.config(fg=self.app.theme.get_accent_blue())
        )

        content = tk.Frame(self, bg=self.app.theme.get_bg_card())
        content.pack()
        self._content = content

        if self.app.favicon_header:
            self._icon = tk.Label(content, image=self.app.favicon_header, bg=self.app.theme.get_bg_card())
            self._icon.pack(pady=(0, 10))
        else:
            self._icon = None

        self._title = tk.Label(
            content,
            text="SECU Password Generator",
            font=(FONT_FAMILY, 12, "bold"),
            bg=self.app.theme.get_bg_card(),
            fg=self.app.theme.get_text_main(),
        )
        self._title.pack()

        self._version = tk.Label(
            content,
            text=self.VERSION,
            font=(FONT_FAMILY, 9),
            bg=self.app.theme.get_bg_card(),
            fg=self.app.theme.get_text_muted(),
        )
        self._version.pack(pady=(2, 12))

        self._details = tk.Label(
            content,
            text=self.ABOUT_DETAILS.strip(),
            font=(FONT_FAMILY, 9),
            bg=self.app.theme.get_bg_card(),
            fg=self.app.theme.get_text_main(),
            justify="center",
        )
        self._details.pack()

    def apply_theme(self):
        bg = self.app.theme.get_bg_card()
        txt = self.app.theme.get_text_main()
        muted = self.app.theme.get_text_muted()
        accent = self.app.theme.get_accent_blue()

        self.configure(bg=bg)
        self._back_btn.config(bg=bg, fg=accent)
        self._content.configure(bg=bg)
        if self._icon:
            self._icon.config(bg=bg)
        self._title.config(bg=bg, fg=txt)
        self._version.config(bg=bg, fg=muted)
        self._details.config(bg=bg, fg=txt)