# Version History (Changelog)

All algorithmic modifications, architectural restructurings, bugfixes, and feature injections concerning the GLRC application ecosystem will be publicly logged in this document.

======================

## version 1.5.5

*UX Polish & Maintenance* — Modal layout improvements, internal search, local status indicators, and Git identity standardization.

### enhancement:
- **Branch Modal Search:** Added a real-time search field within the branch configuration modal. Users can now filter selected repositories to quickly find specific ones.
- **Local/Cloud Status Indicators:** Implemented visual icons in the main list. The 📂 (Folder) icon indicates the repo exists locally, while ☁️ (Cloud) indicates it is remote-only.
- **Advanced Result Dialog:** 
  1. **Show Failed Only:** A toggle to filter results, showing only repositories that failed to clone/pull.
  2. **Copy All Logs:** A new button to copy the entire process log to the clipboard with one click.
  3. **Visual Error Highlights:** Failed repositories are now highlighted in red with a distinct border in the results dialog.
- **Simplified Repo Names:** Repository names in modals now display only the last segment (project name) for a cleaner UI. Tooltips still provide the full path for reference.
- **Layout Alignment Fix:** Standardized column widths (`COL_WIDTHS`) and fixed padding (24px) to ensure visual alignment between the Bulk Apply row and the repository list.
- **Git Identity Enforcement:** Ensures every clone/pull process automatically runs `git config --local user.name` and `user.email` based on the logged-in GitLab profile, without affecting global settings.

======================

## version 1.5.4

*Hotfix & Polish* — Quick fixes for pystray dependency and dialog bugs.

### bugfix:
- **Dependency Fix:** Resolved `pystray cannot find module` by ensuring the library is installed in the execution environment.
- **Reference Fix:** Fixed `show_confirm` typo to `show_confirmation` in the history clearing function.
- **Localization:** Localized the hardcoded "Info" success dialog title.

======================

## version 1.5.3

*Stability & Full Localization* — Final patch for UI stability, data loss prevention via confirmation system, and a comprehensive localization (i18n) audit.

### enhancement:
- **Change Confirmation System:** Implemented "dirty checking" logic in Settings, Interface, and Keyboard Mapping modals. The app now detects unsaved changes and asks for confirmation before closing or saving.
- **Full i18n Audit:** Performed a complete audit of the multi-language system. Added 20+ new keys and localized all remaining hardcoded strings (including git process logs, placeholders, and dialog labels).
- **Quick Export Button:** Added an "Export" button directly to the main screen to speed up the workflow for exporting selected repositories to JSON.
- **Improved Dialog Labels:** Synchronized "OK" and "Cancel" button labels across all dialogs to ensure consistency with the user's language preference.

### bugfix:
- **RecursionError Fix:** Resolved potential `maximum recursion depth exceeded` crashes by using safer UI callback scheduling via `.after()`.
- **Warning Key Fix:** Fixed a bug where the "Select at least one repository" warning appeared as a raw key code (`at_least_one`) instead of localized text.

======================

## version 1.5.2

*Power User & Advanced UI* — A patch for advanced window controls, project resolving, keyboard mapping, and system tray integration.

### enhancement:
- **Advanced Project Resolver:** The app scans repository-root markers such as `.sln`, `.csproj`, `package.json`, `requirements.txt`, `pyproject.toml`, `pom.xml`, and Gradle files so IDE launch targets are smarter.
- **Window State Persistence:** Window size and position are saved on exit, with a screen safety guard to avoid restoring off-screen coordinates.
- **Power User Controls:** Settings now includes controls for Always on Top, 80-100% opacity, minimize to tray, startup state, and modal background dimming.
- **Custom Keyboard Mapping:** Settings now includes a Keyboard Mapping modal for Workspace Tools, Find, and primary action shortcuts.
- **System Tray Integration:** The app can minimize to tray with Show and Exit menu actions when the `pystray` dependency is available.
- **Settings Layout Fix:** The Settings modal is taller and scrollable so the Save button is no longer clipped.

======================

## version 1.5.1

*UX & Navigation Core* — A patch that improves daily navigation with workspace history, keyboard navigation, smarter IDE integration, and clearer clone results.

