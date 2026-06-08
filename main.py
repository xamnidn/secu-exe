import ctypes
import tkinter as tk
from secu.ui.app import SecuApp


def main():
    try:
        PROCESS_SYSTEM_DPI_AWARE = 1
        ctypes.windll.shcore.SetProcessDPIAwareness(PROCESS_SYSTEM_DPI_AWARE)
    except Exception:
        pass
    root = tk.Tk()
    app = SecuApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
