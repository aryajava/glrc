import json
import os
from datetime import datetime
from dpapi_utils import crypt_protect_data, crypt_unprotect_data

CONFIG_FILE = "config.dat"

class ConfigManager:
    """Mengelola pembacaan dan penyimpanan konfigurasi (URL, Destinasi, dan PAT) terenkripsi."""
    def __init__(self):
        self.default_bundled_lang = "en"
        lang_path = os.path.join(os.path.dirname(__file__), "default_lang.txt")
        # In PyInstaller, the bundled file is in sys._MEIPASS. Let's try standard path first.
        import sys
        if hasattr(sys, '_MEIPASS'):
            lang_path = os.path.join(sys._MEIPASS, "default_lang.txt")

        if os.path.exists(lang_path):
            with open(lang_path, "r", encoding="utf-8") as f:
                self.default_bundled_lang = f.read().strip() or "en"

        self.config_data = {
            "gitlab_url": "",
            "dest_folder": "",
            "pat": "",
            "pat_expiry": None,
            "language": self.default_bundled_lang,
            "theme": "System",
            "clone_method": "HTTPS"
        }
        self.load_config()

    def load_config(self):
        """Membaca config.dat dan mendekripsi isinya."""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "rb") as f:
                    encrypted_data = f.read()

                decrypted_bytes = crypt_unprotect_data(encrypted_data)
                if decrypted_bytes:
                    data = json.loads(decrypted_bytes.decode('utf-8'))
                    self.config_data.update(data)
            except Exception as e:
                print(f"Error loading config: {e}")

    def save_config(self):
        """Menyimpan konfigurasi saat ini ke config.dat dengan enkripsi."""
        try:
            json_str = json.dumps(self.config_data, indent=4)
            encrypted_data = crypt_protect_data(json_str.encode('utf-8'))
            if encrypted_data:
                with open(CONFIG_FILE, "wb") as f:
                    f.write(encrypted_data)
        except Exception as e:
            print(f"Error saving config: {e}")

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

    # --- New Settings ---

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

    # --- Pengelolaan PAT Terenkripsi ---

    def save_pat(self, pat: str, expiry_date_iso: str):
        """Menyimpan PAT dan masa berlakunya ke dalam config terenkripsi."""
        if not pat:
            return

        self.config_data["pat"] = pat
        self.config_data["pat_expiry"] = expiry_date_iso
        self.save_config()

    def get_valid_pat(self) -> str:
        """Memuat PAT yang tersimpan. Mengembalikan string kosong jika kadaluarsa atau tidak ada."""
        expiry_str = self.config_data.get("pat_expiry")
        pat = self.config_data.get("pat", "")
        if not expiry_str or not pat:
            return ""

        try:
            # Pengecekan expired
            expiry_date = datetime.fromisoformat(expiry_str)
            if datetime.now() > expiry_date:
                # Sudah kadaluarsa, hapus token
                self.delete_pat()
                return ""

            return pat
        except Exception as e:
            print(f"Error checking PAT expiry: {e}")

        return ""

    def delete_pat(self):
        """Menghapus PAT dan tanggal expiry dari config."""
        self.config_data["pat"] = ""
        self.config_data["pat_expiry"] = None
        self.save_config()
