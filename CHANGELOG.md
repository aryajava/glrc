# Changelog

All notable changes to GLRC (GitLab Repo Cloner) will be documented in this file.

======================

## version 1.3.1

Hotfix kompilasi PyInstaller dan perbaikan rendering antarmuka pengguna *(UI rendering)* peninggalan versi 1.3.0. 

### bugfix:
- pyinstaller keyring bug: Menambahkan flag ekstensif `--copy-metadata keyring` dan `--hidden-import keyrings.alt` ke skrip *bundler* `build.py` untuk menggaransi berjalannya fitur kredensial pada distribusi *binary*.
- portable absolute pathing: Memodifikasi skrip migrasi agar mendeteksi letak sesungguhnya dari `glrc.exe` menggunakan metode `sys.executable` alih-alih `cwd`, menjaga migrasi `config.dat` versi lawas agar selalu stabil.
- modal icon flickering: Menambahkan _delay timing rendering_ yang memaksa sistem menunda sinkronisasi pemunculan (_deiconify_) kotak dialog (modal) sebesar ~15ms hingga widget benar-benar rampung termuat. Ini menuntaskan isu *tearing* / keterlambatan ikon aplikasi pada semua kotak modal.

======================

## version 1.3.0

Cross-Platform & Security — perombakan arsitektur penyimpanan konfigurasi untuk mematangkan dukungan lintas OS (Cross-platform) dan meningkatkan standar keamanan. Rilis ini mengatasi crash fatal pada Linux dan macOS yang terjadi pada versi sebelumnya akibat _dependency_ DPAPI Windows.

### feature:
- cross-platform credential standard: Implementasi penuh pustaka `keyring` (terintegrasi ke *Windows Credential Manager* / *macOS Keychain* / Linux *Secret Service*).
- clean executable vault: Memisahkan file konfigurasi `config.json` sebagai data non-sensitif portabel dan mengisolasi letaknya di direktori khusus *User Profile* (`~/.glrc/`) guna menghindari "file sampah" ketika menjankan _.exe_ secara *portable*.
- automated secure migration: Secara otomatis membongkar file `config.dat` (enkripsi versi 1.2 lama) saat startup pertama kali, memindahkan Sandi ke dalam Keyring, mencadangkannya menjadi `.bak`, lalu menghapus modul Windows Native (`dpapi_utils`).

======================

## version 1.2.3

Perbaikan teks i18n dan penanganan error git binary yang lebih elegan dari versi sebelumnya.

### bugfix:
- fixed raw exception logging: Menangkap `FileNotFoundError` / `[WinError 2]` saat proses clone/pull dan menampilkan log user-friendly ("[!] Git tidak terinstall atau tidak ditemukan") daripada error stack trace kasar yang membingungkan.
- fixed thread start missing git check: Menambahkan pengecekan instalasi `git` di awal proses clone untuk menghentikan proses secepatnya jika `git` tidak ada di sistem.

### improvement:
- i18n completion: Memindahkan semua sisa hardcoded Indonesian strings pada log dan UI (15+ strings) ke dalam sistem translasi `i18n.py`.
- pagination fix: Menambahkan missing translation key `"page"` yang hilang di versi sebelumnya.
- code cleanup: Mengganti parameter koneksi yang hardcoded di `main.py` menggunakan konstanta tersentralisasi di `constants.py` (`MAX_RETRY_ATTEMPTS`, `MAX_CONCURRENT_CLONES`, `RETRY_DELAY_SECONDS`).

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
