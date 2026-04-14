import os

_current_lang = "en"

# Dictionary of translations
_translations = {
    "en": {
        # General
        "app_title": "GLRC: GitLab Repo Cloner",
        "app_subtitle": "Enter your GitLab instance URL and Personal Access Token (PAT).",
        "login_info": "New User Info: Personal Access Token (PAT) is a 'special password' used by this app\nto read repository lists and clone securely.\nGet it on GitLab: Settings -> Access Tokens -> Create a token with 'read_repository' & 'api' scopes.",
        "instance_url": "GitLab Instance URL:",
        "pat_label": "Personal Access Token (PAT):",
        "save_token": "Save Token (Encrypted)",
        "duration": "For:",
        "days": "Days",
        "connect_btn": "Connect & Fetch Repositories",
        "connecting": "Connecting...",
        "warning": "Warning",
        "empty_creds": "URL and Token cannot be empty!",
        "invalid_url_scheme": "URL must start with http:// or https://",
        "invalid_url_host": "URL does not contain a valid hostname.",
        "git_not_found": "Git is not installed or not found in PATH.\nPlease install Git first: https://git-scm.com/downloads",
        "invalid_days": "PAT save duration must be a number (Days).",
        "session_restored": "Session restored. Attempting auto-login...",
        "fetching_error": "API Fetch failed",
        "error": "Error",
        "ok": "OK",
        "repo_per_page": "Repos per page",
        "tooltip_logout": "Logout",
        "tooltip_settings": "Settings",
        "tooltip_about": "About GLRC: GitLab Repo Cloner",
        "tooltip_profile": "User profile",
        "show_token": "Show token",
        "hide_token": "Hide token",
        "pat_days_tooltip": "Set 0 for auto-login without expiration (permanent)",
        "profile_title": "User Profile",
        "profile_default_user": "User",
        "token_duration": "Token Duration:",
        "change_duration_days": "Change Duration (days):",
        "update": "Update",
        "permanent": "Permanent",
        "invalid_date": "Invalid Date",
        "duration_must_number": "Duration must be numeric!",
        "duration_not_negative": "Duration must not be negative!",
        "confirm_update_duration": "Are you sure you want to change token duration?\n\nOld Duration:\n{old}\n\nNew Duration:\n{new}",
        "duration_updated": "Duration updated successfully!",
        "token_missing_relogin": "Token not found, please login again.",
        "settings_saved_restart": "Settings saved. Most UI updates are immediate, but restart app for full effect.",
        "source_code": "Source Code",
        "issues": "Issues",
        "check_updates": "Check Updates",
        "create_branch_tooltip": "Create new branch?",
        "dest_not_found_create": "Destination folder not found:\n\n{path}\n\nCreate this folder now?",
        "dest_create_failed": "Failed to create destination folder:\n{error}",
        
        # Main Frame Step 1
        "step1_title": "Select Destination Folder",
        "step1_hint": "Make sure the folder is empty to avoid overlapping files.",
        "path_label": "Path:",
        "dest_placeholder": "Select clone destination folder...",
        "browse_folder": "Browse Folder",
        
        # Main Frame Step 2
        "step2_title": "Search & Select Repositories",
        "search_placeholder": "Type search or wildcard (e.g. *-api)...",
        "search_btn": "Search",
        "reset_btn": "Reset",
        "select_all": "Select All (This Page)",
        "deselect_all": "Deselect (This Page)",
        "repo_list": "Repository List",
        
        # Pagination
        "rows_per_page": "Rows per page:",
        "prev": "Prev",
        "next": "Next",
        "go_to_page": "Go to page:",
        "loading": "Loading data...",
        "not_found": "Repositories not found.",
        
        # Step 3
        "step3_btn": "Proceed to Branch Config & Clone...",
        "cloning_in_progress": "Cloning in progress...",
        
        # Log Output
        "log_title": "Log Output",
        "show_logs": "Show Logs",
        
        # Modal Branch
        "modal_title": "Branch Configuration",
        "modal_header": "Branch Configuration per Repository",
        "modal_info": "Select the main branch (e.g. main or master) to clone.\nIf you need to create a new development branch (e.g. for a feature), check 'Create new branch' and enter the name.",
        "col_repo": "Repository",
        "col_clone_from": "Clone from Branch",
        "col_new_branch": "New?",
        "col_new_branch_name": "New Branch Name",
        "fetching_branches": "Fetching branch lists from GitLab...",
        "cancel": "Cancel",
        "start_clone": "Start Clone",
        "branch_not_found": "Branch '{typed}' not found in repository:\n{rep_name}",
        "at_least_one": "Select at least 1 repository to clone!",
        "invalid_dest": "Select a valid destination folder in Step 1!",
        
        # Clone execution
        "clone_done": "Process finished!\n\nSuccess: {success}\nFailed: {failed}",
        "done_title": "Finished",
        "retrying": "Retrying... ({i}/3)",
        
        # Settings
        "settings_title": "Settings",
        "language_lbl": "Language:",
        "theme_lbl": "Theme:",
        "clone_method_lbl": "Clone Method:",
        "save_settings": "Save Settings",
        
        # About
        "about_title": "About",
        "about_content": "GLRC: GitLab Repo Cloner\nVersion: {version}\nLicense: MIT\n\nA tool to securely batch-clone GitLab repositories.",
        
        # Workspace Export/Import
        "export_ws": "Export Workspace",
        "import_ws": "Import Workspace",
        "ws_exported": "Workspace exported successfully to {file}",
        "ws_imported": "Workspace imported! Checked {count} repositories.",
        "ws_import_err": "Failed to parse Workspace JSON file.",
        
        # Open in IDE
        "open_in_ide_title": "Open in IDE:",
        "open_ide_btn": "Open",
        "open_ide_failed": "Failed to open {ide}:\n{error}",
        "open_in_explorer": "File Explorer",
        
        # UI Updates
        "app_name": "GLRC: GitLab Repo Cloner",
        "pulling": "[>] Repo exists. Pulling latest code...",
        "cloning_repo": "[>] Cloning '{repo_name}' (from branch: {branch_name})...",
    },
    "id": {
        # General
        "app_title": "GLRC: GitLab Repo Cloner",
        "app_subtitle": "Masukkan URL instance dan Personal Access Token (PAT) GitLab Anda.",
        "login_info": "Info Pemula: Personal Access Token (PAT) adalah 'password khusus' yang digunakan aplikasi ini\nuntuk membaca daftar repositori dan melakukan clone dengan aman.\nDapatkan di GitLab: Settings -> Access Tokens -> Buat token dengan scope 'read_repository' & 'api'.",
        "instance_url": "GitLab Instance URL:",
        "pat_label": "Personal Access Token (PAT):",
        "save_token": "Simpan Token (Aman Terenkripsi)",
        "duration": "Selama:",
        "days": "Hari",
        "connect_btn": "Connect & Fetch Repositories",
        "connecting": "Menghubungkan...",
        "warning": "Peringatan",
        "empty_creds": "URL dan Token tidak boleh kosong!",
        "invalid_url_scheme": "URL harus diawali dengan http:// atau https://",
        "invalid_url_host": "URL tidak mengandung hostname yang valid.",
        "git_not_found": "Git tidak terinstall atau tidak ditemukan di PATH.\nSilakan install Git terlebih dahulu: https://git-scm.com/downloads",
        "invalid_days": "Durasi simpan PAT harus berupa angka (Hari).",
        "session_restored": "Sesi Anda dipulihkan. Mencoba login otomatis...",
        "fetching_error": "Gagal Fetch API",
        "error": "Error",
        "ok": "OK",
        "repo_per_page": "Repo per page",
        "tooltip_logout": "Logout",
        "tooltip_settings": "Pengaturan",
        "tooltip_about": "Tentang GLRC: GitLab Repo Cloner",
        "tooltip_profile": "Profil Pengguna",
        "show_token": "Tampilkan token",
        "hide_token": "Sembunyikan token",
        "pat_days_tooltip": "Isi 0 untuk login otomatis tanpa kedaluwarsa (permanen)",
        "profile_title": "Profil Pengguna",
        "profile_default_user": "Pengguna",
        "token_duration": "Durasi Token:",
        "change_duration_days": "Ubah Durasi (hari):",
        "update": "Update",
        "permanent": "Permanen",
        "invalid_date": "Tanggal tidak valid",
        "duration_must_number": "Durasi harus berupa angka!",
        "duration_not_negative": "Durasi tidak boleh negatif!",
        "confirm_update_duration": "Apakah Anda yakin ingin mengubah durasi token?\n\nDurasi Lama:\n{old}\n\nDurasi Baru:\n{new}",
        "duration_updated": "Durasi berhasil diupdate!",
        "token_missing_relogin": "Token tidak ditemukan, harap login ulang.",
        "settings_saved_restart": "Pengaturan disimpan. Sebagian besar UI langsung berubah, tetapi restart aplikasi untuk hasil penuh.",
        "source_code": "Source Code",
        "issues": "Issues",
        "check_updates": "Cek Update",
        "create_branch_tooltip": "Buat branch baru?",
        "dest_not_found_create": "Folder destinasi tidak ditemukan:\n\n{path}\n\nBuat folder ini sekarang?",
        "dest_create_failed": "Gagal membuat folder destinasi:\n{error}",
        
        # Main Frame Step 1
        "step1_title": "Tentukan Folder Destinasi",
        "step1_hint": "Pastikan folder kosong untuk menghindari file tumpang tindih.",
        "path_label": "Path:",
        "dest_placeholder": "Pilih folder tujuan clone...",
        "browse_folder": "Browse Folder",
        
        # Main Frame Step 2
        "step2_title": "Cari & Pilih Repositori",
        "search_placeholder": "Ketik pencarian atau wildcard (mis. *-api)...",
        "search_btn": "Cari",
        "reset_btn": "Reset",
        "select_all": "Pilih Semua (Hal ini)",
        "deselect_all": "Batal Pilih (Hal ini)",
        "repo_list": "Daftar Repositori",
        
        # Pagination
        "rows_per_page": "Baris per halaman:",
        "prev": "Prev",
        "next": "Next",
        "go_to_page": "Ke halaman:",
        "loading": "Memuat data...",
        "not_found": "Tidak ada repositori ditemukan.",
        
        # Step 3
        "step3_btn": "Lanjut Konfigurasi Branch & Eksekusi Clone...",
        "cloning_in_progress": "Cloning sedang berjalan...",
        
        # Log Output
        "log_title": "Log Output",
        "show_logs": "Tampilkan Log",
        
        # Modal Branch
        "modal_title": "Konfigurasi Branch",
        "modal_header": "Konfigurasi Branch per Repositori",
        "modal_info": "Pilih branch utama (mis. main atau master) yang akan di-clone.\nJika Anda butuh membuat cabang pengembangan baru (mis. untuk fitur/bugfix), centang 'Buat branch baru' dan masukkan namanya.",
        "col_repo": "Repositori",
        "col_clone_from": "Clone dari Branch",
        "col_new_branch": "Baru?",
        "col_new_branch_name": "Nama Branch Baru",
        "fetching_branches": "Mengambil daftar branch dari GitLab...",
        "cancel": "Batal",
        "start_clone": "Mulai Clone",
        "branch_not_found": "Branch '{typed}' tidak ditemukan pada repositori:\n{rep_name}",
        "at_least_one": "Pilih minimal 1 repositori untuk di-clone!",
        "invalid_dest": "Pilih destinasi folder yang valid pada Langkah 1!",
        
        # Clone execution
        "clone_done": "Proses selesai!\n\nBerhasil: {success}\nGagal: {failed}",
        "done_title": "Selesai",
        "retrying": "Mencoba ulang... ({i}/3)",
        
        # Settings
        "settings_title": "Pengaturan",
        "language_lbl": "Bahasa (Language):",
        "theme_lbl": "Tema Warna:",
        "clone_method_lbl": "Metode Clone:",
        "save_settings": "Simpan Pengaturan",
        
        # About
        "about_title": "Tentang Aplikasi",
        "about_content": "GLRC: GitLab Repo Cloner\nVersi: {version}\nLisensi: MIT\n\nAlat untuk mengelola dan clone banyak repositori GitLab secara serentak.",
        
        # Workspace Export/Import
        "export_ws": "Ekspor Workspace",
        "import_ws": "Impor Workspace",
        "ws_exported": "Workspace berhasil diekspor ke {file}",
        "ws_imported": "Workspace diimpor! {count} repositori diceklis.",
        "ws_import_err": "Gagal membaca file JSON Workspace.",
        
        # Open in IDE
        "open_in_ide_title": "Buka di IDE:",
        "open_ide_btn": "Buka",
        "open_ide_failed": "Gagal membuka {ide}:\n{error}",
        "open_in_explorer": "File Explorer",
        
        # UI Updates
        "app_name": "GLRC: GitLab Repo Cloner",
        "pulling": "[>] Repo sudah ada. Melakukan git pull...",
        "cloning_repo": "[>] Cloning '{repo_name}' (dari branch: {branch_name})...",
    }
}

def set_language(lang_code: str):
    global _current_lang
    if lang_code in _translations:
        _current_lang = lang_code

def _(key: str, **kwargs) -> str:
    """
    Translate a string key into the current language.
    If it requires formatting (like {success}), pass those as kwargs.
    """
    text = _translations.get(_current_lang, _translations["en"]).get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text

def get_current_language() -> str:
    return _current_lang
