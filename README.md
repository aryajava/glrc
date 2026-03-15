<div align="center">
  <img src="https://github.com/aryajava/glrc/blob/main/assets/icons/logo.png" alt="GLRC Logo" width="128" height="128" />
  <h1>GLRC: GitLab Repo Cloner</h1>
  <p><strong>A robust, cross-platform desktop application designed to batch clone, update, and manage GitLab repositories effortlessly.</strong></p>
  
  <p>
    <a href="README.md">English</a> • <a href="README_id.md">Bahasa Indonesia</a>
  </p>

  <p>
    <img src="https://img.shields.io/badge/python-%E2%89%A53.8-blue?logo=python&logoColor=white" alt="Python 3.8+">
    <img src="https://img.shields.io/badge/GUI-CustomTkinter-blueviolet" alt="GUI: CustomTkinter">
    <img src="https://img.shields.io/badge/license-MIT-green" alt="License: MIT">
    <img src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey" alt="Cross-Platform">
    <img src="https://img.shields.io/badge/i18n-English%20%7C%20Indonesian-orange" alt="Bilingual">
  </p>
</div>

<hr>

## Table of Contents
- [Why GLRC?](#why-glrc)
- [How It Works](#how-it-works)
- [Key Features](#key-features)
- [Quick Start](#quick-start)
- [Building from Source](#building-from-source)
- [License](#license)

---

## Why GLRC?

Handling hundreds of repositories across multiple projects and teams on GitLab can be excruciating. Finding the right repositories, cloning them one by one, deciding whether you should do HTTPS or SSH, and making sure existing local repositories are updated properly is a tedious task. 

**GLRC** bridges this gap. We created this tool for developers, managers, and DevOps engineers who handle massive workspaces. It entirely automates bulk repository orchestration by bringing it into a fast, threaded, and deeply localized Desktop UI.

## How It Works

At its core, GLRC talks directly to the GitLab API securely using your Personal Access Token. 
1. **Connect & Fetch**: You provide your token, and GLRC fetches all your accessible repositories, supporting multi-page loading and wildcard searches instantly.
2. **Select & Configure**: Check the repositories you want. Choose specific branches dynamically fetched from your repositories en masse, or even map them to spin-up new feature branches.
3. **Execute**: The underlying engine evaluates every selected repository. If the folder already exists and has a `.git` index, it intelligently triggers an auto `git pull`. Otherwise, it securely fires a concurrent `git clone`, handling errors and SSH/HTTPS conversions automatically under the hood.

---

## Key Features

- **Multi-Selection & Batch Operations**: Select multiple repositories and clone them simultaneously.
- **Smart Auto-Pull**: Automatically detects if a repository exists and performs a `git pull` sequence to keep your local repositories up-to-date.
- **Concurrent Execution**: Executes Git commands using a parallel thread pool for maximum speed.
- **Protocol Flexibility**: Clone securely via HTTPS (using encrypted PAT data) or SSH.
- **Auto-Retry Resiliency**: Intermittent connectivity failures are mitigated automatically with a 3-try retry strategy.
- **Workspace State Management**: Export your currently selected repositories as a JSON workspace and import them later to resume work.
- **Intelligent Pagination & Search**: Rapidly fetch hundreds of repositories with a fast, wildcard-supported search system. 
- **Bilingual (i18n)**: Out-of-the-box support for English (`en`) and Indonesian (`id`).
- **Customizable Aesthetics**: Seamlessly integrate with OS System themes, or force Dark/Light GUI modes.

---

## Quick Start

To run the script directly from the source code:

1. Ensure you have **Python 3.8+** installed.
2. Clone or download this project.
3. Initialize and activate your virtual environment:   
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
   *(On macOS/Linux, use `source .venv/bin/activate`)*
4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run the application:
   ```bash
   python main.py
   ```

## Building from Source

This application can be bundled into a standalone executable, meaning users will not need Python installed on their endpoints. We provide builder scripts: `build.bat` (Windows) and `build.sh` (Linux / macOS).

You can supply the default language you want bundled into the executable:
- For English: `build.bat en` or `./build.sh en`
- For Indonesian: `build.bat id` or `./build.sh id`

The finalized application will be placed inside the `dist` directory.

---

## License
Distributed under the [MIT License](LICENSE).

<p align="center">
  <i>Made with ❤️ by the GLRC Contributors</i>
</p>
