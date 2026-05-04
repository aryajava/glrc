# GLRC — Roadmap Versi

## Konvensi Versioning: `x.y.z`

| Segmen | Nama | Kapan Dinaikkan | Contoh |
|---|---|---|---|
| **x** | **MAJOR** | Perubahan arsitektur besar, breaking changes, atau rewrite signifikan | `1.x.x` → `2.0.0` |
| **y** | **MINOR** | Fitur baru atau peningkatan substansial, backward-compatible | `2.0.x` → `2.1.0` |
| **z** | **PATCH** | Perbaikan bug, hotfix, koreksi kecil — tidak ada fitur baru | `1.3.0` → `1.3.1` |

---

## 📜 Riwayat Rilis (Telah Rampung)

| Versi | Rilis | Ringkasan Perubahan |
|---|---|---|
| **v1.0.0** | Awal | Rilis perdana core fungsionalitas clone dan GUI dasar. |
| **v1.1.0** | Minor | Penambahan integrasi _pagination_ dan search. |
| **v1.2.0** | Minor | Peningkatan sistem autentikasi. |
| **v1.2.1** | Patch | Optimasi UI dan bugfix kredensial. |
| **v1.2.2** | Patch | *Hardening* — Validasi URL, deteksi biner `git`, perbaikan exception. |
| **v1.2.3** | Patch | *i18n & Constants* — Pelengkapan lokalisasi seluruh bahasa dan perbaikan *magic numbers*. |
| **v1.3.0** | Minor | *Cross-Platform & Security* — Menghapus DPAPI, migrasi `keyring`, dan struktur config baru. |
| **v1.3.1** | Patch | *Hotfix* — PyInstaller `keyrings.alt` bundling, *absolute pathing*, dan sinkronisasi ikon modal. |
| **v1.3.2** | Patch | *Documentation Shift* — Perombakan dokumen menjadi ekosistem dwibahasa & bahasa IT sehari-hari. |
| **v1.4.0** | Minor | *UX & Clone Control* — Silent clone, Workspace Tools (Generate/Export/Import), Disk Validation, dan fitur Bulk Apply branch. |
| **v1.4.1** | Patch | *Startup Hotfix* — Memperbaiki crash startup akibat referensi tombol export lama setelah Workspace Tools dipindahkan ke modal. |
| **v1.4.2** | Patch | *Workspace Tools Stability* — Menstabilkan modal/focus, mencegah UI terkunci, dan mengamankan callback dari background thread. |
| **v1.4.3** | Patch | *UI Hotfix* — Menghilangkan flickering pada ikon modal melalui immediate apply tanpa timer. |
| **v1.4.4** | Patch | *Hotfix* — Memperbaiki AttributeError pada fungsi Generate Workspace. |

---

## 📋 Peta Rilis Selanjutnya

```mermaid
gantt
    title GLRC Future Roadmap
    dateFormat YYYY-MM-DD
    axisFormat %b %Y

    section v1.x (UX & Feature)
    v1.4.0 - UX & Clone Control      :a1, 2026-05-10, 5d
    v1.5.0 - SSH & Update Notif      :a2, after a1, 5d

    section v2.x (Clean Code & Release)
    v2.0.0 - Core API Overhaul       :b1, after a2, 7d
    v2.1.0 - UI Segmentation         :b2, after b1, 5d
    v2.2.0 - Installer Release       :b3, after b2, 5d
```

---

## 📝 v1.3.2 — Documentation & Community Shift
> **Tipe: PATCH** — Pembaruan standar penulisan *Markdown* untuk pedoman repositori (Non-Code Changes).

| # | Item | Status |
|---|---|---|
| 1 | **Rombak Total Aturan Bahasa Dokumentasi** — Jadikan **Bahasa Indonesia** sebagai bahasa fundamental tunggal proyek. Tulis ulang `README.md` dan `STRUCTURE.md` menargetkan para developer Indonesia. Format English menjadi sekunder (`README_en.md`). | 🟢 Selesai (Released) |
| 2 | **Penyempurnaan Kejelasan & Contoh Nyata** — Menulis ulang seluruh panduan yang berbelit-belit/membingungkan di dalam `README.md`. Menyertakan contoh kasus penggunaan nyata (*real-world examples*) agar pengguna awam dapat langsung paham. | 🟢 Selesai (Released) |
| 3 | **Community Base**: Buat struktur panduan kontribusi resmi (`CONTRIBUTING.md`), standar keamanan (`SECURITY.md`), serta *PR/Issue template* dalam Bahasa Indonesia baku. | 🟢 Selesai (Released) |
| 4 | **GitHub Wiki Setup**: Siapkan struktur landasan untuk GitHub Wiki bagi dokumentasi yang bersifat buku panduan teknis yang ekstensif. | 🟢 Selesai (Released) |

> [!SUCCESS]
> **Status:** Rilis v1.3.2 telah resmi dipublikasikan ke cabang utama GitHub!

---

