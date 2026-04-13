import concurrent
import concurrent.futures
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import subprocess
import threading
import requests
from urllib.parse import urlparse, quote
import os
import sys
import json
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont

# Import dari struktur baru
from src.core.config_manager import ConfigManager
from src.core.gitlab_api import GitLabAPI
from src.core.git_operations import GitOperations
from src.utils import i18n
from src.utils.i18n import _
from src.utils.helpers import center_window, ToolTip
from src.utils.dialogs import show_custom_message, show_info, show_warning, show_error, show_confirmation
from src.constants import (
    ICON_SETTINGS, ICON_INFO, ICON_LOGOUT, ICON_USER, ICON_VISIBILITY,
    ICON_VISIBILITY_OFF, ICON_SEARCH, ICON_RESET,
    ICON_EXPORT, ICON_IMPORT, ICON_CHECK_ALL, ICON_UNCHECK_ALL, ICON_LOGS, ICON_OPEN_IN_NEW,
    DEFAULT_LOGIN_WIDTH, DEFAULT_LOGIN_HEIGHT, DEFAULT_EXPANDED_WIDTH,
    DEFAULT_EXPANDED_HEIGHT, DEFAULT_PER_PAGE
)

class GLRCApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        # Resolve bundled asset path (PyInstaller onefile extracts to _MEIPASS).
        self.base_dir = getattr(sys, "_MEIPASS", os.path.dirname(__file__))
        self.app_version = self.load_app_version()

        # Load Config Manager
        self.config = ConfigManager()
        
        # Set tema & bahasa
        ctk.set_appearance_mode(self.config.get_theme())
        ctk.set_default_color_theme("blue")
        i18n.set_language(self.config.get_language())

        # Load Material Icons Font
        try:
            font_path = os.path.join(self.base_dir, "assets", "fonts", "MaterialIcons-Regular.ttf")
            ctk.FontManager.load_font(font_path)
            self.icon_font = ctk.CTkFont(family="Material Icons", size=22)
            # Render Material Icons glyphs to CTkImage for use in buttons with text
            self._pil_icon_font = ImageFont.truetype(font_path, 20)
            self.icon_search_img = self._render_icon(ICON_SEARCH)
            self.icon_reset_img = self._render_icon(ICON_RESET)
            self.icon_export_img = self._render_icon(ICON_EXPORT)
            self.icon_import_img = self._render_icon(ICON_IMPORT)
            self.icon_check_all_img = self._render_icon(ICON_CHECK_ALL)
            self.icon_uncheck_all_img = self._render_icon(ICON_UNCHECK_ALL)
            self.icon_logs_img = self._render_icon(ICON_LOGS)
            self.open_in_new_img = self._render_icon(ICON_OPEN_IN_NEW)
        except Exception as e:
            self.icon_font = None
            self._pil_icon_font = None
            self.icon_search_img = None
            self.icon_reset_img = None
            self.icon_export_img = None
            self.icon_import_img = None
            self.icon_check_all_img = None
            self.icon_uncheck_all_img = None
            self.icon_logs_img = None
            self.open_in_new_img = None

        # Load Open Sans Font
        try:
            self.opensans_files = {
                "regular": os.path.join("assets", "fonts", "OpenSans-Regular.ttf"),
                "bold": os.path.join("assets", "fonts", "OpenSans-Bold.ttf"),
                "italic": os.path.join("assets", "fonts", "OpenSans-Italic.ttf"),
                "light": os.path.join("assets", "fonts", "OpenSans-Light.ttf"),
                "medium": os.path.join("assets", "fonts", "OpenSans-Medium.ttf"),
            }
            for font_file in self.opensans_files.values():
                font_path = os.path.join(self.base_dir, font_file)
                if os.path.exists(font_path):
                    ctk.FontManager.load_font(font_path)
        except Exception:
            pass
            
        # Set Default Font to Open Sans
        ctk.set_widget_scaling(1.0)
        ctk.set_window_scaling(1.0)

        # Load Logo Image
        try:
            logo_path = os.path.join(self.base_dir, "assets", "icons", "logo.png")
            self.logo_img = ctk.CTkImage(light_image=Image.open(logo_path), dark_image=Image.open(logo_path), size=(28, 28))
            self.logo_img_large = ctk.CTkImage(light_image=Image.open(logo_path), dark_image=Image.open(logo_path), size=(48, 48))
        except Exception:
            self.logo_img = None
            self.logo_img_large = None

        try:
            self.ico_path = os.path.join(self.base_dir, "assets", "icons", "logo.ico")
            self.iconbitmap(self.ico_path)
        except Exception:
            self.ico_path = None

        try:
            png_path = os.path.join(self.base_dir, "assets", "icons", "logo.png")
            if os.path.exists(png_path):
                self.img_icon = tk.PhotoImage(file=png_path)
                self.iconphoto(True, self.img_icon)
        except Exception:
            self.img_icon = None
            pass

        self.title(_("app_name"))

        screen_x = self.winfo_screenwidth()
        screen_y = self.winfo_screenheight()

        self.expanded_w = min(DEFAULT_EXPANDED_WIDTH, screen_x - 100)
        self.expanded_h = min(DEFAULT_EXPANDED_HEIGHT, screen_y - 100)
        self.login_w = DEFAULT_LOGIN_WIDTH
        self.login_h = DEFAULT_LOGIN_HEIGHT

        self.minsize(self.login_w, self.login_h)
        self.geometry(f"{self.login_w}x{self.login_h}")
        center_window(self, self.login_w, self.login_h)
        self.after(100, lambda: self.apply_window_icon(self))

        # Variabel Global
        self.api_token = ""
        self.gitlab_url = ""
        self.repo_items = []
        self.user_name = ""
        self.user_email = ""

        # --- Variabel Pagination & Seleksi ---
        self.current_page = 1
        self.per_page = DEFAULT_PER_PAGE
        self.total_rows = 0
        self.total_pages = 1
        self.selected_repos = {}
        self.cached_projects = []
        self.filtered_projects = None
        
        # --- Variabel State Fetching ---
        self.is_fetching = False

        # Setup UI
        self.setup_login_frame()
        self.setup_main_frame()

        self.login_frame.pack(fill="both", expand=True)
        self.check_saved_token()

    def _render_icon(self, glyph, size=24, render_size=20):
        """Render a Material Icons glyph to CTkImage."""
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.text((size / 2, size / 2), glyph, fill="white", font=self._pil_icon_font, anchor="mm")
        return ctk.CTkImage(light_image=img, dark_image=img, size=(render_size, render_size))

    def load_app_version(self):
        version_path = os.path.join(self.base_dir, "VERSION")
        try:
            if os.path.exists(version_path):
                with open(version_path, "r", encoding="utf-8") as f:
                    value = f.read().strip()
                    if value:
                        return value
        except Exception:
            pass
        return "1.0.0"

    def check_saved_token(self):
        """Memeriksa dan mengisi form jika ada token yang masih valid tersimpan."""
        saved_pat = self.config.get_valid_pat()
        if saved_pat:
            self.token_entry.insert(0, saved_pat)
            self.save_pat_var.set(True)
            self.pat_days_entry.configure(state="normal")

            # Show actual remaining days in the entry
            saved_info = self.config.get_saved_pat()
            if saved_info and saved_info.get("expiry_date"):
                try:
                    exp_dt = datetime.fromisoformat(saved_info["expiry_date"])
                    days_rem = (exp_dt - datetime.now()).days
                    self.pat_days_entry.delete(0, tk.END)
                    self.pat_days_entry.insert(0, "0" if days_rem > 3650 else str(max(days_rem, 1)))
                except Exception:
                    pass
            
            # Otomatis login (opsional) - di sini hanya mengisi field saja
            # Supaya pengguna tahu, kita beri info ringan
            self.subtitle.configure(text=_("session_restored"), text_color="#2ecc71")
            
            # Start auth thread automatically
            self.start_auth_thread()
        else:
            self.save_pat_var.set(False)
            self.pat_days_entry.configure(state="disabled")

    def activate_window(self, window):
        try:
            window.wait_visibility()
        except Exception:
            pass

        self.apply_window_icon(window)

        try:
            window.lift()
            window.attributes("-topmost", True)
            window.after(150, lambda: window.attributes("-topmost", False))
            window.focus_force()
        except Exception:
            pass

    def configure_modal_window(self, modal, width, height, on_escape=None, use_grab=True):
        modal.withdraw()  # Hide while configuring

        modal.geometry(f"{width}x{height}")
        modal.resizable(False, False)
        modal.transient(self)
        center_window(modal, width, height)

        close_action = on_escape or modal.destroy
        modal.protocol("WM_DELETE_WINDOW", close_action)
        modal.bind("<Escape>", lambda event: close_action())

        # Apply icon before showing — no visible flicker
        self.apply_window_icon(modal)

        modal.deiconify()  # Show fully configured window
        self.activate_window(modal)
        # Single backup for CTkToplevel internal callbacks (~150ms)
        modal.after(200, lambda: self.apply_window_icon(modal))
        if use_grab:
            modal.grab_set()

    def reset_to_login_size(self):
        self.geometry(f"{self.login_w}x{self.login_h}")
        self.minsize(self.login_w, self.login_h)
        self.update_idletasks()
        center_window(self, self.login_w, self.login_h)

    def _set_btn_state(self, btn, state):
        """Only call .configure() if state actually changed – avoids CTkButton _draw() jitter."""
        try:
            if str(btn.cget("state")) != state:
                btn.configure(state=state)
        except Exception:
            btn.configure(state=state)

    def update_selection_action_buttons(self):
        has_repos = bool(self.repo_items)
        has_selection = bool(self.selected_repos)

        self._set_btn_state(self.btn_select_all, "normal" if has_repos else "disabled")
        self._set_btn_state(self.btn_deselect_all, "normal" if has_repos else "disabled")
        self._set_btn_state(self.btn_export, "normal" if has_selection else "disabled")

    def update_repo_range_label(self, displayed_count):
        if self.total_rows <= 0 or displayed_count <= 0:
            self.page_label.configure(text=_("page").format(start=0, end=0, total=self.total_rows))
            return

        start_row = ((self.current_page - 1) * self.per_page) + 1
        end_row = start_row + displayed_count - 1
        self.page_label.configure(text=_("page").format(start=start_row, end=end_row, total=self.total_rows))


    # =========================================================================
    # LOGIN FRAME
    # =========================================================================
    def setup_login_frame(self):
        self.login_frame = ctk.CTkFrame(self)

        if getattr(self, "logo_img_large", None):
            title = ctk.CTkLabel(
                self.login_frame, text=f"  {_('app_title')}", image=self.logo_img_large, compound="left",
                font=ctk.CTkFont(family="Open Sans", size=26, weight="bold")
            )
        else:
            title = ctk.CTkLabel(
                self.login_frame, text=f"  {_('app_title')}",
                font=ctk.CTkFont(family="Open Sans", size=26, weight="bold")
            )
        title.pack(pady=(50, 5))

        self.subtitle = ctk.CTkLabel(
            self.login_frame,
            text=_("app_subtitle"),
            font=ctk.CTkFont(family="Open Sans Light", size=13),
            text_color="gray"
        )
        self.subtitle.pack(pady=(0, 10))
        
        # Info Box untuk Pengguna Baru
        info_box = ctk.CTkFrame(self.login_frame, fg_color="#ebf5fb", corner_radius=6)
        info_box.pack(padx=80, pady=(0, 20), fill="x")
        
        info_text = _("login_info")
        ctk.CTkLabel(info_box, text=info_text, justify="center", text_color="#154360", font=ctk.CTkFont(family="Open Sans", size=12)).pack(pady=10, padx=10)

        # --- Form Frame ---
        form = ctk.CTkFrame(self.login_frame, fg_color="transparent")
        form.pack(padx=60, pady=(10, 0))

        ctk.CTkLabel(form, text=_("instance_url"), anchor="w", font=ctk.CTkFont(family="Open Sans", weight="bold")).pack(anchor="w")
        self.url_entry = ctk.CTkEntry(form, width=380, height=38, placeholder_text="https://gitlab.example.com")
        self.url_entry.insert(0, self.config.get_gitlab_url())
        self.url_entry.pack(pady=(2, 14))

        ctk.CTkLabel(form, text=_("pat_label"), anchor="w", font=ctk.CTkFont(family="Open Sans", weight="bold")).pack(anchor="w")
        token_frame = ctk.CTkFrame(form, fg_color="transparent")
        token_frame.pack(fill="x", pady=(2, 10))
        
        self.token_entry = ctk.CTkEntry(token_frame, width=330, height=34, show="*", placeholder_text="glpat-xxxxxxxxxxxx")
        self.token_entry.pack(side="left", expand=True, fill="x")
        
        self.show_pwd_btn = ctk.CTkButton(
            token_frame,
            text=ICON_VISIBILITY if getattr(self, "icon_font", None) else "👁",
            font=getattr(self, "icon_font", None),
            width=34,
            height=34,
            fg_color="gray40",
            hover_color="gray30",
            command=self.toggle_pat_visibility,
        )
        self.show_pwd_btn.pack(side="right", padx=(4, 0))
        ToolTip(self.show_pwd_btn, _("show_token"))
        self.is_pat_visible = False

        # --- PAT Save Options ---
        pat_opt_frame = ctk.CTkFrame(form, fg_color="transparent")
        pat_opt_frame.pack(fill="x", pady=(0, 20))
        
        self.save_pat_var = tk.BooleanVar(value=False)
        self.save_pat_chk = ctk.CTkCheckBox(
            pat_opt_frame, text=_("save_token"), 
            variable=self.save_pat_var, 
            command=self.toggle_pat_days
        )
        self.save_pat_chk.pack(side="left")
        
        ctk.CTkLabel(pat_opt_frame, text=_("duration")).pack(side="left", padx=(15, 5))
        
        # disable input hari jika checkbox tidak dicentang, enable jika dicentang. Default 7 hari.
        self.pat_days_entry = ctk.CTkEntry(pat_opt_frame, width=50, height=28)
        self.pat_days_entry.insert(0, "7")
        self.pat_days_entry.configure(state="disabled")
        self.pat_days_entry.pack(side="left")
        ToolTip(self.pat_days_entry, _("pat_days_tooltip"))
        
        # self.pat_days_entry = ctk.CTkEntry(pat_opt_frame, width=50, height=28)
        # self.pat_days_entry.insert(0, "7")
        # self.pat_days_entry.configure(state="disabled")
        # self.pat_days_entry.pack(side="left")
        # ToolTip(self.pat_days_entry, _("pat_days_tooltip"))
        
        ctk.CTkLabel(pat_opt_frame, text=_("days")).pack(side="left", padx=(5, 0))

        self.connect_btn = ctk.CTkButton(
            form, text=_("connect_btn"),
            height=44,
            font=ctk.CTkFont(family="Open Sans Medium", size=14, weight="bold"),
            command=self.start_auth_thread
        )
        self.connect_btn.pack(fill="x")

    def toggle_pat_visibility(self):
        self.is_pat_visible = not self.is_pat_visible
        if self.is_pat_visible:
            self.token_entry.configure(show='')
            self.show_pwd_btn.configure(text=ICON_VISIBILITY_OFF if getattr(self, "icon_font", None) else '🙈')
            ToolTip(self.show_pwd_btn, _("hide_token"))
        else:
            self.token_entry.configure(show='*')
            self.show_pwd_btn.configure(text=ICON_VISIBILITY if getattr(self, "icon_font", None) else '👁')
            ToolTip(self.show_pwd_btn, _("show_token"))

    def logout(self):
        self.config.delete_pat()
        self.api_token = ""
        self.user_name = ""
        self.user_email = ""
        self.main_frame.pack_forget()
        self.filtered_projects = None
        self.save_pat_var.set(False)
        self.pat_days_entry.configure(state="disabled")
        self.token_entry.delete(0, tk.END)
        self.subtitle.configure(text=_("app_subtitle"), text_color="gray")
        self.login_frame.pack(fill="both", expand=True)
        self.reset_to_login_size()

    def toggle_pat_days(self):
        if self.save_pat_var.get():
            self.pat_days_entry.configure(state="normal")
        else:
            self.pat_days_entry.configure(state="disabled")

    # =========================================================================
    # MAIN FRAME
    # =========================================================================
    def setup_main_frame(self):
        self.main_frame = ctk.CTkFrame(self)

        # === Header bar ===
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(12, 4))

        if getattr(self, "logo_img", None):
            ctk.CTkLabel(
                header_frame, text=f"  {_('app_title')}", image=self.logo_img, compound="left",
                font=ctk.CTkFont(family="Open Sans", size=18, weight="bold")
            ).pack(side="left")
        else:
            ctk.CTkLabel(
                header_frame, text=_("app_title"),
                font=ctk.CTkFont(family="Open Sans", size=18, weight="bold")
            ).pack(side="left")

        # Top Button Frame right side
        top_btn_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        top_btn_frame.pack(side="right", padx=(5, 0))

        # Buttons
        logout_btn = ctk.CTkButton(top_btn_frame, text=ICON_LOGOUT if getattr(self, "icon_font", None) else "Log Out", font=getattr(self, "icon_font", None), width=34, height=34, fg_color="#c0392b", hover_color="#922b21", command=self.logout)
        logout_btn.pack(side="right", padx=(6, 0))
        ToolTip(logout_btn, _("tooltip_logout"))
        
        set_btn = ctk.CTkButton(top_btn_frame, text=ICON_SETTINGS if getattr(self, "icon_font", None) else "⚙", font=getattr(self, "icon_font", None), width=34, height=34, command=self.open_settings_modal)
        set_btn.pack(side="right", padx=(6, 0))
        ToolTip(set_btn, _("tooltip_settings"))
        
        info_btn = ctk.CTkButton(top_btn_frame, text=ICON_INFO if getattr(self, "icon_font", None) else "ℹ", font=getattr(self, "icon_font", None), width=34, height=34, command=self.open_about_modal)
        info_btn.pack(side="right", padx=(6, 0))
        ToolTip(info_btn, _("tooltip_about"))

        self.user_info_btn = ctk.CTkButton(
            top_btn_frame,
            text=ICON_USER if getattr(self, "icon_font", None) else "👤",
            font=getattr(self, "icon_font", None),
            width=34,
            height=34,
            command=self.open_profile_modal
        )
        self.user_info_btn.pack(side="right", padx=(6, 0))
        ToolTip(self.user_info_btn, _("tooltip_profile"))

        ctk.CTkFrame(self.main_frame, height=2, fg_color="gray30").pack(fill="x", padx=20, pady=(4, 8))

        # === STEP 1: Destinasi Folder ===
        # Diberi border untuk membedakan logical step
        step1_frame = ctk.CTkFrame(self.main_frame, border_width=1, border_color="gray50")
        step1_frame.pack(fill="x", pady=(0, 10), padx=20, ipady=5)

        step1_top = ctk.CTkFrame(step1_frame, fg_color="transparent")
        step1_top.pack(fill="x", padx=10, pady=(5,0))
        
        ctk.CTkLabel(step1_top, text=_("step1_title"), font=ctk.CTkFont(family="Open Sans", weight="bold", size=14)).pack(side="left")
        ctk.CTkLabel(step1_top, text=_("step1_hint"), text_color="gray", font=ctk.CTkFont(family="Open Sans Light", size=11)).pack(side="right")

        dest_frame = ctk.CTkFrame(step1_frame, fg_color="transparent")
        dest_frame.pack(fill="x", pady=(5, 5), padx=10)

        ctk.CTkLabel(dest_frame, text=_("path_label"), font=ctk.CTkFont(family="Open Sans", weight="bold")).pack(side="left", padx=(0, 10))
        self.dest_entry = ctk.CTkEntry(dest_frame, height=32, placeholder_text=_("dest_placeholder"))
        
        # Load prev dest
        saved_dest = self.config.get_dest_folder()
        if saved_dest:
            self.dest_entry.insert(0, saved_dest)
            
        self.dest_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(dest_frame, text=_("browse_folder"), width=100, height=32, font=ctk.CTkFont(family="Open Sans"), command=self.browse_folder).pack(side="left")

        # === STEP 2: Tools: Search + Select ===
        step2_frame = ctk.CTkFrame(self.main_frame, border_width=1, border_color="gray50")
        step2_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        ctk.CTkLabel(step2_frame, text=_("step2_title"), font=ctk.CTkFont(family="Open Sans", weight="bold", size=14)).pack(anchor="w", padx=10, pady=(10, 5))

        tools_frame = ctk.CTkFrame(step2_frame, fg_color="transparent")
        tools_frame.pack(fill="x", padx=10, pady=(0, 6))

        # Search group
        self.search_entry = ctk.CTkEntry(tools_frame, height=32, placeholder_text=_("search_placeholder"))
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.search_entry.bind("<Return>", self.trigger_search)

        self.search_btn = ctk.CTkButton(tools_frame, text=_("search_btn"), font=ctk.CTkFont(family="Open Sans"), height=32, image=self.icon_search_img, compound="left", command=self.trigger_search)
        self.search_btn.pack(side="left", padx=(0, 6))

        ToolTip(self.search_entry, _("search_placeholder"))

        self.reset_search_btn = ctk.CTkButton(
            tools_frame, text=_("reset_btn"), font=ctk.CTkFont(family="Open Sans"), height=32,
            image=self.icon_reset_img, compound="left",
            fg_color="gray40", hover_color="gray30",
            command=self.reset_search
        )
        self.reset_search_btn.pack(side="left")

        # Add trace to disable/enable search buttons
        self.search_var = ctk.StringVar()
        self.search_entry.configure(textvariable=self.search_var)
        self.search_var.trace_add("write", self.validate_search_input)

        # Loading animation
        self.loading_bar = ctk.CTkProgressBar(step2_frame, mode="indeterminate", height=4)
        self.loading_bar.pack(fill="x", padx=10, pady=(0, 0))
        self.loading_bar.set(0) # Hide initially by not starting

        # Action Frame (Select & Workspace tools)
        action_frame = ctk.CTkFrame(step2_frame, fg_color="transparent")
        action_frame.pack(fill="x", padx=10, pady=(6, 6))

        self.btn_select_all = ctk.CTkButton(action_frame, text=_("select_all"), font=ctk.CTkFont(family="Open Sans"), height=32, image=self.icon_check_all_img, compound="left", command=self.select_all)
        self.btn_select_all.pack(side="left", padx=(0, 6))

        self.btn_deselect_all = ctk.CTkButton(action_frame, text=_("deselect_all"), font=ctk.CTkFont(family="Open Sans"), height=32, image=self.icon_uncheck_all_img, compound="left", fg_color="gray40", hover_color="gray30", command=self.deselect_all)
        self.btn_deselect_all.pack(side="left")

        self.btn_import = ctk.CTkButton(action_frame, text=_("import_ws"), font=ctk.CTkFont(family="Open Sans"), height=32, image=self.icon_import_img, compound="left", fg_color="#2980b9", hover_color="#1f618d", command=self.import_workspace)
        self.btn_import.pack(side="right")

        self.btn_export = ctk.CTkButton(action_frame, text=_("export_ws"), font=ctk.CTkFont(family="Open Sans"), height=32, image=self.icon_export_img, compound="left", fg_color="#2980b9", hover_color="#1f618d", command=self.export_workspace)
        self.btn_export.pack(side="right", padx=(0, 6))

        # --- Scrollable List Repo ---
        self.scroll_frame = ctk.CTkScrollableFrame(
            step2_frame, label_text=_("repo_list"),
            label_font=ctk.CTkFont(family="Open Sans", weight="bold")
        )
        self.scroll_frame.pack(padx=10, pady=(0, 6), fill="both", expand=True)

        # --- Pagination ---
        self.pagination_frame = ctk.CTkFrame(step2_frame, fg_color="transparent")
        self.pagination_frame.pack(fill="x", padx=10, pady=(0, 10))

        # LEFT SIDE
        left_pag = ctk.CTkFrame(self.pagination_frame, fg_color="transparent")
        left_pag.pack(side="left")
        
        ctk.CTkLabel(left_pag, text=_("repo_per_page"), font=ctk.CTkFont(family="Open Sans")).pack(side="left", padx=(0, 5))
        self.per_page_var = tk.StringVar(value=str(self.per_page))
        self.per_page_combo = ctk.CTkOptionMenu(
            left_pag, variable=self.per_page_var, values=["20", "50", "100"], width=70,
            command=self.on_per_page_change
        )
        self.per_page_combo.pack(side="left", padx=(0, 15))
        
        self.page_range_label = ctk.CTkLabel(left_pag, text="", font=ctk.CTkFont(family="Open Sans", weight="bold"))
        self.page_range_label.pack(side="left")
        self.page_label = self.page_range_label

        # RIGHT SIDE
        right_pag = ctk.CTkFrame(self.pagination_frame, fg_color="transparent")
        right_pag.pack(side="right")
        
        self.first_btn = ctk.CTkButton(right_pag, text="<<", width=34, height=30, font=ctk.CTkFont(family="Open Sans", size=12), command=self.first_page, state="disabled")
        self.first_btn.pack(side="left", padx=(0, 4))

        self.prev_btn = ctk.CTkButton(right_pag, text="<", width=34, height=30, font=ctk.CTkFont(family="Open Sans", size=12), command=self.prev_page, state="disabled")
        self.prev_btn.pack(side="left", padx=(0, 10))
        
        self.goto_page_entry = ctk.CTkEntry(right_pag, width=40, height=30, justify="center")
        self.goto_page_entry.pack(side="left", padx=(0, 5))
        self.goto_page_entry.bind("<Return>", self.goto_page)
        
        self.total_page_label = ctk.CTkLabel(right_pag, text="/ 1")
        self.total_page_label.pack(side="left", padx=(0, 10))

        self.next_btn = ctk.CTkButton(right_pag, text=">", width=34, height=30, font=ctk.CTkFont(family="Open Sans", size=12), command=self.next_page, state="disabled")
        self.next_btn.pack(side="left", padx=(0, 4))
        
        self.last_btn = ctk.CTkButton(right_pag, text=">>", width=34, height=30, font=ctk.CTkFont(family="Open Sans", size=12), command=self.last_page, state="disabled")
        self.last_btn.pack(side="left")

        # === STEP 3: Tombol Clone ===
        step3_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        step3_frame.pack(fill="x", padx=20, pady=(0, 8))
        
        self.clone_btn = ctk.CTkButton(
            step3_frame,
            text=_("step3_btn"),
            fg_color="#1a7f37", hover_color="#15692f",
            font=ctk.CTkFont(family="Open Sans Medium", size=14, weight="bold"),
            height=44,
            command=self.open_branch_selection_modal
        )
        self.clone_btn.pack(fill="x")

        # === Log Modal Button ===
        log_header = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        log_header.pack(fill="x", padx=20, pady=(0, 16))
        ctk.CTkButton(
            log_header, text=_("show_logs"), font=ctk.CTkFont(family="Open Sans"), height=32, image=self.icon_logs_img, compound="left",
            command=self.show_log_modal, fg_color="gray40", hover_color="gray30"
        ).pack(side="left")

        # Create hidden log window
        self.log_window = None
        self.log_content = ""
        self.validate_search_input()
        self.update_selection_action_buttons()

    def browse_folder(self):
        folder_selected = filedialog.askdirectory(title="Pilih Folder Destinasi")
        if folder_selected:
            self.dest_entry.delete(0, tk.END)
            self.dest_entry.insert(0, folder_selected)
            self.config.set_dest_folder(folder_selected)
    def start_auth_thread(self):
        self.gitlab_url = self.url_entry.get().strip().rstrip('/')
        self.api_token = self.token_entry.get().strip()

        if not self.gitlab_url or not self.api_token:
            show_warning(self, _("warning"), _("empty_creds"))
            return

        # Update url ke config supaya tersimpan URL terakhir yang dipakai
        self.config.set_gitlab_url(self.gitlab_url)

        # Proses penyimpanan Token
        if self.save_pat_var.get():
            try:
                days = int(self.pat_days_entry.get().strip())
                if days == 0:
                    expiry_date = datetime.now() + timedelta(days=36500) # 100 years ~ practically never expires
                else:
                    expiry_date = datetime.now() + timedelta(days=days)
                self.config.save_pat(self.api_token, expiry_date.isoformat())
            except ValueError:
                show_warning(self, _("warning"), _("invalid_days"))
                self.connect_btn.configure(state="normal", text=_("connect_btn"))
                return
        else:
            self.config.delete_pat()

        self.connect_btn.configure(state="disabled", text=_("connecting"))
        thread = threading.Thread(target=self._auth_and_fetch)
        thread.daemon = True
        thread.start()

    def _auth_and_fetch(self):
        """Fetch user info first, then fetch repos."""
        headers = {"PRIVATE-TOKEN": self.api_token}
        try:
            user_resp = requests.get(f"{self.gitlab_url}/api/v4/user", headers=headers)
            user_resp.raise_for_status()
            user_data = user_resp.json()
            self.user_name = user_data.get("name", "")
            self.user_email = user_data.get("email", "")
        except Exception:
            self.user_name = ""
            self.user_email = ""

        self.fetch_repositories()

    
    def validate_search_input(self, *args):
        try:
            val = self.search_var.get().strip()
            self._set_btn_state(self.search_btn, "normal" if val and not self.is_fetching else "disabled")
            self._set_btn_state(self.reset_search_btn, "normal" if not self.is_fetching else "disabled")
        except Exception:
            pass
            
    def first_page(self):
        if self.current_page > 1:
            self.current_page = 1
            self.load_page_data()

    def last_page(self):
        if hasattr(self, 'total_pages') and self.current_page < self.total_pages:
            self.current_page = self.total_pages
            self.load_page_data()

    def update_repo_list_ui(self):
        """Render cached filtered projects if present, otherwise fetch from API."""
        if isinstance(self.filtered_projects, list):
            self.total_rows = len(self.filtered_projects)
            self.total_pages = 1 if self.per_page <= 0 else max(1, (self.total_rows + self.per_page - 1) // self.per_page)
            self.current_page = min(max(1, self.current_page), self.total_pages)

            start = (self.current_page - 1) * self.per_page
            end = start + self.per_page
            projects_to_show = self.filtered_projects[start:end]
            self.show_main_frame(projects_to_show, self.current_page < self.total_pages)
            return

        self.load_page_data()

    def trigger_search(self, event=None):
        if self.is_fetching or not self.search_entry.get().strip():
            return
        self.current_page = 1
        self.load_page_data()

    def reset_search(self):
        if self.is_fetching: return

        # Reset now acts as refresh and global unselect.
        self.selected_repos.clear()
        for item in self.repo_items:
            widget = item.get("widget")
            if widget is not None and hasattr(widget, "deselect"):
                widget.deselect()
            var = item.get("var")
            if var is not None and hasattr(var, "set"):
                var.set("")
        self.update_selection_action_buttons()

        self.search_entry.delete(0, tk.END)
        self.current_page = 1
        self.filtered_projects = None
        self.load_page_data()
        
    def on_per_page_change(self, value):
        self.per_page = int(value)
        self.current_page = 1
        self.load_page_data()
        
    def goto_page(self, event=None):
        try:
            page = int(self.goto_page_entry.get().strip())
            if 1 <= page <= self.total_pages:
                self.current_page = page
                self.load_page_data()
            else:
                show_warning(self, _("warning"), f"Halaman harus antara 1 dan {self.total_pages}")
        except ValueError:
            pass

    def prev_page(self):
        if self.current_page > 1 and not self.is_fetching:
            self.current_page -= 1
            self.load_page_data()

    def next_page(self):
        if self.current_page < self.total_pages and not self.is_fetching:
            self.current_page += 1
            self.load_page_data()

    def set_ui_loading_state(self, is_loading):
        self.is_fetching = is_loading
        state = "disabled" if is_loading else "normal"
        self._set_btn_state(self.search_btn, state)
        self._set_btn_state(self.reset_search_btn, state)
        self.search_entry.configure(state=state)
        if is_loading:
            self.per_page_combo.configure(state="disabled")
            self.goto_page_entry.configure(state="disabled")
            self._set_btn_state(self.first_btn, "disabled")
            self._set_btn_state(self.prev_btn, "disabled")
            self._set_btn_state(self.next_btn, "disabled")
            self._set_btn_state(self.last_btn, "disabled")
        else:
            self.validate_search_input()
        
        if is_loading:
            self.loading_bar.start()
        else:
            self.loading_bar.stop()

    def update_pagination_controls(self, has_next=False, is_searching=False):
        self.total_page_label.configure(text=f"/ {self.total_pages}")
        self.goto_page_entry.configure(state="normal")
        self.goto_page_entry.delete(0, tk.END)
        self.goto_page_entry.insert(0, str(self.current_page))

        if is_searching or self.total_pages <= 1:
            self._set_btn_state(self.first_btn, "disabled")
            self._set_btn_state(self.prev_btn, "disabled")
            self._set_btn_state(self.next_btn, "disabled")
            self._set_btn_state(self.last_btn, "disabled")
            if is_searching:
                self.goto_page_entry.configure(state="disabled")
            return

        self._set_btn_state(self.first_btn, "normal" if self.current_page > 1 else "disabled")
        self._set_btn_state(self.prev_btn, "normal" if self.current_page > 1 else "disabled")
        can_go_next = has_next and self.current_page < self.total_pages
        self._set_btn_state(self.next_btn, "normal" if can_go_next else "disabled")
        self._set_btn_state(self.last_btn, "normal" if self.current_page < self.total_pages else "disabled")

    def load_page_data(self):
        self.set_ui_loading_state(True)
        self.page_label.configure(text=_("loading"))
        thread = threading.Thread(target=self.fetch_repositories)
        thread.daemon = True
        thread.start()

    def fetch_repositories(self):
        try:
            import fnmatch
            headers = {"PRIVATE-TOKEN": self.api_token}
            search_query = self.search_entry.get().strip()
            is_wildcard = "*" in search_query
            
            all_projects = []
            
            # If there's a search term, fetch everything to allow filtering client-side or global searching
            if search_query:
                # We'll fetch pages until no more (or up to a reasonable cap like 100 pages * 100 per page to prevent freezing)
                # If there's no wildcard, Gitlab API can search directly, but since we want ALL results disregarding pagination
                # we'll loop through pages.
                
                # Use gitlab's search if no wildcard, else fetch all and filter client side
                api_search = "" if is_wildcard else f"&search={quote(search_query)}"
                page = 1
                while True:
                    api_url = (
                        f"{self.gitlab_url}/api/v4/projects"
                        f"?membership=true&simple=true"
                        f"&per_page=100&page={page}{api_search}"
                    )
                    response = requests.get(api_url, headers=headers)
                    response.raise_for_status()
                    data = response.json()
                    
                    if not data:
                        break
                        
                    if is_wildcard:
                        # Filter by wildcard pattern
                        pattern = search_query.lower()
                        for p in data:
                            if fnmatch.fnmatch(p['path_with_namespace'].lower(), pattern):
                                all_projects.append(p)
                    else:
                        all_projects.extend(data)
                        
                    # Stop if no next page
                    if not response.headers.get('X-Next-Page'):
                        break
                    
                    page += 1
                    
                # For search results, we disable pagination and show all
                self.total_rows = len(all_projects)
                self.total_pages = 1
                self.current_page = 1
                projects_to_show = all_projects
                self.cached_projects = all_projects
                
            else:
                # Normal paginated view
                api_url = (
                    f"{self.gitlab_url}/api/v4/projects"
                    f"?membership=true&simple=true"
                    f"&per_page={self.per_page}&page={self.current_page}"
                )
                response = requests.get(api_url, headers=headers)
                response.raise_for_status()
                projects_to_show = response.json()
                
                # Read pagination headers
                total = response.headers.get('X-Total', '0')
                total_pages = response.headers.get('X-Total-Pages', '1')
                self.total_rows = int(total) if total.isdigit() else len(projects_to_show)
                self.total_pages = int(total_pages) if total_pages.isdigit() else 1
                self.cached_projects = projects_to_show
                
            if not projects_to_show and self.current_page == 1:
                msg = _("not_found")
                self.after(0, lambda root=self: show_info(root, _("ok"), msg))
                self.after(0, lambda: self.show_main_frame([], False))
                self.after(0, lambda: self.connect_btn.configure(state="normal", text=_("connect_btn")))
                self.after(0, lambda: self.set_ui_loading_state(False))
                return

            self.after(0, lambda: self.show_main_frame(projects_to_show, self.current_page < self.total_pages))

        except requests.exceptions.RequestException as e:
            self.after(0, lambda root=self: show_error(root, _("fetching_error"), f"{_('error')}: {e}"))
            self.after(0, lambda: self.connect_btn.configure(state="normal", text=_("connect_btn")))
            self.after(0, lambda: self.page_label.configure(text=f"Halaman {self.current_page} (Error)"))
            self.after(0, lambda: self.set_ui_loading_state(False))

    def show_main_frame(self, projects, has_next):
        self.login_frame.pack_forget()
        self.geometry(f"{self.expanded_w}x{self.expanded_h}")
        self.minsize(800, 720)
        center_window(self, self.expanded_w, self.expanded_h)
        self.main_frame.pack(fill="both", expand=True)

        for item in self.repo_items:
            item["widget"].destroy()
        self.repo_items.clear()

        for project in projects:
            repo_name = project['path_with_namespace']
            http_url = project['http_url_to_repo']
            project_id = project['id']

            is_selected = http_url in self.selected_repos
            var = tk.StringVar(value=http_url if is_selected else "")

            def on_toggle(url=http_url, name=repo_name, p_id=project_id, v=var):
                if v.get():
                    self.selected_repos[url] = {"name": name, "id": p_id}
                else:
                    self.selected_repos.pop(url, None)
                self.update_selection_action_buttons()

            cb = ctk.CTkCheckBox(
                self.scroll_frame, text=repo_name,
                variable=var, onvalue=http_url, offvalue="",
                command=on_toggle
            )
            cb.pack(anchor="w", pady=4, padx=10)

            self.repo_items.append({
                "name": repo_name, "widget": cb,
                "var": var, "url": http_url, "id": project_id
            })

        self.update_repo_range_label(len(projects))
        self.update_pagination_controls(has_next=has_next)
        self.connect_btn.configure(state="normal", text=_("connect_btn"))
        self.update_selection_action_buttons()
        
        self.set_ui_loading_state(False)
        
        # Determine if pagination should be hidden (when searching)
        is_searching = bool(self.search_entry.get().strip())
        if is_searching:
            self.per_page_combo.configure(state="disabled")
            self.update_pagination_controls(has_next=False, is_searching=True)
            self.update_repo_range_label(len(projects))
        else:
            self.per_page_combo.configure(state="normal")

    def apply_window_icon(self, window):
        try:
            if hasattr(self, 'ico_path') and self.ico_path:
                window.iconbitmap(self.ico_path)
        except Exception:
            pass
        try:
            if hasattr(self, 'img_icon') and self.img_icon:
                window.iconphoto(True, self.img_icon)
        except Exception:
            pass

    
    def open_profile_modal(self):
        modal = ctk.CTkToplevel(self)
        modal.title(_("profile_title"))
        self.configure_modal_window(modal, 450, 350)
        
        # User details layout
        top_frame = ctk.CTkFrame(modal, fg_color="transparent")
        top_frame.pack(pady=20, fill="x", padx=20)
        
        avatar_lbl = ctk.CTkLabel(top_frame, text="👤", font=ctk.CTkFont(family="Open Sans", size=60))
        avatar_lbl.pack(side="top", pady=(0, 10))
        
        name_lbl = ctk.CTkLabel(top_frame, text=self.user_name if hasattr(self, 'user_name') and self.user_name else _("profile_default_user"), font=ctk.CTkFont(family="Open Sans", size=18, weight="bold"))
        name_lbl.pack(side="top")
        
        email_lbl = ctk.CTkLabel(top_frame, text=self.user_email if hasattr(self, 'user_email') else "", font=ctk.CTkFont(family="Open Sans", size=12), text_color="gray")
        email_lbl.pack(side="top", pady=(0, 15))
        
        # PAT Duration Info
        info_frame = ctk.CTkFrame(modal)
        info_frame.pack(fill="x", padx=20, pady=10)
        
        saved_pat = self.config.get_saved_pat()
        expiry_str = "?"
        days_rem = 0
        original_expiry = None
        if saved_pat and saved_pat.get('expiry_date'):
            from datetime import datetime
            import dateutil.parser
            try:
                exp_dt = dateutil.parser.isoparse(saved_pat['expiry_date'])
                original_expiry = exp_dt
                days_rem = (exp_dt - datetime.now()).days
                if days_rem > 3650:
                    expiry_str = _("permanent")
                else:
                    expiry_str = f"{exp_dt.strftime('%d %b %Y %H:%M:%S')} ({days_rem} hari)"
            except:
                expiry_str = _("invalid_date")
                
        ctk.CTkLabel(info_frame, text=_("token_duration"), font=ctk.CTkFont(family="Open Sans", weight="bold")).pack(side="top", anchor="w", padx=10, pady=(10, 0))
        dur_lbl = ctk.CTkLabel(info_frame, text=expiry_str, font=ctk.CTkFont(family="Open Sans"))
        dur_lbl.pack(side="top", anchor="w", padx=10, pady=(0, 10))
        
        # Edit Token Duration
        edit_frame = ctk.CTkFrame(modal, fg_color="transparent")
        edit_frame.pack(pady=10)
        
        ctk.CTkLabel(edit_frame, text=_("change_duration_days"), font=ctk.CTkFont(family="Open Sans")).pack(side="left", padx=(0, 10))
        dur_entry = ctk.CTkEntry(edit_frame, width=60)
        dur_entry.insert(0, str(days_rem) if days_rem < 3650 else "0")
        dur_entry.pack(side="left")
        dur_entry.bind("<FocusIn>", lambda e: dur_entry.select_range(0, tk.END))
        
        def save_dur():
            nonlocal saved_pat, expiry_str, days_rem
            val = dur_entry.get().strip()
            if not val.isdigit():
                show_warning(modal, _("error"), _("duration_must_number"))
                return
            
            days = int(val)
            if days < 0:
                show_warning(modal, _("error"), _("duration_not_negative"))
                return

            from datetime import datetime, timedelta
            new_date = datetime.now() + (timedelta(days=36500) if days == 0 else timedelta(days=days))
            new_str = _("permanent") if days == 0 else f"{new_date.strftime('%d %b %Y %H:%M:%S')} ({days} hari)"
            orig_str = expiry_str
            
            # Show confirmation 
            msg = _("confirm_update_duration", old=orig_str, new=new_str)
            if show_confirmation(modal, _("warning"), msg):
                token_to_save = saved_pat.get("pat") if saved_pat else ""
                if not token_to_save:
                    token_to_save = getattr(self, "api_token", "") or self.token_entry.get().strip()

                if not token_to_save:
                    show_error(modal, _("error"), _("token_missing_relogin"))
                    return

                self.config.save_pat(token_to_save, new_date.isoformat())
                saved_pat = self.config.get_saved_pat()
                expiry_str = new_str
                days_rem = days
                dur_lbl.configure(text=new_str)
                show_custom_message(modal, "Info", _("duration_updated"), icon_type="success")

        ctk.CTkButton(edit_frame, text=_("update"), width=80, height=32, command=save_dur, font=ctk.CTkFont(family="Open Sans")).pack(side="left", padx=(10, 0))

    def open_settings_modal(self):
        modal = ctk.CTkToplevel(self)
        modal.title(_("settings_title"))
        self.configure_modal_window(modal, 400, 320)

        ctk.CTkLabel(modal, text=_("settings_title"), font=ctk.CTkFont(family="Open Sans", size=18, weight="bold")).pack(pady=(20, 10))
        
        form = ctk.CTkFrame(modal, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=40)

        # Language
        ctk.CTkLabel(form, text=_("language_lbl"), anchor="w").pack(fill="x")
        lang_var = tk.StringVar(value=self.config.get_language())
        lang_combo = ctk.CTkOptionMenu(form, variable=lang_var, values=["en", "id"])
        lang_combo.pack(fill="x", pady=(0, 10))

        # Theme
        ctk.CTkLabel(form, text=_("theme_lbl"), anchor="w").pack(fill="x")
        theme_var = tk.StringVar(value=self.config.get_theme())
        theme_combo = ctk.CTkOptionMenu(form, variable=theme_var, values=["System", "Light", "Dark"])
        theme_combo.pack(fill="x", pady=(0, 10))

        # Clone Method
        ctk.CTkLabel(form, text=_("clone_method_lbl"), anchor="w").pack(fill="x")
        method_var = tk.StringVar(value=self.config.get_clone_method())
        method_combo = ctk.CTkOptionMenu(form, variable=method_var, values=["HTTPS", "SSH"])
        method_combo.pack(fill="x", pady=(0, 20))

        def save_settings():
            self.config.set_language(lang_var.get())
            self.config.set_theme(theme_var.get())
            self.config.set_clone_method(method_var.get())
            i18n.set_language(lang_var.get())
            ctk.set_appearance_mode(theme_var.get())
            modal.destroy()
            show_info(self, _("ok"), _("settings_saved_restart"))

        ctk.CTkButton(modal, text=_("save_settings"), height=36, font=ctk.CTkFont(family="Open Sans", weight="bold"), command=save_settings).pack(pady=(10, 20))

    def open_about_modal(self):
        modal = ctk.CTkToplevel(self)
        modal.title(_("about_title"))
        self.configure_modal_window(modal, 460, 280)

        hdr = ctk.CTkFrame(modal, fg_color="transparent")
        hdr.pack(pady=(25, 15))
        
        if getattr(self, "logo_img_large", None):
            ctk.CTkLabel(hdr, text="", image=self.logo_img_large).pack(side="left", padx=15)
            
        ctk.CTkLabel(hdr, text=_('app_name'), font=ctk.CTkFont(family="Open Sans", size=22, weight="bold")).pack(side="left")

        ctk.CTkLabel(modal, text=_("about_content", version=self.app_version), font=ctk.CTkFont(family="Open Sans Italic", size=14), justify="center", wraplength=420).pack(pady=10, padx=20)
        
        # Links Frame
        link_frame = ctk.CTkFrame(modal, fg_color="transparent")
        link_frame.pack(pady=5)
        
        import webbrowser
        def open_link(url):
            webbrowser.open_new(url)
            
        l1 = ctk.CTkLabel(link_frame, text=_("source_code"), text_color="#3498db", font=ctk.CTkFont(family="Open Sans", underline=True))
        l1.pack(side="left", padx=10)
        l1.bind("<Button-1>", lambda e: open_link("https://github.com/aryajava/glrc"))
        l1.configure(cursor="hand2")
        
        l2 = ctk.CTkLabel(link_frame, text=_("issues"), text_color="#3498db", font=ctk.CTkFont(family="Open Sans", underline=True))
        l2.pack(side="left", padx=10)
        l2.bind("<Button-1>", lambda e: open_link("https://github.com/aryajava/glrc/issues"))
        l2.configure(cursor="hand2")
        
        l3 = ctk.CTkLabel(link_frame, text=_("check_updates"), text_color="#3498db", font=ctk.CTkFont(family="Open Sans", underline=True))
        l3.pack(side="left", padx=10)
        l3.bind("<Button-1>", lambda e: open_link("https://github.com/aryajava/glrc/releases"))
        l3.configure(cursor="hand2")

        ctk.CTkButton(modal, text=_("ok"), width=120, height=36, font=ctk.CTkFont(family="Open Sans", weight="bold"), command=modal.destroy).pack(pady=(20, 20))

    def show_log_modal(self):
        if self.log_window is None or not self.log_window.winfo_exists():
            self.log_window = ctk.CTkToplevel(self)
            self.log_window.title(_("log_title"))
            def close_log_modal():
                if self.log_window and self.log_window.winfo_exists():
                    self.log_window.destroy()
                self.log_window = None

            self.configure_modal_window(self.log_window, 700, 500, on_escape=close_log_modal)
            
            self.log_window.textbox = ctk.CTkTextbox(
                self.log_window, font=("Consolas", 12), wrap="word", fg_color="#1e1e1e", text_color="#d4d4d4"
            )
            self.log_window.textbox.pack(fill="both", expand=True, padx=10, pady=10)
            self.log_window.textbox.insert("end", self.log_content)
            self.log_window.textbox.configure(state="disabled")
            self.log_window.textbox.see("end")
        else:
            self.activate_window(self.log_window)
            self.log_window.grab_set()

    def export_workspace(self):
        if not self.selected_repos:
            self.update_selection_action_buttons()
            show_warning(self, _("warning"), _("at_least_one"))
            return
            
        filepath = filedialog.asksaveasfilename(
            title=_("export_ws"), defaultextension=".json", filetypes=[("JSON Files", "*.json")]
        )
        if filepath:
            try:
                # Only serialize plain data; skip Tkinter variable objects
                clean_data = {}
                for url, info in self.selected_repos.items():
                    clean_data[url] = {
                        "name": info.get("name", ""),
                        "id": info.get("id", 0)
                    }
                with open(filepath, 'w') as f:
                    json.dump(clean_data, f, indent=4)
                show_info(self, _("ok"), _("ws_exported", file=filepath))
            except Exception as e:
                show_error(self, _("error"), f"Failed: {e}")

    def import_workspace(self):
        filepath = filedialog.askopenfilename(
            title=_("import_ws"), filetypes=[("JSON Files", "*.json")]
        )
        if filepath:
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)

                if not isinstance(data, dict):
                    show_error(self, _("error"), _("ws_import_err"))
                    return

                # Merge into selected_repos
                count = 0
                for url, info in data.items():
                    if url not in self.selected_repos:
                        self.selected_repos[url] = {
                            "name": info.get("name", ""),
                            "id": info.get("id", 0)
                        }
                        count += 1

                # Clear search input
                self.search_entry.delete(0, tk.END)
                self.validate_search_input()

                # Build filtered list: match from cached_projects or create synthetic entries
                cached_by_url = {p.get("http_url_to_repo"): p for p in self.cached_projects}
                projects = []
                for url, info in data.items():
                    if url in cached_by_url:
                        projects.append(cached_by_url[url])
                    else:
                        projects.append({
                            "path_with_namespace": info.get("name", url.rstrip("/").split("/")[-1]),
                            "http_url_to_repo": url,
                            "id": info.get("id", 0),
                        })

                # Use filtered_projects with normal pagination (don't override per_page)
                self.filtered_projects = projects
                self.current_page = 1

                self.update_repo_list_ui()
                self.update_selection_action_buttons()
                show_info(self, _("ok"), _("ws_imported", count=count))
            except json.JSONDecodeError:
                show_error(self, _("error"), _("ws_import_err"))
            except Exception as e:
                show_error(self, _("error"), _("ws_import_err") + f"\n{e}")

    def select_all(self):
        for item in self.repo_items:
            if item["widget"].winfo_ismapped():
                item["widget"].select()
                self.selected_repos[item["url"]] = {"name": item["name"], "id": item["id"]}
        self.update_selection_action_buttons()

    def deselect_all(self):
        for item in self.repo_items:
            if item["widget"].winfo_ismapped():
                item["widget"].deselect()
                self.selected_repos.pop(item["url"], None)
        self.update_selection_action_buttons()

    def write_log(self, text):
        self.log_content += text + "\n"
        def _update():
            if self.log_window and self.log_window.winfo_exists() and hasattr(self.log_window, 'textbox'):
                self.log_window.textbox.configure(state="normal")
                self.log_window.textbox.insert("end", text + "\n")
                self.log_window.textbox.see("end")
                self.log_window.textbox.configure(state="disabled")
        self.after(0, _update)

    # =========================================================================
    # MODAL BRANCH SELECTION
    # =========================================================================
    def open_branch_selection_modal(self):
        dest_folder = self.dest_entry.get().strip()
        urls_to_clone = list(self.selected_repos.keys())

        if not urls_to_clone:
            show_warning(self, _("warning"), _("at_least_one"))
            return
        if not dest_folder:
            show_warning(self, _("warning"), _("invalid_dest"))
            return
        if not os.path.isdir(dest_folder):
            create_folder = show_confirmation(
                self,
                _("warning"),
                _("dest_not_found_create", path=dest_folder)
            )
            if not create_folder:
                return
            try:
                os.makedirs(dest_folder, exist_ok=True)
                self.config.set_dest_folder(dest_folder)
            except Exception as exc:
                show_error(self, _("error"), _("dest_create_failed", error=exc))
                return

        modal = ctk.CTkToplevel(self)
        modal.title(_("modal_title"))
        self.configure_modal_window(modal, 820, 600)

        # --- Header ---
        hdr_frame = ctk.CTkFrame(modal, fg_color="transparent")
        hdr_frame.pack(fill="x", padx=24, pady=(18, 4))

        ctk.CTkLabel(
            hdr_frame, text=_("modal_header"),
            font=ctk.CTkFont(family="Open Sans", size=17, weight="bold")
        ).pack(side="left")

        ctk.CTkFrame(modal, height=2, fg_color="gray30").pack(fill="x", padx=24, pady=(6, 4))
        
        # -- Info text --
        info_frame = ctk.CTkFrame(modal, fg_color="#ebf5fb", corner_radius=6)
        info_frame.pack(fill="x", padx=24, pady=(5, 5))
        
        inst_text = _("modal_info")
        ctk.CTkLabel(info_frame, text=inst_text, text_color="#154360", justify="left", font=ctk.CTkFont(family="Open Sans", size=12)).pack(padx=10, pady=8, anchor="w")

        # Shared column widths (must match render_branch_rows)
        COL_WIDTHS = (260, 200, 90, 165)

        # Column header — use grid so widths are exact
        col_hdr = ctk.CTkFrame(modal, fg_color="transparent")
        col_hdr.pack(fill="x", padx=24, pady=(0, 2))
        col_hdr.columnconfigure(0, minsize=COL_WIDTHS[0])
        col_hdr.columnconfigure(1, minsize=COL_WIDTHS[1])
        col_hdr.columnconfigure(2, minsize=COL_WIDTHS[2])
        col_hdr.columnconfigure(3, minsize=COL_WIDTHS[3])
        ctk.CTkLabel(col_hdr, text=_("col_repo"),            font=ctk.CTkFont(family="Open Sans", size=12), text_color="gray", anchor="center", justify="center").grid(row=0, column=0, sticky="nsew",      padx=(4, 0))
        ctk.CTkLabel(col_hdr, text=_("col_clone_from"),      font=ctk.CTkFont(family="Open Sans", size=12), text_color="gray", anchor="center", justify="center").grid(row=0, column=1, sticky="nsew")
        lbl_new_branch = ctk.CTkLabel(col_hdr, text=_("col_new_branch"), font=ctk.CTkFont(family="Open Sans", size=12), text_color="gray", anchor="center", justify="center")
        lbl_new_branch.grid(row=0, column=2, sticky="nsew")
        ToolTip(lbl_new_branch, _("create_branch_tooltip"))
        ctk.CTkLabel(col_hdr, text=_("col_new_branch_name"), font=ctk.CTkFont(family="Open Sans", size=12), text_color="gray", anchor="center", justify="center").grid(row=0, column=3, sticky="nsew")

        # --- Scrollable content ---
        scroll_frame = ctk.CTkScrollableFrame(modal)
        scroll_frame.pack(padx=20, pady=(0, 6), fill="both", expand=True)

        loading_lbl = ctk.CTkLabel(scroll_frame, text=_("fetching_branches"))
        loading_lbl.pack(pady=30)


        # --- Footer ---
        ctk.CTkFrame(modal, height=2, fg_color="gray30").pack(fill="x", padx=20, pady=(0, 8))

        footer = ctk.CTkFrame(modal, fg_color="transparent")
        footer.pack(fill="x", padx=20, pady=(0, 16))

        ctk.CTkButton(
            footer, text=_("cancel"), width=100, height=36, font=ctk.CTkFont(family="Open Sans"),
            fg_color="gray40", hover_color="gray30",
            command=modal.destroy
        ).pack(side="left")

        action_btn = ctk.CTkButton(
            footer, text=_("start_clone"), state="disabled",
            fg_color="#1a7f37", hover_color="#15692f",
            font=ctk.CTkFont(family="Open Sans", size=13, weight="bold"),
            width=160, height=36,
            command=lambda: self.execute_clone_from_modal(modal)
        )
        action_btn.pack(side="right")

        thread = threading.Thread(
            target=self.fetch_branches_logic,
            args=(modal, scroll_frame, action_btn, loading_lbl)
        )
        thread.daemon = True
        thread.start()

    def fetch_branches_logic(self, modal, scroll_frame, action_btn, loading_lbl):
        headers = {"PRIVATE-TOKEN": self.api_token}

        for url, data in self.selected_repos.items():
            project_id = data["id"]
            try:
                branches = []
                page = 1
                while True:
                    api_url = f"{self.gitlab_url}/api/v4/projects/{project_id}/repository/branches?per_page=100&page={page}"
                    response = requests.get(api_url, headers=headers)
                    if response.status_code != 200: 
                        break
                        
                    page_data = response.json()
                    if not page_data: 
                        break
                        
                    branches.extend([b["name"] for b in page_data])
                    
                    if not response.headers.get('X-Next-Page'):
                        break
                    
                    page += 1
                    
                data["available_branches"] = branches if branches else ["main"]
            except Exception:
                data["available_branches"] = ["main", "master"]

        self.after(0, lambda: self.render_branch_rows(scroll_frame, action_btn, loading_lbl))

    def render_branch_rows(self, scroll_frame, action_btn, loading_lbl):
        loading_lbl.destroy()
        action_btn.configure(state="normal")

        # MUST match COL_WIDTHS in open_branch_config_modal header
        C0, C1, C2, C3 = 260, 200, 90, 165

        for url, data in self.selected_repos.items():
            row = ctk.CTkFrame(scroll_frame, corner_radius=8)
            row.pack(fill="x", pady=3, padx=4)

            # Mirror the exact same columnconfigure as the header
            row.columnconfigure(0, minsize=C0)
            row.columnconfigure(1, minsize=C1)
            row.columnconfigure(2, minsize=C2)
            row.columnconfigure(3, minsize=C3)

            # --- Col 0: Repo name (truncated label + tooltip) ---
            name = data["name"]
            lbl = ctk.CTkEntry(
                row, font=ctk.CTkFont(family="Open Sans", size=12),
                fg_color="transparent", border_width=0
            )
            lbl.grid(row=0, column=0, sticky="we", padx=(10, 4), pady=8)
            lbl.insert(0, name)
            lbl.configure(state="readonly")
            ToolTip(lbl, name)

            # --- Col 1: Branch dropdown ---
            branches = data.get("available_branches", ["main"])
            default_b = "main" if "main" in branches else ("master" if "master" in branches else branches[0])
            branch_var = ctk.StringVar(value=default_b)
            data["selected_branch_var"] = branch_var

            combo = ctk.CTkComboBox(
                row, values=branches, variable=branch_var, width=185,
                dropdown_fg_color="gray30",
                dropdown_text_color="white",
                dropdown_hover_color="gray40"
            )
            try:
                combo.configure(dropdown_height=min(len(branches) * 28, 250))
            except Exception:
                pass
            combo.grid(row=0, column=1, sticky="w", padx=(0, 4), pady=8)

            def on_branch_search(event, widget=combo, all_vals=branches, b_var=branch_var, rep_name=data["name"]):
                typed = widget.get().strip()
                if not typed:
                    return
                exact = [b for b in all_vals if b.lower() == typed.lower()]
                partial = [b for b in all_vals if typed.lower() in b.lower()]
                if exact:
                    b_var.set(exact[0]); widget.set(exact[0])
                elif partial:
                    b_var.set(partial[0]); widget.set(partial[0])
                else:
                    show_warning(widget.winfo_toplevel(), _("warning"), _("branch_not_found", typed=typed, rep_name=rep_name))
                    dv = "main" if "main" in all_vals else (all_vals[0] if all_vals else "")
                    if widget.winfo_exists():
                        b_var.set(dv); widget.set(dv)

            combo.bind("<Return>", on_branch_search)

            # --- Col 2 & 3: checkbox + new branch entry ---
            new_branch_enabled  = tk.BooleanVar(value=False)
            new_branch_name_var = tk.StringVar(value="")
            data["new_branch_enabled"]  = new_branch_enabled
            data["new_branch_name_var"] = new_branch_name_var

            # Create entry first (needed by toggle function)
            new_branch_entry = ctk.CTkEntry(
                row, textvariable=new_branch_name_var,
                width=C3, height=30,
                placeholder_text="branch-name",
                state="disabled"
            )
            data["new_branch_entry"] = new_branch_entry

            def toggle_branch_entry(entry=new_branch_entry, var=new_branch_enabled):
                entry.configure(state="normal" if var.get() else "disabled")
                if not var.get():
                    entry.delete(0, tk.END)

            chk = ctk.CTkCheckBox(row, text="", width=24,
                                  variable=new_branch_enabled,
                                  command=toggle_branch_entry)
            chk.grid(row=0, column=2, pady=8)

            new_branch_entry.grid(row=0, column=3, sticky="w", padx=(0, 8), pady=8)


    # =========================================================================
    # CLONING
    # =========================================================================
    def execute_clone_from_modal(self, modal):
        modal.destroy()
        dest_folder = self.dest_entry.get().strip()

        self.clone_btn.configure(state="disabled", text=_("cloning_in_progress"))
        # self.log_box is replaced by self.log_content conceptually.
        # Clear log
        self.log_content = ""
        if self.log_window and self.log_window.winfo_exists() and hasattr(self.log_window, 'textbox'):
            self.log_window.textbox.configure(state="normal")
            self.log_window.textbox.delete("1.0", "end")
            self.log_window.textbox.configure(state="disabled")

        urls_to_clone = list(self.selected_repos.keys())
        self.write_log(f"[*] Memulai proses clone untuk {len(urls_to_clone)} repositori...")

        thread = threading.Thread(target=self.run_multiple_clones, args=(urls_to_clone, dest_folder))
        thread.daemon = True
        thread.start()

    def run_multiple_clones(self, urls, dest_folder):
        self.sukses = 0
        self.gagal = 0
        self.cloned_paths = []  # Track successfully cloned/updated repos
        self.lock = threading.Lock()
        
        clone_method = self.config.get_clone_method()

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(self._process_single_repo, url, dest_folder, clone_method) for url in urls]
            concurrent.futures.wait(futures)

        self.write_log(f"\n{'=' * 50}")
        self.write_log(f"PROSES SELESAI!  Berhasil: {self.sukses}  |  Gagal: {self.gagal}")
        self.write_log(f"{'=' * 50}")

        self.after(0, lambda: self.clone_btn.configure(
            state="normal", text=_("step3_btn")
        ))
        cloned = list(self.cloned_paths)
        self.after(0, lambda: self.show_clone_result_dialog(cloned))

    def _process_single_repo(self, url, dest_folder, clone_method):
        repo_data = self.selected_repos[url]
        repo_name = repo_data["name"]
        branch_name = repo_data["selected_branch_var"].get()

        new_branch_enabled = repo_data.get("new_branch_enabled")
        new_branch_name_var = repo_data.get("new_branch_name_var")
        create_new_branch = new_branch_enabled and new_branch_enabled.get()
        new_branch_name = new_branch_name_var.get().strip() if new_branch_name_var else ""

        # Tentukan nama folder repo (ambil segment terakhir dari URL)
        repo_folder_name = url.rstrip("/").split("/")[-1]
        if repo_folder_name.endswith(".git"):
            repo_folder_name = repo_folder_name[:-4]
        repo_local_path = os.path.join(dest_folder, repo_folder_name)

        parsed = urlparse(url)
        if clone_method == "SSH":
            # e.g., git@gitlab.com:username/repo.git
            host = parsed.netloc
            path = parsed.path.lstrip('/')
            auth_url = f"git@{host}:{path}"
        else:
            auth_url = parsed._replace(
                netloc=f"oauth2:{quote(self.api_token)}@{parsed.netloc}"
            ).geturl()

        # Environment tanpa credential helper — mencegah token tersimpan di Windows Credential Store
        git_env = os.environ.copy()
        git_env["GIT_TERMINAL_PROMPT"] = "0"
        git_env["GIT_ASKPASS"] = ""

        # Check if dir exists and is a git repo
        if os.path.isdir(repo_local_path) and os.path.isdir(os.path.join(repo_local_path, ".git")):
            self.write_log(f"\n{_('pulling')} ({repo_name})")

            # Simpan original remote URL, lalu set ke auth_url agar pull bisa autentikasi
            original_remote_url = None
            try:
                result = subprocess.run(
                    ["git", "remote", "get-url", "origin"],
                    cwd=repo_local_path, capture_output=True, text=True, env=git_env
                )
                if result.returncode == 0:
                    original_remote_url = result.stdout.strip()

                subprocess.run(
                    ["git", "remote", "set-url", "origin", auth_url],
                    cwd=repo_local_path, capture_output=True, text=True, env=git_env
                )
            except Exception as e:
                self.write_log(f"    [!] Gagal set remote URL: {e}")

            success = False
            for i in range(1, 4):
                try:
                    process = subprocess.Popen(
                        ["git", "-c", "credential.helper=", "pull", "origin", branch_name],
                        cwd=repo_local_path,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True, bufsize=1, universal_newlines=True,
                        env=git_env
                    )
                    for line in process.stdout:
                        clean_line = (
                            line.strip()
                            .replace(self.api_token, "********")
                            .replace("oauth2:********@", "")
                        )
                        self.write_log(f"    {clean_line}")
                    process.wait()

                    if process.returncode == 0:
                        success = True
                        break
                    else:
                        self.write_log(f"[-] Pull failed. {_('retrying', i=i)}")
                        import time; time.sleep(2)
                except Exception as e:
                    self.write_log(f"[-] Kesalahan pada '{repo_name}': {e}")
                    import time; time.sleep(2)

            # Kembalikan remote URL asli agar token tidak tersimpan di .git/config
            if original_remote_url:
                try:
                    subprocess.run(
                        ["git", "remote", "set-url", "origin", original_remote_url],
                        cwd=repo_local_path, capture_output=True, text=True, env=git_env
                    )
                except Exception:
                    pass
            
            if success:
                self.write_log(f"[+] '{repo_name}' berhasil update (branch: {branch_name}).")
                with self.lock:
                    self.sukses += 1
                    self.cloned_paths.append((repo_name, repo_local_path))

                # --- Buat branch baru jika diminta (saat pull) ---
                if create_new_branch and new_branch_name:
                    self.write_log(f"    [>] Membuat branch baru '{new_branch_name}'...")
                    try:
                        cb_proc = subprocess.run(
                            ["git", "checkout", "-b", new_branch_name],
                            cwd=repo_local_path,
                            capture_output=True, text=True,
                            env=git_env
                        )
                        if cb_proc.returncode == 0:
                            self.write_log(f"    [+] Branch '{new_branch_name}' berhasil dibuat.")
                        else:
                            self.write_log(f"    [-] Gagal buat branch: {cb_proc.stderr.strip()}")
                    except Exception as exc:
                        self.write_log(f"    [-] Error saat buat branch: {exc}")
                elif create_new_branch and not new_branch_name:
                    self.write_log("    [!] Checkbox 'Buat branch baru' dicentang tapi nama kosong, dilewati.")
            else:
                self.write_log(f"[-] '{repo_name}' gagal update.")
                with self.lock:
                    self.gagal += 1
        else:
            self.write_log(f"\n{_('cloning_repo', repo_name=repo_name, branch_name=branch_name)}")
            clone_command = ["git", "-c", "credential.helper=", "clone", "-b", branch_name, auth_url]
            success = False
            for i in range(1, 4):
                try:
                    process = subprocess.Popen(
                        clone_command,
                        cwd=dest_folder,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True, bufsize=1, universal_newlines=True,
                        env=git_env
                    )

                    for line in process.stdout:
                        clean_line = (
                            line.strip()
                            .replace(self.api_token, "********")
                            .replace("oauth2:********@", "")
                        )
                        self.write_log(f"    {clean_line}")

                    process.wait()

                    if process.returncode == 0:
                        success = True
                        break
                    else:
                        self.write_log(f"[-] Clone failed. {_('retrying', i=i)}")
                        import time; time.sleep(2)
                except Exception as e:
                    self.write_log(f"[-] Kesalahan pada '{repo_name}': {e}")
                    import time; time.sleep(2)

            if success:
                self.write_log(f"[+] '{repo_name}' berhasil di-clone (branch: {branch_name}).")
                with self.lock:
                    self.sukses += 1
                    self.cloned_paths.append((repo_name, repo_local_path))

                # --- Set git config local ---
                self._set_git_config_local(repo_local_path, repo_name)

                # --- Buat branch baru jika diminta ---
                if create_new_branch and new_branch_name:
                    self.write_log(f"    [>] Membuat branch baru '{new_branch_name}'...")
                    try:
                        cb_proc = subprocess.run(
                            ["git", "checkout", "-b", new_branch_name],
                            cwd=repo_local_path,
                            capture_output=True, text=True,
                            env=git_env
                        )
                        if cb_proc.returncode == 0:
                            self.write_log(f"    [+] Branch '{new_branch_name}' berhasil dibuat.")
                        else:
                            self.write_log(f"    [-] Gagal buat branch: {cb_proc.stderr.strip()}")
                    except Exception as exc:
                        self.write_log(f"    [-] Error saat buat branch: {exc}")
                elif create_new_branch and not new_branch_name:
                    self.write_log("    [!] Checkbox 'Buat branch baru' dicentang tapi nama kosong, dilewati.")

            else:
                self.write_log(f"[-] '{repo_name}' gagal di-clone")
                with self.lock:
                    self.gagal += 1

    def _set_git_config_local(self, repo_path: str, repo_name: str):
        """Set git config user.name dan user.email secara local di repo yang baru di-clone."""
        if not os.path.isdir(repo_path):
            self.write_log(f"    [!] Folder repo tidak ditemukan, skip git config: {repo_path}")
            return

        configs = []
        if self.user_name:
            configs.append(("user.name", self.user_name))
        if self.user_email:
            configs.append(("user.email", self.user_email))
        # Disable credential helper secara local agar tidak mengganggu token VS Code/Visual Studio
        configs.append(("credential.helper", ""))

        if not configs:
            self.write_log("    [!] Data user GitLab tidak tersedia, git config local dilewati.")
            return

        for key, value in configs:
            try:
                result = subprocess.run(
                    ["git", "config", "--local", key, value],
                    cwd=repo_path,
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    self.write_log(f"    [✓] git config --local {key} = \"{value}\"")
                else:
                    self.write_log(f"    [!] Gagal set {key}: {result.stderr.strip()}")
            except Exception as exc:
                self.write_log(f"    [!] Error set git config {key}: {exc}")

    # =========================================================================
    # IDE DETECTION & OPEN IN IDE
    # =========================================================================
    def detect_available_ides(self):
        """Detect programs registered to open directories via OS shell registry."""
        found = []
        seen_cmds = set()

        if sys.platform == "win32":
            import winreg
            # Read from Directory\shell\ — same entries as Windows Explorer right-click menu
            for hive in (winreg.HKEY_CLASSES_ROOT, winreg.HKEY_CURRENT_USER):
                for sub in (r"Directory\shell", r"Directory\Background\shell"):
                    try:
                        shell_key = winreg.OpenKey(hive, sub)
                    except OSError:
                        continue
                    try:
                        i = 0
                        while True:
                            try:
                                entry_name = winreg.EnumKey(shell_key, i)
                                i += 1
                            except OSError:
                                break
                            try:
                                entry_key = winreg.OpenKey(shell_key, entry_name)
                                # Get display name from (Default) value or MUIVerb
                                display_name = None
                                for val_name in (None, "MUIVerb"):
                                    try:
                                        val, _rt = winreg.QueryValueEx(entry_key, val_name)
                                        if val and isinstance(val, str) and not val.startswith("@"):
                                            display_name = val.replace("&", "")
                                            break
                                    except OSError:
                                        pass
                                if not display_name:
                                    display_name = entry_name

                                # Get command
                                try:
                                    cmd_key = winreg.OpenKey(entry_key, "command")
                                    cmd_val, _rt = winreg.QueryValueEx(cmd_key, None)
                                    winreg.CloseKey(cmd_key)
                                except OSError:
                                    winreg.CloseKey(entry_key)
                                    continue
                                winreg.CloseKey(entry_key)

                                if not cmd_val:
                                    continue

                                # Extract exe path from command string like: "C:\...\code.exe" "%V"
                                cmd_str = cmd_val.strip()
                                if cmd_str.startswith('"'):
                                    exe_path = cmd_str.split('"')[1]
                                else:
                                    exe_path = cmd_str.split()[0]

                                exe_lower = exe_path.lower()
                                if exe_lower in seen_cmds:
                                    continue
                                if os.path.isfile(exe_path):
                                    seen_cmds.add(exe_lower)
                                    found.append((display_name, exe_path))
                            except OSError:
                                pass
                    finally:
                        winreg.CloseKey(shell_key)

        # Always add File Explorer as the last option
        found.append((_("open_in_explorer"), "__explorer__"))

        return found

    def open_in_ide(self, ide_cmd, repo_path):
        """Open a repository folder in the specified IDE or File Explorer."""
        try:
            if ide_cmd == "__explorer__":
                if sys.platform == "win32":
                    os.startfile(repo_path)
                elif sys.platform == "darwin":
                    subprocess.Popen(["open", repo_path])
                else:
                    subprocess.Popen(["xdg-open", repo_path])
            elif sys.platform == "win32":
                subprocess.Popen([ide_cmd, repo_path], creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)
            else:
                subprocess.Popen([ide_cmd, repo_path])
        except Exception as e:
            show_error(self, _("error"), _("open_ide_failed", ide=ide_cmd, error=str(e)))

    def show_clone_result_dialog(self, cloned_paths):
        """Show clone results with option to open repos in IDE."""
        available_ides = self.detect_available_ides()

        modal = ctk.CTkToplevel(self)
        modal.title(_("done_title"))

        has_repos = bool(cloned_paths)
        dialog_height = 400 if has_repos else 250
        self.configure_modal_window(modal, 520, dialog_height)

        frame = ctk.CTkFrame(modal, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=(20, 10))

        # Success icon
        icon_frame = ctk.CTkFrame(frame, width=50, height=50, corner_radius=25, fg_color="#2ecc71")
        icon_frame.pack(pady=(0, 12))
        icon_frame.pack_propagate(False)
        ctk.CTkLabel(icon_frame, text="✔", text_color="white",
                     font=ctk.CTkFont(size=24, weight="bold")).pack(expand=True)

        # Summary text
        ctk.CTkLabel(
            frame,
            text=_("clone_done", success=self.sukses, failed=self.gagal),
            font=ctk.CTkFont(family="Open Sans", size=13),
            justify="center", wraplength=460
        ).pack(pady=(0, 10))

        # Open in IDE section — only if there are cloned repos AND IDEs found
        if has_repos:
            ctk.CTkFrame(frame, height=1, fg_color="gray40").pack(fill="x", pady=(4, 8))

            ctk.CTkLabel(
                frame, text=_("open_in_ide_title"),
                font=ctk.CTkFont(family="Open Sans", size=12, weight="bold"),
                anchor="w"
            ).pack(fill="x")

            repo_scroll = ctk.CTkScrollableFrame(frame, height=min(len(cloned_paths) * 42, 180))
            repo_scroll.pack(fill="both", expand=True, pady=(4, 8))

            for repo_name, repo_path in cloned_paths:
                row = ctk.CTkFrame(repo_scroll, fg_color="transparent")
                row.pack(fill="x", pady=2)

                ctk.CTkLabel(
                    row, text=repo_name,
                    font=ctk.CTkFont(family="Open Sans", size=12),
                    anchor="w"
                ).pack(side="left", fill="x", expand=True, padx=(4, 8))

                open_btn = ctk.CTkButton(
                    row,
                    text=_("open_ide_btn"),
                    image=self.open_in_new_img,
                    compound="left",
                    height=30,
                    fg_color="#2980b9", hover_color="#1f618d",
                    font=ctk.CTkFont(family="Open Sans", size=12),
                )
                open_btn.pack(side="right", padx=(0, 4))

                def make_menu_handler(btn, path):
                    def handler():
                        menu = tk.Menu(btn, tearoff=0)
                        for ide_name, ide_cmd in available_ides:
                            menu.add_command(
                                label=ide_name,
                                command=lambda c=ide_cmd, p=path: self.open_in_ide(c, p)
                            )
                        # Show popup menu relative to the button
                        try:
                            x = btn.winfo_rootx()
                            y = btn.winfo_rooty() + btn.winfo_height()
                            menu.tk_popup(x, y)
                        finally:
                            menu.grab_release()
                    return handler

                open_btn.configure(command=make_menu_handler(open_btn, repo_path))

        # OK button
        btn_frame = ctk.CTkFrame(modal, fg_color="transparent")
        btn_frame.pack(pady=(0, 16))
        ctk.CTkButton(btn_frame, text="OK", width=120, height=36, font=ctk.CTkFont(family="Open Sans", weight="bold"), command=modal.destroy).pack()


if __name__ == "__main__":
    app = GLRCApp()
    app.mainloop()
