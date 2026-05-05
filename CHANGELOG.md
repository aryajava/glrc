# Riwayat Versi (Changelog)

Semua modifikasi, *bugfix*, dan penambahan fitur inti pada aplikasi GLRC akan dicatat (*logged*) pada dokumen ini.

======================

## version 1.5.5

*UX Polish & Maintenance* — Peningkatan layout modal, pencarian internal, indikator status lokal, dan standarisasi identitas Git.

### enhancement:
- **Branch Modal Search:** Menambahkan kolom pencarian real-time di dalam modal konfigurasi branch. Pengguna kini bisa memfilter daftar repositori terpilih untuk mencari repo spesifik dengan cepat.
- **Local/Cloud Status Indicators:** Implementasi ikon visual pada daftar utama. Ikon 📂 (Folder) menunjukkan repo sudah ada di lokal, sementara ☁️ (Cloud) menunjukkan repo hanya ada di remote.
- **Advanced Result Dialog:** 
  1. **Show Failed Only:** Toggle untuk menyaring hasil agar hanya menampilkan repositori yang gagal di-clone/pull.
  2. **Copy All Logs:** Tombol baru untuk menyalin seluruh log proses ke clipboard dalam satu klik.
  3. **Visual Error Highlights:** Repositori yang gagal kini ditandai dengan warna merah dan border tegas pada dialog hasil.
- **Simplified Repo Names:** Tampilan nama repositori di modal kini hanya menunjukkan segmen terakhir (nama project) agar lebih bersih. Tooltip tetap menyediakan path lengkap untuk referensi.
- **Layout Alignment Fix:** Standarisasi lebar kolom (`COL_WIDTHS`) dan perbaikan padding (24px) untuk memastikan keselarasan visual antara baris Bulk Apply dan daftar repositori.
- **Git Identity Enforcement:** Memastikan setiap proses clone/pull otomatis menjalankan `git config --local user.name` dan `user.email` sesuai profil GitLab yang login, tanpa mengganggu konfigurasi global.

======================

## version 1.5.4

*Hotfix & Polish* — Perbaikan cepat untuk dependensi pystray dan bug dialog.

### bugfix:
- **Dependency Fix:** Mengatasi isu `pystray cannot find module` dengan memastikan library terinstal di lingkungan eksekusi.
- **Reference Fix:** Memperbaiki typo `show_confirm` menjadi `show_confirmation` pada fungsi pembersihan riwayat.
- **Localization:** Melokalisasi judul dialog sukses yang sebelumnya masih tertulis hardcode "Info".

======================

## version 1.5.3

*Stability & Full Localization* — Patch final untuk stabilitas UI, pencegahan kehilangan data melalui sistem konfirmasi, dan audit lokalisasi (i18n) menyeluruh.

### enhancement:
- **Change Confirmation System:** Implementasi *dirty checking* pada modal Settings, Interface, dan Keyboard Mapping. Aplikasi kini mendeteksi perubahan dan meminta konfirmasi sebelum menutup atau menyimpan untuk mencegah kehilangan data.
- **Full i18n Audit:** Melakukan audit menyeluruh terhadap sistem multibahasa. Menambahkan 20+ key baru dan melokalisasi seluruh string yang sebelumnya masih hardcode (termasuk log proses git, placeholder, dan label dialog).
- **Quick Export Button:** Menambahkan tombol "Export" langsung di halaman utama untuk mempercepat alur kerja ekspor repositori terpilih ke JSON.
- **Improved Dialog Labels:** Sinkronisasi label tombol "OK" dan "Batal" di seluruh sistem dialog agar konsisten dengan pilihan bahasa pengguna.

### bugfix:
- **RecursionError Fix:** Menghilangkan potensi crash `maximum recursion depth exceeded` melalui penjadwalan UI callback yang lebih aman menggunakan `.after()`.
- **Warning Key Fix:** Memperbaiki bug di mana pesan peringatan "Pilih minimal satu repositori" tampil sebagai kode kunci (`at_least_one`) alih-alih teks terjemahan.

======================

## version 1.5.2

*Power User & Advanced UI* — Patch untuk kontrol window lanjutan, resolver proyek, mapping keyboard, dan integrasi system tray.

