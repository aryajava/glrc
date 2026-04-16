<div align="center">
  <img src="assets/icons/logo.png" alt="Logo GLRC" width="128" height="128" />
  <h1>GLRC: GitLab Repo Cloner</h1>
  <p><strong>Aplikasi desktop lintas platform (GUI-based) untuk menjalankan <i>Batch Clone</i> dan <i>Auto-Pull</i> massal ratusan repositori GitLab secara serempak.</strong></p>

  <p>
    <a href="README.md">🇮🇩 Bahasa Indonesia (ID)</a> • <a href="README_en.md">🇬🇧 English (EN)</a>
  </p>

  <p>
    <img src="https://img.shields.io/badge/python-%E2%89%A53.10-blue?logo=python&logoColor=white" alt="Python 3.10+" />
    <img src="https://img.shields.io/badge/GUI-CustomTkinter-blueviolet" alt="GUI: CustomTkinter" />
    <img src="https://img.shields.io/badge/Lisensi-MIT-green" alt="License: MIT" />
    <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey" alt="Cross Platform" />
  </p>
</div>

---

## 📌 Apa itu GLRC?

**GLRC** dibangun khusus untuk *Software Engineer* dan tim *DevOps* yang harus meng-handle banyak repositori GitLab lokal (arsitektur Microservices). Daripada harus membuka terminal dan mengetik `git clone` atau `git pull` secara manual per folder, GLRC menghadirkan UI *dashboard* sederhana untuk mengatur sinkronisasi kode dalam satu ritme (*Batch Execution*).

## 🛠️ Fitur Utama

*   🚀 **Asynchronous Batch Execution:** Memanfaatkan *Threading* untuk memproses clone/pull puluhan repositori secara paralel tanpa bikin UI nge-*freeze*. Kinerja *bandwidth* koneksi akan dimaksimalkan penuh.
*   🛡️ **OS Native Keystore (Vault Integration):** Token API GitLab (PAT) Anda tidak disimpan di file sembarangan. GLRC langsung menyuntikkannya ke dalam pengelola kredensial bawaan (*Windows Credential Manager*, *Linux Secret Service*, *macOS Keychain*).
*   🤖 **State-Aware Git Operations (Auto-Pull):** GLRC cukup cerdas mengetahui apakah sebuah folder/repo sudah terinstal. Jika belum, ia melakukan `git clone`. Jika foler `.git` sudah ada, GLRC otomatis nge-*switch* mode menjadi `git pull --ff-only` untuk update kode terbaru.
*   🎒 **JSON Workspace Export:** Simpan list repositori yang sudah di-checklist menjadi file *Workspace* berformat `.json` agar praktis dibagikan ke anggota tim untuk standardisasi folder kerja.
*   🌐 **Agnostic URL Mode**: Mendukung injeksi *link* **HTTPS** konvensional maupun lewat **SSH** (syarat: *ssh-agent* sudah terkonfigurasi pada mesin Anda).

---

## 📖 Cara Penggunaan (*Quick Start*)

### Tahap 1: Hubungkan Akun (Setup Kredensial)
*   **GitLab URI:** Masukkan URL GitLab server perusahaan/pribadi Anda (Contoh: `https://gitlab.com` atau `https://gitlab.kantor-anda.com`).
*   **Personal Access Token (PAT):** Jangan gunakan *password* aslinya! Generate PAT baru di menu **Preferences > Access Tokens** akun GitLab dengan akses (*scope*) `api` dan `read_repository`. 

### Tahap 2: Tarik & Eksekusi Lapangan
1.  **Target Folder:** Tentukan *path* destinasi absolut (Contoh: `D:\Workspaces\Backend`).
2.  **Filter Repositori:** Tarik list repo dari server dan filter berdasarkan kata kunci/nama regex.
3.  **Eksekusi:** Centang repo yang diinginkan, pilih target *Branch*, lalu hantam tombol *Execute*. Pantau log eksekusinya langsung melalui antarmuka konsol bawaan.

---

## 💻 Panduan Menjalankan Source Code (*Local Development*)

Jika Anda developer Python dan ingin merombak fitur aplikasi ini secara lokal:

**Prerequisites:**
- Python versi 3.10+
- Git terinstall (*environment variables* `PATH` Git sudah valid)

```bash
# 1. Clone source code
git clone https://github.com/aryajava/glrc.git
cd glrc

# 2. Setup Virtual Environment (Venv)
python -m venv .venv
# [Windows]
.venv\Scripts\activate
# [Unix/macOS]
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Jalankan aplikasi GUI
python main.py
```

---

## 📦 Pipa Build Aplikasi (*Bundling Executable*)

Proses *build* menjadi *Standalone Executable* ditenagai oleh mesin *PyInstaller*. Semua hasil biner (File `.exe` / Unix Binary) akan terlempar ke dalam direktori `/dist/`.

**Build di atas OS Windows:**
```cmd
build.bat       # Build biner untuk bahasa EN dan ID sekaligus
build.bat id    # Hanya build versi ID
```

**Build di atas Linux/macOS:**
```bash
./build.sh      # Build untuk EN dan ID sekaligus
./build.sh en   # Hanya build versi EN
```

---

## 🤝 Aturan dan Kontribusi
Silakan merujuk ke dokumen di bawah sebelum melakukan *Pull Request* atau menambah arsitektur kode ke dalam repositori ini:

*   📖 **[Aturan Kontribusi & Pull Request (CONTRIBUTING.md)](CONTRIBUTING.md)**
*   🛡️ **[Kebijakan Keamanan Kredensial (SECURITY.md)](SECURITY.md)**
*   🗺️ **[Struktur Arsitektur Projek (STRUCTURE.md)](STRUCTURE.md)**

## 📄 Payung Hukum (Lisensi)

Perangkat lunak ini didistribusikan di bawah payung **[MIT License](LICENSE)**. Bebas komersialisasi dan pendistribusian terbuka.
