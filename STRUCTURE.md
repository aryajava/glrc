# GLRC: GitLab Repo Cloner - Struktur Project

## Struktur Folder

```
MyRepoManager/
├── assets/                       # Aset visual dan tipografi
│   ├── fonts/                   # Font files (Open Sans, Material Icons)
│   ├── icons/                   # Logo aplikasi (ico, png, svg)
│   └── img/                     # Screenshot dokumentasi
│
├── src/                          # Source code utama (modular)
│   ├── __init__.py              # Inisialisasi Paket
│   ├── constants.py             # Konstanta aplikasi (icons, dimensions, dll)
│   │
│   ├── core/                    # Lapisan Dasar Bisnis (Business logic layer)
│   │   ├── __init__.py
│   │   ├── config_manager.py   # Mengelola konfigurasi (config.json) dan brankas (Keyring)
│   │   ├── gitlab_api.py       # Operasi jaringan API ke server GitLab
│   │   └── git_operations.py   # Eksekusi sinkronisasi Git (clone, pull, checkout)
│   │
│   ├── ui/                      # Komponen UI (masa depan)
│   │   └── __init__.py
│   │
│   └── utils/                   # Utilitas pendukung
│       ├── __init__.py
│       ├── dialogs.py          # Fungsi Dialog kustom (info, error, konfirmasi)
│       ├── helpers.py          # Fungsi Helper (center_window, ToolTip)
│       └── i18n.py             # Dukungan Internasionalisasi (EN/ID)
│
├── main.py                      # Entry point aplikasi (GLRCApp class)
├── requirements.txt             # Dependensi Python
├── VERSION                      # Catatan versi saat ini
├── CHANGELOG.md                 # Riwayat perubahan (ID)
├── CHANGELOG_en.md              # Riwayat perubahan (EN)
├── build.bat / build.sh        # Script build executable
└── default_lang.txt            # Pengaturan bahasa default
```

## Deskripsi Modul

### 1. `src/constants.py`
Berisi semua konstanta yang digunakan dalam aplikasi:
- Pemetaan Material Icons
- Dimensi Jendela (login/expanded)
- Pengaturan Pagination
- Batas Retry dan Delay

### 2. `src/core/` - Business Logic Layer

#### `config_manager.py`
- Mengelola pembacaan dan penyimpanan konfigurasi global.
- **Modern Security**: Menggunakan `keyring` (OS-native vault) untuk menyimpan PAT secara aman, menggantikan sistem enkripsi manual lawas.
- **Storage**: Konfigurasi non-sensitif disimpan di `config.json`.

#### `gitlab_api.py`
- `GitLabAPI` class untuk semua operasi API GitLab.
- Methods: `test_connection()`, `fetch_all_projects()`, `get_repository_branches()`.

#### `git_operations.py`
- `GitOperations` class untuk operasi Git tingkat rendah.
- Methods: `clone_repository()`, `pull_repository()`, `create_new_branch()`, `is_git_repository()`.
- Mendukung fitur *Graceful Cancellation* menggunakan `threading.Event()`.

### 3. `src/utils/` - Utilities Layer

#### `dialogs.py`
- Fungsi dialog kustom yang mendukung tema gelap/terang dan lokalisasi.
- `show_info()`, `show_warning()`, `show_error()`, `show_confirmation()`.

#### `helpers.py`
- `center_window()` - Menyeimbangkan posisi jendela di tengah layar.
- `ToolTip` class - Menyediakan informasi tambahan saat kursor diarahkan ke widget.

#### `i18n.py`
- Mesin utama internasionalisasi.
- Mendukung bahasa: Inggris (EN) dan Indonesia (ID).
- Berisi kamus terjemahan pusat yang dipetakan melalui fungsi `_()`.

### 4. `main.py`
- Titik masuk (Entry Point) utama aplikasi.
- `GLRCApp` class - Mengelola siklus hidup jendela utama dan alur kerja UI.
- Implementasi integrasi *System Tray* menggunakan `pystray`.

## Evolusi Arsitektur

### Modernisasi v1.3.0+:
1. ✅ **Security Overhaul**: Migrasi dari Windows-only DPAPI ke `keyring` yang mendukung lintas platform (Windows, macOS, Linux).
2. ✅ **Config Migration**: File `config.dat` (biner) telah digantikan oleh `config.json` yang lebih standar untuk pengaturan aplikasi.
3. ✅ **Asset Reorganization**: Memindahkan font dan ikon ke folder `assets/` agar root project lebih bersih.

### Peningkatan Terbaru v1.5.3 - v1.5.4:
1. ✅ **Change Confirmation**: Implementasi *dirty checking* pada modal pengaturan.
2. ✅ **Localization Audit**: Audit total i18n untuk memastikan tidak ada lagi teks hardcode.
3. ✅ **Dependency Hardening**: Penanganan error jika modul opsional seperti `pystray` tidak ditemukan.

---

**Catatan**: Struktur ini dirancang untuk menjaga keseimbangan antara modularitas dan kemudahan pemeliharaan, sangat ideal untuk project skala menengah seperti GLRC.