### enhancement:
- **Advanced Project Resolver:** Aplikasi memindai marker proyek di root repo seperti `.sln`, `.csproj`, `package.json`, `requirements.txt`, `pyproject.toml`, `pom.xml`, dan Gradle files agar target pembukaan IDE lebih tepat.
- **Window State Persistence:** Ukuran dan posisi window disimpan saat keluar, dengan guard agar posisi lama yang berada di luar layar tidak dipulihkan secara berbahaya.
- **Power User Controls:** Settings kini menyediakan modal kontrol untuk Always on Top, opacity 80-100%, minimize to tray, startup state, dan modal background dimming.
- **Custom Keyboard Mapping:** Settings kini menyediakan modal Keyboard Mapping untuk mengubah shortcut Workspace Tools, Find, dan aksi utama.
- **System Tray Integration:** Aplikasi dapat minimize ke tray dengan menu Show dan Exit jika dependency `pystray` tersedia.
- **Settings Layout Fix:** Modal Settings dibuat lebih tinggi dan scrollable sehingga tombol Save tidak lagi terpotong.

======================

## version 1.5.1

*UX & Navigation Core* — Patch untuk mempercepat alur kerja harian melalui riwayat workspace, navigasi keyboard, integrasi IDE yang lebih pintar, dan tampilan hasil clone yang lebih jelas.

### enhancement:
- **Recent Workspaces v1:** Workspace `.json` yang diekspor, digenerate, atau diimpor otomatis masuk riwayat terbaru, bisa dimuat ulang dari Workspace Tools, dibersihkan manual, dan dibatasi dari Settings.
- **Basic Smart IDE Integration:** Deteksi VS Code, Cursor, Visual Studio, dan File Explorer kini lebih cerdas melalui registry, PATH, dan lokasi instalasi umum; tombol Open selalu menampilkan menu pilihan.
- **System Theme Sync:** Perubahan tema Light/Dark/System diterapkan langsung pada UI dan komponen kustom tanpa perlu restart.
- **Basic Keyboard Shortcuts:** Menambahkan `Ctrl+G`, `Ctrl+F`, `Ctrl+Enter`, dan `Esc` sesuai konteks modal.
- **Smart Tooltips:** Tooltip kini lebih halus, mengikuti tema, mendukung teks dinamis, dan mencakup tombol Workspace Tools serta Success Dialog.
- **Enhanced Success Dialog:** Dialog hasil clone menampilkan path absolut, tombol salin path, feedback visual, dan menu IDE/File Explorer terintegrasi.
- **Empty State UI:** Daftar repositori kosong kini menampilkan panduan visual dan CTA, bukan popup not found.

======================

## version 1.5.0

*Workspace Tools Maturation* — Pembaruan fitur untuk mematangkan utilitas Workspace Tools dengan berbagai fungsi produktivitas.

### enhancement:
- **Find & Replace:** Menambahkan frame baru di bawah teks input untuk mencari dan mengganti teks (contoh: menghapus suffix `-sit` dari daftar repo).
- **Format & Clean:** Menambahkan tombol untuk merapikan teks secara instan (mengurutkan abjad, menghapus baris kosong, dan menghapus duplikat) sebelum divalidasi.
- **Clear All:** Tombol cepat untuk mengosongkan teks input.
- **Bulk Import from File:** Mendukung impor daftar repositori langsung dari file `.txt`, `.csv`, dan `.xlsx` (Excel) ke dalam kotak input.
- **Validation Preview:** Kini aplikasi menampilkan jendela dialog berisi rangkuman validasi (berapa banyak repo yang valid dan invalid) dan meminta persetujuan sebelum file JSON disimpan.

======================

## version 1.4.5

*Branch Configuration Selection Hotfix* — Patch untuk memastikan modal Branch Configuration selalu memakai daftar repositori yang benar-benar dipilih pengguna.

### bugfix:
- **Selected Repository Snapshot:** Branch Configuration kini membuat snapshot repositori terpilih saat tombol clone ditekan, sehingga daftar repo, branch yang dipilih, dan job clone tidak lagi bergantung pada state global yang bisa berubah setelah modal dibuka.
- **Visible Selection Ordering:** Repo yang sedang terlihat dan dicentang di halaman aktif ditampilkan lebih dulu di modal Branch Configuration, lalu diikuti pilihan dari halaman lain jika ada.
- **Stale Pagination Guard:** Hasil fetch repositori yang sudah kedaluwarsa kini diabaikan agar halaman lama tidak bisa menimpa halaman baru dan memunculkan kondisi seperti `Page 17 of 7`.