## ✨ v1.4.0 — UX & Clone Control
> **Tipe: MINOR** — Fitur interaksi GUI utama dan pemantauan proses.

| # | Item | Status |
|---|---|---|
| 1 | **Tombol Cancel/Abort** saat clone berjalan — menggunakan `threading.Event()` untuk graceful stop | 🟢 Selesai (Released) |
| 2 | **Progress per-repo** — tampilkan status setiap repo (cloning/pulling/done/failed) di log atau UI | 🟢 Selesai (Released) |
| 3 | **Tombol Export/Copy Log** — simpan log ke file `.txt` atau copy ke clipboard | 🟢 Selesai (Released) |
| 4 | **Disk space check** — peringatan sebelum clone batch besar jika disk space kurang | 🟢 Selesai (Released) |
| 5 | **Fitur "Bulk Apply" Branch** — master input di atas tabel untuk mengisi serentak (Clone from Branch, New?, New Branch Name) ke semua baris | 🟢 Selesai (Released) |
| 6 | **Pencegahan Error & Validasi UI** — *Sticky Header* pada tabel, pemotongan teks (*middle truncation*) nama repo panjang, dan *error state* merah jika form kosong | 🟢 Selesai (Released) |
| 7 | **Silent Clone (OS Windows)** — Menyembunyikan jendela *command prompt* berkedip (*flashing terminal*) saat mengeksekusi subprocess `git` via argumen `CREATE_NO_WINDOW` | 🟢 Selesai (Released) |
| 8 | **Generate Workspace dari Teks Mentah** — Jendela *Input Text/TextArea* untuk *copy-paste* puluhan/ratusan list nama repositori (biasanya dari Excel/Notepad/Jira) untuk disulap otomatis menjadi file `.json` Workspace. Terdiri dari 4 subsistem teknis:<br><br>• **UI De-cluttering:** Menyatukan tombol *Export, Import, Generate* ke dalam satu *Dropdown/Modal* "Workspace Tools".<br>• **Auto-Parsing Level Lanjut:** *Cleansing* menggunakan *Set()* untuk membuang baris duplikat, serta *Regex* untuk memotong URL penuh (misal membuang `https://` dan `.git`) atau spasi kosong.<br>• **API Existence Validation:** Melakukan *ping* massal ke server GitLab untuk mem-validasi apakah nama repo tersebut benar-benar ada sebelum menuliskannya ke `.json` (Mencegah error *Repository Not Found 404* saat dikloning).<br>• **Count Feedback:** Dialog pop-up pelaporan visual ke pengguna (Contoh: *"Dari 81 input, ditemukan 15 Repositori unik. Workspace berhasil di-Generate"*). | 🟢 Selesai (Released) |

> [!SUCCESS]
> **Status:** Rilis v1.4.0 telah resmi diselesaikan dan di-patch.

---

## 🛠️ v1.4.2 — Workspace Tools Stability
> **Tipe: PATCH** — Hotfix stabilitas modal, Workspace Tools, dan callback UI dari proses background.

| # | Item | Status |
|---|---|---|
| 1 | **Modal Visibility & Focus** — Modal yang masih aktif secara logika kini dipaksa tampil, fokus, dan melepas `grab_set()` dengan aman saat ditutup. | 🟢 Selesai (Released) |
| 2 | **Workspace Tools Guard** — Import/Export tidak lagi menghancurkan modal sebelum file dialog, Generate tidak mengunci seluruh modal, dan klik berulang hanya memfokuskan modal yang sudah ada. | 🟢 Selesai (Released) |
| 3 | **Thread-Safe UI Callback** — Callback dari proses background dijadwalkan melalui helper UI agar tidak memanggil widget setelah mainloop/window berakhir. | 🟢 Selesai (Released) |
| 4 | **Clone Workflow Polish** — Label repo dark theme, reset tombol Clone, dan judul dialog pilih folder dirapikan agar konsisten dengan UI/i18n. | 🟢 Selesai (Released) |

> [!SUCCESS]
> **Status:** Patch v1.4.2 telah dicatat sebagai perbaikan stabilitas rilis 1.4.x.

---

## ✨ v1.5.0 — SSH Maturity & Version Update
> **Tipe: MINOR** — Fitur baru: Kematangan infrastruktur SSH dan Notifikasi Update.

| # | Item | Status |
|---|---|---|
| 1 | **SSH key validation** — cek `~/.ssh/id_rsa` atau `id_ed25519` ada sebelum clone SSH | ⚪ Pending |
| 2 | **SSH error feedback** — pesan error khusus jika SSH key tidak ditemukan atau agent tidak running | ⚪ Pending |
| 3 | **Auto-check version** — cek GitHub API `/releases/latest` saat startup, tampilkan notifikasi jika versi baru tersedia | ⚪ Pending |
| 4 | **IDE detection Linux/macOS** — extend `detect_available_ides()` untuk scan PATH (Linux) dan Applications (macOS) | ⚪ Pending |

