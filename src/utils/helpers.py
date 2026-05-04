"""
Helper functions untuk GLRC Application
"""
import customtkinter as ctk
import tkinter as tk


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
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)

    def enter(self, event=None):
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify='left',
                       background="#ffffe0", relief='solid', borderwidth=1,
                       font=("Open Sans", 9))
        label.pack(ipadx=4, ipady=2)

    def leave(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
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