### enhancement:
- **Recent Workspaces v1:** Exported, generated, and imported `.json` workspaces are remembered automatically, can be quick-loaded from Workspace Tools, cleared manually, and limited from Settings.
- **Basic Smart IDE Integration:** VS Code, Cursor, Visual Studio, and File Explorer detection now checks registry entries, PATH, and common install paths; the Open button always shows a choice menu.
- **System Theme Sync:** Light/Dark/System theme changes are applied immediately to the UI and custom components without restart.
- **Basic Keyboard Shortcuts:** Added contextual `Ctrl+G`, `Ctrl+F`, `Ctrl+Enter`, and `Esc` behavior.
- **Smart Tooltips:** Tooltips are smoother, theme-aware, dynamic, and cover Workspace Tools plus the Success Dialog actions.
- **Enhanced Success Dialog:** Clone results now show absolute paths, one-click path copy, visual feedback, and integrated IDE/File Explorer selection.
- **Empty State UI:** Empty repository lists now render helpful in-list guidance and CTAs instead of a not-found popup.

======================

## version 1.5.0

*Workspace Tools Maturation* — Feature update to mature the Workspace Tools utility with productivity enhancements.

### enhancement:
- **Find & Replace:** Added a new frame below the input textbox to quickly find and replace substrings (e.g., stripping the `-sit` suffix from repo names).
- **Format & Clean:** Added a button to instantly tidy up the input text (sort alphabetically, remove empty lines, and remove duplicates) prior to validation.
- **Clear All:** Added a quick action button to empty the textbox.
- **Bulk Import from File:** Supports direct repository list import from `.txt`, `.csv`, and `.xlsx` (Excel) files into the input textbox.
- **Validation Preview:** The application now displays a confirmation dialog summarizing validation results (counts of valid and invalid repos) before prompting to save the JSON workspace file.

======================

## version 1.4.5

*Branch Configuration Selection Hotfix* — A patch to ensure the Branch Configuration modal always uses the repositories the user actually selected.

### bugfix:
- **Selected Repository Snapshot:** Branch Configuration now creates a snapshot of selected repositories when the clone button is pressed, so repository rows, selected branches, and clone jobs no longer depend on global selection state that may change after the modal opens.
- **Visible Selection Ordering:** Repositories visible and checked on the active page are shown first in the Branch Configuration modal, followed by selections from other pages when present.
- **Stale Pagination Guard:** Expired repository fetch results are now ignored so an old page cannot overwrite a newer page and create invalid states such as `Page 17 of 7`.

======================

## version 1.4.4

*Hotfix* for a runtime error in Workspace Tools.

### bugfix & enhancement:
- **Generate Workspace:** 
  1. Fixed two consecutive `AttributeError` exceptions related to the logging function and `GitLabAPI` (`self.api`) instantiation.
  2. **Smart Search Fallback**: The `Generate Workspace` input now accepts simple **repository names** without needing full namespaces (e.g. `msf_posting_maintenance`). If the exact path is invalid, the API will automatically perform a smart search and match the exact repository name.

======================

## version 1.4.3

*Hotfix* addressing lingering user interface quirks concerning icon flickering on secondary modal windows.

### bugfix:
- **modal icon flickering:** Fixed the icon flickering issue without using the `withdraw` method or `after()` delays. The application now applies the favicon immediately upon creation and intercepts CustomTkinter's internal icon methods, preventing it from reverting to the default Tkinter icon. Modals will now load instantly without any flickering or delays.

======================

## version 1.4.2

*Workspace Tools Stability* — A patch to stabilize the Workspace Tools modal and prevent the app from feeling locked while workspace operations are running.

### bugfix:
- **Modal Lifecycle:** Import/Export no longer destroys the Workspace Tools modal before opening file dialogs, so the modal does not appear to vanish unexpectedly.
- **Modal Visibility & Focus:** Fixed cases where a modal remained logically active but did not render or raise on screen, including the profile overlay left behind after pressing `ESC`.
- **UI Freeze Guard:** Generate no longer disables the whole grabbed modal. The app stays responsive while validation runs, with a visible status and temporarily locked input controls.
- **Duplicate Modal Guard:** Repeated clicks on Workspace Tools now focus the existing modal instead of creating multiple focus-grabbing modals.
- **Thread-Safe UI Callback:** Background process callbacks are now scheduled with mainloop guards so the app does not raise errors when a window has already closed or a worker finishes late.
- **Clone Workflow Polish:** Repository labels are readable in dark theme, the Clone button returns to its normal style after completion, and the folder picker title now follows the translation system.

