# Panduan Kontribusi GLRC

Selamat datang di ekosistem **GLRC**! Kami sangat senang Anda mempertimbangkan untuk menyumbang waktu dan kode demi membesarkan projek ini. 
Mengelola ratusan repositori GitLab bukanlah tugas yang mudah, dan kontribusi Anda akan sangat membantu *developer* lain meringankan *daily task* mereka.

Dokumen ini adalah *guidelines* resmi agar proses *Pull Request (PR)* Anda bisa langsung di-*merge* dengan aman, tertib, dan rapi.

---

## 1. Tata Cara Melaporkan Kesalahan (Bug)
Bahkan aplikasi terhebat sekalipun bisa saja tersandung. Jika Anda menemukan layar *error*, tombol yang *freeze*, atau aplikasi *force close*, tolong bantu kami.

**Sebelum Bikin Laporan:**
1. Cek menu [Issues](https://github.com/aryajava/glrc/issues) dan cari menggunakan *keyword* spesifik. Pastikan belum ada yang me-*report* bug serupa.
2. Gunakan versi GLRC **paling mutakhir (terbaru)**. Bisa jadi bug yang Anda temukan sudah kami *fix* atau tambal di rilis kemarin.

**Cara Bikin Laporan:**
1. Buka repo GitHub kami, klik tombol `New Issue`.
2. Pilih *template* **Laporan Bug**.
3. **Penting:** Pastikan Anda menyertakan "Langkah Pasti untuk Men-Reproduce Kerusakan" (*Steps to Reproduce*). Misalnya: *"Klik tombol A, isi text B, lalu aplikasinya nge-freeze"*. Tanpa hal ini, kami susah nge-*debug*-nya.

---

## 2. Mengusulkan Fitur Keren (Feature Request)
Anda punya ide atau *feedback* asik untuk membuat GLRC lebih garang? 
Pilih *template* **Usulan Fitur Baru**. Ceritakan apa masalah/kesulitan Anda waktu bekerja, dan jelaskan fitur apa yang ada di kepala Anda untuk memecahkan *pain point* tersebut.

---

## 3. Setup Lokal & Membuat Pull Request (PR)

GLRC dikembangkan secara penuh menggunakan ekosistem **Python** & implementasi GUI dari **CustomTkinter**. Kami merawat baris kode ini layaknya bayi, mohon jangan sekadar lempar revisi *commit*.

### A. Konfigurasi Komputer Lokal (Local Environment)
1. Lakukan *Fork* pada repositori ini ke Github pribadi Anda.
2. Tarik kodenya ke komputer lokal (`git clone`).
3. Setup *Virtual Environment* (Venv) khusus agar tidak tabrakan/konflik dengan paket Python lain di laptop Anda:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate      # Windows
   source .venv/bin/activate   # Linux / Mac
   ```
4. Pasang *dependencies* yang diperlukan:
   ```bash
   pip install -r requirements.txt
   ```

### B. Standardisasi Penulisan Kode (Code Style Standard)
- **Hindari God Class:** Jangan menaruh segala macem *logic* numpuk ke dalam satu class/fungsi `main.py`! Usahakan membaginya ke dalam sub-folder `/src/...` agar tertata (Modular).
- **Berbahasa Ganda (Bilingual):** Jika Anda menyuntikkan *string* baru untuk UI (Contoh: Menambah teks pesan *error* baru), Anda **WAJIB** menambahkannya ke file kamus translasi di `src/utils/i18n.py`. Sangat dilarang keras menaruh teks (*hardcode*) langsung di dalam file GUI frontend!

### C. Prosedur Bikin Pull Request (PR)
Siap mempersembahkan *update* fitur gila Anda secara publik?
1. Jangan langsung ngulik dan nge-*commit* ke branch `main`. Buatlah sub-*branch* secara terpisah.
   > ❌ Bad Practice: `git checkout main` \
   > ✅ Good Practice: `git checkout -b feature/cancel-btn`
2. Kirim (*Push*) catatan *commit* tersebut menuju *fork* repo GitHub Anda, lalu pencet tombol pengajuan **Pull Request (PR)**.
3. Anda otomatis disuguhkan template PR Checklist. Centang (✓) seluruh persyaratannya jika Anda yakin kode tersebut sudah beroperasi sempurna (*tested*) pada SO lokal masing-masing tanpa ngerusak fitur lain (*breaking changes*).

---

## 4. Penghargaan Kontributor (Wall of Fame)
Di dunia *open-source*, pengakuan adalah mata uang utama. Semua nama kreator (PR yang sukses di-*merge*) akan otomatis direkam dan masuk ke jajaran figur penghormatan histori proyek ini.

Mari kita mendaki hierarki dan memangkas waktu kerja kotor di ekosistem koding Indonesia!
