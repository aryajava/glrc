<div align="center">
  <img src="https://raw.githubusercontent.com/FreeTubeApp/FreeTube/development/assets/logo.png" alt="GLRC Logo" width="128" height="128" />
  <h1>GLRC: GitLab Repo Cloner</h1>
  <p><strong>Aplikasi desktop lintas platform nan tangguh yang dirancang khusus untuk mengelola, menarik (pull), dan menyalin (clone) ratusan repositori GitLab secara serentak dan instan.</strong></p>
  
  <p>
    <a href="README.md">English</a> • <a href="README_id.md">Bahasa Indonesia</a>
  </p>

  <p>
    <img src="https://img.shields.io/badge/python-%E2%89%A53.8-blue?logo=python&logoColor=white" alt="Python 3.8+">
    <img src="https://img.shields.io/badge/GUI-CustomTkinter-blueviolet" alt="GUI: CustomTkinter">
    <img src="https://img.shields.io/badge/lisensi-MIT-green" alt="Lisensi: MIT">
    <img src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey" alt="Cross-Platform">
    <img src="https://img.shields.io/badge/i18n-English%20%7C%20Indonesian-orange" alt="Bilingual">
  </p>
</div>

<hr>

## Daftar Isi
- [Kenapa GLRC Dibuat?](#kenapa-glrc-dibuat)
- [Bagaimana Cara Kerjanya?](#bagaimana-cara-kerjanya)
- [Fitur Utama](#fitur-utama)
- [Mulai Cepat (Quick Start)](#mulai-cepat-quick-start)
- [Kompilasi Aplikasi (Build)](#kompilasi-aplikasi-build)
- [Lisensi](#lisensi)

---

## Kenapa GLRC Dibuat?

Mengelola ratusan repositori yang terbagi di berbagai proyek dan tim pada GitLab sangatlah merepotkan. Mencari repositori yang tepat, melakukan clone satu per satu, menentukan kapan harus menggunakan HTTP/SSH, dan memastikan repositori lokal yang sudah ada sinkron secara manual adalah tugas yang menguras waktu dan tidak efisien.

Oleh karena itu **GLRC** hadir. Kami merancang alat ini khusus untuk para *Developer*, *Manaoajer Proyek*, dan *DevOps Engineers* yang harus mengelola ruang kerja raksasa. GLRC mengotomatisasi pekerjaan panjang ini dan menyajikannya lewat antarmuka desktop (GUI) yang berkinerja tinggi, multi-thread, dan sangat mudah digunakan oleh pemula sekalipun.

## Bagaimana Cara Kerjanya?

Secara teknis, GLRC berkomunikasi langsung di belakang layar dengan GitLab API menggunakan Token Akses Anda.
1. **Pilih & Tarik Data**: Begitu kredensial Anda diautentikasi dengan aman, GLRC akan menarik (fetch) seluruh daftar repositori Anda secara instan bahkan jika daftarnya berjumlah ratusan (didukung fitur pencarian instan wildcard `*`).
2. **Atur Cabang (Branch)**: Anda centang seluruh repositori yang Anda mau, lalu tentukan *branch* yang ingin diambil, layaknya Anda berbelanja pada keranjang digital. Anda bahkan bisa menyuruhnya membuat *branch local* baru jika ada fitur yang ingin digarap keroyokan.
3. **Eksekusi Otomatis**: Mesin intinya akan membaca antrian ini, jika folder lokalnya **belum ada** maka dia akan menjalankan `git clone` bersamaan dalam beberapa utas paralel. Jika foldernya **sudah ada**, maka dia otomatis pintar beralih menjadi operasi `git pull --rebase`. Menakjubkan bukan?

---

## Fitur Utama

- **Multi-Selection & Operasi Batch**: Pilih banyak repositori sekaligus dan clone semuanya langsung bersamaan.
- **Smart Auto-Pull / Update**: Jika repositori sudah ada, aplikasi akan otomatis membatalkan clone dan beralih menjalankan rutinitas `git pull` untuk memperbarui folder lokal Anda.
- **Eksekusi Paralel (Kencang)**: Mengeksekusi instruksi Clone & Pull menggunakan multi-threading untuk mempercepat proses.
- **Fleksibilitas Protokol (HTTPS & SSH)**: Lakukan clone dengan aman melalui HTTPS (menggunakan PAT terenkripsi yang anti curi) atau mode SSH klasik.
- **Mekanisme Auto-Retry Anti Gagal**: Hilangnya sinyal atau rintangan server diatasi otomatis lewat loop *3-kali percobaan* saat gagal clone/pull.
- **Manajemen Workspace**: Ekspor status centang Anda ke sebuah file JSON, lalu suatu hari Anda bisa "Impor" lagi jika butuh clone cepat dengan struktur yang sama. Benar-benar sekali klik.
- **Sistem Pencarian Mutakhir**: Telusuri ratusan proyek secara leluasa dengan dukungan karakter wildcard `*` dan sistem halaman paginasi anti-lag.
- **Bilingual Terintegrasi (i18n)**: Tersedia penuh dalam dukungan Bahasa Indonesia (`id`) maupun Bahasa Inggris (`en`).
- **Tema Bebas Pilih**: Bergabung harmonis dengan Mode tampilan Sistem (Light/Dark mode) layar Anda.

---

## Mulai Cepat (Quick Start)

Untuk menjalankan file script dengan *Python*:

1. Pastikan mesin Anda sudah terinstall **Python 3.8+**.
2. Clone atau unduh kode sumber proyek ini.
3. Inisialisasi dan hidupkan virtual environment Anda:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
   *(Pada sistem macOS/Linux, silakan gunakan `source .venv/bin/activate`)*
4. Install paket dan modul dependensi Python di PIP:
   ```bash
   pip install -r requirements.txt
   ```
5. Lepas landas dengan satu perintah sederhana:
   ```bash
   python main.py
   ```

## Kompilasi Aplikasi (Build)

Keajaiban sebenarnya ada di sini. Aplikasi mentah ini siap dibungkus menjadi file satu klik (`.exe` atau `.app`) yang mandiri! Pengguna (Tim Anda) tidak wajib menginstal Python. Anda cukup menggunakan alat rakit (builder script) dari kami: `build.bat` (Windows) dan `build.sh` (Mac/Linux).

Dan Anda dapat menentukan default bahasanya pula! Masukkan argumen bahasa pasca skrip:
- Jika ingin default Bahasa Inggris: jalankan `build.bat en` atau `./build.sh en`
- Jika ingin default Bahasa Indonesia: jalankan `build.bat id` atau `./build.sh id`

Aplikasi tunggal akhir siap saji Anda akan terkompilasi ciamik di dalam folder bernama `dist`. 

---

## Lisensi
Aplikasi ini didistribusikan secara transparan di bawah payung aturan [Lisensi MIT](LICENSE).

<p align="center">
  <i>Dirangkai dengan penuh ❤️ oleh Para Kontributor GLRC</i>
</p>
