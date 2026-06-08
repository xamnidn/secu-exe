import tkinter as tk


class BaseView(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.configure(bg=self.app.theme.get_bg_card())

    def apply_theme(self):
        self.configure(bg=self.app.theme.get_bg_card())
