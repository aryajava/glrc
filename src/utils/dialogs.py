"""
Dialog functions untuk GLRC Application
"""
import customtkinter as ctk
from src.utils.helpers import center_window
from src.utils.i18n import _

# Global set untuk tracking active message dialogs (mencegah duplikasi)
_active_messages = set()


def _resolve_app_window(widget):
    """Find the top-level app window from any child/modal widget."""
    current = widget
    while hasattr(current, "master") and current.master:
        current = current.master
    return current


def _apply_dialog_icon(dialog, parent):
    """Apply logo icon to message dialog when available."""
    app_window = _resolve_app_window(parent)

    try:
        icon_target = parent if hasattr(parent, "ico_path") else app_window
        if hasattr(icon_target, "ico_path") and icon_target.ico_path:
            dialog.iconbitmap(icon_target.ico_path)
    except Exception:
        pass

    try:
        photo_target = parent if hasattr(parent, "img_icon") else app_window
        if hasattr(photo_target, "img_icon") and photo_target.img_icon:
            dialog.iconphoto(True, photo_target.img_icon)
    except Exception:
        pass


def _activate_dialog(dialog):
    """Bring dialog to front consistently on Windows."""
    def clear_topmost():
        try:
            if dialog.winfo_exists():
                # Keep topmost if main app has always_on_top enabled
                app = _resolve_app_window(dialog)
                keep_top = False
                if hasattr(app, "config"):
                    try:
                        keep_top = app.config.get_window_state().get("always_on_top", False)
                    except Exception:
                        pass
                if not keep_top:
                    dialog.attributes("-topmost", False)
        except Exception:
            pass

    try:
        if hasattr(dialog, "deiconify"):
            dialog.deiconify()
        dialog.update_idletasks()
        dialog.lift()
        dialog.attributes("-topmost", True)
        dialog.after(250, clear_topmost)
        dialog.focus_force()
    except Exception:
        pass


def show_custom_message(parent, title, message, icon_type="info", is_confirmation=False):
    """Base function untuk menampilkan message box kustom dengan tema."""
    msg_key = f"{title}_{message}"
    if msg_key in _active_messages:
        return None
    _active_messages.add(msg_key)

    dialog = ctk.CTkToplevel(parent)
    dialog.title(title)
    dialog.withdraw() # Sembunyikan dulu sampai siap

    width, height = 400, 240
    center_window(dialog, width, height)
    dialog.resizable(False, False)

    # Styling colors
    is_dark = ctk.get_appearance_mode() == "Dark"
    bg_color = "#1e1e1e" if is_dark else "#f0f0f0"
    text_color = "white" if is_dark else "black"
    muted_text = "gray70" if is_dark else "gray30"

    frame = ctk.CTkFrame(dialog, fg_color="transparent")
    frame.pack(fill="both", expand=True, padx=20, pady=(20, 10))

    if icon_type == "info":
        color = "#3498db"
        icon_str = "ℹ"
    elif icon_type == "warning":
        color = "#e67e22"
        icon_str = "⚠"
    elif icon_type == "error":
        color = "#e74c3c"
        icon_str = "❌"
    elif icon_type == "success":
        color = "#2ecc71"
        icon_str = "✔"
    else:
        color = "#3498db"
        icon_str = "ℹ"

    # Top-center Icon
    icon_frame = ctk.CTkFrame(frame, width=50, height=50, corner_radius=25, fg_color=color)
    icon_frame.pack(pady=(0, 15))
    icon_frame.pack_propagate(False)
    ctk.CTkLabel(icon_frame, text=icon_str, text_color="white",
                 font=ctk.CTkFont(size=24, weight="bold")).pack(expand=True)

    msg_lbl = ctk.CTkLabel(frame, text=message, font=ctk.CTkFont(size=13),
                          justify="center", wraplength=340, text_color=muted_text)
    msg_lbl.pack(fill="x", expand=True)

    result = [None]

    def release_dialog_grab():
        try:
            if dialog.grab_current() == dialog:
                dialog.grab_release()
        except Exception:
            pass

    def on_close(val=None):
        release_dialog_grab()
        _active_messages.discard(msg_key)
        result[0] = val
        if dialog.winfo_exists():
            dialog.destroy()

    dialog.protocol("WM_DELETE_WINDOW", lambda: on_close(False))
    dialog.bind("<Escape>", lambda event: (on_close(False if is_confirmation else True), "break")[1])
    dialog.bind("<Destroy>", lambda event: release_dialog_grab(), add="+")

    btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
    btn_frame.pack(pady=(0, 20))

    if is_confirmation:
        ctk.CTkButton(btn_frame, text=_("cancel"), width=100, fg_color="gray40",
                     hover_color="gray30", command=lambda: on_close(False)).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text=_("ok"), width=100,
                     command=lambda: on_close(True)).pack(side="left", padx=10)
    else:
        ctk.CTkButton(btn_frame, text=_("ok"), width=120,
                     command=lambda: on_close(True)).pack()

    dialog.deiconify()
    _activate_dialog(dialog)
    dialog.after(200, lambda d=dialog: d.winfo_exists() and _apply_dialog_icon(d, parent))
    dialog.grab_set()
    dialog.wait_window()
    return result[0]


def show_confirmation(parent, title, message):
    """Menampilkan confirmation dialog dengan tombol Cancel/OK."""
    return show_custom_message(parent, title, message, icon_type="warning", is_confirmation=True)


def show_info(parent, title, message):
    """Menampilkan info dialog."""
    show_custom_message(parent, title, message, "info")


def show_warning(parent, title, message):
    """Menampilkan warning dialog."""
    show_custom_message(parent, title, message, "warning")


def show_error(parent, title, message):
    """Menampilkan error dialog."""
    show_custom_message(parent, title, message, "error")
