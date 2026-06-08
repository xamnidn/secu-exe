import math
import threading
import tkinter as tk
from tkinter import messagebox

from secu.core.crypto_engine import CryptoEngine, HAS_ARGON
from secu.ui.components import Tooltip
from secu.ui.theme import *
from secu.utils.platform import ClipboardManager
from secu.utils.normalizer import ServiceNormalizer

from .base_view import BaseView


class MainView(BaseView):
    VERSION_TAG = "v1.3.0"
    PLACEHOLDER_MASTER = "Type master password..."
    PLACEHOLDER_SERVICE = "e.g., google.com"

    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.clear_timer = None
        self.countdown_id = None
        self.remaining = 0
        self.current_service = ""
        self.current_version = 0
        self._clipboard_dirty = False

        # Advanced overlay state
        self._advanced_open = False
        self._adv_animating = False
        self._adv_container = None   # shadow wrapper
        self._adv_frame = None       # inner panel

        # Generation variables -- always available regardless of accordion state
        self.var_upper = tk.BooleanVar(value=True)
        self.var_lower = tk.BooleanVar(value=True)
        self.var_number = tk.BooleanVar(value=True)
        self.var_symbol = tk.BooleanVar(value=True)
        self.var_device_bind = tk.BooleanVar(value=False)
        self._pw_length = tk.StringVar(value="16")
        self._service_var = tk.StringVar(value=self.PLACEHOLDER_SERVICE)
        self.spin_length = None

        self.build()
        self.apply_theme()
        self._setup_tab_order()
        self._setup_return_bindings()

        # Live preview trace
        self._service_var.trace_add("write", self._update_preview)

    def build(self):
        self._build_header()
        self._build_master_field()
        self._build_service_field()
        self._build_generate_button()
        self._build_output_area()
        self._build_bottom_bar()

    # -- Header ---------------------------------------------------------------

    def _build_header(self):
        top_row = tk.Frame(self, bg=self.app.theme.get_bg_card())
        top_row.pack(fill="x", pady=(0, 2))
        self._top_row = top_row

        left_group = tk.Frame(top_row, bg=self.app.theme.get_bg_card())
        left_group.pack(side="left")
        self._left_group = left_group

        if self.app.favicon_header:
            self._lbl_icon = tk.Label(
                left_group, image=self.app.favicon_header,
                bg=self.app.theme.get_bg_card()
            )
            self._lbl_icon.pack(side="left", padx=(0, 10), anchor="center")
        else:
            self._lbl_icon = None

        text_col = tk.Frame(left_group, bg=self.app.theme.get_bg_card())
        text_col.pack(side="left", anchor="center")

        self._header_title_lbl = tk.Label(
            text_col,
            text="secu.my.id",
            font=(FONT_FAMILY, 14, "bold"),
            bg=self.app.theme.get_bg_card(),
            fg=self.app.theme.get_text_main(),
        )
        self._header_title_lbl.pack(anchor="w")

        self._header_sub_lbl = tk.Label(
            text_col,
            text="Secure argon2id\u2011based deterministic password generator",
            font=(FONT_FAMILY, 9),
            bg=self.app.theme.get_bg_card(),
            fg=self.app.theme.get_text_muted(),
        )
        self._header_sub_lbl.pack(anchor="w")

        self._hamburger_btn = tk.Button(
            top_row,
            text="\u2630",
            bg=self.app.theme.get_bg_card(),
            fg=self.app.theme.get_text_muted(),
            font=(FONT_FAMILY, 13),
            relief="flat", bd=0, cursor="hand2",
            padx=4, pady=0,
            command=self._on_hamburger,
        )
        self._hamburger_btn.pack(side="right", pady=(8, 8))
        self._hamburger_btn.bind("<Enter>", lambda e: self._hamburger_btn.config(fg=self.app.theme.get_accent_blue()))
        self._hamburger_btn.bind("<Leave>", self._on_hamburger_leave)

    def _on_hamburger(self):
        self.app.show_hamburger_menu()
        self.app.position_hamburger_menu(self._hamburger_btn)

    def _on_hamburger_leave(self, event=None):
        self._hamburger_btn.config(
            fg=self.app.theme.get_text_main()
            if self.app.theme.dark_mode
            else self.app.theme.get_text_muted()
        )

    # -- Master Password ------------------------------------------------------

    def _build_master_field(self):
        self._master_lbl = tk.Label(
            self,
            text="Master password",
            bg=self.app.theme.get_bg_card(),
            fg=self.app.theme.get_text_main(),
            anchor="w",
            font=(FONT_FAMILY, 10, "bold"),
        )
        self._master_lbl.pack(anchor="w")

        self._master_frame = tk.Frame(
            self,
            bg=self.app.theme.get_bg_card(),
            highlightthickness=1,
            highlightbackground=self.app.theme.get_border_color(),
        )
        self._master_frame.pack(fill="x", pady=(6, 16))

        self.entry_master = tk.Entry(
            self._master_frame,
            bg=self.app.theme.get_bg_card(),
            fg=self.app.theme.get_text_main(),
            bd=0, font=(FONT_FAMILY, 11),
            insertbackground=self.app.theme.get_text_main(),
        )
        self.entry_master.pack(side="left", fill="x", expand=True, ipady=9, padx=10)
        self.entry_master.insert(0, self.PLACEHOLDER_MASTER)
        self.entry_master.config(fg=self.app.theme.get_text_muted(), show="")

        self.entry_master.bind("<FocusIn>",  self._on_master_focus_in)
        self.entry_master.bind("<FocusOut>", self._on_master_focus_out)
        self.entry_master.bind("<FocusIn>",  lambda e: self._master_frame.config(
            highlightbackground=self.app.theme.get_input_border_focus()), add="+")
        self.entry_master.bind("<FocusOut>", lambda e: self._master_frame.config(
            highlightbackground=self.app.theme.get_border_color()), add="+")

        self.btn_toggle = tk.Button(
            self._master_frame,
            text="Show",
            bg=self.app.theme.get_bg_card(),
            fg=self.app.theme.get_text_muted(),
            font=(FONT_FAMILY, 9, "bold"),
            relief="flat", bd=0, cursor="hand2",
            padx=8, takefocus=0,
            command=self._toggle_password,
            activebackground=self.app.theme.get_bg_card(),
            activeforeground=self.app.theme.get_accent_hover(),
        )
        self.btn_toggle.pack(side="right", padx=(0, 8), pady=5, fill="y")
        self.btn_toggle.bind("<Enter>", self._on_toggle_hover_in)
        self.btn_toggle.bind("<Leave>", self._on_toggle_hover_out)

    def _on_master_focus_in(self, event=None):
        if self.entry_master.get() == self.PLACEHOLDER_MASTER:
            self.entry_master.delete(0, tk.END)
            self.entry_master.config(fg=self.app.theme.get_text_main(), show="*")

    def _on_master_focus_out(self, event=None):
        if self.entry_master.get() == "":
            self.entry_master.insert(0, self.PLACEHOLDER_MASTER)
            self.entry_master.config(fg=self.app.theme.get_text_muted(), show="")

    def _toggle_password(self):
        if self.entry_master.cget("show") == "*":
            self.entry_master.config(show="")
            self.btn_toggle.config(text="Hide", fg=self.app.theme.get_accent_blue())
        else:
            self.entry_master.config(show="*")
            self.btn_toggle.config(text="Show", fg=self.app.theme.get_text_muted())

    def _on_toggle_hover_in(self, event=None):
        if self.btn_toggle.cget("text") == "Show":
            self.btn_toggle.config(fg=self.app.theme.get_accent_hover())

    def _on_toggle_hover_out(self, event=None):
        if self.btn_toggle.cget("text") == "Hide":
            self.btn_toggle.config(fg=self.app.theme.get_accent_blue())
        else:
            self.btn_toggle.config(fg=self.app.theme.get_text_muted())

    # -- Service Field --------------------------------------------------------

    def _build_service_field(self):
        lbl_row = tk.Frame(self, bg=self.app.theme.get_bg_card())
        lbl_row.pack(fill="x")
        self._lbl_row = lbl_row

        self._service_lbl = tk.Label(
            lbl_row,
            text="Service / Website",
            bg=self.app.theme.get_bg_card(),
            fg=self.app.theme.get_text_main(),
            anchor="w",
            font=(FONT_FAMILY, 10, "bold"),
        )
        self._service_lbl.pack(side="left")

        ver_group = tk.Frame(lbl_row, bg=self.app.theme.get_bg_card())
        ver_group.pack(side="right")
        self._ver_group = ver_group

        ver_lbl = tk.Label(
            ver_group,
            text="Ver",
            bg=self.app.theme.get_bg_card(),
            fg=self.app.theme.get_text_muted(),
            font=(FONT_FAMILY, 9, "bold"),
            cursor="question_arrow",
        )
        ver_lbl.pack(side="left")
        Tooltip(ver_lbl, "Rotation Version: increment when a site requires a new password", self.app.theme)

        self.spin_version = tk.Spinbox(
            ver_group,
            from_=1, to=999, width=4,
            font=(FONT_FAMILY, 9),
            bg=self.app.theme.get_spin_bg(),
            fg=self.app.theme.get_text_main(),
            buttonbackground=self.app.theme.get_spin_bg(),
            bd=0,
            highlightthickness=1,
            highlightbackground=self.app.theme.get_border_color(),
        )
        self.spin_version.pack(side="left", padx=(4, 0))
        self.spin_version.delete(0, tk.END)
        self.spin_version.insert(0, "1")
        self.spin_version.bind("<FocusIn>", lambda e: self.spin_version.config(
            highlightbackground=self.app.theme.get_input_border_focus()))
        self.spin_version.bind("<FocusOut>", lambda e: self.spin_version.config(
            highlightbackground=self.app.theme.get_border_color()))

        self._svc_frame = tk.Frame(
            self,
            bg=self.app.theme.get_bg_card(),
            highlightthickness=1,
            highlightbackground=self.app.theme.get_border_color(),
        )
        self._svc_frame.pack(fill="x", pady=(6, 0))

        self.entry_service = tk.Entry(
            self._svc_frame,
            bg=self.app.theme.get_bg_card(),
            fg=self.app.theme.get_text_muted(),
            bd=0, font=(FONT_FAMILY, 11),
            insertbackground=self.app.theme.get_text_main(),
            textvariable=self._service_var,
        )
        self.entry_service.pack(fill="x", expand=True, ipady=9, padx=10)
        # Hapus insert, karena StringVar sudah berisi placeholder

        self.entry_service.bind("<FocusIn>",  self._on_svc_focus_in)
        self.entry_service.bind("<FocusOut>", self._on_svc_focus_out)
        self.entry_service.bind("<FocusIn>",  lambda e: self._svc_frame.config(
            highlightbackground=self.app.theme.get_input_border_focus()), add="+")
        self.entry_service.bind("<FocusOut>", lambda e: self._svc_frame.config(
            highlightbackground=self.app.theme.get_border_color()), add="+")

        # Live preview of normalized service name
        self._preview_label = tk.Label(
            self,
            text="",
            font=(FONT_FAMILY, 9),
            fg=self.app.theme.get_text_muted(),
            bg=self.app.theme.get_bg_card(),
        )
        self._preview_label.pack(anchor="w", padx=10, pady=(2, 4))

    def _on_svc_focus_in(self, event=None):
        if self._service_var.get() == self.PLACEHOLDER_SERVICE:
            self._service_var.set("")
            self.entry_service.config(fg=self.app.theme.get_text_main())

    def _on_svc_focus_out(self, event=None):
        if self._service_var.get() == "":
            self._service_var.set(self.PLACEHOLDER_SERVICE)
            self.entry_service.config(fg=self.app.theme.get_text_muted())

    def _update_preview(self, *args):
        """Live preview of normalized service name."""
        raw = self._service_var.get()
        if raw == self.PLACEHOLDER_SERVICE:
            self._preview_label.config(text="")
            return
        preview = ServiceNormalizer.preview(raw)
        if preview and preview != raw.strip().lower():
            self._preview_label.config(text=f"Preview: {preview}")
        else:
            self._preview_label.config(text="")

    # -- Generate Button ------------------------------------------------------

    def _build_generate_button(self):
        # Shadow wrapper -- 2px offset bottom-right
        self._gen_shadow = tk.Frame(
            self,
            bg=self.app.theme.get_shadow_color(),
        )
        self._gen_shadow.pack(fill="x", pady=(0, 16))

        self._gen_inner = tk.Frame(self._gen_shadow, bg=self.app.theme.get_bg_card())
        self._gen_inner.pack(fill="x", padx=(0, 2), pady=(0, 2))

        self.btn_generate = tk.Button(
            self._gen_inner,
            text="Generate password",
            bg=self.app.theme.get_accent_blue(),
            fg="white",
            font=(FONT_FAMILY, 11, "bold"),
            relief="flat", bd=0,
            cursor="hand2",
            pady=11,
            command=self.generate_logic,
            activebackground=self.app.theme.get_accent_hover(),
            activeforeground="white",
        )
        self.btn_generate.pack(fill="x")
        self.btn_generate.bind("<Enter>", lambda e: (
            self.btn_generate.config(bg=self.app.theme.get_accent_hover()),
            self._gen_shadow.config(bg=self.app.theme.get_shadow_color()),
        ))
        self.btn_generate.bind("<Leave>", lambda e: (
            self.btn_generate.config(bg=self.app.theme.get_accent_blue()),
        ))
        self.btn_generate.bind("<FocusIn>", lambda e: (
            self.btn_generate.config(bg=self.app.theme.get_accent_hover())))
        self.btn_generate.bind("<FocusOut>", lambda e: (
            self.btn_generate.config(bg=self.app.theme.get_accent_blue())))

    # -- Output Area ----------------------------------------------------------

    def _build_output_area(self):
        self._output_lbl = tk.Label(
            self,
            text="Your password",
            font=(FONT_FAMILY, 10, "bold"),
            bg=self.app.theme.get_bg_card(),
            fg=self.app.theme.get_text_main(),
        )
        self._output_lbl.pack(anchor="w")

        self._output_frame = tk.Frame(
            self,
            bg=self.app.theme.get_bg_card(),
            highlightthickness=1,
            highlightbackground=self.app.theme.get_accent_blue(),
        )
        self._output_frame.pack(fill="x", pady=(6, 4))

        self.entry_output = tk.Entry(
            self._output_frame,
            font=("Consolas", 14, "bold"),
            bg=self.app.theme.get_bg_card(),
            fg=self.app.theme.get_accent_blue(),
            bd=0,
            highlightthickness=0,
            insertwidth=0,
            justify="center",
            takefocus=0,
        )
        self.entry_output.pack(side="left", fill="x", expand=True, ipady=13, padx=12)
        self.entry_output.config(state="readonly")

        self.btn_copy = tk.Button(
            self._output_frame,
            text="Copy",
            bg=self.app.theme.get_bg_card(),
            fg=self.app.theme.get_accent_blue(),
            font=(FONT_FAMILY, 9, "bold"),
            relief="flat", bd=0,
            cursor="hand2",
            padx=8, takefocus=0,
            command=self.copy_to_clipboard,
            activebackground=self.app.theme.get_bg_card(),
            activeforeground=self.app.theme.get_accent_hover(),
        )
        self.btn_copy.pack(side="right", padx=(6, 10), pady=6, fill="y")
        self.btn_copy.bind("<Enter>", self._on_copy_hover_in)
        self.btn_copy.bind("<Leave>", self._on_copy_hover_out)

        info_row = tk.Frame(self, bg=self.app.theme.get_bg_card())
        info_row.pack(fill="x", pady=(2, 4))
        self._info_row = info_row

        self.strength_label = tk.Label(
            info_row,
            text="Estimated Entropy: \u2014",
            font=(FONT_FAMILY, 8, "italic"),
            bg=self.app.theme.get_bg_card(),
            fg=self.app.theme.get_text_muted(),
            cursor="question_arrow",
        )
        self.strength_label.pack(side="left")
        Tooltip(
            self.strength_label,
            "Reflects output space only. Master password quality is not measured.",
            self.app.theme,
        )

        self.countdown_label = tk.Label(
            info_row,
            text="",
            font=(FONT_FAMILY, 8, "bold"),
            bg=self.app.theme.get_bg_card(),
            fg=self.app.theme.get_warning_color(),
        )
        self.countdown_label.pack(side="right")

    def _on_copy_hover_in(self, event=None):
        if self.btn_copy.cget("text") != "\u2713 COPIED":
            self.btn_copy.config(fg=self.app.theme.get_accent_hover())

    def _on_copy_hover_out(self, event=None):
        if self.btn_copy.cget("text") != "\u2713 COPIED":
            self.btn_copy.config(fg=self.app.theme.get_accent_blue())

    # -- Bottom Bar -----------------------------------------------------------

    def _build_bottom_bar(self):
        self._spacer = tk.Frame(self, bg=self.app.theme.get_bg_card())
        self._spacer.pack(fill="both", expand=True)

        self._bottom = tk.Frame(self, bg=self.app.theme.get_bg_card())
        self._bottom.pack(fill="x", pady=(4, 0))

        self._tip_text = "Portable mode \u2014 password reproducible on any device"
        self._tip_fg = None

        self.bottom_label = tk.Label(
            self._bottom,
            text=self._tip_text,
            font=(FONT_FAMILY, 8),
            bg=self.app.theme.get_bg_card(),
            fg=self.app.theme.get_text_muted(),
        )
        self.bottom_label.pack(side="left", anchor="w")
        self.tip_label = self.bottom_label
        self.status_bar = self.bottom_label

        self.btn_advanced = tk.Button(
            self._bottom,
            text="\u25bc  Advanced options",
            bg=self.app.theme.get_bg_card(),
            fg=self.app.theme.get_accent_blue(),
            font=(FONT_FAMILY, 8, "bold"),
            relief="flat", bd=0,
            cursor="hand2",
            padx=0, pady=0,
            takefocus=0,
            command=self._toggle_advanced,
            activebackground=self.app.theme.get_bg_card(),
            activeforeground=self.app.theme.get_accent_hover(),
        )
        self.btn_advanced.pack(side="right", anchor="e")
        self.btn_advanced.bind("<Enter>", lambda e: self.btn_advanced.config(fg=self.app.theme.get_accent_hover()))
        self.btn_advanced.bind("<Leave>", lambda e: self.btn_advanced.config(
            fg=self.app.theme.get_accent_blue()))

    # -- Advanced Options overlay -----------------------------------------------

    def _toggle_advanced(self):
        if self._adv_animating:
            return
        if self._advanced_open:
            self._close_advanced()
        else:
            self._open_advanced()

    def _open_advanced(self):
        self._advanced_open = True
        self._adv_animating = True
        self.btn_advanced.config(text="\u25b2  Advanced options")

        self.update_idletasks()
        self_h = self.winfo_height()
        self_w = self.winfo_width()
        overlay_h = self_h // 2
        target_y = self_h - overlay_h
        shadow_offset = 2

        # Shadow container -- slightly larger, offset bottom-right
        self._adv_container = tk.Frame(
            self,
            bg=self.app.theme.get_shadow_color(),
        )
        self._adv_container.place(
            x=shadow_offset,
            y=self_h + shadow_offset,
            width=self_w - shadow_offset,
            height=overlay_h,
        )

        # Inner panel sits on top, offset top-left leaving shadow visible bottom-right
        self._adv_frame = tk.Frame(
            self._adv_container,
            bg=self.app.theme.get_bg_card(),
            highlightthickness=1,
            highlightbackground=self.app.theme.get_border_color(),
        )
        self._adv_frame.place(x=0, y=0, width=self_w - shadow_offset - shadow_offset,
                              height=overlay_h - shadow_offset)

        self._build_advanced_content(self._adv_frame)
        self._animate_open(target_y, self_h, overlay_h, self_w, shadow_offset)

    def _animate_open(self, target_y, self_h, overlay_h, self_w, shadow_offset):
        start_y = self_h
        steps = 6
        delta = (target_y - start_y) / steps
        container = self._adv_container

        def step(current_y, count):
            if container is None or not container.winfo_exists():
                self._adv_animating = False
                return
            if count >= steps:
                container.place(x=shadow_offset, y=target_y + shadow_offset,
                                width=self_w - shadow_offset, height=overlay_h)
                self._adv_animating = False
                return
            new_y = int(current_y + delta)
            container.place(x=shadow_offset, y=new_y + shadow_offset,
                            width=self_w - shadow_offset, height=overlay_h)
            self.app.root.after(12, lambda: step(new_y, count + 1))

        step(start_y, 0)

    def _close_advanced(self):
        self._advanced_open = False
        self._adv_animating = True
        self.btn_advanced.config(text="\u25bc  Advanced options")

        if self.spin_length is not None:
            try:
                self._pw_length.set(self.spin_length.get())
            except Exception:
                pass

        self.update_idletasks()
        self_h = self.winfo_height()
        self_w = self.winfo_width()
        overlay_h = self_h // 2
        current_y = self_h - overlay_h
        shadow_offset = 2

        container = self._adv_container
        self._adv_container = None
        self._adv_frame = None
        self.spin_length = None

        self._animate_close(container, current_y, self_h, overlay_h, self_w, shadow_offset)

    def _animate_close(self, container, start_y, self_h, overlay_h, self_w, shadow_offset):
        steps = 6
        delta = (self_h - start_y) / steps

        def step(current_y, count):
            if container is None or not container.winfo_exists():
                self._adv_animating = False
                return
            if count >= steps:
                container.destroy()
                self._adv_animating = False
                return
            new_y = int(current_y + delta)
            container.place(x=shadow_offset, y=new_y + shadow_offset,
                            width=self_w - shadow_offset, height=overlay_h)
            self.app.root.after(12, lambda: step(new_y, count + 1))

        step(start_y, 0)

    def _build_advanced_content(self, parent):
        # Top bar
        top = tk.Frame(parent, bg=self.app.theme.get_bg_card())
        top.pack(fill="x", padx=18, pady=(14, 8))
        self._adv_top = top

        self._adv_title = tk.Label(
            top,
            text="Advanced options",
            font=(FONT_FAMILY, 10, "bold"),
            bg=self.app.theme.get_bg_card(),
            fg=self.app.theme.get_text_main(),
        )
        self._adv_title.pack(side="left")

        self._adv_close_btn = tk.Button(
            top,
            text="\u2715",
            bg=self.app.theme.get_bg_card(),
            fg=self.app.theme.get_text_muted(),
            font=(FONT_FAMILY, 11),
            relief="flat", bd=0,
            cursor="hand2",
            padx=4, pady=0,
            takefocus=0,
            command=self._close_advanced,
            activebackground=self.app.theme.get_bg_card(),
            activeforeground=self.app.theme.get_warning_color(),
        )
        self._adv_close_btn.pack(side="right")
        self._adv_close_btn.bind("<Enter>", lambda e: self._adv_close_btn.config(fg=self.app.theme.get_warning_color()))
        self._adv_close_btn.bind("<Leave>", lambda e: self._adv_close_btn.config(
            fg=self.app.theme.get_text_muted()))

        # Separator
        self._adv_sep = tk.Frame(parent, height=1, bg=self.app.theme.get_separator_color())
        self._adv_sep.pack(fill="x", padx=18, pady=(0, 12))

        # Character Parameters
        self._adv_char_lbl = tk.Label(
            parent,
            text="Character parameters",
            bg=self.app.theme.get_bg_card(),
            fg=self.app.theme.get_text_muted(),
            anchor="w",
            font=(FONT_FAMILY, 8, "bold"),
        )
        self._adv_char_lbl.pack(anchor="w", padx=18)

        param_frame = tk.Frame(parent, bg=self.app.theme.get_bg_card())
        param_frame.pack(fill="x", padx=18, pady=(6, 12))
        param_frame.columnconfigure((0, 1), weight=1)
        self._param_frame = param_frame

        self._chip_upper = self._create_chip(param_frame, "A-Z  Uppercase", self.var_upper, 0, 0)
        self._chip_lower = self._create_chip(param_frame, "a-z  Lowercase", self.var_lower, 0, 1)
        self._chip_number = self._create_chip(param_frame, "0-9  Numbers",   self.var_number, 1, 0)
        self._chip_symbol = self._create_chip(param_frame, "!@#  Symbols",   self.var_symbol, 1, 1)

        # Password Length + Device Bind
        length_frame = tk.Frame(parent, bg=self.app.theme.get_bg_card())
        length_frame.pack(fill="x", padx=18, pady=(0, 8))
        self._length_frame = length_frame

        self._length_lbl = tk.Label(
            length_frame,
            text="Password Length:",
            font=(FONT_FAMILY, 9),
            bg=self.app.theme.get_bg_card(),
            fg=self.app.theme.get_text_main(),
        )
        self._length_lbl.pack(side="left")

        self.spin_length = tk.Spinbox(
            length_frame,
            from_=8, to=128, width=5,
            font=(FONT_FAMILY, 9),
            bg=self.app.theme.get_spin_bg(),
            fg=self.app.theme.get_text_main(),
            buttonbackground=self.app.theme.get_spin_bg(),
            bd=0,
            highlightthickness=1,
            highlightbackground=self.app.theme.get_border_color(),
            textvariable=self._pw_length,
        )
        self.spin_length.pack(side="left", padx=(8, 0), ipady=2)
        self.spin_length.bind("<FocusIn>", lambda e: self.spin_length.config(
            highlightbackground=self.app.theme.get_input_border_focus()))
        self.spin_length.bind("<FocusOut>", lambda e: self.spin_length.config(
            highlightbackground=self.app.theme.get_border_color()))

        self._length_hint = tk.Label(
            length_frame,
            text="(8\u2013128)",
            font=(FONT_FAMILY, 8),
            bg=self.app.theme.get_bg_card(),
            fg=self.app.theme.get_text_muted(),
        )
        self._length_hint.pack(side="left", padx=(6, 0))

        self.chk_device = tk.Checkbutton(
            length_frame,
            text="Bind to device",
            variable=self.var_device_bind,
            font=(FONT_FAMILY, 8),
            bg=self.app.theme.get_bg_card(),
            fg=self.app.theme.get_text_muted(),
            activebackground=self.app.theme.get_bg_card(),
            selectcolor=self.app.theme.get_bg_card(),
            cursor="hand2",
            takefocus=0,
            command=self._on_device_bind_toggle,
        )
        self.chk_device.pack(side="right")
        Tooltip(
            self.chk_device,
            "Bind to device: password can only be regenerated on this machine.\n"
            "Leave unchecked for portability across devices.",
            self.app.theme,
        )

    def _create_chip(self, parent, text, variable, row, col):
        btn = tk.Checkbutton(
            parent,
            text=text,
            variable=variable,
            indicatoron=False,
            relief="flat", bd=1,
            highlightthickness=1,
            highlightbackground=self.app.theme.get_border_color(),
            bg=self.app.theme.get_chip_off(),
            fg=self.app.theme.get_text_main(),
            selectcolor=self.app.theme.get_chip_on(),
            activebackground=self.app.theme.get_chip_off(),
            font=(FONT_FAMILY, 9),
            cursor="hand2",
            padx=12, pady=6,
        )
        btn.grid(row=row, column=col, sticky="ew", padx=3, pady=3)

        def on_enter(e):
            btn.config(bg=self.app.theme.get_chip_hov_on()
                       if variable.get() else self.app.theme.get_chip_hov_off())

        def on_leave(e):
            btn.config(bg=self.app.theme.get_chip_on()
                       if variable.get() else self.app.theme.get_chip_off())

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        variable.trace_add("write", lambda *a: btn.config(
            bg=self.app.theme.get_chip_on()
            if variable.get() else self.app.theme.get_chip_off()
        ))
        return btn

    # -- Tab / Return bindings ------------------------------------------------

    def _setup_tab_order(self):
        def goto(w):
            w.focus_set()
            return "break"
        self.entry_master.bind("<Tab>",        lambda e: goto(self.entry_service))
        self.entry_service.bind("<Tab>",       lambda e: goto(self.spin_version))
        self.spin_version.bind("<Tab>",        lambda e: goto(self.btn_generate))
        self.btn_generate.bind("<Shift-Tab>",  lambda e: goto(self.spin_version))
        self.spin_version.bind("<Shift-Tab>",  lambda e: goto(self.entry_service))
        self.entry_service.bind("<Shift-Tab>", lambda e: goto(self.entry_master))

    def _setup_return_bindings(self):
        self.entry_master.bind("<Return>",  lambda e: self.generate_logic())
        self.entry_service.bind("<Return>", lambda e: self.generate_logic())
        self.spin_version.bind("<Return>",  lambda e: self.generate_logic())

    # -- Theme ----------------------------------------------------------------

    def apply_theme(self):
        bg       = self.app.theme.get_bg_card()
        txt      = self.app.theme.get_text_main()
        muted    = self.app.theme.get_text_muted()
        border   = self.app.theme.get_border_color()
        accent   = self.app.theme.get_accent_blue()
        hover    = self.app.theme.get_accent_hover()
        success  = self.app.theme.get_success_fg()
        warning  = self.app.theme.get_warning_color()
        spin_bg  = self.app.theme.get_spin_bg()
        shadow   = self.app.theme.get_shadow_color()

        self.configure(bg=bg)
        self._spacer.configure(bg=bg)

        # Header
        self._top_row.configure(bg=bg)
        self._left_group.configure(bg=bg)
        if self._lbl_icon:
            self._lbl_icon.config(bg=bg)
        self._header_title_lbl.config(bg=bg, fg=txt)
        self._hamburger_btn.config(bg=bg)
        self._on_hamburger_leave()
        self._header_sub_lbl.config(bg=bg, fg=muted)

        # Master
        self._master_lbl.config(bg=bg, fg=txt)
        self._master_frame.config(bg=bg, highlightbackground=border)
        self.entry_master.config(bg=bg, insertbackground=txt)
        self.entry_master.config(fg=muted if self.entry_master.get() == self.PLACEHOLDER_MASTER else txt)
        self.btn_toggle.config(bg=bg, activebackground=bg,
                               fg=accent if self.btn_toggle.cget("text") == "Hide" else muted)

        # Service
        self._lbl_row.configure(bg=bg)
        self._service_lbl.config(bg=bg, fg=txt)
        self._ver_group.configure(bg=bg)
        for w in self._ver_group.winfo_children():
            if isinstance(w, tk.Label):
                w.config(bg=bg, fg=muted)
            elif isinstance(w, tk.Spinbox):
                w.config(bg=spin_bg, fg=txt, highlightbackground=border,
                         buttonbackground=spin_bg)
        self._svc_frame.config(bg=bg, highlightbackground=border)
        self.entry_service.config(bg=bg, insertbackground=txt)
        self.entry_service.config(fg=muted if self._service_var.get() == self.PLACEHOLDER_SERVICE else txt)
        self._preview_label.config(bg=bg, fg=muted)

        # Generate button + shadow
        self._gen_shadow.config(bg=shadow)
        self._gen_inner.config(bg=bg)
        self.btn_generate.config(bg=accent, activebackground=hover)

        # Output
        self._output_lbl.config(bg=bg, fg=txt)
        self._output_frame.config(bg=bg, highlightbackground=accent)
        self.entry_output.config(bg=bg, fg=accent)
        self.btn_copy.config(bg=bg, activebackground=bg,
                             fg=success if self.btn_copy.cget("text") == "\u2713 COPIED" else accent)
        self._info_row.configure(bg=bg)
        self.strength_label.config(bg=bg)
        self.countdown_label.config(bg=bg, fg=warning)

        # Bottom
        self._bottom.configure(bg=bg)
        self.bottom_label.config(bg=bg,
                                 fg=self._tip_fg if self._tip_fg else muted)
        self.btn_advanced.config(bg=bg, fg=accent, activebackground=bg)

        # Advanced overlay (if open)
        if self._adv_frame and self._adv_frame.winfo_exists():
            chip_off = self.app.theme.get_chip_off()
            chip_on  = self.app.theme.get_chip_on()
            sep      = self.app.theme.get_separator_color()
            self._adv_container.config(bg=shadow)
            self._adv_frame.config(bg=bg, highlightbackground=border)
            self._adv_top.configure(bg=bg)
            self._adv_title.config(bg=bg, fg=txt)
            self._adv_close_btn.config(bg=bg, activebackground=bg)
            self._adv_sep.config(bg=sep)
            self._adv_char_lbl.config(bg=bg, fg=muted)
            self._param_frame.configure(bg=bg)
            for w in self._param_frame.winfo_children():
                if isinstance(w, tk.Checkbutton):
                    w.config(bg=chip_off, fg=txt, selectcolor=chip_on,
                             highlightbackground=border, activebackground=chip_off)
            self._length_frame.configure(bg=bg)
            self._length_lbl.config(bg=bg, fg=txt)
            if self.spin_length is not None:
                self.spin_length.config(bg=spin_bg, fg=txt,
                                        highlightbackground=border, buttonbackground=spin_bg)
            if hasattr(self, '_length_hint') and self._length_hint.winfo_exists():
                self._length_hint.config(bg=bg, fg=muted)
            self.chk_device.config(bg=bg, activebackground=bg, selectcolor=bg,
                                   fg=warning if self.var_device_bind.get() else muted)

    # -- Status helpers -------------------------------------------------------

    def _set_status(self, text, fg=None):
        self.bottom_label.config(text=text or self._tip_text,
                                 fg=fg or self.app.theme.get_warning_color())

    def _restore_tip(self):
        self.bottom_label.config(
            text=self._tip_text,
            fg=self._tip_fg if self._tip_fg else self.app.theme.get_text_muted()
        )

    # -- Clipboard --------------------------------------------------------------

    def copy_to_clipboard(self):
        text = self.entry_output.get()
        if not text:
            return
        ClipboardManager.copy(self.app.root, text)
        self._clipboard_dirty = True
        self.btn_copy.config(text="\u2713 COPIED", fg=self.app.theme.get_success_fg())
        self._set_status("Copied! Clipboard clears in 10s", self.app.theme.get_success_fg())
        self.app.root.after(1500, lambda: self.btn_copy.config(text="Copy", fg=self.app.theme.get_accent_blue()))
        self.cancel_auto_clear()
        self._clear_ui_only()
        self.clear_timer = self.app.root.after(10000, self._finalize_clipboard_clear)

    def _finalize_clipboard_clear(self):
        if self._clipboard_dirty:
            ClipboardManager.overwrite(self.app.root)
            self._clipboard_dirty = False
        self._set_status("Clipboard cleared!", self.app.theme.get_success_fg())
        self.app.root.after(1500, lambda: self._restore_tip()
                            if self.bottom_label.cget("text") == "Clipboard cleared!" else None)
        self.clear_timer = None

    def cancel_auto_clear(self):
        if self.clear_timer:
            self.app.root.after_cancel(self.clear_timer)
            self.clear_timer = None
        if self.countdown_id:
            self.app.root.after_cancel(self.countdown_id)
            self.countdown_id = None

    def update_countdown(self):
        if self.remaining > 0:
            self.countdown_label.config(
                text=f"{self.current_service} v{self.current_version} \u2013 clears in {self.remaining}s",
                fg=self.app.theme.get_warning_color(),
            )
            self.remaining -= 1
            self.countdown_id = self.app.root.after(1000, self.update_countdown)
        else:
            self._perform_clear()

    def _perform_clear(self):
        self.entry_output.config(state="normal")
        self.entry_output.delete(0, tk.END)
        self.entry_output.config(state="readonly")
        self.strength_label.config(text="Estimated Entropy: \u2014",
                                   fg=self.app.theme.get_text_muted())
        self.countdown_label.config(text="")
        if self._clipboard_dirty:
            ClipboardManager.overwrite(self.app.root)
            self._clipboard_dirty = False
        self._set_status("Cleared!", self.app.theme.get_success_fg())
        self.app.root.after(1500, lambda: self._restore_tip()
                            if self.bottom_label.cget("text") == "Cleared!" else None)
        self.clear_timer = None
        self.countdown_id = None
        self.current_service = ""
        self.current_version = 0

    def _clear_ui_only(self):
        self.entry_output.config(state="normal")
        self.entry_output.delete(0, tk.END)
        self.entry_output.config(state="readonly")
        self.strength_label.config(text="Estimated Entropy: \u2014",
                                   fg=self.app.theme.get_text_muted())
        self.countdown_label.config(text="")

    def force_clear(self):
        self.cancel_auto_clear()
        self._perform_clear()

    # -- Generate logic -------------------------------------------------------

    def generate_logic(self):
        # Close advanced panel if open
        if self._advanced_open and not self._adv_animating:
            self._close_advanced()

        if not HAS_ARGON:
            messagebox.showerror(
                "Missing Library", "Please install argon2-cffi first:\n\npip install argon2-cffi"
            )
            return

        master_pass = self.entry_master.get()
        if not master_pass or master_pass == self.PLACEHOLDER_MASTER:
            messagebox.showwarning("Warning", "Master password cannot be empty.")
            return

        raw_service = self.entry_service.get()
        if not raw_service or raw_service == self.PLACEHOLDER_SERVICE:
            messagebox.showwarning(
                "Service Name Required",
                "Service name is required as a unique salt per site.\n\n"
                "Without it, every site would receive an identical password.\n"
                "Enter a domain or service name (e.g., google.com).",
            )
            return

        # Normalize BEFORE building salt
        try:
            service_name = ServiceNormalizer.normalize(raw_service)
        except (TypeError, ValueError) as e:
            messagebox.showwarning('Invalid Service Name', str(e))
            return

        rotation_version = self.get_version()
        device_component = self.app.device_id if self.var_device_bind.get() else ""
        service_salt = f"{self.VERSION_TAG}:{device_component}:{service_name}:{rotation_version}"

        self.entry_master.delete(0, tk.END)
        self.entry_master.config(fg=self.app.theme.get_text_main(), show="*")
        self.cancel_auto_clear()
        self.btn_generate.config(state="disabled", text="Generating...")
        self._set_status("Deriving key...", self.app.theme.get_accent_blue())
        target_length = self.get_length()

        thread = threading.Thread(
            target=self._argon_hash_thread,
            args=(master_pass, service_salt, target_length, service_name, rotation_version),
            daemon=True,
        )
        thread.start()

    def _argon_hash_thread(self, master_pass, service_salt, target_length,
                           display_service, display_version):
        try:
            final_password = CryptoEngine.derive_password(
                master_pass, service_salt, target_length,
                self.var_upper.get(), self.var_lower.get(),
                self.var_number.get(), self.var_symbol.get(),
            )
            self.app.root.after(0, self._on_hash_complete,
                                final_password, display_service, display_version)
        except Exception as e:
            self.app.root.after(0, self._on_hash_error, str(e))

    def _on_hash_complete(self, password, service_name, version_num):
        self.entry_output.config(state="normal")
        self.entry_output.delete(0, tk.END)
        self.entry_output.insert(0, password)
        self.entry_output.config(state="readonly", fg=self.app.theme.get_accent_blue())
        strength_text, color = self.evaluate_strength(password)
        self.strength_label.config(text=strength_text, fg=color)
        self.current_service = service_name
        self.current_version = version_num
        self.remaining = 10
        self.update_countdown()
        # Baris berikut DIHAPUS untuk mencegah eksekusi ganda pembersihan
        self.btn_generate.config(state="normal", text="Generate password")

    def _on_hash_error(self, error_msg):
        self.btn_generate.config(state="normal", text="Generate password")
        self._set_status("Error!", self.app.theme.get_warning_color())
        messagebox.showerror("Hash Error", f"Argon2 failed:\n{error_msg}")

    def _on_device_bind_toggle(self):
        if self.var_device_bind.get():
            self.chk_device.config(fg=self.app.theme.get_warning_color())
            self._tip_text = "Device key stored locally \u2014 locked to this machine"
            self._tip_fg = self.app.theme.get_warning_color()
        else:
            self.chk_device.config(fg=self.app.theme.get_text_muted())
            self._tip_text = "Portable mode \u2014 password reproducible on any device"
            self._tip_fg = None
        self._restore_tip()

    # -- Helpers --------------------------------------------------------------

    def get_length(self):
        try:
            return max(8, min(128, int(self._pw_length.get())))
        except (ValueError, tk.TclError):
            return 16

    def get_version(self):
        try:
            return max(1, min(999, int(self.spin_version.get())))
        except ValueError:
            return 1

    def get_charset_size(self):
        charset = CryptoEngine.build_charset(
            self.var_upper.get(), self.var_lower.get(),
            self.var_number.get(), self.var_symbol.get(),
        )
        return max(len(charset), 1)

    def evaluate_strength(self, password):
        entropy = len(password) * math.log2(self.get_charset_size())
        if entropy >= 128:
            return f"Est. Entropy: {entropy:.0f} bits (Very Strong)", self.app.theme.get_very_strong_color()
        elif entropy >= 80:
            return f"Est. Entropy: {entropy:.0f} bits (Strong)", self.app.theme.get_success_fg()
        elif entropy >= 50:
            return f"Est. Entropy: {entropy:.0f} bits (Medium)", self.app.theme.get_accent_blue()
        else:
            return f"Est. Entropy: {entropy:.0f} bits (Weak)", self.app.theme.get_warning_color()