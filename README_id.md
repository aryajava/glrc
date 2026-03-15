<div align="center">
  <img src="assets/icons/logo.png" alt="Logo GLRC" width="128" height="128" />
  <h1>GLRC: GitLab Repo Cloner</h1>
  <p><strong>Aplikasi desktop lintas platform untuk clone, update, dan kelola banyak repositori GitLab secara cepat.</strong></p>

  <p>
    <a href="README.md">English</a> • <a href="README_id.md">Bahasa Indonesia</a>
  </p>

  <p>
    <img src="https://img.shields.io/badge/python-%E2%89%A53.10-blue?logo=python&logoColor=white" alt="Python 3.10+" />
    <img src="https://img.shields.io/badge/GUI-CustomTkinter-blueviolet" alt="GUI: CustomTkinter" />
    <img src="https://img.shields.io/badge/lisensi-MIT-green" alt="Lisensi: MIT" />
    <img src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey" alt="Lintas Platform" />
    <img src="https://img.shields.io/badge/i18n-English%20%7C%20Indonesian-orange" alt="Dwi Bahasa" />
  </p>
</div>

## Ringkasan

GLRC dibuat untuk tim yang mengelola banyak repositori GitLab dan membutuhkan alur kerja yang cepat dari satu antarmuka desktop.

Alur utama:
1. Hubungkan aplikasi ke GitLab dengan Personal Access Token.
2. Ambil/cari repositori dengan pagination.
3. Pilih repositori dan strategi branch.
4. Jalankan clone paralel atau auto-pull.

## Fitur Utama

- Pilih banyak repositori sekaligus dan eksekusi paralel.
- Auto-pull otomatis jika repositori lokal sudah ada.
- Mode clone HTTPS atau SSH.
- Mekanisme retry untuk kegagalan sementara.
- Ekspor/impor workspace (`.json`).
- UI bilingual (`en`, `id`).
- Tema tampilan (System, Light, Dark).
- Dapat dibungkus jadi binary standalone dengan PyInstaller.

## Mulai Cepat

1. Buat dan aktifkan virtual environment.
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```
2. Install dependensi.
   ```bash
   pip install -r requirements.txt
   ```
3. Jalankan aplikasi.
   ```bash
   python main.py
   ```

## Build

Script build memakai pipeline lintas platform terpadu (`scripts/build.py`).

- Windows:
  - `build.bat`
  - `build.bat en`
  - `build.bat id`
- Linux/macOS:
  - `./build.sh`
  - `./build.sh en`
  - `./build.sh id`

Hasil build ada di folder `dist/`.

## Asset Release

Asset release dipublikasikan untuk:
- Windows: `glrc-en-windows.exe`, `glrc-id-windows.exe`
- Linux: `glrc-en-linux`, `glrc-id-linux`
- macOS: `glrc-en-macos`, `glrc-id-macos`

## Struktur Proyek

- `main.py`: entry point GUI.
- `src/`: modul core, utilitas, konstanta.
- `assets/fonts/`: font yang dibundle.
- `assets/icons/`: icon/logo aplikasi.
- `scripts/`: helper build/generate icon.
- `.github/workflows/`: otomasi CI/release.

## Lisensi

Didistribusikan di bawah [Lisensi MIT](LICENSE).