**Estimasi**: ~3-5 hari

---

## 🚀 v2.0.0 — Core Architecture Overhaul
> **Tipe: MAJOR** — Pembersihan pondasi inti aplikasi (Backend-side) memecah "God Class" pada logika koneksi dan sistem shell file.

| # | Item | Status |
|---|---|---|
| 1 | **Extract: GitLabAPI Class** — Pisahkan semua pemanggilan `requests.get()` menjadi kelas mandiri yang diinjeksi (*Dependency Injection*). | ⚪ Pending |
| 2 | **Extract: GitOperations Class** — Pindahkan seluruh instruksi command `subprocess.run` (Clone, Pull, Checkout) menjadi entitas terpisah. | ⚪ Pending |
| 3 | **Extract Method di _process_single_repo** — Cincang kerumitan error handling menjadi fungsi bertahap (Validasi -> Exec -> Config -> Clean). | ⚪ Pending |

**Estimasi**: ~4-7 hari

---

## 🎨 v2.1.0 — UI Component Segmentation
> **Tipe: MINOR** — Pembersihan pondasi grafis (Frontend-side) untuk mengeliminasi sisa "God Class" pada `main.py`.

| # | Item | Status |
|---|---|---|
| 1 | Pindahkan desain `LoginFrame` ke /src/ui/login.py. | ⚪ Pending |
| 2 | Pindahkan desain `SettingsModal`/`ProfileModal` menjadi object Class independen. | ⚪ Pending |
| 3 | Implementasikan *Callback / Event Emitters* yang menghubungkan UI terpisah dengan Core API. | ⚪ Pending |

**Estimasi**: ~3-5 hari

---

## 🌍 v2.2.0 — Cross-Platform Installers
> **Tipe: MINOR** — Publikasi kemudahan instalasi untuk *End-User*.

| # | Item | Status |
|---|---|---|
| 1 | **Distribusi Resmi Terinstal**: Buat installer `Setup-GLRC.exe` via Inno Setup mendampingi rilis executable portable saat ini. | ⚪ Pending |
| 2 | **Target Cross-Platform Build**: Otomasi penyusunan `.AppImage` (Linux) atau `.dmg` (macOS) di arsitektur CI/CD. | ⚪ Pending |

**Estimasi**: ~3-5 hari

---

## 🌌 Eksplorasi Skala Cloner (Beyond v2.x)
Sesuai haluan utama GLRC yang berstatus mutlak sebagai **GitLab Repo Cloner**, berikut adalah potensi perluasan kekuatan *cloning & pulling* tanpa merusak identitas aplikasi:

| # | Potensi Fitur *Enterprise Cloner* | Penjelasan | Status |
|---|---|---|---|
| 1 | **Sub-Group & Folder Batch Target** | Mengizinkan pengguna mencantumkan link spesifik folder tim (co: `gitlab.com/tim-backend/service/*`). GLRC akan memanen seluruh repositori yang memijak tanah *group* tersebut secara rekursif hanya dengan 1 link grup. | ⚪ Pending |
| 2 | **Cron / Auto-Fetch Sinkron Cepat** | Menyediakan mode pemanggilan UI tersembunyi (*headless mode*). Melalui *Windows Task Scheduler / Linux CronJob*, aplikasi berjalan otomatis jam 3 pagi menarik puluhan data pembaharuan repo, memperbarui status komputer pengguna secara _offline_ tiap hari. | ⚪ Pending |
| 3 | **Smart Template Cloning (Boilerplate Maker)** | Setelah berhasil mengunduh suatu pola repo (misalnya project _template-vuejs_), GLRC akan menambahkan perintah opsi "Buat Menjadi Proyek Kosong" (menghancurkan direktori `.git/` bawaan otomatis). Berfungsi brilian untuk setup awal developer! | ⚪ Pending |
| 4 | **Data Filter & Size Estimation** | Saat mencari puluhan repositori, berikan saringan: *Abaikan repositori di atas 2GB* atau *Sortir repositori yang baru di-update 1 minggu terakhir* untuk menghindari clone yang membengkakkan _hardisk_ karena salah pilih. | ⚪ Pending |
| 5 | **OAuth2 Login (Identity Provider)** | Implementasi login satu tombol via Browser menggunakan alur *Authorization Code Flow with PKCE*. Menghilangkan kebutuhan *copy-paste* PAT secara manual. | ⚪ Pending |

> [!NOTE]
> **Spesifikasi Teknis Registrasi OAuth2 (Tahap 1):**
> - **Nama:** `GLRC: GitLab Repo Cloner`
> - **Redirect URI:** `http://localhost:15842` (Port unik untuk menghindari tabrakan servis lain).
> - **Confidential:** **Uncheck** (Aplikasi desktop adalah *Public Client*).
> - **Scopes:** Centang `api` dan `read_repository`.
> - **Keamanan:** Mendukung GitLab Perusahaan (*Self-hosted*) secara aman melalui protokol OAuth2 standar.
