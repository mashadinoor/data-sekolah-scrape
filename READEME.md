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
- Google Chrome terpasang di komputer

## Instalasi

```bash
git clone https://github.com/<username-anda>/npsn-scraper.git
cd npsn-scraper
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Cara pakai

1. Buka `scrape_sekolah.py`
2. Isi daftar NPSN yang ingin dicari pada variabel `DAFTAR_NPSN`:
   ```python
   DAFTAR_NPSN = [
       "20254054",
       "20254055",
   ]
   ```
3. Jalankan:
   ```bash
   python scrape_sekolah.py
   ```
4. Hasil akan tersimpan di `hasil_sekolah.csv` dengan kolom:
   `npsn, nama_kepala_sekolah, telepon, yayasan, status`

## Struktur Proyek

```
npsn-scraper/
├── scrape_sekolah.py     # skrip utama
├── requirements.txt      # daftar dependensi
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