======================

## version 1.4.1

*Startup Hotfix* — A small patch to fix a crash when opening the application from the 1.4.0 release build.

### bugfix:
- **Workspace Tools Startup Crash:** Fixed the action button state updater still referencing the old `btn_export` button after export was moved into the *Workspace Tools* modal in 1.4.0. The app no longer fails at startup with `_tkinter.tkapp object has no attribute 'btn_export'`.

======================

## version 1.4.0

*UX & Clone Control* — A massive user interface revamp introducing streamlined workspace tools, active clone monitoring, and safe real-time background task cancellation.

### feature:
- **Workspace Tools:** Consolidated the Import/Export buttons and introduced a *Generate Workspace* capability from raw text. This seamlessly strips duplicates and empty lines, actively validating repository existence against the GitLab API.
- **Graceful Cancellation:** The bulk repository *clone* process is now safely terminable. Click the red *Cancel* button, and the app will halt its active processing queue gracefully utilizing `threading.Event()`.
- **Bulk Apply & UI Refresh:** Implemented a new *Bulk Apply* master row in the clone configuration table alongside dynamic *middle truncation* for obscenely long repository titles to preserve a crisp layout.
- **Disk Protection Check:** Introduced a proactive validation gate against minimum disk limits (configurable in *Settings*) before firing off large-batch git operations to avert full-disk crashes.
- **Progress Tracking & Log Export:** Fleshed out live logs with `[1/N]` counter notation for granular progress visibility. Also embedded an *Export Log* button into the completion dialog to save `.txt` dumps.

### bugfix:
- **Flashing Terminal (Windows):** Forcibly injected `CREATE_NO_WINDOW` flags into all hidden subprocess executions. Cmd pop-ups will no longer flicker across the screen during intense behind-the-scenes git interactions.

======================

## version 1.3.2

*Documentation & Community Shift* — This minor patch release is dedicated entirely to refactoring the Markdown (Documentation) structure across the project source. We pivoted the repository identity towards an extensive Bilingual Ecosystem (Indonesian logic and English globally scaled framework structures).

### docs:
- **Language Normalization:** Rewriting the entirety of the application's guidebook inside `README.md` adapting an IT-natural terminology (mixing English industry tech-speak into localized phrases) to make it highly digestible for software engineers.
- **Bilingual Equality:** Sculpting a true Dual-Language ecosystem by replicating all fundamental organizational guidelines into `.en.md` equivalents (`CONTRIBUTING_en.md`, `SECURITY_en.md`, `STRUCTURE_en.md`).
- **Community Templates:** Publishing structural PR and GitHub Issue templates nested inside the `/.github/` directory to construct a barrier of standards against external user-submitted error reports and enhancement requests.

======================

## version 1.3.1

*Hotfix* PyInstaller logic compilation logic and exterminating major graphic UI rendering (tearing) remnants lingering from the v1.3.0 architectural disruption.

### bugfix:
- **pyinstaller keyring bug:** Injected aggressive `--copy-metadata keyring` & `--hidden-import keyrings.alt` parameters directly onto the `build.py` bundler script to ensure the executable binaries do not crash due to missing Keyring API module exports upon freeze.
- **portable absolute pathing:** Rewritten dynamic path targeting logic from retrieving execution dir (`cwd`) into enforcing the absolute `sys.executable` binary. The `.exe` build will strictly no longer deploy junk backup files arbitrarily upon random launch across Windows Explorer sub-directories.
- **modal icon flickering:** Patched a severe ~15ms `deiconify` logic desync. Modal dialogue windows will perfectly delay their popup rendering thread up until the underlying icon parameters are fully mapped resulting in 100% flicker-free experiences.

======================

## version 1.3.0

*Cross-Platform OS Vault* — Huge underlying configuration architectural overhaul (Erasing old DPAPI dependency encryption schemas) entirely into the `Secret Service` DBus layer mechanisms. This release purely repairs immediate startup Fatal Crashes provoked upon macOS execution constraints.

### feature:
- **cross-platform credential:** Executed absolute integration involving the `keyring` Python module. Your PAT token access strings are dynamically bolted downward towards your local secured hardware vaults (*Windows Credential Manager* / *macOS Keychain* / Linux *Secret Service*).
- **clean executable config:** Directed generic user config (`config.json`) dumps, isolating them cleanly upwards routing toward your global OS User Profile Absolute Directory bounds (`~/.glrc/`).
- **automated migration:** The booting script now autonomously disassembles legacy encryption logic format files (`config.dat`), rips the credential, formats it onto the new Keyring setup, deletes the old files effortlessly via a unified startup hook iteration.

