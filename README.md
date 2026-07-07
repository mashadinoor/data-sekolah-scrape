# npsn-scraper

Skrip Python untuk mengambil data sekolah (nama kepala sekolah, nomor telepon, dan nama yayasan) berdasarkan **NPSN** dari dua sumber data publik Kementerian Pendidikan:

- `https://sekolah.data.kemendikdasmen.go.id/` — untuk nomor telepon & yayasan (via Selenium, karena situs berbasis Angular/SPA)
- `https://referensi.data.kemendikdasmen.go.id/snpmb/site/sekolah` — untuk nama kepala sekolah (via requests + BeautifulSoup, halaman server-rendered)

Hasil disimpan ke file CSV.

## Fitur

- Input banyak NPSN sekaligus
- Otomatis membuka & mengklik tombol "Lihat" di halaman pencarian
- Menggabungkan data dari dua sumber berbeda per NPSN
- Output rapi ke `hasil_sekolah.csv`
- Jeda antar-request agar tidak membebani server

## Prasyarat

- Python 3.9+
- [uv](https://docs.astral.sh/uv/) — package & environment manager Python
- Google Chrome terpasang di komputer

## Instalasi

```bash
git clone https://github.com/<username-anda>/npsn-scraper.git
cd npsn-scraper
uv sync
```

`uv sync` otomatis membuat virtual environment `.venv` dan menginstal semua dependensi sesuai `pyproject.toml` / `uv.lock`.

## Cara pakai

1. Siapkan file CSV daftar sekolah Anda, beri nama **`daftar_sekolah.csv`**, letakkan di folder yang sama dengan `scrape_sekolah.py`. Formatnya dipisah `;` (semicolon), dengan header:

   ```
   NO; PROVINSI; KABUPATEN/KOTA; NPSN; SEKOLAH
   1; JAWA BARAT; KAB. BANDUNG; 20254054; SMAN 1 RANCAEKEK
   2; JAWA BARAT; KAB. BANDUNG; 20206151; SMAN 1 BALEENDAH
   ```

   Jika nama file atau delimiter Anda beda, sesuaikan variabel `INPUT_CSV` dan `INPUT_DELIMITER` di awal `scrape_sekolah.py`.

2. Jalankan:
   ```bash
   uv run scrape_sekolah.py
   ```
3. Hasil akan tersimpan di `hasil_sekolah.csv` dengan kolom:
   `no, provinsi, kabupaten_kota, npsn, sekolah, nama_kepala_sekolah, telepon, yayasan, status`

   (kolom asal dari file input digabung dengan data hasil scraping)

## Struktur Proyek

```
npsn-scraper/
├── scrape_sekolah.py     # skrip utama
├── daftar_sekolah.csv    # file input Anda (TIDAK di-commit, lihat .gitignore)
├── pyproject.toml        # metadata proyek & daftar dependensi (dikelola uv)
├── uv.lock               # lock file versi dependensi (auto-generated oleh uv)
├── LICENSE
├── README.md
└── .gitignore
```

## Catatan Etika Penggunaan

- Data yang diambil merupakan **data publik** yang memang ditampilkan untuk umum oleh Kemendikdasmen, bukan data pribadi sensitif.
- Skrip ini sudah menyertakan jeda (`time.sleep`) antar-permintaan agar tidak membebani server.
- Gunakan secukupnya dan hormati ketentuan penggunaan (Terms of Service) situs sumber data.
- Selector HTML/CSS/XPath dapat berubah sewaktu-waktu jika tampilan situs sumber diperbarui — silakan sesuaikan kembali jika skrip berhenti bekerja.

## Lisensi

Proyek ini menggunakan lisensi [MIT](LICENSE).