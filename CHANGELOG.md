# Riwayat Versi (Changelog)

Semua modifikasi, *bugfix*, dan penambahan fitur inti pada aplikasi GLRC akan dicatat (*logged*) pada dokumen ini.

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