======================

## version 1.2.3

Cosmetic UI/i18n restructuring and eradication of bare-bones Subprocess Shell tracebacks.

### bugfix:
- **fixed raw exception logging:** Encapsulated `FileNotFoundError` (`[WinError 2]`) bounds over the async target threads upon executing a missing or unavailable local Git installation binary path. Throws standard GUI alerts rather than terminal tracebacks.
- **smart git detection:** Immediately evaluates OS level Git Path integrity instantaneously upon firing the execution batch button.

### improvement:
- **i18n completion:** Relocated remaining 15+ hard-coded isolated Indonesian strings off Python core logic explicitly onto the translation matrix `i18n.py`.
- **clean magic variables:** Decentralized hardcoded numbers (retry limits, clone concurrent boundaries, async thresholds) fully isolating them exclusively as global variables inside `constants.py`.

======================

## version 1.2.2

Network Operations Layer Hardening.

### bugfix:
- **fixed timeout hang:** Injected explicit `15-30s` timeout disconnection boundaries onto all API `requests.get()` handlers to actively dismiss unlimited UI looping caused upon pinging corrupted/offline intra-net GitLab servers.
- **fixed bare except logic:** Trimmed out generic bare `except:` blocks rendering via Modal configurations avoiding Python's global `SystemExit` interrupt interceptions.

### feature:
- **URL host validation:** The application will aggressively throw exceptions refusing generic invalid URL schema string inputs strictly requiring structural components initiating `https://`.

======================

## version 1.2.1

Git Auth Logic Iteration Hotfix — Fixing broken git auto-pull synchronizations failing at local Authentication blocks.

### bugfix:
- **fixed git pull loop:** Pull logic looping failed throwing blocked subprocess loops resulting from non-configured origin SSH bounds. Fixed by dynamically spoofing repo parameters allocating a pseudo Origin remote config embedded with the fake injected token precisely a single second before initiating pull, and sequentially purging it (destroying config trace).

======================

## version 1.2.0

*UI Polish & Matrix Scaling* — Total interface scaling manipulation replacing previous unicode generic emojis natively un-renderable across arbitrary Windows parameters, converting everything directly mapping via native Material Icon graphics via internal rendering hooks.

### bugfix:
- **icon jitter alignments:** Mitigated grid bouncing errors causing UI elements (icon anchors) visibly moving 1-2 pixels apart rapidly over cursor hover updates. PIL renders bounded correctly utilizing anchor `anchor="mm"`.
- **ghost pat expiry:** The token lifecycle bounds Modal incessantly displays a spoofed `7 days` duration string notwithstanding permanent configuration constraints assigned during token creations. Patched!

### feature:
- **material design injection:** Graphic UI module currently iterates dynamically to rasterize raw Glyph Material variables exclusively invoking native Pillow (PIL) integrations handling rendering standardizing the global interface size parity perfectly aligned without spacing jitters.

======================

## version 1.1.0

Post-clone GUI Integration Modals & dynamic IDE bootloader functionality incorporating robust JSON workspace configurations schemas imports.

### bugfix:
- **json import glitch:** Ingesting Workspace `.json` arrays fundamentally wrecks numerical page count (`Pagination`) UI logics breaking back to Null boundary loops integers.
- **modal ghost clicks:** Multi-window TopLevel UI configurations colliding triggering dual `grab_set()` locks internally under Unix constraints provoking memory OS stalls natively deleting redundant function triggers.

### feature:
- **IDE cross-shell detection:** An extremely elegant modal intercept pops up cleanly terminating repository download arrays launching buttons actively firing out to local bootloaders deploying specifically *VS Code Executables / Fallback IDEs*. Smart logical routing redirects bounds down to native File Explores OS bounds whenever local installations aren't structurally locatable.

======================

## version 1.0.0

*Initial Release* (Production Release Phase). Launching the mass cloner logical execution subsystem natively scaling multithreaded array iterations supporting dynamic Language Translations matrices (EN/ID) visually running on modern CustomTkinter frameworks natively supporting GUI windows instances bounds implementations.
