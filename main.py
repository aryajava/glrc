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
import time
import shutil
import logging
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
try:
    import pystray
except Exception:
    pystray = None

logger = logging.getLogger("glrc")

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
    DEFAULT_EXPANDED_HEIGHT, DEFAULT_PER_PAGE,
    MAX_CONCURRENT_CLONES, MAX_RETRY_ATTEMPTS, RETRY_DELAY_SECONDS
)


class Dimmer:
    """Subtle overlay behind modal windows when enabled."""
    def __init__(self, parent, enabled=True):
        self.parent = parent
        self.enabled = enabled
        self.window = None

    def show(self):
        if not self.enabled or self.window is not None:
            return
        try:
            self.window = tk.Toplevel(self.parent)
            self.window.overrideredirect(True)
            self.window.transient(self.parent)
            self.window.attributes("-alpha", 0.24)
            self.window.configure(bg="#000000")
            self._sync_geometry()
            self.window.lift(self.parent)
            # Store binding ID for proper cleanup
            self._bind_id = self.parent.bind("<Configure>", self._sync_geometry, add="+")
        except Exception:
            self.destroy()

    def _sync_geometry(self, event=None):
        if not self.window or not self.window.winfo_exists():
            return
        if getattr(self, "_in_sync", False):
            return
        try:
            self._in_sync = True
            w, h = self.parent.winfo_width(), self.parent.winfo_height()
            x, y = self.parent.winfo_rootx(), self.parent.winfo_rooty()
            
            # Only update if changed
            last = getattr(self, "_last_geom", None)
            current = (w, h, x, y)
            if last != current:
                self.window.geometry(f"{w}x{h}+{x}+{y}")
                self._last_geom = current
        except Exception:
            pass
        finally:
            self._in_sync = False

    def destroy(self):
        # Clean up binding first
        if hasattr(self, "_bind_id") and self.parent.winfo_exists():
            try:
                self.parent.unbind("<Configure>", self._bind_id)
            except Exception:
                pass
        
        if self.window is not None:
            try:
                if self.window.winfo_exists():
                    self.window.destroy()
            except Exception:
                pass
        self.window = None

class GLRCApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        # Resolve bundled asset path (PyInstaller onefile extracts to _MEIPASS).
        self.base_dir = getattr(sys, "_MEIPASS", os.path.dirname(__file__))
        self.app_version = self.load_app_version()

        # Load Config Manager
        self.config = ConfigManager()
        self.window_state = self.config.get_window_state()
        
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
        self.restore_window_state(self.login_w, self.login_h)
        self.after(100, lambda: self.apply_window_icon(self))
        self.apply_power_window_settings()
        self.protocol("WM_DELETE_WINDOW", self.on_main_close)

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
        self.fetch_request_id = 0
        self.modal_stack = []
        self.modal_dimmers = {}
        self.theme_sensitive_widgets = []
        self.empty_state_frame = None
        self.last_effective_theme = None
        self.tray_icon = None
        self.tray_thread = None
        self.tray_minimizing = False
        
        # --- Variabel State Fetching ---
        self.is_fetching = False

        # Setup UI
        self.setup_login_frame()
        self.setup_main_frame()

        self.login_frame.pack(fill="both", expand=True)
        self.bind_global_shortcuts()
        self.bind("<Unmap>", self.on_window_unmap, add="+")
        self.start_theme_sync()
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
        self.apply_window_icon(window)

        def clear_topmost():
            try:
                if window.winfo_exists():
                    window.attributes("-topmost", False)
            except Exception:
                pass

        try:
            if hasattr(window, "deiconify"):
                window.deiconify()
            window.update_idletasks()
            window.lift()
            window.attributes("-topmost", True)
            window.after(150, clear_topmost)
            window.focus_force()
        except Exception:
            pass

    def is_geometry_on_screen(self, x, y, width, height):
        try:
            screen_w = self.winfo_screenwidth()
            screen_h = self.winfo_screenheight()
            return (
                x is not None and y is not None
                and x + max(160, width // 3) > 0
                and y + 80 > 0
                and x < screen_w - 80
                and y < screen_h - 80
            )
        except Exception:
            return False

    def restore_window_state(self, default_width, default_height):
        state = self.window_state
        startup_state = state.get("startup_state", "Center")
        width = int(state.get("width") or default_width)
        height = int(state.get("height") or default_height)
        width = max(640, min(width, self.winfo_screenwidth()))
        height = max(520, min(height, self.winfo_screenheight()))

        if startup_state == "Last Position":
            x = state.get("x")
            y = state.get("y")
            if self.is_geometry_on_screen(x, y, width, height):
                self.geometry(f"{width}x{height}+{int(x)}+{int(y)}")
                return

        self.geometry(f"{default_width}x{default_height}")
        if startup_state in ("Center", "Last Position"):
            center_window(self, default_width, default_height)

    def save_window_geometry(self):
        try:
            self.update_idletasks()
            self.config.set_window_state({
                "width": self.winfo_width(),
                "height": self.winfo_height(),
                "x": self.winfo_x(),
                "y": self.winfo_y(),
            })
        except Exception:
            pass

    def apply_power_window_settings(self):
        state = self.config.get_window_state()
        self.window_state = state
        try:
            self.attributes("-topmost", bool(state.get("always_on_top", False)))
        except Exception:
            pass
        try:
            opacity = int(state.get("opacity", 100))
            self.attributes("-alpha", max(80, min(opacity, 100)) / 100)
        except Exception:
            pass
        # Lock window position (via Windows API – no flicker)
        self._apply_lock_move(self, state.get("lock_window_pos", False))

    def _apply_lock_move(self, window, lock=True):
        """Enable or disable window dragging via Windows API (SC_MOVE).
        Falls back silently on non-Windows platforms."""
        try:
            import ctypes
            hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
            SC_MOVE = 0xF010
            MF_BYCOMMAND = 0x00000000
            if lock:
                hmenu = ctypes.windll.user32.GetSystemMenu(hwnd, False)
                ctypes.windll.user32.DeleteMenu(hmenu, SC_MOVE, MF_BYCOMMAND)
                ctypes.windll.user32.DrawMenuBar(hwnd)
            else:
                # Reset the system menu to default (restores SC_MOVE)
                ctypes.windll.user32.GetSystemMenu(hwnd, True)
                ctypes.windll.user32.DrawMenuBar(hwnd)
        except Exception:
            pass

    def on_main_close(self):
        state = self.config.get_window_state()
        if state.get("minimize_to_tray"):
            self.minimize_to_tray()
            return
        self.exit_app()

    def on_window_unmap(self, event=None):
        if event is not None and event.widget is not self:
            return
        if self.tray_minimizing:
            return
        try:
            if pystray is not None and self.state() == "iconic" and self.config.get_window_state().get("minimize_to_tray"):
                self.after(50, self.minimize_to_tray)
        except Exception:
            pass

    def exit_app(self):
        self.save_window_geometry()
        try:
            if self.tray_icon:
                self.tray_icon.stop()
                self.tray_icon = None
        except Exception:
            pass
        self.destroy()

    def show_from_tray(self, icon=None, item=None):
        def _show():
            self.tray_minimizing = False
            self.deiconify()
            self.activate_window(self)
        self.schedule_ui(_show)

    def minimize_to_tray(self):
        if pystray is None:
            show_warning(self, _("warning"), _("tray_unavailable"))
            self.iconify()
            return
        self.tray_minimizing = True
        self.withdraw()
        if self.tray_icon is not None:
            return

        def tray_show(icon, item):
            self.show_from_tray(icon, item)

        def tray_exit(icon, item):
            self.schedule_ui(self.exit_app)

        try:
            logo_path = os.path.join(self.base_dir, "assets", "icons", "logo.png")
            image = Image.open(logo_path) if os.path.exists(logo_path) else Image.new("RGB", (64, 64), "#1f6aa5")
            menu = pystray.Menu(
                pystray.MenuItem(_("tray_show"), tray_show),
                pystray.MenuItem(_("tray_exit"), tray_exit)
            )
            self.tray_icon = pystray.Icon("GLRC", image, _("app_name"), menu)
            self.tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
            self.tray_thread.start()
        except Exception as exc:
            logger.warning("Failed to create tray icon: %s", exc)
            self.tray_icon = None
            self.iconify()

    def configure_modal_window(self, modal, width, height, on_escape=None, use_grab=True):
        # Apply icon immediately
        self.apply_window_icon(modal)
        
        # Override icon methods to prevent CustomTkinter's internal 200ms timer from reverting the icon
        def dummy_icon_method(*args, **kwargs):
            pass
        try:
            modal.iconbitmap = dummy_icon_method
            modal.wm_iconbitmap = dummy_icon_method
            modal.iconphoto = dummy_icon_method
            modal.wm_iconphoto = dummy_icon_method
        except Exception:
            pass

        modal.geometry(f"{width}x{height}")
        modal.resizable(False, False)
        modal.transient(self)
        center_window(modal, width, height)
        if modal not in self.modal_stack:
            self.modal_stack.append(modal)
        dimmer = Dimmer(self, enabled=self.config.get_window_state().get("modal_dimming", True))
        dimmer.show()
        self.modal_dimmers[modal] = dimmer

        def release_modal_grab():
            try:
                if modal.grab_current() == modal:
                    modal.grab_release()
            except Exception:
                pass

        def close_action():
            release_modal_grab()
            if on_escape:
                on_escape()
            elif modal.winfo_exists():
                modal.destroy()

        def cleanup_on_destroy(_event=None):
            release_modal_grab()
            if modal in self.modal_stack:
                self.modal_stack.remove(modal)
            dimmer = self.modal_dimmers.pop(modal, None)
            if dimmer is not None:
                dimmer.destroy()

        modal.protocol("WM_DELETE_WINDOW", close_action)
        modal.bind("<Escape>", lambda event: (close_action(), "break")[1])
        modal.bind("<Destroy>", cleanup_on_destroy, add="+")

        # If main window is always-on-top, modal must also be topmost
        # This MUST be set before grab_set to ensure modal appears above main window
        try:
            if self.config.get_window_state().get("always_on_top"):
                modal.attributes("-topmost", True)
        except Exception:
            pass

        # Activate window normally (deiconify, lift, topmost)
        try:
            modal.deiconify()
            modal.lift()
            modal.focus_force()
            if use_grab:
                modal.grab_set()
        except Exception:
            pass

        # Lock modal position (via Windows API – no flicker)
        if self.config.get_window_state().get("lock_modal_pos"):
            modal.after(200, lambda: self._apply_lock_move(modal, True))

    def bind_global_shortcuts(self):
        for sequence in getattr(self, "bound_global_shortcuts", []):
            try:
                self.unbind_all(sequence)
            except Exception:
                pass
        self.bound_global_shortcuts = []

        def open_workspace_shortcut(event=None):
            self.open_workspace_tools_modal()
            return "break"

        workspace_shortcut = self.get_shortcut_sequence("workspace_tools")
        for sequence in self.shortcut_variants(workspace_shortcut):
            self.bind_all(sequence, open_workspace_shortcut)
            self.bound_global_shortcuts.append(sequence)
        self.bind_all("<Escape>", self.close_top_modal)

    def get_shortcut_sequence(self, action):
        shortcuts = self.config.get_keyboard_shortcuts()
        return shortcuts.get(action, {
            "workspace_tools": "Control-g",
            "find": "Control-f",
            "primary_action": "Control-Return",
        }.get(action, "Control-g"))

    def shortcut_variants(self, shortcut):
        if not shortcut:
            return []
        if shortcut.startswith("<") and shortcut.endswith(">"):
            shortcut = shortcut[1:-1]
        variants = {f"<{shortcut}>"}
        if shortcut.endswith("-g"):
            variants.add("<Control-G>")
        if shortcut.endswith("-f"):
            variants.add("<Control-F>")
        return list(variants)

    def close_top_modal(self, event=None):
        for modal in reversed(list(getattr(self, "modal_stack", []))):
            try:
                if modal.winfo_exists():
                    modal.event_generate("<Escape>")
                    return "break"
            except Exception:
                pass
        return None

    def get_effective_theme(self):
        mode = ctk.get_appearance_mode()
        return "dark" if str(mode).lower() == "dark" else "light"

    def theme_colors(self):
        if self.get_effective_theme() == "dark":
            return {
                "panel": "#1f2937",
                "subtle_panel": "#111827",
                "text": "#f9fafb",
                "muted": "#9ca3af",
                "border": "#374151",
                "accent": "#3b82f6",
            }
        return {
            "panel": "#f8fafc",
            "subtle_panel": "#eef2f7",
            "text": "#111827",
            "muted": "#64748b",
            "border": "#cbd5e1",
            "accent": "#2563eb",
        }

    def register_theme_widget(self, widget, **roles):
        if widget is None:
            return
        self.theme_sensitive_widgets.append((widget, roles))
        self.apply_theme_to_widget(widget, roles)

    def apply_theme_to_widget(self, widget, roles):
        try:
            if not widget.winfo_exists():
                return
            colors = self.theme_colors()
            config = {}
            for option, color_key in roles.items():
                config[option] = colors.get(color_key, color_key)
            if config:
                widget.configure(**config)
        except Exception:
            pass

    def refresh_theme_sensitive_widgets(self):
        alive = []
        for widget, roles in self.theme_sensitive_widgets:
            try:
                if widget.winfo_exists():
                    self.apply_theme_to_widget(widget, roles)
                    alive.append((widget, roles))
            except Exception:
                pass
        self.theme_sensitive_widgets = alive

    def start_theme_sync(self):
        self.last_effective_theme = self.get_effective_theme()
        self.poll_theme_changes()

    def poll_theme_changes(self):
        current_theme = self.get_effective_theme()
        if current_theme != self.last_effective_theme:
            self.last_effective_theme = current_theme
            self.refresh_theme_sensitive_widgets()
        self.after(1200, self.poll_theme_changes)

    def reset_to_login_size(self):
        self.geometry(f"{self.login_w}x{self.login_h}")
        self.minsize(self.login_w, self.login_h)
        self.update_idletasks()
        if self.config.get_window_state().get("startup_state") == "Center":
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

        for button_name, state in (
            ("btn_select_all", "normal" if has_repos else "disabled"),
            ("btn_deselect_all", "normal" if has_repos else "disabled"),
            ("btn_export", "normal" if has_selection else "disabled"),
        ):
            button = getattr(self, button_name, None)
            if button is not None:
                self._set_btn_state(button, state)

    def schedule_ui(self, callback, delay=0):
        try:
            if self.winfo_exists():
                self.after(delay, callback)
        except (RuntimeError, tk.TclError):
            logger.debug("Skipped UI callback because the main loop is no longer available.")

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
        ToolTip(self.search_btn, _("tooltip_search"))

        self.reset_search_btn = ctk.CTkButton(
            tools_frame, text=_("reset_btn"), font=ctk.CTkFont(family="Open Sans"), height=32,
            image=self.icon_reset_img, compound="left",
            fg_color="gray40", hover_color="gray30",
            command=self.reset_search
        )
        self.reset_search_btn.pack(side="left")
        ToolTip(self.reset_search_btn, _("tooltip_reset_search"))

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
        ToolTip(self.btn_select_all, _("tooltip_select_all"))

        self.btn_deselect_all = ctk.CTkButton(action_frame, text=_("deselect_all"), font=ctk.CTkFont(family="Open Sans"), height=32, image=self.icon_uncheck_all_img, compound="left", fg_color="gray40", hover_color="gray30", command=self.deselect_all)
        self.btn_deselect_all.pack(side="left")
        ToolTip(self.btn_deselect_all, _("tooltip_deselect_all"))

        self.btn_export = ctk.CTkButton(action_frame, text=_("btn_export"), font=ctk.CTkFont(family="Open Sans"), height=32, image=self.icon_export_img, compound="left", fg_color="gray40", hover_color="gray30", command=self.export_workspace)
        self.btn_export.pack(side="left", padx=(6, 0))
        ToolTip(self.btn_export, _("tooltip_btn_export"))

        self.btn_workspace_tools = ctk.CTkButton(action_frame, text=_("workspace_tools"), font=ctk.CTkFont(family="Open Sans"), height=32, compound="left", fg_color="#2980b9", hover_color="#1f618d", command=self.open_workspace_tools_modal)
        self.btn_workspace_tools.pack(side="right", padx=(0, 6))
        ToolTip(self.btn_workspace_tools, _("tooltip_workspace_tools"))

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
        self.show_empty_state("initial")

    def browse_folder(self):
        folder_selected = filedialog.askdirectory(title=_("step1_title"))
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

        # Validasi format URL
        try:
            parsed = urlparse(self.gitlab_url)
            if parsed.scheme not in ("http", "https"):
                show_warning(self, _("warning"), _("invalid_url_scheme"))
                return
            if not parsed.hostname:
                show_warning(self, _("warning"), _("invalid_url_host"))
                return
        except Exception:
            show_warning(self, _("warning"), _("invalid_url_scheme"))
            return

        # Cek git binary tersedia
        if not shutil.which("git"):
            show_error(self, _("error"), _("git_not_found"))
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
            user_resp = requests.get(f"{self.gitlab_url}/api/v4/user", headers=headers, timeout=15)
            user_resp.raise_for_status()
            user_data = user_resp.json()
            self.user_name = user_data.get("name", "")
            self.user_email = user_data.get("email", "")
        except Exception:
            self.user_name = ""
            self.user_email = ""

        self.fetch_repositories(search_query="", current_page=1, per_page=self.per_page)

    
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
                show_warning(self, _("warning"), _("page_out_of_range", total_pages=self.total_pages))
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
        self.fetch_request_id += 1
        request_id = self.fetch_request_id
        self.set_ui_loading_state(True)
        self.page_label.configure(text=_("loading"))
        search_query = self.search_entry.get().strip()
        current_page = self.current_page
        per_page = self.per_page
        thread = threading.Thread(
            target=self.fetch_repositories,
            kwargs={
                "search_query": search_query,
                "current_page": current_page,
                "per_page": per_page,
                "request_id": request_id,
            }
        )
        thread.daemon = True
        thread.start()

    def fetch_repositories(self, search_query="", current_page=None, per_page=None, request_id=None):
        try:
            import fnmatch
            headers = {"PRIVATE-TOKEN": self.api_token}
            current_page = current_page or self.current_page
            per_page = per_page or self.per_page
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
                    response = requests.get(api_url, headers=headers, timeout=30)
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
                    
                projects_to_show = all_projects
                total_rows = len(all_projects)
                total_pages = 1
                render_page = 1
                cached_projects = all_projects
                
            else:
                # Normal paginated view
                api_url = (
                    f"{self.gitlab_url}/api/v4/projects"
                    f"?membership=true&simple=true"
                    f"&per_page={per_page}&page={current_page}"
                )
                response = requests.get(api_url, headers=headers, timeout=30)
                response.raise_for_status()
                projects_to_show = response.json()
                
                total = response.headers.get('X-Total', '0')
                total_pages_header = response.headers.get('X-Total-Pages', '1')
                total_rows = int(total) if total.isdigit() else len(projects_to_show)
                total_pages = int(total_pages_header) if total_pages_header.isdigit() else 1
                render_page = current_page
                cached_projects = projects_to_show

            if request_id is not None and request_id != self.fetch_request_id:
                logger.debug("Skipped stale repository fetch result.")
                return

            def apply_fetch_result():
                if request_id is not None and request_id != self.fetch_request_id:
                    logger.debug("Skipped stale repository render.")
                    return

                self.total_rows = total_rows
                self.total_pages = total_pages
                self.current_page = min(max(1, render_page), self.total_pages)
                self.cached_projects = cached_projects

                if not projects_to_show and self.current_page == 1:
                    self.show_main_frame([], False)
                    self.connect_btn.configure(state="normal", text=_("connect_btn"))
                    self.set_ui_loading_state(False)
                    return

                self.show_main_frame(projects_to_show, self.current_page < self.total_pages)

            self.schedule_ui(apply_fetch_result)

        except requests.exceptions.RequestException as e:
            self.schedule_ui(lambda root=self: show_error(root, _("fetching_error"), f"{_('error')}: {e}"))
            self.schedule_ui(lambda: self.connect_btn.configure(state="normal", text=_("connect_btn")))
            self.schedule_ui(lambda: self.page_label.configure(text=_("page_error", current_page=self.current_page)))
            self.schedule_ui(lambda: self.set_ui_loading_state(False))

    def clear_repo_list_widgets(self):
        for item in self.repo_items:
            try:
                item["widget"].destroy()
            except Exception:
                pass
        self.repo_items.clear()
        if self.empty_state_frame is not None:
            try:
                self.empty_state_frame.destroy()
            except Exception:
                pass
            self.empty_state_frame = None

    def show_empty_state(self, context="initial"):
        if not hasattr(self, "scroll_frame"):
            return
        self.clear_repo_list_widgets()
        colors = self.theme_colors()
        frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=24, pady=36)
        self.empty_state_frame = frame

        icon_text = "⌕" if context == "search" else ("↧" if context == "workspace" else "▦")
        icon_label = ctk.CTkLabel(
            frame, text=icon_text, width=64, height=64,
            font=ctk.CTkFont(family="Open Sans", size=34, weight="bold"),
            text_color=colors["muted"]
        )
        icon_label.pack(pady=(8, 10))
        self.register_theme_widget(icon_label, text_color="muted")

        title_key = {
            "search": "empty_search_title",
            "workspace": "empty_workspace_title",
        }.get(context, "empty_initial_title")
        body_key = {
            "search": "empty_search_body",
            "workspace": "empty_workspace_body",
        }.get(context, "empty_initial_body")

        title_label = ctk.CTkLabel(
            frame, text=_(title_key),
            font=ctk.CTkFont(family="Open Sans", size=15, weight="bold"),
            text_color=colors["text"]
        )
        title_label.pack(pady=(0, 6))
        self.register_theme_widget(title_label, text_color="text")
        body_label = ctk.CTkLabel(
            frame, text=_(body_key), wraplength=460, justify="center",
            font=ctk.CTkFont(family="Open Sans", size=12),
            text_color=colors["muted"]
        )
        body_label.pack(pady=(0, 14))
        self.register_theme_widget(body_label, text_color="muted")

        if context == "search":
            cta = ctk.CTkButton(frame, text=_("reset_btn"), width=140, command=self.reset_search)
            cta.pack()
            ToolTip(cta, _("tooltip_reset_search"))
        else:
            cta = ctk.CTkButton(frame, text=_("workspace_tools"), width=170, command=self.open_workspace_tools_modal)
            cta.pack()
            ToolTip(cta, _("tooltip_workspace_tools"))

    def show_main_frame(self, projects, has_next):
        self.login_frame.pack_forget()
        self.geometry(f"{self.expanded_w}x{self.expanded_h}")
        self.minsize(800, 720)
        if self.config.get_window_state().get("startup_state") == "Center":
            center_window(self, self.expanded_w, self.expanded_h)
        self.main_frame.pack(fill="both", expand=True)

        self.clear_repo_list_widgets()

        if not projects:
            context = "search" if self.search_entry.get().strip() else "initial"
            if isinstance(self.filtered_projects, list):
                context = "workspace"
            self.show_empty_state(context)
            self.update_repo_range_label(0)
            self.update_pagination_controls(has_next=False, is_searching=bool(self.search_entry.get().strip()))
            self.connect_btn.configure(state="normal", text=_("connect_btn"))
            self.update_selection_action_buttons()
            self.set_ui_loading_state(False)
            return

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
            except Exception:
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
                show_custom_message(modal, _("done_title"), _("duration_updated"), icon_type="success")

        ctk.CTkButton(edit_frame, text=_("update"), width=80, height=32, command=save_dur, font=ctk.CTkFont(family="Open Sans")).pack(side="left", padx=(10, 0))

    def open_settings_modal(self):
        modal = ctk.CTkToplevel(self)
        modal.title(_("settings_title"))
        self.configure_modal_window(modal, 580, 700)
        colors = self.theme_colors()
        state = self.config.get_window_state()

        # Header
        hdr = ctk.CTkFrame(modal, fg_color="transparent")
        hdr.pack(fill="x", pady=(15, 2))
        hdr_content = ctk.CTkFrame(hdr, fg_color="transparent")
        hdr_content.pack(expand=True)
        ctk.CTkLabel(hdr_content, text="⚙", font=ctk.CTkFont(size=26)).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(hdr_content, text=_("settings_title"), font=ctk.CTkFont(family="Open Sans", size=19, weight="bold")).pack(side="left")

        form = ctk.CTkScrollableFrame(modal, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=30, pady=(0, 10))

        # --- Section: General ---
        self._settings_section_header(form, _("settings_general"), colors)
        gen_grid = ctk.CTkFrame(form, fg_color="transparent")
        gen_grid.pack(fill="x", pady=(0, 10))
        gen_grid.columnconfigure(0, weight=1)
        gen_grid.columnconfigure(1, weight=1)

        ctk.CTkLabel(gen_grid, text=_("language_lbl"), anchor="w", font=ctk.CTkFont(family="Open Sans", size=12)).grid(row=0, column=0, sticky="w", padx=(0, 8))
        lang_var = tk.StringVar(value=self.config.get_language())
        ctk.CTkOptionMenu(gen_grid, variable=lang_var, values=["en", "id"]).grid(row=1, column=0, sticky="ew", padx=(0, 8), pady=(0, 4))

        ctk.CTkLabel(gen_grid, text=_("theme_lbl"), anchor="w", font=ctk.CTkFont(family="Open Sans", size=12)).grid(row=0, column=1, sticky="w", padx=(8, 0))
        theme_var = tk.StringVar(value=self.config.get_theme())
        ctk.CTkOptionMenu(gen_grid, variable=theme_var, values=["System", "Light", "Dark"]).grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=(0, 4))

        # Preferred IDE
        ctk.CTkLabel(form, text=_("preferred_ide_lbl"), anchor="w", font=ctk.CTkFont(family="Open Sans", size=12)).pack(fill="x", pady=(4, 2))
        ide_var = tk.StringVar(value=self.config.config_data.get("preferred_ide", "Always Ask"))
        ctk.CTkOptionMenu(form, variable=ide_var, values=["Always Ask", "VS Code", "Visual Studio", "Cursor", "File Explorer"]).pack(fill="x", pady=(0, 4))

        # --- Section: Clone & Sync ---
        self._settings_section_header(form, _("settings_clone"), colors)
        clone_grid = ctk.CTkFrame(form, fg_color="transparent")
        clone_grid.pack(fill="x", pady=(0, 10))
        clone_grid.columnconfigure(0, weight=1)
        clone_grid.columnconfigure(1, weight=1)

        ctk.CTkLabel(clone_grid, text=_("clone_method_lbl"), anchor="w", font=ctk.CTkFont(family="Open Sans", size=12)).grid(row=0, column=0, sticky="w", padx=(0, 8))
        method_var = tk.StringVar(value=self.config.get_clone_method())
        ctk.CTkOptionMenu(clone_grid, variable=method_var, values=["HTTPS", "SSH"]).grid(row=1, column=0, sticky="ew", padx=(0, 8), pady=(0, 4))

        ctk.CTkLabel(clone_grid, text=_("min_disk_space_lbl"), anchor="w", font=ctk.CTkFont(family="Open Sans", size=12)).grid(row=0, column=1, sticky="w", padx=(8, 0))
        disk_var = tk.StringVar(value=str(self.config.get_min_disk_space_gb()))
        ctk.CTkEntry(clone_grid, textvariable=disk_var).grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=(0, 4))

        # --- Section: Workspace ---
        self._settings_section_header(form, _("settings_workspace"), colors)
        ws_row = ctk.CTkFrame(form, fg_color="transparent")
        ws_row.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(ws_row, text=_("recent_limit_lbl"), anchor="w", font=ctk.CTkFont(family="Open Sans", size=12)).pack(side="left")
        recent_limit_var = tk.StringVar(value=str(self.config.get_recent_limit()))
        ctk.CTkOptionMenu(ws_row, variable=recent_limit_var, values=["5", "10", "20"], width=80).pack(side="left", padx=10)
        
        def clear_history():
            if show_confirmation(modal, _("warning"), _("confirm_clear_history")):
                self.config.clear_recent_workspaces()
                show_info(modal, _("ok"), _("history_cleared"))

        clear_btn = ctk.CTkButton(ws_row, text=_("clear_history_btn"), height=28, fg_color="transparent", 
                                  border_width=1, text_color=colors["muted"], border_color=colors["border"],
                                  command=clear_history)
        clear_btn.pack(side="right")
        ToolTip(clear_btn, _("tooltip_clear_history"))

        # --- Section: Interface (Direct Controls) ---
        self._settings_section_header(form, _("settings_interface"), colors)
        
        # Always on Top
        aot_var = tk.BooleanVar(value=bool(state.get("always_on_top")))
        aot_row = ctk.CTkFrame(form, fg_color="transparent")
        aot_row.pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(aot_row, text=_("always_on_top_lbl"), font=ctk.CTkFont(family="Open Sans", size=12)).pack(side="left")
        ctk.CTkSwitch(aot_row, text="", variable=aot_var, width=44).pack(side="right")

        # Opacity
        opacity_var = tk.IntVar(value=int(state.get("opacity", 100)))
        op_label = ctk.CTkLabel(form, text=_("opacity_lbl", value=opacity_var.get()), anchor="w", font=ctk.CTkFont(family="Open Sans", size=12))
        op_label.pack(fill="x")
        
        def on_opacity_change(val):
            v = int(float(val))
            opacity_var.set(v)
            op_label.configure(text=_("opacity_lbl", value=v))
            try: self.attributes("-alpha", v / 100)
            except: pass

        ctk.CTkSlider(form, from_=80, to=100, number_of_steps=20, variable=opacity_var, command=on_opacity_change).pack(fill="x", pady=(2, 10))

        # --- Section: Advanced ---
        self._settings_section_header(form, _("settings_advanced"), colors)
        adv_btn_frame = ctk.CTkFrame(form, fg_color="transparent")
        adv_btn_frame.pack(fill="x", pady=(0, 8))
        adv_btn_frame.columnconfigure(0, weight=1)
        adv_btn_frame.columnconfigure(1, weight=1)

        wc_btn = ctk.CTkButton(adv_btn_frame, text="🖥  " + _("window_controls_btn"), height=36,
                      command=lambda: self.open_window_controls_modal(parent=modal))
        wc_btn.grid(row=0, column=0, sticky="ew", padx=(0, 4))
        ToolTip(wc_btn, _("tooltip_window_controls"))

        kb_btn = ctk.CTkButton(adv_btn_frame, text="⌨  " + _("keyboard_mapping_btn"), height=36,
                      fg_color="gray40", hover_color="gray30",
                      command=lambda: self.open_keyboard_mapping_modal(parent=modal))
        kb_btn.grid(row=0, column=1, sticky="ew", padx=(4, 0))
        ToolTip(kb_btn, _("tooltip_keyboard_mapping"))

        initial_state = {
            "lang": self.config.get_language(),
            "theme": self.config.get_theme(),
            "ide": self.config.config_data.get("preferred_ide", "Always Ask"),
            "method": self.config.get_clone_method(),
            "disk": str(self.config.get_min_disk_space_gb()),
            "limit": str(self.config.get_recent_limit()),
            "aot": bool(state.get("always_on_top")),
            "opacity": int(state.get("opacity", 100))
        }

        def has_changes():
            try:
                return (
                    lang_var.get() != initial_state["lang"] or
                    theme_var.get() != initial_state["theme"] or
                    ide_var.get() != initial_state["ide"] or
                    method_var.get() != initial_state["method"] or
                    disk_var.get() != initial_state["disk"] or
                    recent_limit_var.get() != initial_state["limit"] or
                    aot_var.get() != initial_state["aot"] or
                    opacity_var.get() != initial_state["opacity"]
                )
            except Exception: return True

        # Footer: Version & Update
        footer = ctk.CTkFrame(form, fg_color="transparent")
        footer.pack(fill="x", pady=(15, 0))
        
        ver_lbl = ctk.CTkLabel(footer, text=_("app_version_lbl", version="1.5.4"), 
                               font=ctk.CTkFont(family="Open Sans", size=11), text_color=colors["muted"])
        ver_lbl.pack(side="left")
        
        upd_btn = ctk.CTkButton(footer, text=_("check_updates_btn"), width=100, height=24, 
                                fg_color="transparent", text_color=colors["accent"], hover_color=colors["subtle_panel"],
                                font=ctk.CTkFont(family="Open Sans", size=11, weight="bold"))
        upd_btn.pack(side="right")

        # Save
        def save_settings(force=False):
            if not has_changes() and not force:
                modal.destroy()
                return

            if not force:
                if not show_confirmation(modal, _("confirm_save_title"), _("confirm_save_msg")):
                    return

            try:
                space_val = float(disk_var.get())
                if space_val < 0: raise ValueError
            except ValueError:
                show_error(modal, _("error"), _("disk_space_invalid"))
                return

            # Update Config
            self.config.set_language(lang_var.get())
            self.config.set_theme(theme_var.get())
            self.config.set_clone_method(method_var.get())
            self.config.set_min_disk_space_gb(space_val)
            self.config.set_recent_limit(int(recent_limit_var.get()))
            self.config.config_data["preferred_ide"] = ide_var.get()
            
            # Window State updates
            self.config.set_window_state({
                "always_on_top": bool(aot_var.get()),
                "opacity": int(opacity_var.get())
            })

            # Apply immediate
            i18n.set_language(lang_var.get())
            ctk.set_appearance_mode(theme_var.get())
            self.apply_power_window_settings()
            self.refresh_theme_sensitive_widgets()
            modal.destroy()
            show_info(self, _("ok"), _("settings_saved"))

        def on_close():
            if has_changes():
                if show_confirmation(modal, _("confirm_save_title"), _("confirm_exit_save_msg")):
                    save_settings(force=True)
                else:
                    modal.destroy()
            else:
                modal.destroy()

        modal.protocol("WM_DELETE_WINDOW", on_close)

        ctk.CTkButton(modal, text=_("save_settings"), height=40,
                      font=ctk.CTkFont(family="Open Sans", weight="bold"),
                      command=save_settings).pack(fill="x", padx=30, pady=(4, 20))

    def _settings_section_header(self, parent, title, colors=None):
        """Render a visually separated section header inside a settings form."""
        if colors is None:
            colors = self.theme_colors()
        sep = ctk.CTkFrame(parent, height=1, fg_color=colors["border"])
        sep.pack(fill="x", pady=(12, 6))
        self.register_theme_widget(sep, fg_color="border")
        lbl = ctk.CTkLabel(parent, text=title, anchor="w",
                           font=ctk.CTkFont(family="Open Sans", size=13, weight="bold"),
                           text_color=colors["muted"])
        lbl.pack(fill="x", pady=(0, 6))
        self.register_theme_widget(lbl, text_color="muted")

    def open_window_controls_modal(self, parent=None):
        modal = ctk.CTkToplevel(parent or self)
        modal.title(_("window_controls_title"))
        self.configure_modal_window(modal, 480, 560)
        state = self.config.get_window_state()
        colors = self.theme_colors()

        hdr = ctk.CTkFrame(modal, fg_color="transparent")
        hdr.pack(fill="x", pady=(15, 2))
        hdr_content = ctk.CTkFrame(hdr, fg_color="transparent")
        hdr_content.pack(expand=True)
        ctk.CTkLabel(hdr_content, text="🖥", font=ctk.CTkFont(size=24)).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(hdr_content, text=_("window_controls_title"), font=ctk.CTkFont(family="Open Sans", size=18, weight="bold")).pack(side="left")

        ctk.CTkLabel(modal, text=_("window_controls_desc"), wraplength=410, font=ctk.CTkFont(family="Open Sans", size=11), text_color=colors["muted"], justify="center").pack(fill="x", padx=28, pady=(0, 10))

        form = ctk.CTkScrollableFrame(modal, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=28)

        tray_var = tk.BooleanVar(value=bool(state.get("minimize_to_tray")))
        dim_var = tk.BooleanVar(value=bool(state.get("modal_dimming", True)))
        lock_win_var = tk.BooleanVar(value=bool(state.get("lock_window_pos")))
        lock_modal_var = tk.BooleanVar(value=bool(state.get("lock_modal_pos")))
        startup_var = tk.StringVar(value=state.get("startup_state", "Center"))

        def _toggle_row(parent_f, label, desc, variable):
            row = ctk.CTkFrame(parent_f, corner_radius=8)
            row.pack(fill="x", pady=(0, 6))
            self.register_theme_widget(row, fg_color="subtle_panel")
            
            inner = ctk.CTkFrame(row, fg_color="transparent")
            inner.pack(fill="x", padx=12, pady=8)
            inner.grid_columnconfigure(0, weight=1)
            
            info = ctk.CTkFrame(inner, fg_color="transparent")
            info.grid(row=0, column=0, sticky="nsew")
            
            ctk.CTkLabel(info, text=label, anchor="w", font=ctk.CTkFont(family="Open Sans", size=12, weight="bold")).pack(fill="x")
            d = ctk.CTkLabel(info, text=desc, anchor="w", font=ctk.CTkFont(family="Open Sans", size=10), text_color=colors["muted"], wraplength=350)
            d.pack(fill="x")
            self.register_theme_widget(d, text_color="muted")
            
            ctk.CTkSwitch(inner, text="", variable=variable, width=44).grid(row=0, column=1, sticky="e", padx=(10, 0))

        _toggle_row(form, _("minimize_to_tray_lbl"), _("minimize_to_tray_desc"), tray_var)
        _toggle_row(form, _("modal_dimming_lbl"), _("modal_dimming_desc"), dim_var)
        _toggle_row(form, _("lock_window_pos_lbl"), _("lock_window_pos_desc"), lock_win_var)
        _toggle_row(form, _("lock_modal_pos_lbl"), _("lock_modal_pos_desc"), lock_modal_var)

        ctk.CTkFrame(form, height=1, fg_color=colors["border"]).pack(fill="x", pady=(8, 10))

        # Startup State — card-style row
        startup_row = ctk.CTkFrame(form, corner_radius=8)
        startup_row.pack(fill="x", pady=(0, 6))
        self.register_theme_widget(startup_row, fg_color="subtle_panel")
        startup_inner = ctk.CTkFrame(startup_row, fg_color="transparent")
        startup_inner.pack(fill="x", padx=12, pady=10)
        startup_inner.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(startup_inner, text=_("startup_state_lbl"), anchor="w", font=ctk.CTkFont(family="Open Sans", size=12, weight="bold")).grid(row=0, column=0, sticky="w")
        ctk.CTkOptionMenu(startup_inner, variable=startup_var, values=["Last Position", "Center", "Default"], width=140).grid(row=0, column=1, sticky="e")

        initial_state = {
            "tray": bool(state.get("minimize_to_tray")),
            "dim": bool(state.get("modal_dimming", True)),
            "lock_win": bool(state.get("lock_window_pos")),
            "lock_modal": bool(state.get("lock_modal_pos")),
            "startup": state.get("startup_state", "Center")
        }

        def has_changes():
            return (
                tray_var.get() != initial_state["tray"] or
                dim_var.get() != initial_state["dim"] or
                lock_win_var.get() != initial_state["lock_win"] or
                lock_modal_var.get() != initial_state["lock_modal"] or
                startup_var.get() != initial_state["startup"]
            )

        def save_controls(force=False):
            if not has_changes() and not force:
                modal.destroy()
                return

            if not force:
                if not show_confirmation(modal, _("confirm_save_title"), _("confirm_save_msg")):
                    return

            self.config.set_window_state({
                "minimize_to_tray": bool(tray_var.get()),
                "modal_dimming": bool(dim_var.get()),
                "lock_window_pos": bool(lock_win_var.get()),
                "lock_modal_pos": bool(lock_modal_var.get()),
                "startup_state": startup_var.get(),
            })
            self.apply_power_window_settings()
            modal.destroy()
            show_info(parent or self, _("ok"), _("settings_saved"))

        def on_close():
            if has_changes():
                if show_confirmation(modal, _("confirm_save_title"), _("confirm_exit_save_msg")):
                    save_controls(force=True)
                else:
                    modal.destroy()
            else:
                modal.destroy()

        modal.protocol("WM_DELETE_WINDOW", on_close)

        ctk.CTkButton(modal, text=_("save_settings"), height=38, font=ctk.CTkFont(family="Open Sans", weight="bold"), command=save_controls).pack(fill="x", padx=28, pady=(4, 18))


    def open_keyboard_mapping_modal(self, parent=None):
        modal = ctk.CTkToplevel(parent or self)
        modal.title(_("keyboard_mapping_title"))
        self.configure_modal_window(modal, 480, 440)
        shortcuts = self.config.get_keyboard_shortcuts()
        colors = self.theme_colors()

        hdr = ctk.CTkFrame(modal, fg_color="transparent")
        hdr.pack(fill="x", pady=(15, 2))
        hdr_content = ctk.CTkFrame(hdr, fg_color="transparent")
        hdr_content.pack(expand=True)
        ctk.CTkLabel(hdr_content, text="⌨", font=ctk.CTkFont(size=24)).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(hdr_content, text=_("keyboard_mapping_title"), font=ctk.CTkFont(family="Open Sans", size=18, weight="bold")).pack(side="left")

        ctk.CTkLabel(modal, text=_("click_to_edit_shortcut"), wraplength=400, font=ctk.CTkFont(family="Open Sans", size=11), text_color=colors["muted"], justify="center").pack(fill="x", padx=28, pady=(0, 10))

        form = ctk.CTkFrame(modal, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=28)

        action_config = [
            ("workspace_tools", _("shortcut_workspace_tools"), _("shortcut_workspace_tools_desc")),
            ("find", _("shortcut_find"), _("shortcut_find_desc")),
            ("primary_action", _("shortcut_primary_action"), _("shortcut_primary_action_desc")),
        ]

        # State management
        state = {"active_action": None}
        row_data = {} # action -> {badge_frame, row_frame, render_func}
        initial_shortcuts = {a: shortcuts.get(a, self.get_shortcut_sequence(a)) for a, _, _ in action_config}
        current_shortcuts = initial_shortcuts.copy()

        def has_changes():
            return any(current_shortcuts[a] != initial_shortcuts[a] for a, _, _ in action_config)

        def save_and_apply(force=False):
            if not has_changes() and not force:
                modal.destroy()
                return
            
            if not force:
                if not show_confirmation(modal, _("confirm_save_title"), _("confirm_save_msg")):
                    return

            self.config.set_keyboard_shortcuts(current_shortcuts)
            self.bind_global_shortcuts()
            modal.destroy()
            show_info(parent or self, _("ok"), _("settings_saved"))

        def stop_recording():
            if state["active_action"]:
                action = state["active_action"]
                state["active_action"] = None
                row_data[action]["render_func"](current_shortcuts.get(action))

        def on_keypress(e):
            if not state["active_action"]: return
            key = e.keysym
            if key in ["Control_L", "Control_R", "Alt_L", "Alt_R", "Shift_L", "Shift_R", "Win_L", "Win_R", "Caps_Lock", "Num_Lock"]:
                return "break"
            
            mods = []
            if e.state & 0x4: mods.append("Control")
            if e.state & 0x20000: mods.append("Alt")
            if e.state & 0x1: mods.append("Shift")
            
            key_map = {"Return": "Return", "space": "space", "BackSpace": "BackSpace", "Tab": "Tab", "Delete": "Delete", "Escape": "Escape"}
            key = key_map.get(key, key.lower())
            
            current_shortcuts[state["active_action"]] = "-".join(mods + [key]) if mods else key
            stop_recording()
            return "break"

        def on_click_anywhere(e):
            if not state["active_action"]: return
            try:
                # Find which widget was clicked
                widget = modal.winfo_containing(e.x_root, e.y_root)
                # Check if it's inside the active row's frame
                is_inside = False
                curr = widget
                target_frame = row_data[state["active_action"]]["row_frame"]
                while curr:
                    if curr == target_frame:
                        is_inside = True
                        break
                    curr = curr.master
                if not is_inside:
                    stop_recording()
            except:
                stop_recording()

        # Bind listeners ONCE at modal level
        modal.bind("<Key>", on_keypress)
        modal.bind("<Button-1>", on_click_anywhere, "+")

        def build_row(parent_f, action, label, desc, is_editable=True):
            current_val = current_shortcuts.get(action)

            row = ctk.CTkFrame(parent_f, fg_color="transparent")
            row.pack(fill="x", pady=(0, 2))

            sep = ctk.CTkFrame(parent_f, height=1, fg_color=colors["border"])
            sep.pack(fill="x", pady=(0, 6))
            self.register_theme_widget(sep, fg_color="border")

            info = ctk.CTkFrame(row, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(info, text=label, anchor="w", font=ctk.CTkFont(family="Open Sans", size=13)).pack(fill="x")
            d = ctk.CTkLabel(info, text=desc, anchor="w", font=ctk.CTkFont(family="Open Sans", size=10), text_color=colors["muted"])
            d.pack(fill="x")
            self.register_theme_widget(d, text_color="muted")

            badge_frame = ctk.CTkFrame(row, fg_color="transparent")
            badge_frame.pack(side="right")

            def render_badges(seq):
                for w in badge_frame.winfo_children(): w.destroy()
                parts = [p for p in seq.replace("Control", "Ctrl").replace("Return", "Enter").replace("Alt", "Alt").split("-") if p]
                for part in parts:
                    b = ctk.CTkLabel(badge_frame, text=part, width=max(36, len(part) * 10 + 12), height=28, corner_radius=6, 
                                     font=ctk.CTkFont(family="Open Sans", size=12, weight="bold"), 
                                     fg_color=colors["border"], text_color=colors["text"])
                    b.pack(side="left", padx=2)
                    self.register_theme_widget(b, fg_color="border", text_color="text")

            render_badges(current_val)
            row_data[action] = {"badge_frame": badge_frame, "row_frame": row, "render_func": render_badges}

            if not is_editable: return

            def on_start_edit(e=None):
                if state["active_action"] == action: return
                if state["active_action"]: stop_recording()
                
                state["active_action"] = action
                for w in badge_frame.winfo_children(): w.destroy()
                ctk.CTkLabel(badge_frame, text=_("kb_press_keys"), 
                             font=ctk.CTkFont(family="Open Sans", size=12, slant="italic"),
                             text_color=colors.get("accent", "#3b82f6")).pack()

            # Bind row click
            for w in [row, info, badge_frame]:
                w.bind("<Button-1>", on_start_edit)
                for child in w.winfo_children(): child.bind("<Button-1>", on_start_edit)

        for action, label, desc in action_config:
            build_row(form, action, label, desc, is_editable=True)

        # Esc row
        esc_sep = ctk.CTkFrame(form, height=1, fg_color=colors["border"])
        esc_sep.pack(fill="x", pady=(2, 6))
        self.register_theme_widget(esc_sep, fg_color="border")
        esc_row = ctk.CTkFrame(form, fg_color="transparent")
        esc_row.pack(fill="x", pady=(0, 4))
        esc_info = ctk.CTkFrame(esc_row, fg_color="transparent")
        esc_info.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(esc_info, text=_("shortcut_close_modal"), anchor="w", font=ctk.CTkFont(family="Open Sans", size=13)).pack(fill="x")
        esc_d = ctk.CTkLabel(esc_info, text=_("shortcut_close_modal_desc"), anchor="w", font=ctk.CTkFont(family="Open Sans", size=10, slant="italic"), text_color=colors["muted"])
        esc_d.pack(fill="x")
        self.register_theme_widget(esc_d, text_color="muted")
        
        esc_badge_lbl = ctk.CTkLabel(esc_row, text="Esc", width=42, height=28, corner_radius=6, font=ctk.CTkFont(family="Open Sans", size=12, weight="bold"), fg_color=colors["border"], text_color=colors["text"])
        esc_badge_lbl.pack(side="right")
        self.register_theme_widget(esc_badge_lbl, fg_color="border", text_color="text")

        def on_close():
            if has_changes():
                if show_confirmation(modal, _("confirm_save_title"), _("confirm_exit_save_msg")):
                    save_and_apply(force=True)
                else:
                    modal.destroy()
            else:
                modal.destroy()

        modal.protocol("WM_DELETE_WINDOW", on_close)

        ctk.CTkButton(modal, text=_("save_settings"), height=38, font=ctk.CTkFont(family="Open Sans", weight="bold"), 
                      command=save_and_apply).pack(fill="x", padx=28, pady=(4, 18))






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

        link_frame = ctk.CTkFrame(modal, fg_color="transparent")
        link_frame.pack(pady=5)

        import webbrowser
        def open_link(url):
            webbrowser.open_new(url)

        for text_key, url in [
            ("source_code", "https://github.com/aryajava/glrc"),
            ("issues", "https://github.com/aryajava/glrc/issues"),
            ("check_updates", "https://github.com/aryajava/glrc/releases"),
        ]:
            lnk = ctk.CTkLabel(link_frame, text=_(text_key), text_color="#3498db", font=ctk.CTkFont(family="Open Sans", underline=True))
            lnk.pack(side="left", padx=10)
            lnk.bind("<Button-1>", lambda e, u=url: open_link(u))
            lnk.configure(cursor="hand2")

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

    def open_workspace_tools_modal(self):
        if getattr(self, "workspace_tools_modal", None) and self.workspace_tools_modal.winfo_exists():
            self.activate_window(self.workspace_tools_modal)
            self.workspace_tools_modal.grab_set()
            return

        modal = ctk.CTkToplevel(self)
        self.workspace_tools_modal = modal
        modal.title(_("workspace_tools_title"))

        def close_workspace_tools():
            if modal.winfo_exists():
                modal.destroy()
            self.workspace_tools_modal = None

        self.configure_modal_window(modal, 600, 760, on_escape=close_workspace_tools)

        ctk.CTkLabel(modal, text=_("workspace_tools_title"), font=ctk.CTkFont(family="Open Sans", size=18, weight="bold")).pack(pady=(20, 10))

        recent_paths = []
        recent_display_map = {}
        recent_var = tk.StringVar(value=_("recent_empty"))

        def recent_label(path):
            from src.utils.helpers import middle_truncate
            return f"{os.path.basename(path)} — {middle_truncate(os.path.dirname(path), 42)}"

        def refresh_recent_dropdown():
            nonlocal recent_paths, recent_display_map
            recent_paths = self.config.get_recent_workspaces()
            recent_display_map = {recent_label(path): path for path in recent_paths}
            labels = list(recent_display_map.keys()) or [_("recent_empty")]
            recent_menu.configure(values=labels)
            recent_var.set(labels[0])
            load_recent_btn.configure(state="normal" if recent_paths else "disabled")
            clear_recent_btn.configure(state="normal" if recent_paths else "disabled")

        recent_frame = ctk.CTkFrame(modal, corner_radius=6)
        recent_frame.pack(fill="x", padx=20, pady=(0, 10))
        self.register_theme_widget(recent_frame, fg_color="subtle_panel")
        ctk.CTkLabel(
            recent_frame, text=_("recent_workspaces"),
            font=ctk.CTkFont(family="Open Sans", size=13, weight="bold")
        ).pack(anchor="w", padx=12, pady=(10, 4))

        recent_row = ctk.CTkFrame(recent_frame, fg_color="transparent")
        recent_row.pack(fill="x", padx=12, pady=(0, 10))
        recent_menu = ctk.CTkOptionMenu(recent_row, variable=recent_var, values=[_("recent_empty")])
        recent_menu.pack(side="left", fill="x", expand=True, padx=(0, 6))
        ToolTip(recent_menu, lambda: recent_display_map.get(recent_var.get(), _("tooltip_recent_empty")))

        def on_load_recent():
            path = recent_display_map.get(recent_var.get())
            if not path:
                return
            self._do_import_workspace(path, parent=modal)
            refresh_recent_dropdown()

        load_recent_btn = ctk.CTkButton(recent_row, text=_("load_recent"), width=80, command=on_load_recent)
        load_recent_btn.pack(side="left", padx=(0, 6))
        ToolTip(load_recent_btn, lambda: _("tooltip_recent_load") if recent_paths else _("tooltip_recent_empty"))

        def on_clear_recent():
            if show_confirmation(modal, _("warning"), _("recent_clear_confirm")):
                self.config.clear_recent_workspaces()
                refresh_recent_dropdown()

        clear_recent_btn = ctk.CTkButton(
            recent_row, text=_("clear_recent"), width=90,
            fg_color="gray40", hover_color="gray30", command=on_clear_recent
        )
        clear_recent_btn.pack(side="left")
        ToolTip(clear_recent_btn, _("tooltip_recent_clear"))

        # Import/Export frame
        btn_frame = ctk.CTkFrame(modal, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=10)

        import_btn = ctk.CTkButton(
            btn_frame,
            text=_("import_ws"),
            image=self.icon_import_img,
            compound="left",
            command=lambda: (self.import_workspace(parent=modal), refresh_recent_dropdown())
        )
        import_btn.pack(side="left", expand=True, padx=(0, 5))
        ToolTip(import_btn, _("tooltip_import_workspace"))
        export_btn = ctk.CTkButton(
            btn_frame,
            text=_("export_ws"),
            image=self.icon_export_img,
            compound="left",
            command=lambda: (self.export_workspace(parent=modal), refresh_recent_dropdown())
        )
        export_btn.pack(side="right", expand=True, padx=(5, 0))
        ToolTip(export_btn, _("tooltip_export_workspace"))

        ctk.CTkFrame(modal, height=2, fg_color="gray50").pack(fill="x", padx=20, pady=15)

        # Generate Frame
        ctk.CTkLabel(modal, text=_("workspace_generate"), font=ctk.CTkFont(family="Open Sans", size=14, weight="bold")).pack(pady=(0, 5))
        ctk.CTkLabel(modal, text=_("generate_ws_desc"), wraplength=450, text_color="gray70").pack(pady=(0, 10))

        text_input = ctk.CTkTextbox(modal, height=130)
        text_input.pack(fill="both", expand=True, padx=20, pady=(0, 5))

        # --- NEW: Toolbar Mini (Format & Clean, Clear All) ---
        toolbar_frame = ctk.CTkFrame(modal, fg_color="transparent")
        toolbar_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        def on_format_clean():
            raw_text = text_input.get("1.0", tk.END)
            from src.utils.helpers import parse_raw_repo_text
            cleaned_paths = parse_raw_repo_text(raw_text)
            text_input.delete("1.0", tk.END)
            text_input.insert("1.0", "\n".join(sorted(cleaned_paths)))
            
        def on_clear_all():
            text_input.delete("1.0", tk.END)

        def on_import_file():
            file_path = filedialog.askopenfilename(
                parent=modal,
                title=_("import_from_file"),
                filetypes=[
                    (_("import_file_types"), "*.txt *.csv *.xlsx"),
                    ("All Files", "*.*")
                ]
            )
            if not file_path:
                return
            
            ext = os.path.splitext(file_path)[1].lower()
            items = []
            try:
                if ext == ".txt":
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        items = [line.strip() for line in f if line.strip()]
                elif ext == ".csv":
                    import csv
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        reader = csv.reader(f)
                        for row in reader:
                            items.extend([cell.strip() for cell in row if cell.strip()])
                elif ext == ".xlsx":
                    try:
                        import openpyxl
                        wb = openpyxl.load_workbook(file_path, data_only=True)
                        for sheet in wb.worksheets:
                            for row in sheet.iter_rows(values_only=True):
                                for cell in row:
                                    if cell and str(cell).strip():
                                        items.append(str(cell).strip())
                    except ImportError:
                        show_error(modal, _("error"), _("import_err_openpyxl"))
                        return
                
                if items:
                    current_text = text_input.get("1.0", tk.END).strip()
                    new_content = "\n".join(items)
                    if current_text:
                        text_input.insert(tk.END, "\n" + new_content)
                    else:
                        text_input.insert("1.0", new_content)
                    show_info(modal, _("done_title"), _("import_success", count=len(items)))
            except Exception as e:
                show_error(modal, _("error"), str(e))
            
        ctk.CTkButton(
            toolbar_frame, text=_("format_clean_btn"), width=110, height=28,
            font=ctk.CTkFont(family="Open Sans", size=10),
            command=on_format_clean
        ).pack(side="left")
        ToolTip(toolbar_frame.winfo_children()[-1], _("tooltip_format_clean"))

        import_file_btn = ctk.CTkButton(
            toolbar_frame, text=_("import_from_file"), width=110, height=28,
            font=ctk.CTkFont(family="Open Sans", size=10), fg_color="#27ae60", hover_color="#2ecc71",
            command=on_import_file
        )
        import_file_btn.pack(side="left", padx=5)
        ToolTip(import_file_btn, _("tooltip_import_file"))
        
        clear_all_btn = ctk.CTkButton(
            toolbar_frame, text=_("clear_all_btn"), width=100, height=28,
            font=ctk.CTkFont(family="Open Sans", size=10), fg_color="#e74c3c", hover_color="#c0392b",
            command=on_clear_all
        )
        clear_all_btn.pack(side="right")
        ToolTip(clear_all_btn, _("tooltip_clear_all"))

        # --- NEW: Find & Replace Frame ---
        fr_frame = ctk.CTkFrame(modal, corner_radius=6)
        fr_frame.pack(fill="x", padx=20, pady=(0, 10))
        self.register_theme_widget(fr_frame, fg_color="subtle_panel")
        
        # Row 1: Find
        f_row = ctk.CTkFrame(fr_frame, fg_color="transparent")
        f_row.pack(fill="x", padx=10, pady=(10, 5))
        find_lbl = ctk.CTkLabel(f_row, text=_("find_lbl"), width=80, anchor="w")
        find_lbl.pack(side="left")
        self.register_theme_widget(find_lbl, text_color="text")
        find_entry = ctk.CTkEntry(f_row, height=28)
        find_entry.pack(side="left", fill="x", expand=True)
        
        # Row 2: Replace
        r_row = ctk.CTkFrame(fr_frame, fg_color="transparent")
        r_row.pack(fill="x", padx=10, pady=(0, 10))
        replace_lbl = ctk.CTkLabel(r_row, text=_("replace_lbl"), width=80, anchor="w")
        replace_lbl.pack(side="left")
        self.register_theme_widget(replace_lbl, text_color="text")
        replace_entry = ctk.CTkEntry(r_row, height=28)
        replace_entry.pack(side="left", fill="x", expand=True)
        
        def on_replace_all():
            find_text = find_entry.get()
            replace_text = replace_entry.get()
            if not find_text:
                return
            current_text = text_input.get("1.0", tk.END)
            new_text = current_text.replace(find_text, replace_text)
            text_input.delete("1.0", tk.END)
            text_input.insert("1.0", new_text)
            
        replace_btn = ctk.CTkButton(
            r_row, text=_("replace_btn"), width=100, height=28,
            command=on_replace_all
        )
        replace_btn.pack(side="left", padx=(10, 0))
        ToolTip(replace_btn, _("tooltip_replace_all"))

        status_label = ctk.CTkLabel(modal, text="", text_color="gray70")
        status_label.pack(pady=(0, 8))

        generate_btn = None

        def set_generating(is_generating):
            state = "disabled" if is_generating else "normal"
            text_input.configure(state=state)
            find_entry.configure(state=state)
            replace_entry.configure(state=state)
            if generate_btn is not None:
                generate_btn.configure(state=state)
            status_label.configure(text=_("generate_validating") if is_generating else "")

        def on_generate():
            raw_text = text_input.get("1.0", tk.END)
            total_lines = len([line for line in raw_text.splitlines() if line.strip()])
            
            from src.utils.helpers import parse_raw_repo_text
            cleaned_paths = parse_raw_repo_text(raw_text)
            
            if not cleaned_paths:
                show_error(modal, _("error"), _("generate_error_empty"))
                return

            set_generating(True)
            
            def _validate():
                try:
                    from src.core.gitlab_api import GitLabAPI
                    api = GitLabAPI(self.gitlab_url, self.api_token)
                    
                    self.write_log(_("generate_validating"))
                    valid, invalid = api.validate_projects(cleaned_paths)
                    self.schedule_ui(lambda: self._on_validation_complete(valid, invalid, total_lines, modal, set_generating))
                except Exception as e:
                    def _show_validation_error(err=e):
                        if modal.winfo_exists():
                            set_generating(False)
                            show_error(modal, _("error"), str(err))
                    self.schedule_ui(_show_validation_error)

            thread = threading.Thread(target=_validate)
            thread.daemon = True
            thread.start()

        generate_btn = ctk.CTkButton(modal, text=_("generate_btn"), height=36, font=ctk.CTkFont(family="Open Sans", weight="bold"), command=on_generate)
        generate_btn.pack(pady=(0, 20))
        ToolTip(generate_btn, _("tooltip_generate_workspace"))
        def focus_find_shortcut(event=None):
            find_entry.focus_set()
            return "break"

        def generate_shortcut(event=None):
            if str(generate_btn.cget("state")) != "disabled":
                on_generate()
            return "break"

        for sequence in self.shortcut_variants(self.get_shortcut_sequence("find")):
            modal.bind(sequence, focus_find_shortcut)
        for sequence in self.shortcut_variants(self.get_shortcut_sequence("primary_action")):
            modal.bind(sequence, generate_shortcut)
        refresh_recent_dropdown()

    def _on_validation_complete(self, valid, invalid, total_lines, modal, set_generating=None):
        if not modal.winfo_exists():
            return

        if set_generating is not None:
            set_generating(False)
        
        if not valid:
            show_error(modal, _("error"), _("generate_error_empty") + _("invalid_formats_count", count=len(invalid)))
            return
            
        # Validation Preview Dialog
        msg = _("ws_preview_msg", valid=len(valid), invalid=len(invalid))
        proceed = show_custom_message(modal, _("ws_preview_title"), msg, icon_type="info", is_confirmation=True)
        if not proceed:
            return
            
        filepath = filedialog.asksaveasfilename(
            parent=modal,
            title=_("export_ws"), defaultextension=".json", filetypes=[("JSON Files", "*.json")]
        )
        if filepath:
            clean_data = {}
            for proj in valid:
                url = proj.get("http_url_to_repo", "")
                if url:
                    clean_data[url] = {
                        "name": proj.get("path_with_namespace", ""),
                        "id": proj.get("id", 0)
                    }
            try:
                with open(filepath, 'w') as f:
                    json.dump(clean_data, f, indent=4)
                self.config.add_recent_workspace(filepath)
                show_info(modal, _("ok"), _("generate_success", total=total_lines, unique=len(valid)))
                if modal.winfo_exists():
                    modal.destroy()
                self.workspace_tools_modal = None
                
                self._do_import_workspace(filepath)
            except Exception as e:
                show_error(modal, _("error"), _("failed_with_err", err=e))

    def export_workspace(self, parent=None):
        dialog_parent = parent or self
        if not self.selected_repos:
            self.update_selection_action_buttons()
            show_warning(dialog_parent, _("warning"), _("at_least_one"))
            return
            
        filepath = filedialog.asksaveasfilename(
            parent=dialog_parent,
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
                self.config.add_recent_workspace(filepath)
                show_info(dialog_parent, _("ok"), _("ws_exported", file=filepath))
            except Exception as e:
                show_error(dialog_parent, _("error"), _("failed_with_err", err=e))

    def import_workspace(self, parent=None):
        dialog_parent = parent or self
        filepath = filedialog.askopenfilename(
            parent=dialog_parent,
            title=_("import_ws"), filetypes=[("JSON Files", "*.json")]
        )
        if filepath:
            self._do_import_workspace(filepath, parent=dialog_parent)

    def _do_import_workspace(self, filepath, parent=None):
        dialog_parent = parent or self
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)

            if not isinstance(data, dict):
                show_error(dialog_parent, _("error"), _("ws_import_err"))
                return
            self.config.add_recent_workspace(filepath)

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
            show_info(dialog_parent, _("ok"), _("ws_imported", count=count))
        except json.JSONDecodeError:
            show_error(dialog_parent, _("error"), _("ws_import_err"))
        except Exception as e:
            show_error(dialog_parent, _("error"), _("ws_import_err") + f"\n{e}")

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
        self.schedule_ui(_update)

    # =========================================================================
    # MODAL BRANCH SELECTION
    # =========================================================================
    def get_selected_repo_snapshot(self):
        """Snapshot selected repositories with the visible page order first."""
        snapshot = []
        seen_urls = set()

        for item in self.repo_items:
            url = item.get("url")
            var = item.get("var")
            is_checked = False
            try:
                is_checked = bool(var and var.get())
            except tk.TclError:
                is_checked = url in self.selected_repos

            if is_checked and url in self.selected_repos:
                snapshot.append((url, dict(self.selected_repos[url])))
                seen_urls.add(url)

        for url, info in self.selected_repos.items():
            if url not in seen_urls:
                snapshot.append((url, dict(info)))

        return snapshot

    def open_branch_selection_modal(self):
        dest_folder = self.dest_entry.get().strip()
        selected_repo_snapshot = self.get_selected_repo_snapshot()
        urls_to_clone = [url for url, _ in selected_repo_snapshot]

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

        # --- Bulk Apply Row ---
        bulk_row = ctk.CTkFrame(modal, fg_color="#f0f3f4", corner_radius=6)
        bulk_row.pack(fill="x", padx=24, pady=(2, 6))
        bulk_row.columnconfigure(0, minsize=COL_WIDTHS[0])
        bulk_row.columnconfigure(1, minsize=COL_WIDTHS[1])
        bulk_row.columnconfigure(2, minsize=COL_WIDTHS[2])
        bulk_row.columnconfigure(3, minsize=COL_WIDTHS[3])
        
        ctk.CTkLabel(bulk_row, text=_("bulk_apply"), font=ctk.CTkFont(family="Open Sans", size=12, weight="bold"), text_color="#2c3e50").grid(row=0, column=0, sticky="e", padx=(4, 15), pady=8)
        
        bulk_branch_var = ctk.StringVar(value="")
        bulk_combo = ctk.CTkEntry(bulk_row, textvariable=bulk_branch_var, width=185, placeholder_text=_("type_branch"))
        bulk_combo.grid(row=0, column=1, sticky="w")
        
        bulk_new_enabled = tk.BooleanVar(value=False)
        bulk_cb = ctk.CTkCheckBox(bulk_row, text="", variable=bulk_new_enabled, width=20)
        bulk_cb.grid(row=0, column=2, sticky="w", padx=30)
        
        bulk_new_name_var = tk.StringVar(value="")
        bulk_entry = ctk.CTkEntry(bulk_row, textvariable=bulk_new_name_var, width=COL_WIDTHS[3], height=28, placeholder_text=_("placeholder_new_branch"), state="disabled")
        bulk_entry.grid(row=0, column=3, sticky="we", padx=(0, 4))
        
        def on_bulk_cb_toggle():
            if bulk_new_enabled.get():
                bulk_entry.configure(state="normal")
            else:
                bulk_entry.configure(state="disabled")
                bulk_new_name_var.set("")
            
            # Apply to all
            for _, data in selected_repo_snapshot:
                if "new_branch_enabled" in data:
                    data["new_branch_enabled"].set(bulk_new_enabled.get())
                    # The trace on data["new_branch_enabled"] will handle disabling/enabling its entry
        
        bulk_cb.configure(command=on_bulk_cb_toggle)
        
        def on_bulk_branch_write(*args):
            val = bulk_branch_var.get()
            if val:
                for _, data in selected_repo_snapshot:
                    if "selected_branch_var" in data:
                        # Only apply if it's available or we force it? Let's force it for power users
                        data["selected_branch_var"].set(val)
        
        def on_bulk_name_write(*args):
            val = bulk_new_name_var.get()
            for _, data in selected_repo_snapshot:
                if "new_branch_name_var" in data and data.get("new_branch_enabled", tk.BooleanVar()).get():
                    data["new_branch_name_var"].set(val)
                    
        bulk_branch_var.trace_add("write", on_bulk_branch_write)
        bulk_new_name_var.trace_add("write", on_bulk_name_write)

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
            command=lambda: self.execute_clone_from_modal(modal, selected_repo_snapshot)
        )
        action_btn.pack(side="right")

        def start_clone_shortcut(event=None):
            if str(action_btn.cget("state")) != "disabled":
                self.execute_clone_from_modal(modal, selected_repo_snapshot)
            return "break"

        for sequence in self.shortcut_variants(self.get_shortcut_sequence("primary_action")):
            modal.bind(sequence, start_clone_shortcut)

        thread = threading.Thread(
            target=self.fetch_branches_logic,
            args=(modal, scroll_frame, action_btn, loading_lbl, selected_repo_snapshot)
        )
        thread.daemon = True
        thread.start()

    def fetch_branches_logic(self, modal, scroll_frame, action_btn, loading_lbl, selected_repo_snapshot):
        headers = {"PRIVATE-TOKEN": self.api_token}

        for url, data in selected_repo_snapshot:
            if not modal.winfo_exists():
                return

            project_id = data["id"]
            try:
                branches = []
                page = 1
                while True:
                    api_url = f"{self.gitlab_url}/api/v4/projects/{project_id}/repository/branches?per_page=100&page={page}"
                    response = requests.get(api_url, headers=headers, timeout=15)
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

        self.schedule_ui(lambda: self.render_branch_rows(modal, scroll_frame, action_btn, loading_lbl, selected_repo_snapshot))

    def render_branch_rows(self, modal, scroll_frame, action_btn, loading_lbl, selected_repo_snapshot):
        if not (modal.winfo_exists() and scroll_frame.winfo_exists() and action_btn.winfo_exists()):
            return

        if loading_lbl.winfo_exists():
            loading_lbl.destroy()
        action_btn.configure(state="normal")

        # MUST match COL_WIDTHS in open_branch_config_modal header
        C0, C1, C2, C3 = 260, 200, 90, 165

        for url, data in selected_repo_snapshot:
            row = ctk.CTkFrame(scroll_frame, corner_radius=8)
            row.pack(fill="x", pady=3, padx=4)

            # Mirror the exact same columnconfigure as the header
            row.columnconfigure(0, minsize=C0)
            row.columnconfigure(1, minsize=C1)
            row.columnconfigure(2, minsize=C2)
            row.columnconfigure(3, minsize=C3)

            # --- Col 0: Repo name (truncated label + tooltip) ---
            from src.utils.helpers import middle_truncate
            name = data["name"]
            
            lbl = ctk.CTkLabel(
                row, font=ctk.CTkFont(family="Open Sans", size=12, weight="bold"),
                text=middle_truncate(name, 35), anchor="w", text_color=("gray20", "gray85")
            )
            lbl.grid(row=0, column=0, sticky="we", padx=(10, 4), pady=8)
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
                placeholder_text=_("placeholder_branch_name"),
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
    def execute_clone_from_modal(self, modal, selected_repo_snapshot):
        # 1. Validation for New Branch Name
        clone_jobs = []
        for url, data in selected_repo_snapshot:
            branch_var = data.get("selected_branch_var")
            branch_name = branch_var.get().strip() if branch_var else "main"
            new_branch_enabled = data.get("new_branch_enabled")
            new_branch_name_var = data.get("new_branch_name_var")
            create_new_branch = bool(new_branch_enabled and new_branch_enabled.get())
            new_b_name = new_branch_name_var.get().strip() if new_branch_name_var else ""

            if create_new_branch:
                if not new_b_name:
                    repo_name = data.get("name", "Unknown")
                    show_error(modal, _("error"), _("new_branch_empty_err", repo_name=repo_name))
                    return

            clone_jobs.append({
                "url": url,
                "repo_name": data.get("name", url.rstrip("/").split("/")[-1]),
                "branch_name": branch_name or "main",
                "create_new_branch": create_new_branch,
                "new_branch_name": new_b_name,
            })

        # 2. Disk Space Check
        dest_folder = self.dest_entry.get().strip()
        min_disk_gb = self.config.get_min_disk_space_gb()
        try:
            total, used, free = shutil.disk_usage(dest_folder)
            free_gb = free / (1024**3)
            if free_gb < min_disk_gb:
                proceed = show_confirmation(
                    modal,
                    _("warning"),
                    _("disk_space_warning", free_gb=free_gb, min_disk_gb=min_disk_gb)
                )
                if not proceed:
                    return
        except Exception as e:
            logger.warning(f"Failed to check disk space: {e}")

        modal.destroy()
        
        self.cancel_event = threading.Event()
        self.clone_btn.configure(text=_("cancel"), fg_color="#c0392b", hover_color="#922b21", command=self.cancel_cloning)
        
        self.log_content = ""
        if self.log_window and self.log_window.winfo_exists() and hasattr(self.log_window, 'textbox'):
            self.log_window.textbox.configure(state="normal")
            self.log_window.textbox.delete("1.0", "end")
            self.log_window.textbox.configure(state="disabled")

        if not shutil.which("git"):
            self.write_log(_("git_not_found_log"))
            self.clone_btn.configure(state="normal", text=_("step3_btn"), fg_color="#1a7f37", hover_color="#15692f", command=self.open_branch_selection_modal)
            return

        self.write_log(_("start_clone_process", count=len(clone_jobs)))

        thread = threading.Thread(target=self.run_multiple_clones, args=(clone_jobs, dest_folder))
        thread.daemon = True
        thread.start()

    def cancel_cloning(self):
        self.write_log(_("cancel_signal"))
        self.cancel_event.set()
        self.clone_btn.configure(state="disabled", text=_("canceling"))

    def run_multiple_clones(self, clone_jobs, dest_folder):
        self.sukses = 0
        self.gagal = 0
        self.processed_count = 0
        self.total_repos = len(clone_jobs)
        self.cloned_paths = []  # Track successfully cloned/updated repos
        self.lock = threading.Lock()
        
        clone_method = self.config.get_clone_method()

        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_CONCURRENT_CLONES) as executor:
            futures = [executor.submit(self._process_single_repo, job, dest_folder, clone_method) for job in clone_jobs]
            concurrent.futures.wait(futures)

        self.write_log(f"\n{'=' * 50}")
        self.write_log(_("process_finished", success=self.sukses, failed=self.gagal))
        self.write_log(f"{'=' * 50}")

        self.schedule_ui(lambda: self.clone_btn.configure(
            state="normal",
            text=_("step3_btn"),
            fg_color="#1a7f37",
            hover_color="#15692f",
            command=self.open_branch_selection_modal
        ))
        cloned = list(self.cloned_paths)
        self.schedule_ui(lambda: self.show_clone_result_dialog(cloned))

    def _process_single_repo(self, clone_job, dest_folder, clone_method):
        if hasattr(self, 'cancel_event') and self.cancel_event.is_set():
            return
            
        with self.lock:
            self.processed_count += 1
            current_idx = self.processed_count
            
        url = clone_job["url"]
        repo_name = clone_job["repo_name"]
        branch_name = clone_job["branch_name"]
        create_new_branch = clone_job["create_new_branch"]
        new_branch_name = clone_job["new_branch_name"]

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
            self.write_log(f"\n[{current_idx}/{self.total_repos}] {_('pulling')} ({repo_name})")

            # Setup creationflags for Windows to hide the terminal
            creationflags = 0
            if os.name == 'nt' or sys.platform == 'win32':
                creationflags = 0x08000000  # CREATE_NO_WINDOW

            # Simpan original remote URL, lalu set ke auth_url agar pull bisa autentikasi
            original_remote_url = None
            try:
                result = subprocess.run(
                    ["git", "remote", "get-url", "origin"],
                    cwd=repo_local_path, capture_output=True, text=True, env=git_env, creationflags=creationflags
                )
                if result.returncode == 0:
                    original_remote_url = result.stdout.strip()

                subprocess.run(
                    ["git", "remote", "set-url", "origin", auth_url],
                    cwd=repo_local_path, capture_output=True, text=True, env=git_env, creationflags=creationflags
                )
            except Exception as e:
                self.write_log(_("fail_set_remote", err=str(e)))

            success = False
            for i in range(1, MAX_RETRY_ATTEMPTS + 1):
                try:
                    process = subprocess.Popen(
                        ["git", "-c", "credential.helper=", "pull", "origin", branch_name],
                        cwd=repo_local_path,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True, bufsize=1, universal_newlines=True,
                        env=git_env, creationflags=creationflags
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
                        self.write_log(_("pull_failed_retry", retry_msg=_('retrying', i=i)))
                        time.sleep(RETRY_DELAY_SECONDS)
                except Exception as e:
                    if isinstance(e, FileNotFoundError) or (hasattr(e, 'winerror') and e.winerror == 2):
                        self.write_log(_("git_not_found_log"))
                    else:
                        self.write_log(_("error_on_repo", repo_name=repo_name, err=str(e)))
                    time.sleep(RETRY_DELAY_SECONDS)

            # Kembalikan remote URL asli agar token tidak tersimpan di .git/config
            if original_remote_url:
                try:
                    subprocess.run(
                        ["git", "remote", "set-url", "origin", original_remote_url],
                        cwd=repo_local_path, capture_output=True, text=True, env=git_env, creationflags=creationflags
                    )
                except Exception:
                    pass
            
            if success:
                self.write_log(_("repo_update_success", repo_name=repo_name, branch_name=branch_name))
                with self.lock:
                    self.sukses += 1
                    self.cloned_paths.append((repo_name, repo_local_path))

                # --- Buat branch baru jika diminta (saat pull) ---
                if create_new_branch and new_branch_name:
                    self.write_log(_("create_new_branch_log", new_branch_name=new_branch_name))
                    try:
                        cb_proc = subprocess.run(
                            ["git", "checkout", "-b", new_branch_name],
                            cwd=repo_local_path,
                            capture_output=True, text=True,
                            env=git_env, creationflags=creationflags
                        )
                        if cb_proc.returncode == 0:
                            self.write_log(_("branch_create_success", new_branch_name=new_branch_name))
                        else:
                            self.write_log(_("branch_create_failed", err=cb_proc.stderr.strip()))
                    except Exception as exc:
                        if isinstance(exc, FileNotFoundError) or (hasattr(exc, 'winerror') and exc.winerror == 2):
                            self.write_log(_("git_not_found_log"))
                        else:
                            self.write_log(_("branch_create_error", err=str(exc)))
                elif create_new_branch and not new_branch_name:
                    self.write_log(_("skip_empty_branch_name"))
            else:
                self.write_log(_("repo_update_failed", repo_name=repo_name))
                with self.lock:
                    self.gagal += 1
        else:
            self.write_log(f"\n[{current_idx}/{self.total_repos}] {_('cloning_repo', repo_name=repo_name, branch_name=branch_name)}")
            clone_command = ["git", "-c", "credential.helper=", "clone", "-b", branch_name, auth_url]
            success = False
            
            # Setup creationflags for Windows to hide the terminal
            creationflags = 0
            if os.name == 'nt' or sys.platform == 'win32':
                creationflags = 0x08000000  # CREATE_NO_WINDOW
            for i in range(1, MAX_RETRY_ATTEMPTS + 1):
                try:
                    process = subprocess.Popen(
                        clone_command,
                        cwd=dest_folder,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True, bufsize=1, universal_newlines=True,
                        env=git_env, creationflags=creationflags
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
                        self.write_log(_("clone_failed_retry", retry_msg=_('retrying', i=i)))
                        time.sleep(RETRY_DELAY_SECONDS)
                except Exception as e:
                    if isinstance(e, FileNotFoundError) or (hasattr(e, 'winerror') and e.winerror == 2):
                        self.write_log(_("git_not_found_log"))
                    else:
                        self.write_log(_("error_on_repo", repo_name=repo_name, err=str(e)))
                    time.sleep(RETRY_DELAY_SECONDS)

            if success:
                self.write_log(_("repo_clone_success", repo_name=repo_name, branch_name=branch_name))
                with self.lock:
                    self.sukses += 1
                    self.cloned_paths.append((repo_name, repo_local_path))

                # --- Set git config local ---
                self._set_git_config_local(repo_local_path, repo_name)

                # --- Buat branch baru jika diminta ---
                if create_new_branch and new_branch_name:
                    self.write_log(_("create_new_branch_log", new_branch_name=new_branch_name))
                    try:
                        cb_proc = subprocess.run(
                            ["git", "checkout", "-b", new_branch_name],
                            cwd=repo_local_path,
                            capture_output=True, text=True,
                            env=git_env, creationflags=creationflags
                        )
                        if cb_proc.returncode == 0:
                            self.write_log(_("branch_create_success", new_branch_name=new_branch_name))
                        else:
                            self.write_log(_("branch_create_failed", err=cb_proc.stderr.strip()))
                    except Exception as exc:
                        if isinstance(exc, FileNotFoundError) or (hasattr(exc, 'winerror') and exc.winerror == 2):
                            self.write_log(_("git_not_found_log"))
                        else:
                            self.write_log(_("branch_create_error", err=str(exc)))
                elif create_new_branch and not new_branch_name:
                    self.write_log(_("skip_empty_branch_name"))

            else:
                self.write_log(_("repo_clone_failed", repo_name=repo_name))
                with self.lock:
                    self.gagal += 1

    def _set_git_config_local(self, repo_path: str, repo_name: str):
        """Set git config user.name dan user.email secara local di repo yang baru di-clone."""
        if not os.path.isdir(repo_path):
            self.write_log(_("repo_dir_not_found"))
            return

        configs = []
        if self.user_name:
            configs.append(("user.name", self.user_name))
        if self.user_email:
            configs.append(("user.email", self.user_email))
        # Disable credential helper secara local agar tidak mengganggu token VS Code/Visual Studio
        configs.append(("credential.helper", ""))

        if not configs:
            self.write_log(_("gitlab_user_data_unavailable"))
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
                    self.write_log(_("fail_set_git_config", key=key, err=result.stderr.strip()))
            except Exception as exc:
                self.write_log(_("fail_set_git_config", key=key, err=exc))

    # =========================================================================
    # IDE DETECTION & OPEN IN IDE
    # =========================================================================
    def detect_available_ides(self):
        """Detect popular IDEs from registry, PATH, and common install paths."""
        found = []
        seen_cmds = set()

        def add_ide(name, command, kind, source):
            if not command:
                return
            if command != "__explorer__" and not os.path.isfile(command):
                return
            key = os.path.normcase(command)
            if key in seen_cmds:
                return
            seen_cmds.add(key)
            found.append({
                "name": name,
                "command": command,
                "kind": kind,
                "source": source,
            })

        def infer_ide(display_name, exe_path, source):
            haystack = f"{display_name} {exe_path}".lower()
            if "cursor" in haystack:
                add_ide("Cursor", exe_path, "cursor", source)
            elif "code.exe" in haystack or "visual studio code" in haystack or "vs code" in haystack:
                add_ide("Visual Studio Code", exe_path, "vscode", source)
            elif "devenv.exe" in haystack or "visual studio" in haystack:
                add_ide("Visual Studio", exe_path, "visual_studio", source)

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

                                if os.path.isfile(exe_path):
                                    infer_ide(display_name, exe_path, "registry")
                            except OSError:
                                pass
                    finally:
                        winreg.CloseKey(shell_key)

        for name, command_name, kind in (
            ("Visual Studio Code", "code", "vscode"),
            ("Cursor", "cursor", "cursor"),
        ):
            path = shutil.which(command_name)
            if path:
                add_ide(name, path, kind, "path")

        if sys.platform == "win32":
            local_app_data = os.environ.get("LOCALAPPDATA", "")
            program_files = [os.environ.get("ProgramFiles", ""), os.environ.get("ProgramFiles(x86)", "")]
            common_paths = [
                ("Visual Studio Code", os.path.join(local_app_data, "Programs", "Microsoft VS Code", "Code.exe"), "vscode"),
                ("Cursor", os.path.join(local_app_data, "Programs", "Cursor", "Cursor.exe"), "cursor"),
            ]
            for base in program_files:
                if not base:
                    continue
                common_paths.extend([
                    ("Visual Studio Code", os.path.join(base, "Microsoft VS Code", "Code.exe"), "vscode"),
                    ("Cursor", os.path.join(base, "Cursor", "Cursor.exe"), "cursor"),
                ])
                vs_root = os.path.join(base, "Microsoft Visual Studio")
                if os.path.isdir(vs_root):
                    for root, _dirs, files in os.walk(vs_root):
                        if "devenv.exe" in files:
                            common_paths.append(("Visual Studio", os.path.join(root, "devenv.exe"), "visual_studio"))
                            break
            for name, path, kind in common_paths:
                add_ide(name, path, kind, "common_path")

        add_ide(_("open_in_explorer"), "__explorer__", "explorer", "fallback")

        return found

    def detect_project_profile(self, repo_path):
        profile = {"kind": "generic", "markers": [], "primary_target": repo_path}
        marker_map = [
            ("visual_studio_solution", "*.sln"),
            ("dotnet_project", "*.csproj"),
            ("node", "package.json"),
            ("python", "requirements.txt"),
            ("python", "pyproject.toml"),
            ("java_maven", "pom.xml"),
            ("java_gradle", "build.gradle"),
            ("java_gradle", "build.gradle.kts"),
        ]
        try:
            entries = os.listdir(repo_path)
        except Exception:
            return profile

        for kind, marker in marker_map:
            matched = []
            if marker.startswith("*."):
                suffix = marker[1:].lower()
                matched = [name for name in entries if name.lower().endswith(suffix)]
            elif marker in entries:
                matched = [marker]
            if matched:
                profile["kind"] = kind
                profile["markers"].extend(matched)
                profile["primary_target"] = os.path.join(repo_path, matched[0])
                if kind == "visual_studio_solution":
                    break
        return profile

    def build_ide_command(self, ide, repo_path):
        ide_cmd = ide.get("command") if isinstance(ide, dict) else ide
        profile = self.detect_project_profile(repo_path)
        target_path = repo_path

        if isinstance(ide, dict) and ide.get("kind") == "visual_studio":
            if profile["kind"] in ("visual_studio_solution", "dotnet_project"):
                target_path = profile["primary_target"]
        elif isinstance(ide, dict) and ide.get("kind") in ("vscode", "cursor"):
            target_path = repo_path
            return [ide_cmd, "--reuse-window", target_path]
        else:
            target_path = repo_path

        return [ide_cmd, target_path]

    def open_in_ide(self, ide, repo_path):
        """Open a repository folder in the specified IDE or File Explorer."""
        ide_cmd = ide.get("command") if isinstance(ide, dict) else ide
        ide_name = ide.get("name", ide_cmd) if isinstance(ide, dict) else ide_cmd
        try:
            if ide_cmd == "__explorer__":
                if sys.platform == "win32":
                    os.startfile(repo_path)
                elif sys.platform == "darwin":
                    subprocess.Popen(["open", repo_path])
                else:
                    subprocess.Popen(["xdg-open", repo_path])
            elif sys.platform == "win32":
                subprocess.Popen(self.build_ide_command(ide, repo_path), creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)
            else:
                subprocess.Popen(self.build_ide_command(ide, repo_path))
        except Exception as e:
            show_error(self, _("error"), _("open_ide_failed", ide=ide_name, error=str(e)))

    def show_clone_result_dialog(self, cloned_paths):
        """Show clone results with option to open repos in IDE."""
        available_ides = self.detect_available_ides()

        modal = ctk.CTkToplevel(self)
        modal.title(_("done_title"))

        has_repos = bool(cloned_paths)
        dialog_height = 520 if has_repos else 280
        self.configure_modal_window(modal, 680, dialog_height)

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
                abs_repo_path = os.path.abspath(repo_path)
                row = ctk.CTkFrame(repo_scroll, corner_radius=6)
                row.pack(fill="x", pady=4, padx=2)
                self.register_theme_widget(row, fg_color="subtle_panel")

                info_frame = ctk.CTkFrame(row, fg_color="transparent")
                info_frame.pack(side="left", fill="x", expand=True, padx=(10, 8), pady=7)

                ctk.CTkLabel(
                    info_frame, text=repo_name,
                    font=ctk.CTkFont(family="Open Sans", size=12, weight="bold"),
                    anchor="w"
                ).pack(fill="x", anchor="w")
                from src.utils.helpers import middle_truncate
                path_label = ctk.CTkLabel(
                    info_frame, text=middle_truncate(abs_repo_path, 72),
                    font=ctk.CTkFont(family="Open Sans", size=10),
                    anchor="w", text_color="gray"
                )
                path_label.pack(fill="x", anchor="w")
                ToolTip(path_label, abs_repo_path)

                copy_tooltip_text = {"value": _("tooltip_copy_path")}
                copy_btn = ctk.CTkButton(
                    row, text=_("copy_path_btn"), width=72, height=30,
                    fg_color="gray40", hover_color="gray30",
                    font=ctk.CTkFont(family="Open Sans", size=11),
                )
                copy_btn.pack(side="right", padx=(0, 6))
                copy_tooltip = ToolTip(copy_btn, lambda ref=copy_tooltip_text: ref["value"])

                def make_copy_handler(btn, tooltip_ref, path):
                    def handler():
                        self.clipboard_clear()
                        self.clipboard_append(path)
                        btn.configure(text=_("copied_btn"))
                        tooltip_ref["value"] = _("path_copied")
                        btn.after(1400, lambda: (
                            btn.winfo_exists() and btn.configure(text=_("copy_path_btn")),
                            tooltip_ref.update({"value": _("tooltip_copy_path")})
                        ))
                    return handler

                copy_btn.configure(command=make_copy_handler(copy_btn, copy_tooltip_text, abs_repo_path))

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
                ToolTip(open_btn, _("tooltip_open_ide_menu"))

                def make_menu_handler(btn, path):
                    def handler():
                        menu = tk.Menu(btn, tearoff=0)
                        for ide in available_ides:
                            menu.add_command(
                                label=ide["name"],
                                command=lambda c=ide, p=path: self.open_in_ide(c, p)
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
        btn_frame.pack(fill="x", padx=20, pady=(0, 16))
        
        def export_log():
            filepath = filedialog.asksaveasfilename(
                parent=modal,
                title=_("export_log_btn"), defaultextension=".txt", filetypes=[("Text Files", "*.txt")]
            )
            if filepath:
                try:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(self.log_content)
                    show_info(modal, _("ok"), _("log_exported_success"))
                except Exception as e:
                    show_error(modal, _("error"), _("failed_with_err", err=e))

        ctk.CTkButton(btn_frame, text=_("export_log_btn"), width=120, height=36, font=ctk.CTkFont(family="Open Sans", weight="bold"), fg_color="#2980b9", hover_color="#1f618d", command=export_log).pack(side="left", padx=5, expand=True)
        ctk.CTkButton(btn_frame, text=_("ok"), width=120, height=36, font=ctk.CTkFont(family="Open Sans", weight="bold"), command=modal.destroy).pack(side="right", padx=5, expand=True)


if __name__ == "__main__":
    app = GLRCApp()
    app.mainloop()
