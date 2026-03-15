# GLRC: GitLab Repo Cloner - Struktur Project

## Struktur Folder

```
MyRepoManager/
├── src/                          # Source code utama (modular)
│   ├── __init__.py              # Package initialization
│   ├── constants.py             # Konstanta aplikasi (icons, dimensions, dll)
│   │
│   ├── core/                    # Business logic layer
│   │   ├── __init__.py
│   │   ├── config_manager.py   # Mengelola konfigurasi terenkripsi
│   │   ├── dpapi_utils.py      # Windows DPAPI encryption utilities
│   │   ├── gitlab_api.py       # GitLab API operations
│   │   └── git_operations.py   # Git operations (clone, pull, checkout)
│   │
│   ├── ui/                      # UI components (future expansion)
│   │   └── __init__.py
│   │
│   └── utils/                   # Utility functions
│       ├── __init__.py
│       ├── dialogs.py          # Dialog functions (show_info, show_error, dll)
│       ├── helpers.py          # Helper functions (center_window, ToolTip)
│       └── i18n.py             # Internationalization support
│
├── main.py                      # Entry point aplikasi (GLRCApp class)
├── requirements.txt             # Python dependencies
├── build.bat / build.sh        # Build scripts
├── default_lang.txt            # Default language setting
├── config.dat                  # Encrypted configuration file
│
├── MaterialIcons-Regular.ttf   # Material icons font
├── OpenSans-Regular.ttf        # Font files
├── OpenSans-Bold.ttf
├── logo.png / logo.ico        # Application icons
│
└── README.md                   # Project documentation
```

## Deskripsi Modul

### 1. `src/constants.py`
Berisi semua konstanta yang digunakan dalam aplikasi:
- Material Icons mapping
- Window dimensions (login/expanded)
- Pagination settings
- Retry attempts dan delays

### 2. `src/core/` - Business Logic Layer

#### `config_manager.py`
- Mengelola pembacaan dan penyimpanan konfigurasi
- Enkripsi/dekripsi menggunakan Windows DPAPI
- Menyimpan: GitLab URL, PAT, destination folder, preferences

#### `dpapi_utils.py`
- Windows DPAPI (Data Protection API) wrapper
- Fungsi enkripsi dan dekripsi data sensitif

#### `gitlab_api.py`
- `GitLabAPI` class untuk semua operasi API GitLab
- Methods: `test_connection()`, `fetch_all_projects()`, `get_repository_branches()`

#### `git_operations.py`
- `GitOperations` class untuk operasi Git
- Methods: `clone_repository()`, `pull_repository()`, `create_new_branch()`, `is_git_repository()`

### 3. `src/utils/` - Utilities Layer

#### `dialogs.py`
- Custom dialog functions
- `show_info()`, `show_warning()`, `show_error()`, `show_confirmation()`

#### `helpers.py`
- `center_window()` - Center window di layar
- `ToolTip` class - Tooltip untuk widgets

#### `i18n.py`
- Internationalization support
- Mendukung bahasa: English dan Indonesian
- Translation dictionary dan helper functions

### 4. `main.py`
- Entry point aplikasi
- `GLRCApp` class - Main application window
- Setup UI (login frame, main frame)
- Event handlers dan UI logic

## Perubahan dari Struktur Lama

### Bug yang Diperbaiki:
1. ✅ **Line 62**: Syntax error class definition dan function definition di satu baris
2. ✅ **Undefined variable**: `_active_messages` sekarang didefinisikan di `dialogs.py`
3. ✅ **Unused code**: `RepoMasterApp` class yang tidak digunakan telah dihapus

### Peningkatan Struktur:
1. ✅ **Modular Architecture**: Kode dipecah ke dalam modul-modul yang terorganisir
2. ✅ **Separation of Concerns**: Business logic terpisah dari UI logic
3. ✅ **Reusability**: Helper functions dan utilities dapat digunakan ulang
4. ✅ **Maintainability**: Kode lebih mudah dipelihara dan dikembangkan
5. ✅ **Constants Management**: Semua magic numbers dan strings di satu tempat

## Import Statements Baru

File `main.py` sekarang menggunakan imports dari struktur modular:

```python
from src.core.config_manager import ConfigManager
from src.core.gitlab_api import GitLabAPI
from src.core.git_operations import GitOperations
from src.utils import i18n
from src.utils.i18n import _
from src.utils.helpers import center_window, ToolTip
from src.utils.dialogs import show_info, show_warning, show_error, show_confirmation
from src.constants import ICON_*, DEFAULT_*
```

## Backwards Compatibility

File-file original (`config_manager.py`, `dpapi_utils.py`, `i18n.py`) masih ada di root folder untuk backward compatibility. Namun, disarankan untuk menggunakan modul dari `src/` untuk development ke depan.

## Next Steps (Opsional)

Untuk pengembangan lebih lanjut, bisa dipertimbangkan:

1. Memisahkan `GLRCApp` class ke dalam sub-classes yang lebih kecil
2. Membuat UI components terpisah di `src/ui/` (LoginFrame, MainFrame, dll)
3. Menambahkan unit tests di folder `tests/`
4. Menambahkan logging system yang lebih robust
5. Dokumentasi API dengan docstrings yang lebih lengkap

---

**Catatan**: Struktur ini dirancang untuk menjaga balance antara modularitas dan kesederhanaan, cocok untuk project skala menengah seperti GLRC.
