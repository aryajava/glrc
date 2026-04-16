# Kebijakan Keamanan (Security Policy) GLRC

GLRC adalah aplikasi *client-side* yang menjembatani mesin lokal/laptop Anda dengan repositori dari akun GitLab korporat perusahaan Anda. Kami sangat menyadari besarnya visibilitas dan *impact* keamanan siber (*Cyber Security*) yang harus dipegang teguh, dan menjadikan hal ini sebagai pilar utama *development* proyek.

## 1. Versi Support Keamanan Terkini

Sebagai aplikasi berskala kecil hingga menengah (Independent *open-source*), **kami HANYA akan menopang *update* darurat untuk celah keamanan (*Vulnerability/Security Patch*) pada Rilis Mayor paling mentok (Terbaru).** 

| Rilis (Version GLRC) | Status Pembaruan Keamanan (Security Update) |
| --- | --- |
| > 1.3.0 | Tersokong (Supported) |
| < 1.3.0 | Kadaluarsa (Unsupported) |

> **Catatan Krusial:** Anda sangat dihimbau menjauh atau men-*uninstall* eksekutor *legacy build* atau kode di bawah v1.3.0. Kenapa? Sandi rahasia Anda pada saat itu belum 100% matang dilindungi (masih menggunakan primitivitas fungsi sistem DPAPI Windows saja), berpotensi bahaya kompromi kredensial manakala dieksploitasi lewat mesin macOS atau Linux Anda. Segeralah bermigrasi ke modul *cross-platform keyring* terbaru v1.3.1+.

---

## 2. Di manakah dan bagaimana "Otorisasi API Anda" dititipkan?

Aplikasi *Cloner* jenis apa pun di bumi ini pasti meminta semacam "Akses Izin Khusus" (Biasanya berupa *Personal Access Token* atau `PAT`). Ibaratnya Anda memberikan kunci gembok kantor agar alat kami diizinkan nge-*clone*.

GLRC sangat menjunjung privasi sandi Anda. **Kami berjanji tak sedikit pun mengekspos `PAT` rahasia tersebut ke dalam bentuk teks terbaca (plaintext) baik pada cache `.txt`, riwayat log konsol, apalagi pada settingan (*.json).**

Di bawah arsitektur rilis moderen (Mulai _v1.3.0_ ke atas):
- Data Anda dilindungi dengan cara mengurungnya langsung di brankas digital milik Sistem Operasi lokal (OS Native *Keystore/Vault*).
- Pada **Windows**, diinjeksi lewat **Windows Credential Manager**.
- Pada **Linux**, diproteksi oleh lapisan komunikasi **DBus Secret Service**.
- Pada platform **macOS**, diseret masuk dalam perlindungan eksklusif **Apple Keychain Access**.

Data ringan teknis lainnya (Seperti setelan warna tema GUI / path *folder* tujuan) dibiarkan pada berkas ringan `config.json` di profil user anda agar transparan untuk Anda ulik secara bebas.

---

## 3. Ketemu Bug Keamanan? Jangan Diekspos Sembrono!

Walau kami belum mampu menggelar kontes berhadiah (*Bug Bounty* program), jika Anda berniat membantai mesin enkripsi kami guna memperbaiki keamanan proyek—kami sangat menghormatinya.

Kami menganut paham *Responsible Disclosure*:
1. **Harap JANGAN pernah melayangkan isunya blak-blakan ke Forum GitHub `Issues` publik!** Ini rahasia, jangan sampai ngerugiin orang yang sedang *deploy* aplikasi ini sebelum kita siapkan obatnya (*Patch*).
2. Tembak pelaporan cacatnya langsung (*private email*) menuju alamat tertera pada profil pengelola repositori (*Contact Maintainer*).
3. Buat pembuktian sederhana kelayakannya menggunakan semacam *Proof-of-Concept/PoC* singkat (Contoh mem*bypass* config di Sistem Operasi X, dsb).

Tim *Core Contributor* sebisa mungkin akan menajamkan proteksinya dan melontarkan **Security Release Patch** untuk seluruh komunitas, seraya mencetak nama panggung (*Handle*) Anda di jajaran Apresiasi Kontributor Keamanan.