======================

## version 1.4.4

*Hotfix* untuk isu *runtime error* pada Workspace Tools.

### bugfix & enhancement:
- **Generate Workspace:** 
  1. Memperbaiki dua `AttributeError` beruntun terkait fungsi *logging* (`update_log_threadsafe` diganti menjadi `write_log`) dan instansiasi `GitLabAPI` (`self.api`) yang mencegah proses berjalan.
  2. **Smart Search Fallback**: `Generate Workspace` kini bisa menerima *input* berupa **nama repositori saja** tanpa *namespace* (contoh: `msf_posting_maintenance`). Jika *path* tidak valid secara absolut, API akan otomatis melakukan pencarian pintar dan memilih repositori dengan nama yang persis sama.

======================

## version 1.4.3

*Hotfix* untuk isu antarmuka (UI) sisa dari *patch* lawas terkait berkedipnya ikon pada jendela aplikasi sekunder.

### bugfix:
- **modal icon flickering:** Memperbaiki masalah *icon flickering* tanpa menggunakan metode *withdraw* maupun *delay* `after()`. Kini aplikasi langsung menerapkan *favicon* sejak awal dan melakukan *intercept* (*override*) terhadap metode internal bawaan `CustomTkinter` agar tidak bisa menimpa kembali *favicon* tersebut dengan ikon *default* Tkinter. Jendela *modal* akan langsung tampil instan tanpa *flicker* maupun jeda (*delay*).

======================

## version 1.4.2

*Workspace Tools Stability* — Patch untuk menstabilkan modal Workspace Tools dan mencegah aplikasi terasa terkunci saat operasi workspace dijalankan.

### bugfix:
- **Modal Lifecycle:** Tombol Import/Export tidak lagi menghancurkan modal Workspace Tools sebelum file dialog dibuka, sehingga modal tidak tampak hilang mendadak.
- **Modal Visibility & Focus:** Memperbaiki kasus modal yang secara logika masih aktif tetapi tidak tampil/terangkat di layar, termasuk overlay profil yang tertinggal setelah ditekan `ESC`.
- **UI Freeze Guard:** Proses Generate tidak lagi men-disable seluruh modal yang sedang memegang `grab_set()`. Aplikasi tetap responsif dengan status validasi dan tombol input yang dikunci sementara.
- **Duplicate Modal Guard:** Klik berulang pada tombol Workspace Tools kini hanya memfokuskan modal yang sudah terbuka, bukan membuat beberapa modal yang saling berebut fokus.
- **Thread-Safe UI Callback:** Callback dari proses background kini dijadwalkan dengan penjagaan mainloop agar aplikasi tidak memunculkan error saat window sudah ditutup atau thread selesai terlambat.
- **Clone Workflow Polish:** Label repositori pada dark theme kini terbaca, tombol Clone kembali ke gaya normal setelah proses selesai, dan judul dialog pilih folder mengikuti sistem terjemahan.

======================

## version 1.4.1

*Startup Hotfix* — Patch kecil untuk memperbaiki crash saat aplikasi dibuka dari build release 1.4.0.

### bugfix:
- **Workspace Tools Startup Crash:** Memperbaiki pemanggilan status tombol `btn_export` yang masih mengarah ke tombol lama, sementara pada 1.4.0 export sudah dipindahkan ke modal *Workspace Tools*. Aplikasi tidak lagi gagal start dengan error `_tkinter.tkapp object has no attribute 'btn_export'`.

======================

## version 1.4.0

*UX & Clone Control* — Pembaruan masif pada antarmuka pengguna untuk interaksi *Workspace* yang lebih praktis serta pemantauan kloning repositori yang sangat informatif dan bisa dibatalkan secara *real-time*.

