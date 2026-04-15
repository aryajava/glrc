import json
import os
import logging
from datetime import datetime
import keyring
from pathlib import Path

logger = logging.getLogger("glrc")

CONFIG_DIR = Path.home() / ".glrc"
CONFIG_FILE = CONFIG_DIR / "config.json"
OLD_CONFIG_FILE = "config.dat"

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
            "clone_method": "HTTPS"
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

    def get_dest_folder(self) -> str:
        return self.config_data.get("dest_folder", "")

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
