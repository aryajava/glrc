# Version History (Changelog)

All algorithmic modifications, architectural restructurings, bugfixes, and feature injections concerning the GLRC application ecosystem will be publicly logged in this document.

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
