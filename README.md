# Data Scraping Sekolah (by NPSN)

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

1. Siapkan file CSV daftar sekolah Anda, beri nama **`daftar_sekolah.csv`**, letakkan di folder yang sama dengan `scrape_sekolah.py`. Formatnya dipisah `,` (comma), dengan header:

    ```
    NO, PROVINSI, KABUPATEN/KOTA, NPSN, SEKOLAH
    ...
    ```

    Jika nama file atau delimiter Anda beda, sesuaikan variabel `INPUT_CSV` dan `INPUT_DELIMITER` di awal `scrape_sekolah.py`.

2. Jalankan:
    ```bash
    uv run scrape_sekolah.py
    ```
3.  Hasil akan tersimpan di `hasil_sekolah.csv` dengan kolom:
    `no, provinsi, kabupaten_kota, npsn, sekolah, nama_kepala_sekolah, telepon, yayasan, status`

    (kolom asal dari file input digabung dengan data hasil scraping)

## Menjalankan di Google Colab

Selain di komputer lokal, skrip ini juga bisa dijalankan langsung di Google Colab lewat notebook `scrape_colab.ipynb` — cocok kalau kamu tidak mau install Python/Chrome di komputer sendiri, atau mau menjalankan scraping dari HP/Chromebook.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/<username-anda>/npsn-scraper/blob/main/scrape_colab.ipynb)

Perbedaan utama dari versi lokal:

- **Chrome & chromedriver** di-install otomatis lewat `apt-get` di cell pertama notebook (Colab tidak punya Chrome bawaan seperti laptop kamu).
- **Input CSV** diupload langsung lewat cell "Upload file input" (pakai widget upload bawaan Colab), bukan diletakkan manual di folder `data/`.
- **Hasil scraping** diunduh otomatis lewat cell terakhir (`files.download(...)`), karena file di Colab akan hilang begitu runtime disconnect/restart.

Cara pakai singkat:

1. Buka `scrape_colab.ipynb` di Google Colab (klik badge di atas, atau upload manual filenya ke [colab.research.google.com](https://colab.research.google.com/)).
2. Jalankan cell demi cell dari atas ke bawah (Runtime → Run all juga bisa).
3. Saat diminta upload, pilih file CSV daftar sekolah kamu (format kolom sama seperti versi lokal: `NO, PROVINSI, KABUPATEN/KOTA, NPSN, SEKOLAH`).
4. Tunggu proses scraping selesai, lalu file `hasil-scrape.csv` akan otomatis terunduh ke komputer/HP kamu.

> Opsional: kalau mau hasilnya tersimpan permanen (tidak hilang saat sesi Colab berakhir) atau mau menjalankan scraping berkali-kali tanpa upload ulang, notebook menyediakan opsi mount Google Drive — tinggal uncomment 2 baris kode di bagian awal notebook.

## Struktur Proyek

```
npsn-scraper/
├── scrape_sekolah.py     # skrip utama (jalan di komputer lokal)
├── scrape_colab.ipynb    # versi siap-pakai untuk Google Colab
├── data
    ├──example.csv        # file input Anda
    └──hasil-scrape.csv   # file hasil scraping Anda
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