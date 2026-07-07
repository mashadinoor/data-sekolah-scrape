"""
Scraper data sekolah (nama kepala sekolah, no. telepon, yayasan) berdasarkan NPSN
dari https://sekolah.data.kemendikdasmen.go.id/

Cara pakai:
    1. uv sync   (atau: pip install selenium webdriver-manager requests beautifulsoup4)
    2. Pastikan Google Chrome terpasang di komputer Anda
    3. Salin "data/example.csv" menjadi file baru di folder "data/" (misal
       "data/sekolah.csv"), lalu isi dengan data Anda sendiri. Semua *.csv
       di folder "data/" (kecuali example.csv) akan otomatis dibaca & digabung.
       Format kolom (dipisah ';'): NO; PROVINSI; KABUPATEN/KOTA; NPSN; SEKOLAH
    4. Jalankan: uv run scrape_sekolah.py
    5. Hasil tersimpan di "data/hasil-scrape.csv"

Catatan penting:
    - Situs ini adalah aplikasi Angular (Single Page Application), jadi kontennya
      dimuat lewat JavaScript. Karena itu kita pakai Selenium (browser asli),
      bukan requests biasa.
    - Selector CSS/XPath di bawah dibuat berdasarkan contoh HTML yang diberikan.
      Jika situs berubah struktur, mungkin perlu disesuaikan lagi.
    - Beri jeda antar-request (sudah ada time.sleep) supaya tidak membebani
      server dan tidak dianggap serangan/bot berlebihan.
"""

import time
import csv
import glob
import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

BASE_URL = "https://sekolah.data.kemendikdasmen.go.id/sekolah?keyword={npsn}"

# Situs kedua: server-rendered (tabel HTML biasa), cukup requests + BeautifulSoup
URL_REFERENSI = "https://referensi.data.kemendikdasmen.go.id/snpmb/site/sekolah?npsn={npsn}"

HEADERS_REQUESTS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"
    )
}


def ambil_kepala_sekolah(npsn, timeout=10):
    """
    Ambil nama Kepala Sekolah dari referensi.data.kemendikdasmen.go.id
    Halaman ini berupa tabel HTML biasa:
        <tr><td>Kepala Sekolah</td><td>RUSMIATI</td></tr>
    """
    url = URL_REFERENSI.format(npsn=npsn)
    try:
        resp = requests.get(url, headers=HEADERS_REQUESTS, timeout=timeout)
        resp.raise_for_status()
    except requests.RequestException as e:
        return None, f"gagal request: {e}"

    soup = BeautifulSoup(resp.text, "html.parser")

    for row in soup.find_all("tr"):
        sel = row.find_all("td")
        if len(sel) >= 2:
            label = sel[0].get_text(strip=True)
            value = sel[1].get_text(strip=True)
            if label.lower() == "kepala sekolah":
                return value, "sukses"

    return None, "label 'Kepala Sekolah' tidak ditemukan di halaman"

# -----------------------------------------------------------------------
# Konfigurasi file input & output
# -----------------------------------------------------------------------
# Letakkan semua file CSV daftar sekolah Anda di folder "data/".
# Semua file *.csv di folder ini akan dibaca dan digabung, KECUALI
# "example.csv" (hanya contoh format) dan file output itu sendiri.
# Format kolom yang diharapkan (dipisah ','):
#   NO, PROVINSI, KABUPATEN/KOTA, NPSN, SEKOLAH
DATA_DIR = "data"
INPUT_DELIMITER = ","
FILE_DIKECUALIKAN = {"example.csv"}  # tidak dianggap data asli

OUTPUT_CSV = os.path.join(DATA_DIR, "hasil-scrape.csv")
HEADLESS = True          # set False kalau ingin lihat browser saat proses jalan
TUNGGU_MAKSIMAL = 15      # detik, waktu tunggu maksimal elemen muncul


def cari_file_input(data_dir, dikecualikan):
    """Cari semua *.csv di data_dir, kecuali nama file yang dikecualikan
    (termasuk otomatis mengecualikan file output hasil-scrape.csv)."""
    semua_csv = sorted(glob.glob(os.path.join(data_dir, "*.csv")))
    nama_output = os.path.basename(OUTPUT_CSV)
    return [
        f for f in semua_csv
        if os.path.basename(f) not in dikecualikan
        and os.path.basename(f) != nama_output
    ]


def baca_daftar_sekolah(path_csv, delimiter=";"):
    """
    Baca satu file CSV input dengan kolom: NO; PROVINSI; KABUPATEN/KOTA; NPSN; SEKOLAH
    Mengembalikan list of dict, contoh:
        {"no": "1", "provinsi": "JAWA BARAT", "kabupaten_kota": "KAB. BANDUNG",
         "npsn": "20254054", "sekolah": "SMAN 1 RANCAEKEK"}
    """
    daftar = []
    with open(path_csv, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        # Normalisasi nama header (hilangkan spasi, ubah jadi lowercase & underscore)
        # supaya tidak terlalu sensitif terhadap variasi penulisan header.
        fieldmap = {}
        for h in reader.fieldnames:
            key = h.strip().lower()
            if key == "no":
                fieldmap[h] = "no"
            elif "provinsi" in key:
                fieldmap[h] = "provinsi"
            elif "kabupaten" in key or "kab" in key:
                fieldmap[h] = "kabupaten_kota"
            elif key == "npsn":
                fieldmap[h] = "npsn"
            elif "sekolah" in key:
                fieldmap[h] = "sekolah"
            else:
                fieldmap[h] = key

        for row in reader:
            item = {fieldmap[k]: (v.strip() if v else v) for k, v in row.items()}
            if item.get("npsn"):
                daftar.append(item)

    return daftar


def baca_semua_input(data_dir, delimiter=";", dikecualikan=None):
    """Baca dan gabungkan semua file CSV input di data_dir."""
    dikecualikan = dikecualikan or set()
    file_list = cari_file_input(data_dir, dikecualikan)

    if not file_list:
        raise FileNotFoundError(
            f"Tidak ada file CSV input ditemukan di folder '{data_dir}/'. "
            f"Salin 'data/example.csv' menjadi file baru (misal 'data/sekolah.csv') "
            f"lalu isi dengan data Anda."
        )

    semua = []
    for path in file_list:
        baris = baca_daftar_sekolah(path, delimiter=delimiter)
        print(f"  - {path}: {len(baris)} baris")
        semua.extend(baris)

    return semua


def buat_driver():
    options = Options()
    if HEADLESS:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1366,900")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"
    )
    driver = webdriver.Chrome(options=options)
    return driver


