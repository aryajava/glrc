# Changelog

All notable changes to GLRC (GitLab Repo Cloner) will be documented in this file.

======================

## version 1.2.2

Bugfix & hardening — perbaikan keamanan, validasi input, dan stabilitas jaringan.

### bugfix:
- fixed timeout: semua `requests.get()` sekarang menggunakan timeout (15-30s) untuk mencegah UI freeze jika GitLab server down/hang
- fixed bare except: `except:` (bare except) di profile modal diganti `except Exception:` agar tidak menangkap `KeyboardInterrupt`/`SystemExit`
- fixed inline import: `import time` dipindahkan ke top-level module, bukan inline di dalam retry loop

### feature:
- added git binary detection: validasi `git` terinstall di PATH saat klik Connect — menampilkan pesan error user-friendly jika tidak ditemukan
- added URL validation: validasi format URL GitLab (harus `http://` atau `https://`, hostname tidak boleh kosong) sebelum mengirim token

### improvement:
- replaced `print()` dengan `logging` di `config_manager.py` dan `gitlab_api.py` — output error sekarang terintegrasi dengan Python logging system, bukan hilang di stdout PyInstaller binary

======================

## version 1.2.1

Hotfix — git pull gagal autentikasi pada repository yang sudah ada di lokal.

### bugfix:
- fixed git pull authentication: perintah `git pull origin <branch>` gagal karena remote URL tidak mengandung token (error: `could not read Username ... terminal prompts disabled`). Sekarang remote origin di-set sementara ke authenticated URL sebelum pull, lalu dikembalikan ke URL asli setelah selesai agar token tidak tersimpan di `.git/config`
- fixed pull log sanitization: output log saat pull sekarang juga menyembunyikan token (di-mask `********`), sama seperti pada clone

======================

## version 1.2.0

UI polish and icon system overhaul — replacing emoji text with Material Icons rendered via PIL, fixing visual jitter, and standardizing button sizes across the application.

### bugfix:
- fixed icon alignment: icon dalam tombol tidak sejajar dengan teks, diganti rendering dengan anchor="mm" (PIL center)
- fixed button jitter: klik tombol/checkbox menyebabkan tombol ber-icon bergeser karena CTkButton _draw() dipanggil ulang meskipun state tidak berubah
- fixed token duration display: setelah restore token, pat_days_entry selalu menampilkan "7" (default) alih-alih sisa hari aktual

### feature:
- added Material Icons untuk semua tombol: search, reset, select all, deselect all, export, import, logs (mengganti emoji teks)
- added _render_icon() helper: rendering glyph Material Icons ke CTkImage via PIL untuk digunakan sebagai button image
- added _set_btn_state() helper: mencegah configure() dipanggil jika state tidak berubah, menghilangkan visual jitter

### improvement:
- standardized button sizes: semua tombol icon+text height=32, toolbar icon-only 34x34, CTA height=44, modal footer height=36
- removed fixed width dari tombol icon+text: width otomatis menyesuaikan konten, mencegah content shift saat klik
- removed unused ICON_* imports: ICON_SEARCH, ICON_RESET, ICON_EXPORT, ICON_IMPORT, ICON_CHECK_ALL, ICON_UNCHECK_ALL, ICON_LOGS tidak lagi diimport sebagai CTkFont glyph (diganti CTkImage)

======================

## version 1.1.0

Post-clone IDE integration and import/export workspace fixes — adding OS-native IDE detection, cross-platform support, and resolving modal/icon rendering issues.

### bugfix:
- fixed import workspace: per_page override menyebabkan pagination rusak setelah import
- fixed import workspace: checkbox selection loop redundan yang tidak diperlukan
- fixed modal icon: mengganti double-delay (100ms+300ms) dengan pattern withdraw/deiconify + single backup
- fixed modal grab_set: menghapus panggilan grab_set() redundan di clone result dialog dan branch modal
- fixed i18n shadowing: variabel _ dari winreg.QueryValueEx meng-shadow fungsi _() i18n
- fixed clone result button: icon dan teks terpisah karena CTkButton hanya support satu font

### feature:
- added open in IDE: popup menu setelah clone untuk membuka repo di IDE yang tersedia
- added IDE detection via OS registry: membaca Windows Registry shell entries (Directory\shell) untuk mendeteksi IDE
- added cross-platform IDE detection: support macOS (Applications scan) dan Linux (PATH lookup)
- added File Explorer fallback: opsi buka folder di file manager selalu tersedia
- added Material Icons: icon open_in_new (e89f) untuk tombol "Buka"

### cleanup:
- removed duplicate root files: dpapi_utils.py, config_manager.py, i18n.py (sudah ada di src/)
- removed unused import shutil dari main.py

======================

## version 1.0.0

Initial release — GitLab repository cloner with GUI, multi-language support (EN/ID), encrypted token storage via Windows DPAPI, branch selection, and cross-platform build pipeline.
