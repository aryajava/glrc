# GLRC Project Structure

## Directory Structure

```
MyRepoManager/
├── src/                          # Main modular source code
│   ├── __init__.py
│   ├── constants.py             # Application constants (icons, dimensions, API constraints)
│   │
│   ├── core/                    # Core business logic layer
│   │   ├── __init__.py
│   │   ├── config_manager.py   # Manages base config and Native OS Keyring credentials
│   │   ├── gitlab_api.py       # GitLab API Network Operations
│   │   └── git_operations.py   # Subprocess Git execution (clone, pull, checkout)
│   │
│   ├── ui/                      # Segmented UI components (future decoupling target)
│   │   └── __init__.py
│   │
│   └── utils/                   # Shared utility logic
│       ├── __init__.py
│       ├── dialogs.py          # Custom GUI dialogs (show_info, show_error)
│       ├── helpers.py          # Functional helpers (center_window, ToolTip)
│       └── i18n.py             # Internalization strings map (Bilingual Dictionary)
│
├── main.py                      # Main Python Entry Point (GUI Bootloader)
├── requirements.txt             # Python Library External Dependencies
├── build.bat / build.sh        # PyInstaller Native Compilers
├── default_lang.txt            # Localized language runtime cache
├── config.dat                  # Base configuration properties
│
├── MaterialIcons-Regular.ttf   # Bundled Font Artifacts
├── OpenSans-Regular.ttf
├── OpenSans-Bold.ttf
├── logo.png / logo.ico        # Branding Icons
│
└── README.md                   # Repositories Landing Page
```

## Modular Description

### 1. `src/constants.py`
Container for every hardcoded GUI elements and connection states:
- Material Icons hexadecimal mapping
- Layout Window dimensions
- Git API Pagination rules
- Network connection retry limiters

### 2. `src/core/` - Business Logic Layer

#### `config_manager.py`
- Parses non-sensitive parameters over to user's config folder hierarchy.
- Re-routes PAT (Personal Access Token) strictly towards native OS Vault components (`keyring`).

#### `gitlab_api.py`
- Houses `GitLabAPI` instance for raw HTTP Requests handling.
- Performs connectivity validations and parses nested paginations natively.

#### `git_operations.py`
- Subprocess commander (`GitOperations`) running shell variables.
- Dynamically validates `.git` paths to determine clone, pull, and branch strategies.

### 3. `src/utils/` - Utilities Layer

#### `dialogs.py`
- Instantiates TopLevel modals preventing total app hang/freeze states.

#### `i18n.py`
- Native lookup dictionary translating contextual parameters.
- Replaces raw hardcoded UI bindings into variable pointers `_("...text")`.

### 4. `main.py`
- The monolithic parent shell wrapping CustomTkinter window objects.

---

## Future Blueprint Scaling

Planned technical expansions projected under v2.0.0 Refactoring overhaul:
1. Slicing monolithic `main.py` UI codes into chunked classes within `src/ui/`
2. Decoupling Event Logic variables from visual grids.
3. Injection of test coverage matrices inside `/tests/`
4. Automated native Release Packaging via InnoSetup (Installer wrappers).
