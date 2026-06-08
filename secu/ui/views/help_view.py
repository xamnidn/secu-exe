import tkinter as tk
from secu.ui.theme import FONT_FAMILY
from .base_view import BaseView


class HelpView(BaseView):
    HELP_TEXT = """GENERATING A PASSWORD

1. Master Password
   Enter your master password -- the single secret that seeds all derived passwords. This value is never stored. Use a passphrase of at least 20 characters combining mixed case, digits, and symbols. Do not reuse it anywhere else.

2. Service / Website
   Enter the domain or service identifier (e.g., google.com). This value acts as a per-site salt, ensuring each service receives a unique password even when the master password is identical.

3. Version
   Defaults to 1. Increment this value when a site requires you to change your password without altering your master password. Keep an offline record of the version in use per service.

4. Character Parameters
   Select the character sets to include in the output. Enabling all four sets (uppercase, lowercase, digits, symbols) produces the highest entropy for a given length.

5. Password Length
   Recommended minimum: 16 characters. For high-value accounts, use 24 or more.

6. Generate
   Press GENERATE PASSWORD or hit Enter. The password appears in the output field and is automatically copied to the clipboard. It is cleared from both the field and the clipboard after 10 seconds.


DEVICE BINDING

The "Bind to device" option (shown to the right of Password Length) controls whether a hidden device-specific key is mixed into the salt.

  Disabled -- Portable mode (default)
    The device key is omitted. The same password can be regenerated on any device using identical inputs. This is the recommended mode for most users.

  Enabled (opt-in)
    A secret key unique to this installation is included in the salt. Passwords can only be regenerated on this machine. The status bar displays a notice while this mode is active.

When switching between modes, existing passwords for a service will change. Decide on a mode before generating passwords for production accounts.


MASTER PASSWORD GUIDANCE

The security of every derived password depends entirely on the strength of your master password. Treat it with the same care as a private cryptographic key.

  * Minimum recommended length: 20 characters
  * Use a random combination of uppercase, lowercase, digits, and symbols
  * Do not base it on dictionary words, names, or dates
  * Do not reuse it for any other account or application
  * Store it only in a location you fully trust -- never digitally alongside this application

There is no recovery mechanism. A forgotten master password cannot be reconstructed.


SECURITY NOTES

  * All computation is performed locally. No data is transmitted over a network.
  * No passwords, master passwords, or service names are written to disk.
  * The clipboard is overwritten with random data after 10 seconds.
  * Argon2id is used for key derivation with parameters meeting current OWASP recommendations (time cost 3, memory 64 MB, parallelism 4).
  * Due to Python's memory model, the master password may persist in process memory until garbage collection. On a healthy, single-user system this risk is minimal. Clear sensitive sessions by closing the application when done.


CLIPBOARD SECURITY

SECU automatically clears the clipboard after 10 seconds and overwrites it with 48 bytes of random data. However, the operating system or third-party applications may still retain the password.

Please be aware of the following limitations:

  * Windows 10/11 Clipboard History (Win+V) may retain the password in its history.
  * macOS Universal Clipboard can synchronize the password to other devices.
  * Third-party clipboard managers (Ditto, CopyQ, Klipper, GPaste) may keep their own history.
  * Screenshot tools, screen recorders, or keyloggers may capture the password while displayed.

RECOMMENDATIONS:
  * Disable clipboard history in your OS settings if possible.
  * Avoid using third-party clipboard managers while operating SECU.
  * Lock your screen immediately after using SECU.
  * Use full-disk encryption on your device.

Final security responsibility rests with you. SECU provides the tools; how you use them is your choice.
"""

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

        self._title = tk.Label(
            self,
            text="User Guide",
            font=(FONT_FAMILY, 12, "bold"),
            bg=self.app.theme.get_bg_card(),
            fg=self.app.theme.get_text_main(),
        )
        self._title.pack(anchor="w", pady=(0, 10))

        text_frame = tk.Frame(self, bg=self.app.theme.get_bg_card())
        text_frame.pack(fill="both", expand=True)
        self._text_frame = text_frame

        self._text = tk.Text(
            text_frame,
            wrap="word",
            font=(FONT_FAMILY, 9),
            bg=self.app.theme.get_bg_card(),
            fg=self.app.theme.get_text_main(),
            relief="flat",
            bd=0,
            padx=2,
            pady=2,
            state="normal",
            highlightthickness=0,
        )
        self._text.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(text_frame, command=self._text.yview)
        scrollbar.pack(side="right", fill="y")
        self._text.config(yscrollcommand=scrollbar.set)
        self._scrollbar = scrollbar

        self._text.insert("1.0", self.HELP_TEXT.strip())
        self._text.config(state="disabled")

    def apply_theme(self):
        bg = self.app.theme.get_bg_card()
        txt = self.app.theme.get_text_main()
        accent = self.app.theme.get_accent_blue()

        self.configure(bg=bg)
        self._back_btn.config(bg=bg, fg=accent)
        self._title.config(bg=bg, fg=txt)
        self._text_frame.configure(bg=bg)
        self._text.config(bg=bg, fg=txt)
        self._scrollbar.config(bg=bg)
