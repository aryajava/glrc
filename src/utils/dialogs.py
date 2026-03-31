"""
Dialog functions untuk GLRC Application
"""
import customtkinter as ctk
from src.utils.helpers import center_window

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
    try:
        dialog.wait_visibility()
    except Exception:
        pass

    try:
        dialog.lift()
        dialog.attributes("-topmost", True)
        dialog.after(150, lambda: dialog.attributes("-topmost", False))
        dialog.focus_force()
    except Exception:
        pass

def show_custom_message(parent, title, message, icon_type="info", is_confirmation=False):
    """
    Menampilkan custom message dialog.

    Args:
        parent: Parent window
        title: Dialog title
        message: Dialog message
        icon_type: Type of icon ("info", "warning", "error", "success")
        is_confirmation: Boolean, True jika dialog konfirmasi dengan tombol Cancel/OK

    Returns:
        True jika OK, False jika Cancel (untuk confirmation), True untuk message biasa
    """
    msg_key = (title, message)
    if msg_key in _active_messages:
        return None
    _active_messages.add(msg_key)

    dialog = ctk.CTkToplevel(parent)
    dialog.withdraw()  # Hide while configuring
    dialog.title(title)
    dialog.geometry("400x250")
    dialog.resizable(False, False)

    center_window(dialog, 400, 250)
    dialog.transient(parent)
    _apply_dialog_icon(dialog, parent)

    dialog.deiconify()  # Show fully configured
    _activate_dialog(dialog)
    # Single backup for CTkToplevel internal callbacks (~150ms)
    dialog.after(200, lambda: _apply_dialog_icon(dialog, parent))

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

    # Top-center Icon (Filled circle approximation via rounded frame + label)
    icon_frame = ctk.CTkFrame(frame, width=50, height=50, corner_radius=25, fg_color=color)
    icon_frame.pack(pady=(0, 15))
    icon_frame.pack_propagate(False)
    ctk.CTkLabel(icon_frame, text=icon_str, text_color="white",
                 font=ctk.CTkFont(size=24, weight="bold")).pack(expand=True)

    msg_lbl = ctk.CTkLabel(frame, text=message, font=ctk.CTkFont(size=13),
                          justify="center", wraplength=340)
    msg_lbl.pack(fill="x", expand=True)

    result = [None]

    def on_close(val=None):
        _active_messages.discard(msg_key)
        result[0] = val
        dialog.destroy()

    dialog.protocol("WM_DELETE_WINDOW", lambda: on_close(False))
    dialog.bind("<Escape>", lambda event: on_close(False if is_confirmation else True))

    btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
    btn_frame.pack(pady=(0, 20))

    if is_confirmation:
        ctk.CTkButton(btn_frame, text="Batal", width=100, fg_color="gray40",
                     hover_color="gray30", command=lambda: on_close(False)).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="OK", width=100,
                     command=lambda: on_close(True)).pack(side="left", padx=10)
    else:
        ctk.CTkButton(btn_frame, text="OK", width=120,
                     command=lambda: on_close(True)).pack()

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