### feature:
- **Workspace Tools:** Penyatuan tombol Import/Export dan penambahan fitur *Generate Workspace* dari *raw text* (otomatis menghapus duplikasi dan spasi, ditambah proses validasi URL repositori via *ping* GitLab API).
- **Graceful Cancelation:** Proses *cloning* repositori massal kini dilengkapi perlindungan *Abort*. Tekan tombol *Cancel* merah di UI dan aplikasi akan menghentikan antrean saat ini juga menggunakan teknologi `threading.Event()`.
- **Bulk Apply & UI Refresh:** Menghadirkan *master input* untuk *Bulk Apply* pada jendela pengaturan kloning, serta mengaktifkan pemotongan teks (*middle truncation*) supaya nama repositori yang terlampau panjang tidak merusak tata letak tabel.
- **Disk Protection Check:** Peringatan pro-aktif apabila kuota sisa disk pengguna (terkonfigurasi pada menu *Settings*) tak mencukupi sebelum rentetan *cloning* dijalankan.
- **Progress Tracking & Export:** *Live update log* diperkaya format angka `[1/N]` demi transparansi. Tersedia pula fungsi untuk *Export Log* format `.txt` bagi kepentingan dokumentasi di dialog hasil akhir.

### bugfix:
- **Flashing Terminal (Windows):** Melampirkan proteksi param `CREATE_NO_WINDOW` ke seluruh *shell execution*. Terminal hitam tidak akan melompat dan berkedip acak lagi ketika interaksi Git terjadi di balik layar.

======================

## version 1.3.2

*Documentation & Community Shift* — Rilis ini didedikasikan eksklusif untuk me-*refactor* tatanan bahasa Markdown (Teks) di seluruh proyek. Kita merombak identitas repositori kembali menjadi *Native Indonesian* dengan gaya bahasa sehari-hari *programmer*.

### docs:
- **Language Normalization:** Menulis ulang struktur buku panduan di `README.md` menggunakan tatanan bahasa IT campuran (*mix* Inggris-Indonesia) yang lugas dan *to-the-point* sehingga mudah dicerna *developer* lokal.
- **Bilingual Equality:** Menciptakan ekosistem ganda (*Dual-Language*) dengan mereplikasi seluruh panduan korporat menjadi rupa `.en.md` (`CONTRIBUTING_en.md`, `SECURITY_en.md`, `STRUCTURE_en.md`).
- **Community Templates:** Menerbitkan *template Pull Request (PR)* dan *Issue Github* di direktori `/.github/` untuk me-standardisasi format pelaporan *error* dari luar.

======================

## version 1.3.1

*Hotfix* kompilasi mesin PyInstaller dan memberantas isu rendering grafis (*UI rendering tearing*) sisa *impact* versi 1.3.0. 

### bugfix:
- **pyinstaller keyring bug:** Menyuntikkan flag `--copy-metadata keyring` dan `--hidden-import keyrings.alt` pada *script bundler* `build.py` demi menggaransi modul OS Keyring sukses tereksekusi pada *binary/exe*.
- **portable absolute pathing:** Me-*rewrite* deteksi logik *path config* dari yang asalnya `cwd` menjadi `sys.executable`. Eksekutor kini tidak lagi ngebikin file sampah tiap ditekan secara acak dari folder *Windows Explorer* manapun.
- **modal icon flickering:** Menciptakan fungsi *delay rendering* ~15ms yang menahan sinkronisasi `deiconify` sampai jendela *modal* rampung ter-*render*. *Flickering* kedipan logo sirna seratus persen.

======================

## version 1.3.0

*Cross-Platform OS Vault* — Perombakan arsitektur lapis bawah (Enkripsi DPAPI) menjadi pustaka *Secret Service*. Rilis ini murni menambal isu *Crash Fatal* aplikasi saat dipaksa jalan via terminal macOS dan Linux Debian.

### feature:
- **cross-platform credential:** Eksekusi integrasi pustaka Python `keyring`. Akses token PAT Anda kini langsung ditanam ke brankas rahasia lokal (*Windows Credential Manager* / *macOS Keychain* / Linux *Secret Service*).
- **clean executable config:** Menggeser pembuatan file log/dump `config.json` yang asalnya berserakan kemana-mana menjadi di isolasi di *User Profile* absolut komputer Anda (`~/.glrc/`).
- **automated migration:** Fungsi yang merobohkan file lama berenkripsi jadul (`config.dat`), merebut isi tokennya lalu melemparnya ke dalam arsitektur `keyring` baru saat aplikasi *Booting* pertama. Sangat mulus (Seemless).

