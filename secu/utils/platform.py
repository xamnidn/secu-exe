import secrets
import tkinter as tk

try:
    import pyperclip
    HAS_CLIP = True
except ImportError:
    HAS_CLIP = False


class ClipboardManager:
    @staticmethod
    def copy(root: tk.Tk, text: str):
        if HAS_CLIP:
            pyperclip.copy(text)
        else:
            root.clipboard_clear()
            root.clipboard_append(text)
            root.update()

    @staticmethod
    def overwrite(root: tk.Tk):
        noise = secrets.token_urlsafe(48)
        ClipboardManager.copy(root, noise)
