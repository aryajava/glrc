import json
import os
import logging
from datetime import datetime
import keyring
from pathlib import Path

logger = logging.getLogger("glrc")

CONFIG_DIR = Path.home() / ".glrc"
CONFIG_FILE = CONFIG_DIR / "config.json"

import sys
if getattr(sys, 'frozen', False):
    _base_dir = Path(sys.executable).parent
else:
    _base_dir = Path(os.path.abspath(os.path.dirname(sys.argv[0])))

OLD_CONFIG_FILE = _base_dir / "config.dat"

SERVICE_NAME = "GLRC_App"
USERNAME = "gitlab_token"

class ConfigManager:
    """Mengelola pembacaan dan penyimpanan konfigurasi (URL, Destinasi) di JSON transparan, 
    dan mengelola PAT menggunakan OS keyring yang aman secara cross-platform."""
    def __init__(self):
        self.default_bundled_lang = "en"
        lang_path = os.path.join(os.path.dirname(__file__), "default_lang.txt")
        import sys
        if hasattr(sys, '_MEIPASS'):
            lang_path = os.path.join(sys._MEIPASS, "default_lang.txt")

        if os.path.exists(lang_path):
            with open(lang_path, "r", encoding="utf-8") as f:
                self.default_bundled_lang = f.read().strip() or "en"

        self.config_data = {
            "gitlab_url": "",
            "dest_folder": "",
            "pat_expiry": None,
            "language": self.default_bundled_lang,
            "theme": "System",
            "clone_method": "HTTPS",
            "recent_workspaces": [],
            "recent_limit": 10,
            "window_state": {
                "width": None,
                "height": None,
                "x": None,
                "y": None,
                "always_on_top": False,
                "opacity": 100,
                "minimize_to_tray": False,
                "startup_state": "Center",
                "modal_dimming": True,
                "keyboard_shortcuts": {
                    "workspace_tools": "Control-g",
                    "find": "Control-f",
                    "primary_action": "Control-Return"
                }
            }
        }
        
        # Buat direktori jika belum ada
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        
        self.migrate_old_config()
        self.load_config()

    def migrate_old_config(self):
        """Memigrasi data dari config.dat lama yang menggunakan enkripsi DPAPI Windows ke format baru."""
        if os.path.exists(OLD_CONFIG_FILE):
            logger.warning("Mendeteksi config.dat versi lama. Memulai migrasi...")
            try:
                # Coba parse dengan DPAPI. Hanya work di Windows.
                if os.name == 'nt':
                    import ctypes
                    import ctypes.wintypes
                    from ctypes import windll

                    class DATA_BLOB(ctypes.Structure):
                        _fields_ = [
                            ("cbData", ctypes.wintypes.DWORD),
                            ("pbData", ctypes.POINTER(ctypes.c_char))
                        ]

                    def unprotect(encrypted_bytes):
                        data_in = DATA_BLOB()
                        data_in.cbData = len(encrypted_bytes)
                        data_in.pbData = ctypes.cast(ctypes.c_char_p(encrypted_bytes), ctypes.POINTER(ctypes.c_char))
                        data_out = DATA_BLOB()
                        
                        success = windll.crypt32.CryptUnprotectData(
                            ctypes.byref(data_in), None, None, None, None, 0, ctypes.byref(data_out)
                        )
                        if not success: return None
                        result = ctypes.string_at(data_out.pbData, data_out.cbData)
                        if data_out.pbData:
                            windll.kernel32.LocalFree(ctypes.cast(data_out.pbData, ctypes.c_void_p))
                        return result

                    with open(OLD_CONFIG_FILE, "rb") as f:
                        enc = f.read()
                    
                    dec = unprotect(enc)
                    if dec:
                        data = json.loads(dec.decode('utf-8'))
                        # Pindahkan password ke keyring
                        pat = data.get("pat")
                        if pat:
                            try:
                                keyring.set_password(SERVICE_NAME, USERNAME, pat)
                            except Exception as e:
                                logger.warning(f"Gagal memigrasi token ke keyring: {e}")
                        
                        # Hapus pat dari data
                        data.pop("pat", None)
                        self.config_data.update(data)
                        self.save_config()
            except Exception as e:
                logger.warning(f"Gagal migrasi config.dat lama: {e}")
            finally:
                # Pindahkan agar tidak terbaca lagi
                try:
                    os.rename(OLD_CONFIG_FILE, OLD_CONFIG_FILE + ".bak")
                    logger.warning("Migrasi selesai, config lama di-rename ke .bak")
                except Exception:
                    pass

    def load_config(self):
        """Membaca konfigurasi non-sensitif dari config.json."""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.config_data.update(data)
            except Exception as e:
                logger.warning("Error loading config.json: %s", e)

    def save_config(self):
        """Menyimpan konfigurasi non-sensitif ke config.json."""
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config_data, f, indent=4)
        except Exception as e:
            logger.warning("Error saving config.json: %s", e)

    def set_gitlab_url(self, url: str):
        self.config_data["gitlab_url"] = url
        self.save_config()

    def set_dest_folder(self, folder_path: str):
        self.config_data["dest_folder"] = folder_path
        self.save_config()

    def set_pat_expiry(self, expiry_iso_str: str):
        self.config_data["pat_expiry"] = expiry_iso_str
        self.save_config()

    def set_min_disk_space_gb(self, space_gb: float):
        self.config_data["min_disk_space_gb"] = space_gb
        self.save_config()

    def get_dest_folder(self) -> str:
        return self.config_data.get("dest_folder", "")

    def get_min_disk_space_gb(self) -> float:
        # Avoid direct import loop by importing inside function or assume constants is available.
        # However constants is not imported in config_manager yet. I'll just use 2.0 as fallback.
        return float(self.config_data.get("min_disk_space_gb", 2.0))

    def get_gitlab_url(self) -> str:
        return self.config_data.get("gitlab_url", "")

    def set_language(self, lang: str):
        self.config_data["language"] = lang
        self.save_config()

    def get_language(self) -> str:
        return self.config_data.get('language', self.default_bundled_lang)

    def set_theme(self, theme: str):
        self.config_data["theme"] = theme
        self.save_config()

    def get_theme(self) -> str:
        return self.config_data.get("theme", "System")

    def set_clone_method(self, method: str):
        self.config_data["clone_method"] = method
        self.save_config()

    def get_clone_method(self) -> str:
        return self.config_data.get("clone_method", "HTTPS")

    # --- Recent Workspaces ---

    def get_recent_limit(self) -> int:
        try:
            limit = int(self.config_data.get("recent_limit", 10))
        except (TypeError, ValueError):
            limit = 10
        return limit if limit in (5, 10, 20) else 10

    def set_recent_limit(self, limit: int):
        try:
            limit = int(limit)
        except (TypeError, ValueError):
            limit = 10
        if limit not in (5, 10, 20):
            limit = 10
        self.config_data["recent_limit"] = limit
        self.config_data["recent_workspaces"] = self.get_recent_workspaces(prune_missing=True)[:limit]
        self.save_config()

    def add_recent_workspace(self, path: str):
        if not path:
            return
        try:
            workspace_path = str(Path(path).expanduser().resolve())
        except Exception:
            workspace_path = os.path.abspath(os.path.expanduser(path))

        if not workspace_path.lower().endswith(".json"):
            return

        recent = self.get_recent_workspaces(prune_missing=True)
        recent = [item for item in recent if os.path.normcase(item) != os.path.normcase(workspace_path)]
        recent.insert(0, workspace_path)
        self.config_data["recent_workspaces"] = recent[:self.get_recent_limit()]
        self.save_config()

    def get_recent_workspaces(self, prune_missing: bool = True) -> list:
        raw_recent = self.config_data.get("recent_workspaces", [])
        if not isinstance(raw_recent, list):
            raw_recent = []

        recent = []
        seen = set()
        for item in raw_recent:
            if not isinstance(item, str) or not item.strip():
                continue
            try:
                workspace_path = str(Path(item).expanduser().resolve())
            except Exception:
                workspace_path = os.path.abspath(os.path.expanduser(item))
            norm_path = os.path.normcase(workspace_path)
            if norm_path in seen:
                continue
            if prune_missing and not os.path.isfile(workspace_path):
                continue
            if not workspace_path.lower().endswith(".json"):
                continue
            seen.add(norm_path)
            recent.append(workspace_path)

        recent = recent[:self.get_recent_limit()]
        if recent != raw_recent:
            self.config_data["recent_workspaces"] = recent
            self.save_config()
        return recent

    def clear_recent_workspaces(self):
        self.config_data["recent_workspaces"] = []
        self.save_config()

    # --- Window State & Power UI ---

    def get_window_state(self) -> dict:
        defaults = {
            "width": None,
            "height": None,
            "x": None,
            "y": None,
            "always_on_top": False,
            "opacity": 100,
            "minimize_to_tray": False,
            "startup_state": "Center",
            "modal_dimming": True,
            "lock_window_pos": False,
            "lock_modal_pos": False,
            "keyboard_shortcuts": {
                "workspace_tools": "Control-g",
                "find": "Control-f",
                "primary_action": "Control-Return"
            }
        }
        state = self.config_data.get("window_state", {})
        if not isinstance(state, dict):
            state = {}
        merged = defaults.copy()
        merged.update({k: v for k, v in state.items() if k != "keyboard_shortcuts"})
        shortcuts = defaults["keyboard_shortcuts"].copy()
        if isinstance(state.get("keyboard_shortcuts"), dict):
            shortcuts.update(state["keyboard_shortcuts"])
        merged["keyboard_shortcuts"] = shortcuts
        return merged

    def set_window_state(self, updates: dict):
        state = self.get_window_state()
        for key, value in updates.items():
            if key == "keyboard_shortcuts" and isinstance(value, dict):
                shortcuts = state.get("keyboard_shortcuts", {}).copy()
                shortcuts.update(value)
                state["keyboard_shortcuts"] = shortcuts
            else:
                state[key] = value
        self.config_data["window_state"] = state
        self.save_config()

    def get_keyboard_shortcuts(self) -> dict:
        return self.get_window_state().get("keyboard_shortcuts", {})

    def set_keyboard_shortcuts(self, shortcuts: dict):
        self.set_window_state({"keyboard_shortcuts": shortcuts})

    # --- Pengelolaan PAT via Keyring ---

    def save_pat(self, pat: str, expiry_date_iso: str):
        """Menyimpan PAT menggunakan OS Keyring dan konfig expiry ke JSON."""
        if not pat:
            return

        try:
            keyring.set_password(SERVICE_NAME, USERNAME, pat)
            self.config_data["pat_expiry"] = expiry_date_iso
            self.save_config()
        except Exception as e:
            logger.error("Error menyimpan password ke OS Keyring: %s", e)
            pass

    def get_valid_pat(self) -> str:
        """Memuat PAT dari Keyring dan memvalidasi kadaluarsa."""
        expiry_str = self.config_data.get("pat_expiry")
        if not expiry_str:
            return ""

        try:
            pat = keyring.get_password(SERVICE_NAME, USERNAME)
            if not pat:
                return ""

            # Pengecekan expired
            expiry_date = datetime.fromisoformat(expiry_str)
            if datetime.now() > expiry_date:
                self.delete_pat()
                return ""

            return pat
        except Exception as e:
            logger.warning("Error membaca PAT dari Keyring atau cek expiry: %s", e)
            return ""

    def get_saved_pat(self) -> dict:
        """Accessor untuk UI profile modal."""
        try:
            pat = keyring.get_password(SERVICE_NAME, USERNAME) or ""
        except Exception:
            pat = ""
            
        return {
            "pat": pat,
            "expiry_date": self.config_data.get("pat_expiry")
        }

    def delete_pat(self):
        """Menghapus PAT dari Keyring dan unset tanggal expiry dari config."""
        try:
            if keyring.get_password(SERVICE_NAME, USERNAME) is not None:
                keyring.delete_password(SERVICE_NAME, USERNAME)
        except Exception as e:
            logger.warning("Gagal menghapus pat dari keyring: %s", e)
            
        self.config_data["pat_expiry"] = None
        self.save_config()