======================

## version 1.2.3

Penambalan kosmetik i18n dan pembuangan Exception Error kasar bawaan Terminal *Subprocess*.

### bugfix:
- **fixed raw exception logging:** *Catch* `FileNotFoundError` (`[WinError 2]`) di *thread* saat biner `git` tiba-tiba macet atau tidak terinstall, dan melempar pesan *user-friendly* ketimbang *stack-trace* merah pening.
- **smart git detection:** Memeriksa status path `git` segera sesudah tombol ditekan agar eksekusi di- *terminate* instan jika deteksinya fiktif.

### improvement:
- **i18n completion:** Mendorong 15+ teks statis tambahan dari dalam logika *Python* ke *dictionary* penterjemah di `i18n.py`.
- **clean magic variables:** Men-sentralisasi ulang angka absolut (jumlah *retry, clone concurrent limits*) ke dalam direktori konfig dasar di `constants.py`.

======================

## version 1.2.2

*Hardening* lapisan jaringan (Menangkap pengecualian pada Network Requests).

### bugfix:
- **fixed timeout hang:** Menyuntikkan parameter batas putus *timeout* 15-30s di seluruh pemanggilan Request API untuk menolak UI nge-*freeze* gara-gara nge-*ping* server intranet rusak.
- **fixed bare except logic:** Blok `except:` telanjang pada *modal* profil dipangkas jadi `except Exception:` untuk ngebela `SystemExit`.

### feature:
- **URL host validation:** Sistem bakal memarahi dan men-*drop* *request URL API GitLab* jika pengguna iseng ngirim argumen tanpa `https://`.

======================

## version 1.2.1

*Hotfix* Git Auth Logic — Sinkronisasi git auto-pull memantul (*Failed Authentication*).

### bugfix:
- **fixed git pull loop:** Eksekusi auto-pull selalu mandek gara-gara origin SSH tanpa ID terlempar ke *blocking shell*. Kita mengakali parameter repo agar mengeset URL Origin beserta Token API palsu sedetik sebelum narik, lalu memutuskannya (Me-robek Token) dari memori PC detik setelah kode selesai disinkronkan. Keamanan maksimal terjamin!

======================

## version 1.2.0

*UI Polish & Matrix Scaling* — Perombakan drastis ukuran elemen desain *Grid* menggunakan icon berbasis grafis (*Material Icons*), bukan lagi memakai Emoji Unicode yang suka nge-*bug* di beda-beda Windows OS.

### bugfix:
- **icon jitter alignments:** Teks dan Ikon bergeser beberapa piksel setiap kali kursor dihover (*visual jumping*). *Hook render* PIL sekarang disetel pas pakai jangkar geometris `anchor="mm"`.
- **ghost pat expiry:** Modal pat terus menampilkan angka palsu `7 hari` sekalipun token asli Anda sedang ter-set ngga ada kedaluwarsa (permanen). Fix!

### feature:
- **material design injection:** Mesin GUI sekarang ngerender Glyph Material Design secara real-time via paket modul *Pillow* (PIL). Tombol-tombol kini konsisten besar-sejajar.

======================

## version 1.1.0

Fitur Paska-Kloning (*Post-Clone*) IDE dan manajemen bongkar pasang (*Export/Import*) Workspace format `.json`.

### bugfix:
- **json import glitch:** Impor file Workspace langsung mematahkan hitungan logik daftar UI (*Pagination*) ke titik *Null*.
- **modal ghost clicks:** UI Modal ganda terbentur berebut `grab_set()` di OS Unix. Pemanggilan redundan dihapus. 

### feature:
- **IDE cross-shell detection:** Menu dialog (*pop-up*) elegan akan nampil seketika repositori selesai di-*clone*. Terdapat tombol otomatis untuk membanting dan menyuapkan projek tersebut ke *VS Code / IDE Launcher* (Mampu me-nolak dan *fallback* ke pembaca partisi standar *File Explorer* jika Editor kagak ketemu!).

======================

## version 1.0.0

*Initial Release* (Rilis Perdana). Kepingan sistem fungsional pengkloning repositori massal rilis secara fungsional. Mampu mendukung kloning Git asinkron dengan fitur dwibahasa (ID/EN) bersenjatakan GUI *CustomTkinter* moderen.
