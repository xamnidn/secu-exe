import tkinter as tk
from secu.core.config_manager import ConfigManager
from secu.ui.theme import *
from secu.ui.assets import load_favicon
from secu.ui.views.main_view import MainView
from secu.ui.views.help_view import HelpView
from secu.ui.views.about_view import AboutView
from secu.utils.path import get_config_dir


class SecuApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SECU Password Generator")
        self.root.geometry("540x690")
        self.root.minsize(540, 690)
        self.root.resizable(True, True)

        self.theme = ThemeManager(config_dir=get_config_dir())
        self._menu_win = None

        self.config_manager = ConfigManager()
        self.device_id = self.config_manager.get_device_id()

        self.favicon_window, self.favicon_header = load_favicon(root)

        self.root.configure(bg=self.theme.get_bg_main())

        self.main_card = tk.Frame(
            self.root,
            bg=self.theme.get_bg_card(),
            highlightthickness=1,
            highlightbackground=self.theme.get_border_color(),
            padx=25,
            pady=22,
        )
        self.main_card.pack(fill="both", expand=True, padx=20, pady=20)

        self.views = {}
        self._create_views()
        self.show_view("main")

    def _create_views(self):
        self.views["main"] = MainView(self.main_card, self)
        self.views["help"] = HelpView(self.main_card, self)
        self.views["about"] = AboutView(self.main_card, self)

    def show_view(self, name):
        for view in self.views.values():
            view.pack_forget()
        view = self.views[name]
        view.pack(fill="both", expand=True)
        if name == "main":
            self.root.title("SECU Password Generator")
        elif name == "help":
            self.root.title("Help — SECU Password Generator")
        elif name == "about":
            self.root.title("About — SECU Password Generator")

    def go_back(self):
        self.show_view("main")

    def toggle_dark_mode(self):
        self.theme.toggle()
        self.root.configure(bg=self.theme.get_bg_main())
        self.main_card.configure(
            bg=self.theme.get_bg_card(),
            highlightbackground=self.theme.get_border_color(),
        )
        for view in self.views.values():
            if hasattr(view, "apply_theme"):
                view.apply_theme()

    def show_hamburger_menu(self):
        self._close_hamburger()
        bg = self.theme.get_bg_card()
        fg = self.theme.get_text_main()
        sep = self.theme.get_border_color()
        hov = self.theme.get_bg_main()

        self._menu_win = tk.Toplevel(self.root)
        self._menu_win.overrideredirect(True)
        self._menu_win.configure(bg=sep)
        self._menu_win.attributes("-topmost", True)

        inner = tk.Frame(self._menu_win, bg=bg, padx=0, pady=0)
        inner.pack(padx=1, pady=1)

        dm_label = "Dark Mode: ON" if self.theme.dark_mode else "Dark Mode: OFF"

        items = [
            (dm_label, self._do_dark_mode),
            ("Help", lambda: [self._close_hamburger(), self.show_view("help")]),
            ("About", lambda: [self._close_hamburger(), self.show_view("about")]),
        ]

        for label, fn in items:
            btn = tk.Button(
                inner,
                text=label,
                anchor="w",
                bg=bg,
                fg=fg,
                activebackground=hov,
                activeforeground=fg,
                font=(FONT_FAMILY, 9),
                relief="flat",
                bd=0,
                cursor="hand2",
                padx=18,
                pady=7,
                width=16,
                command=fn,
            )
            btn.pack(fill="x")
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=hov))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=bg))
            if label == dm_label:
                tk.Frame(inner, height=1, bg=sep).pack(fill="x", padx=4)

        self._menu_win.bind("<FocusOut>", lambda e: self._close_hamburger())
        self._menu_win.focus_set()

    def position_hamburger_menu(self, btn):
        self._menu_win.update_idletasks()
        btn_x = btn.winfo_rootx()
        btn_y = btn.winfo_rooty() + btn.winfo_height()
        mw = self._menu_win.winfo_reqwidth()
        self._menu_win.geometry(f"+{btn_x - mw + btn.winfo_width()}+{btn_y + 2}")

    def _do_dark_mode(self):
        self._close_hamburger()
        self.toggle_dark_mode()

    def _close_hamburger(self):
        if getattr(self, "_menu_win", None):
            try:
                self._menu_win.destroy()
            except Exception:
                pass
            self._menu_win = None
