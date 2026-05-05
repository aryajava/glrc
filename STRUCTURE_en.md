# GLRC: GitLab Repo Cloner - Project Structure

## Folder Structure

```
MyRepoManager/
├── assets/                       # Visual assets and typography
│   ├── fonts/                   # Font files (Open Sans, Material Icons)
│   ├── icons/                   # App logos (ico, png, svg)
│   └── img/                     # Documentation screenshots
│
├── src/                          # Main source code (modular)
│   ├── __init__.py              # Package Initialization
│   ├── constants.py             # App constants (icons, dimensions, etc.)
│   │
│   ├── core/                    # Business Logic Layer
│   │   ├── __init__.py
│   │   ├── config_manager.py   # Config management (config.json) & Vault (Keyring)
│   │   ├── gitlab_api.py       # GitLab API network operations
│   │   └── git_operations.py   # Git sync execution (clone, pull, checkout)
│   │
│   ├── ui/                      # UI components (future expansion)
│   │   └── __init__.py
│   │
│   └── utils/                   # Support utilities
│       ├── __init__.py
│       ├── dialogs.py          # Custom Dialog functions (info, error, confirmation)
│       ├── helpers.py          # Helper functions (center_window, ToolTip)
│       └── i18n.py             # Internationalization support (EN/ID)
│
├── main.py                      # App entry point (GLRCApp class)
├── requirements.txt             # Python dependencies
├── VERSION                      # Current version record
├── CHANGELOG.md                 # Change history (ID)
├── CHANGELOG_en.md              # Change history (EN)
├── build.bat / build.sh        # Executable build scripts
└── default_lang.txt            # Default language setting
```

## Module Description

### 1. `src/constants.py`
Contains all constants used across the application:
- Material Icons mapping
- Window dimensions (login/expanded)
- Pagination settings
- Retry attempts and delays

### 2. `src/core/` - Business Logic Layer

#### `config_manager.py`
- Manages reading and writing global configurations.
- **Modern Security**: Utilizes `keyring` (OS-native vault) to store PAT securely, replacing legacy manual encryption systems.
- **Storage**: Non-sensitive settings are stored in `config.json`.

#### `gitlab_api.py`
- `GitLabAPI` class for all GitLab API interactions.
- Methods: `test_connection()`, `fetch_all_projects()`, `get_repository_branches()`.

#### `git_operations.py`
- `GitOperations` class for low-level Git actions.
- Methods: `clone_repository()`, `pull_repository()`, `create_new_branch()`, `is_git_repository()`.
- Supports *Graceful Cancellation* via `threading.Event()`.

### 3. `src/utils/` - Utilities Layer

#### `dialogs.py`
- Custom dialog functions supporting dark/light themes and localization.
- `show_info()`, `show_warning()`, `show_error()`, `show_confirmation()`.

#### `helpers.py`
- `center_window()` - Centers windows on the screen.
- `ToolTip` class - Provides hover information for widgets.

#### `i18n.py`
- Main internationalization engine.
- Supports: English (EN) and Indonesian (ID).
- Contains the central translation dictionary mapped via the `_()` function.

### 4. `main.py`
- Main application Entry Point.
- `GLRCApp` class - Manages the main window lifecycle and UI workflow.
- Implements *System Tray* integration using `pystray`.

## Architectural Evolution

### Modernization v1.3.0+:
1. ✅ **Security Overhaul**: Migrated from Windows-only DPAPI to `keyring` supporting cross-platform (Windows, macOS, Linux).
2. ✅ **Config Migration**: Binary `config.dat` replaced by standard `config.json` for application settings.
3. ✅ **Asset Reorganization**: Moved fonts and icons to the `assets/` folder for a cleaner project root.

### Recent Enhancements v1.5.3 - v1.5.4:
1. ✅ **Change Confirmation**: Implemented "dirty checking" in settings modals.
2. ✅ **Localization Audit**: Complete i18n audit to eliminate hardcoded strings.
3. ✅ **Dependency Hardening**: Graceful handling for missing optional modules like `pystray`.

---

**Note**: This structure is designed to balance modularity and maintainability, ideal for medium-scale projects like GLRC.
