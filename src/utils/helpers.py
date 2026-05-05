"""
Helper functions untuk GLRC Application
"""
import customtkinter as ctk
import tkinter as tk
from typing import Callable, Union


def center_window(window, width, height):
    """
    Fungsi helper untuk menengahkan window di layar.

    Args:
        window: Tkinter window object
        width: Lebar window
        height: Tinggi window
    """
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")


class ToolTip:
    """
    Class untuk membuat tooltip pada widget.
    """
    def __init__(self, widget, text: Union[str, Callable[[], str]], delay=450):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.delay = delay
        self._after_id = None
        self._alpha_after_id = None
        self.widget.bind("<Enter>", self.enter, add="+")
        self.widget.bind("<Leave>", self.leave, add="+")
        self.widget.bind("<Destroy>", self.leave, add="+")

    def get_text(self):
        if callable(self.text):
            try:
                return self.text() or ""
            except Exception:
                return ""
        return self.text or ""

    def set_text(self, text: Union[str, Callable[[], str]]):
        self.text = text
        if self.tooltip_window and self.tooltip_window.winfo_exists():
            label = getattr(self.tooltip_window, "label", None)
            if label is not None:
                label.configure(text=self.get_text())

    def _theme_colors(self):
        mode = ctk.get_appearance_mode().lower()
        if mode == "dark":
            return "#1f2937", "#f9fafb", "#374151"
        return "#ffffff", "#111827", "#d1d5db"

    def enter(self, event=None):
        self.leave()
        self._after_id = self.widget.after(self.delay, self.show)

    def show(self):
        text = self.get_text()
        if not text:
            return
        if not self.widget.winfo_exists():
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        bg, fg, border = self._theme_colors()
        try:
            tw.attributes("-alpha", 0.0)
        except Exception:
            pass
        label = tk.Label(
            tw, text=text, justify="left",
            background=bg, foreground=fg, relief="solid", borderwidth=1,
            highlightthickness=1, highlightbackground=border,
            font=("Open Sans", 9), padx=8, pady=5
        )
        tw.label = label
        label.pack()
        self._fade_in(0.0)

    def _fade_in(self, alpha):
        if not self.tooltip_window or not self.tooltip_window.winfo_exists():
            return
        alpha = min(alpha + 0.18, 0.96)
        try:
            self.tooltip_window.attributes("-alpha", alpha)
        except Exception:
            return
        if alpha < 0.96:
            self._alpha_after_id = self.tooltip_window.after(20, lambda: self._fade_in(alpha))

    def leave(self, event=None):
        if self._after_id:
            try:
                self.widget.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None
        if self._alpha_after_id and self.tooltip_window:
            try:
                self.tooltip_window.after_cancel(self._alpha_after_id)
            except Exception:
                pass
            self._alpha_after_id = None
        if self.tooltip_window:
            try:
                self.tooltip_window.destroy()
            except Exception:
                pass
            self.tooltip_window = None

def middle_truncate(text: str, max_length: int = 50) -> str:
    """
    Truncates a string in the middle if it exceeds max_length.
    Example: "very_long_repository_name_in_the_group" -> "very_long_repo...in_the_group"
    """
    if len(text) <= max_length:
        return text
    
    half_len = (max_length - 3) // 2
    return text[:half_len] + "..." + text[-half_len:]

def parse_raw_repo_text(raw_text: str) -> set:
    """
    Cleans up a raw block of text (e.g. from copy-paste) into a set of unique repository paths.
    - Trims whitespace
    - Removes empty lines
    - Strips 'https://', 'http://', domain names, and '.git'
    """
    import re
    cleaned_repos = set()
    lines = raw_text.splitlines()
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Remove https://domain.com/ prefix if exists
        line = re.sub(r'^https?://[^/]+/', '', line)
        # Remove .git suffix if exists
        if line.endswith('.git'):
            line = line[:-4]
            
        line = line.strip('/')
        if line:
            cleaned_repos.add(line)
            
    return cleaned_repos
