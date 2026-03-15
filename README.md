<div align="center">
  <img src="assets/icons/logo.png" alt="GLRC Logo" width="128" height="128" />
  <h1>GLRC: GitLab Repo Cloner</h1>
  <p><strong>Cross-platform desktop app to batch clone, update, and manage GitLab repositories.</strong></p>

  <p>
    <a href="README.md">English</a> • <a href="README_id.md">Bahasa Indonesia</a>
  </p>

  <p>
    <img src="https://img.shields.io/badge/python-%E2%89%A53.10-blue?logo=python&logoColor=white" alt="Python 3.10+" />
    <img src="https://img.shields.io/badge/GUI-CustomTkinter-blueviolet" alt="GUI: CustomTkinter" />
    <img src="https://img.shields.io/badge/license-MIT-green" alt="License: MIT" />
    <img src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey" alt="Cross-Platform" />
    <img src="https://img.shields.io/badge/i18n-English%20%7C%20Indonesian-orange" alt="Bilingual" />
  </p>
</div>

## Overview

GLRC is built for teams that handle many GitLab repositories and need fast, repeatable operations from one desktop interface.

Core flow:
1. Connect to GitLab using Personal Access Token.
2. Fetch/search repositories with pagination.
3. Select repositories and branch strategy.
4. Execute concurrent clone or auto-pull.

## Key Features

- Batch repository selection and concurrent execution.
- Smart auto-pull for existing local repositories.
- HTTPS or SSH clone mode.
- Retry mechanism for intermittent failures.
- Workspace export/import (`.json`).
- Bilingual UI (`en`, `id`).
- Theme options (System, Light, Dark).
- Packaged standalone binaries via PyInstaller.

## Quick Start

1. Create and activate a virtual environment.
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```
2. Install dependencies.
   ```bash
   pip install -r requirements.txt
   ```
3. Run application.
   ```bash
   python main.py
   ```

## Build

Build scripts use a unified cross-platform pipeline (`scripts/build.py`).

- Windows:
  - `build.bat`
  - `build.bat en`
  - `build.bat id`
- Linux/macOS:
  - `./build.sh`
  - `./build.sh en`
  - `./build.sh id`

Output is generated in `dist/`.

## Release Assets

Release assets are published for:
- Windows: `glrc-en-windows.exe`, `glrc-id-windows.exe`
- Linux: `glrc-en-linux`, `glrc-id-linux`
- macOS: `glrc-en-macos`, `glrc-id-macos`

## Project Structure

- `main.py`: GUI entry point.
- `src/`: core modules, utilities, constants.
- `assets/fonts/`: bundled fonts.
- `assets/icons/`: app icons/logos.
- `scripts/`: build/icon helper scripts.
- `.github/workflows/`: CI/release automation.

## License

Distributed under the [MIT License](LICENSE).
