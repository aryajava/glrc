<div align="center">
  <img src="assets/icons/logo.png" alt="GLRC Logo" width="128" height="128" />
  <h1>GLRC: GitLab Repo Cloner</h1>
  <p><strong>A battle-tested cross-platform desktop application to effortlessly batch clone, update, and manage your GitLab repositories.</strong></p>

  <p>
    <a href="README.md">🇮🇩 Bahasa Indonesia (Situs Utama)</a> • <a href="README_en.md">🇬🇧 English</a>
  </p>

  <p>
    <img src="https://img.shields.io/badge/python-%E2%89%A53.10-blue?logo=python&logoColor=white" alt="Python 3.10+" />
    <img src="https://img.shields.io/badge/GUI-CustomTkinter-blueviolet" alt="GUI: CustomTkinter" />
    <img src="https://img.shields.io/badge/license-MIT-green" alt="License: MIT" />
    <img src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey" alt="Cross-Platform" />
  </p>
</div>

## 📌 Overview

GLRC is designed specifically for software engineers and DevOps teams who handle a massive amount of GitLab repositories. Instead of manually running `git clone` or `git pull` from the terminal one by one, GLRC provides a lightning-fast desktop interface to execute concurrent Git operations.

### How it Works
1. Connect securely to your GitLab server using a **Personal Access Token**.
2. GLRC fetches your repositories with smooth pagination.
3. Select multiple repositories and choose your target branch.
4. Execute **batch cloning** or **auto-pulling** concurrently with a single click.

## ✨ Key Features

- **Concurrent Execution Engine**: Clone or pull dozens of repositories at the same time.
- **Smart Auto-Pull**: Safely skip existing folders or pull the latest changes automatically.
- **Universal Connection**: Native support for **HTTPS** and **SSH** Git links.
- **Cross-Platform Vault**: Stores your token securely using the OS Keychain (Windows Credential Manager / Linux Secret Service).
- **Workspace Portability**: Export your selected repos to a `.json` file and share it with your team.
- **Standalone Binaries**: Works perfectly as a portable `.exe`, Linux executable, or macOS binary.

## 🚀 Quick Start (Developers)

If you want to run GLRC from the Python source code:

1. **Clone & Setup Environment**
   ```bash
   python -m venv .venv
   
   # Windows
   .venv\Scripts\activate
   
   # macOS/Linux
   source .venv/bin/activate
   ```
2. **Install Requirements**
   ```bash
   pip install -r requirements.txt
   ```
3. **Launch Application**
   ```bash
   python main.py
   ```

## 📦 Building Standalone Binaries

GLRC utilizes a unified build pipeline heavily optimized by PyInstaller.

- **Windows:**
  Run `build.bat` or `build.bat id` (for Indonesian binary).
- **Linux/macOS:**
  Run `./build.sh` or `./build.sh en`.

All generated binaries will strictly be forwarded to the `/dist` directory.

## 🤝 Community & Documentation

GLRC heavily embraces the Indonesian localized software engineering community. Therefore, our primary documentation is hosted in **Bahasa Indonesia**.

- [Contributing Guidelines & PR Rules](CONTRIBUTING.md)
- [Security Policy](SECURITY.md)
- [Architecture & Structure](STRUCTURE.md)

## 📄 License

Distributed under the [MIT License](LICENSE).