def ambil_teks_aman(driver, by, selector, timeout=5):
    """Ambil teks elemen, kembalikan None kalau tidak ditemukan/timeout."""
    try:
        elemen = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, selector))
        )
        return elemen.text.strip()
    except (TimeoutException, NoSuchElementException):
        return None


def scrape_satu_npsn(driver, npsn):
    hasil = {
        "npsn": npsn,
        "nama_kepala_sekolah": None,
        "telepon": None,
        "yayasan": None,
        "status": "gagal",
    }

    try:
        url = BASE_URL.format(npsn=npsn)
        driver.get(url)

        # 1) Tunggu tombol "Lihat" muncul di hasil pencarian, lalu klik
        tombol_lihat = WebDriverWait(driver, TUNGGU_MAKSIMAL).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[.//span[contains(text(),'Lihat')]]")
            )
        )
        tombol_lihat.click()

        # 2) Tunggu halaman detail termuat -> tunggu elemen telepon muncul
        WebDriverWait(driver, TUNGGU_MAKSIMAL).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href^='tel:']"))
        )
        time.sleep(1)  # jeda kecil supaya semua field sempat ke-render

        # --- Ambil nomor telepon ---
        try:
            telp_elem = driver.find_element(By.CSS_SELECTOR, "a[href^='tel:']")
            hasil["telepon"] = telp_elem.text.strip()
        except NoSuchElementException:
            pass

        # --- Ambil nama yayasan ---
        # Cari label "Yayasan" lalu ambil div senilai di sebelah/bawahnya.
        try:
            label_yayasan = driver.find_element(
                By.XPATH,
                "//*[contains(normalize-space(text()),'Yayasan')]"
            )
            # value biasanya ada di elemen berikutnya dengan class font-semibold
            nilai_yayasan = label_yayasan.find_element(
                By.XPATH,
                "following::div[contains(@class,'font-semibold')][1]"
            )
            hasil["yayasan"] = nilai_yayasan.text.strip()
        except NoSuchElementException:
            pass

        hasil["status"] = "sukses"

    except TimeoutException:
        hasil["status"] = "timeout / elemen tidak ditemukan"
    except Exception as e:
        hasil["status"] = f"error: {e}"

    return hasil


def main():
    print(f"Membaca file input dari folder '{DATA_DIR}/' ...")
    daftar_sekolah = baca_semua_input(
        DATA_DIR, delimiter=INPUT_DELIMITER, dikecualikan=FILE_DIKECUALIKAN
    )
    print(f"Total {len(daftar_sekolah)} baris akan diproses.\n")

    driver = buat_driver()
    semua_hasil = []

    try:
        for item in daftar_sekolah:
            npsn = item["npsn"]
            nama_sekolah = item.get("sekolah", "")
            print(f"Memproses NPSN {npsn} ({nama_sekolah}) ...")

            # 1) Ambil telepon & yayasan via Selenium (situs Angular)
            hasil = scrape_satu_npsn(driver, npsn)

            # 2) Ambil kepala sekolah via requests+bs4 (situs referensi, lebih ringan)
            nama_kepsek, status_kepsek = ambil_kepala_sekolah(npsn)
            hasil["nama_kepala_sekolah"] = nama_kepsek
            if nama_kepsek is None:
                hasil["status"] += f" | kepsek: {status_kepsek}"

            # 3) Gabungkan dengan kolom asal dari file input
            baris_akhir = {
                "no": item.get("no", ""),
                "provinsi": item.get("provinsi", ""),
                "kabupaten_kota": item.get("kabupaten_kota", ""),
                "npsn": npsn,
                "sekolah": nama_sekolah,
                "nama_kepala_sekolah": hasil["nama_kepala_sekolah"],
                "telepon": hasil["telepon"],
                "yayasan": hasil["yayasan"],
                "status": hasil["status"],
            }

            print(f"  -> {baris_akhir}")
            semua_hasil.append(baris_akhir)
            time.sleep(2)  # jeda antar-NPSN, sopan ke server
    finally:
        driver.quit()

    # simpan ke CSV
    os.makedirs(os.path.dirname(OUTPUT_CSV) or ".", exist_ok=True)
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "no", "provinsi", "kabupaten_kota", "npsn", "sekolah",
                "nama_kepala_sekolah", "telepon", "yayasan", "status",
            ],
        )
        writer.writeheader()
        writer.writerows(semua_hasil)

    print(f"\nSelesai. Hasil disimpan di: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()