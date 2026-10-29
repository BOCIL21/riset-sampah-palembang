# Sistem Scraping Sosial Media & Analisis AI Keluhan Sampah Kota Palembang (2 Jurnal)

Repositori ini dirancang dengan arsitektur Python modular untuk mendukung **2 judul publikasi jurnal ilmiah** secara terpisah, namun berbagi fondasi *data scraping*, *anonimisasi privasi data*, dan *normalisasi Bahasa Palembang (Baso Palembang)*.

---

## 1. Pembagian Fokus 2 Judul Jurnal

| Karakteristik | Jurnal 1 (`src/jurnal_1_nlp/`) | Jurnal 2 (`src/jurnal_2_geospasial/`) |
| :--- | :--- | :--- |
| **Usulan Judul (ID)** | *Analisis Sentimen dan Pemodelan Topik Keluhan Masyarakat Terkait Pengelolaan Sampah di Kota Palembang Menggunakan IndoBERT dan BERTopic* | *Ekstraksi Entitas Lokasi dan Klasifikasi Tingkat Urgensi Keluhan Sampah di Kota Palembang Berbasis Large Language Models (LLM) untuk Mendukung Smart Environment* |
| **Usulan Judul (EN / Scopus)** | *Unveiling Public Complaints on Urban Waste Management in Palembang: A Hybrid IndoBERT and BERTopic Approach on Social Media Data* | *Automated Geotagging and Urgency Classification of Citizen Waste Complaints in Palembang Using Large Language Models for Smart Governance* |
| **Fokus Metodologi AI** | Normalisasi Bahasa Palembang + Klasifikasi Sentimen/Emosi (`IndoBERT` / `LLM`) + Topic Clustering (`BERTopic`) + Evaluasi `Cohen's Kappa` & `Macro F1-Score`. | Named Entity Recognition (`NER`) Geospasial Palembang + Skoring Tingkat Urgensi (`0–100`) + Rekomendasi SLA Tindakan DLHK + Pemetaan Interaktif GIS (`Leaflet HTML`). |
| **File Eksekusi Utama** | `python main_jurnal1.py` | `python main_jurnal2.py` |
| **Folder Output** | `data/outputs/jurnal_1/` | `data/outputs/jurnal_2/` |

---

## 2. Struktur Direktori Proyek

```text
C:\laragon\www\riset_sampah_palembang\
├── .env.example                    # Template konfigurasi API Key & Akun Sosmed
├── requirements.txt                # Daftar dependensi library Python
├── README.md                       # Dokumentasi & Tutorial Lengkap
├── config/
│   ├── settings.py                 # Loader konfigurasi terpusat (.env)
│   ├── kamus_palembang.json        # Kamus Slang Bahasa Palembang -> Indonesia Baku
│   └── gazetteer_palembang.json    # Database Koordinat, Pasar, Sungai & Kecamatan di Palembang
├── data/
│   ├── raw/
│   │   └── sample_keluhan_palembang.csv  # Dataset sampel realistis untuk pengujian
│   ├── processed/
│   └── outputs/
│       ├── jurnal_1/               # Output CSV & JSON ringkasan statistik Jurnal 1
│       └── jurnal_2/               # Output CSV, JSON & Peta HTML Interaktif Jurnal 2
├── src/
│   ├── ai_providers/
│   │   └── llm_client.py           # Wrapper LLM (Gemini, OpenAI, & Offline Fallback)
│   ├── scrapers/
│   │   ├── base_scraper.py         # Base class + Anonimisasi SHA-256 (etika jurnal)
│   │   ├── instagram_scraper.py    # Scraper komentar Instagram (Instaloader / Apify)
│   │   ├── threads_scraper.py      # Scraper diskusi & balasan Meta Threads (threads.net)
│   │   ├── youtube_scraper.py      # Scraper komentar YouTube (YouTube Data API v3)
│   │   └── twitter_scraper.py      # Scraper X / Twitter (Tweet-Harvest CLI / CSV)
│   ├── preprocessing/
│   │   ├── text_cleaner.py         # Pembersihan URL, mention, hashtag, karakter khusus
│   │   └── palembang_normalizer.py # Hybrid Normalizer (Kamus Palembang + LLM)
│   ├── jurnal_1_nlp/               # Modul Khusus Jurnal 1
│   │   ├── sentiment_analyzer.py   # Analisis Sentimen & Emosi
│   │   ├── topic_modeler.py        # Pemodelan 5 Topik Utama Sampah Palembang / BERTopic
│   │   ├── evaluator.py            # Perhitungan Accuracy, Precision, Recall, F1, Cohen's Kappa
│   │   └── pipeline_jurnal1.py     # Orchestrator Pipeline Jurnal 1
│   └── jurnal_2_geospasial/        # Modul Khusus Jurnal 2
│       ├── location_extractor.py   # Ekstraksi Entitas Lokasi & Koordinat Palembang
│       ├── urgency_classifier.py   # Skoring Urgensi (0-100) & Rekomendasi Tindakan DLHK
│       ├── gis_mapper.py           # Generator Peta Hotspot HTML Interaktif (Leaflet.js)
│       └── pipeline_jurnal2.py     # Orchestrator Pipeline Jurnal 2
├── main_jurnal1.py                 # Entry point eksekusi riset Jurnal 1
├── main_jurnal2.py                 # Entry point eksekusi riset Jurnal 2
├── colab/                          # Notebook siap pakai untuk Google Colab (GPU T4 Gratis)
│   ├── Colab_Jurnal_1_IndoBERT_BERTopic.ipynb
│   └── Colab_Jurnal_2_NER_GIS_Palembang.ipynb
└── tests/                          # Unit & Integration Tests (15 pengujian otomatis)
    ├── test_preprocessing.py
    ├── test_scrapers.py
    ├── test_jurnal1_nlp.py
    └── test_jurnal2_geospasial.py
```

---

## 3. Kebutuhan Kredensial, Username, Password & API Key

Secara bawaan (*default*), aplikasi berjalan dalam mode **`offline_fallback`** sehingga Anda dapat langsung menguji seluruh pipeline tanpa API Key. Namun, untuk melakukan **Live Scraping** dan **Live AI Inference**, Anda memerlukan kredensial berikut di dalam file `.env`:

### A. Kebutuhan AI / Large Language Model (LLM)
Digunakan untuk menormalisasi kalimat *slang* Bahasa Palembang yang kompleks, *Zero-Shot Sentiment Analysis*, serta ekstraksi entitas lokasi (NER).

| Parameter `.env` | Apa yang Dibutuhkan? | Cara Mendapatkan |
| :--- | :--- | :--- |
| `AI_PROVIDER` | Isi dengan `gemini`, `openai`, atau `offline_fallback` | Pilih `gemini` jika memakai Google AI Studio, atau `openai` jika memakai ChatGPT API. |
| `GEMINI_API_KEY` | API Key dari Google Gemini | 1. Buka [Google AI Studio](https://aistudio.google.com/)<br>2. Login dengan akun Google<br>3. Klik **Get API Key** -> **Create API Key**.<br>*(Sangat direkomendasikan karena memiliki tier gratis dan model `gemini-1.5-flash` sangat cepat)*. |
| `OPENAI_API_KEY` | API Key dari OpenAI *(Opsional jika sudah pakai Gemini)* | Buat melalui dashboard [OpenAI Platform](https://platform.openai.com/api-keys). |

### B. Kebutuhan Scraping Sosial Media
Pilih platform sosial media yang ingin dijadikan sumber data utama penelitian Anda:

| Platform | Parameter `.env` | Apa yang Dibutuhkan & Cara Mendapatkan | Catatan Keamanan Penting |
| :--- | :--- | :--- | :--- |
| **1. Instagram** *(Akun berita lokal seperti `@palembang.terkini`, `@plglipp`, `@infopalembang`)* | `IG_USERNAME`<br>`IG_PASSWORD`<br>*(atau)*<br>`APIFY_API_TOKEN` | **Opsi 1 (Gratis via Instaloader):** Masukkan username dan password akun Instagram.<br>**Opsi 2 (Aman via Apify):** Daftar di [Apify.com](https://apify.com/), buka menu *Settings -> Integrations*, lalu salin **Personal API Token**. | **WAJIB gunakan akun Instagram kedua (akun dummy/riset)** jika memakai `IG_USERNAME` & `IG_PASSWORD`. Jangan gunakan akun pribadi utama untuk menghindari pembatasan (*rate-limit*) dari pihak Instagram. |
| **2. YouTube** *(Berita lokal PALTV, Sriwijaya TV, KompasTV Sumsel)* | `YOUTUBE_API_KEY` | 1. Buka [Google Cloud Console](https://console.cloud.google.com/)<br>2. Buat Project baru -> Masuk ke **APIs & Services -> Library**<br>3. Cari **YouTube Data API v3** lalu klik **Enable**<br>4. Masuk ke menu **Credentials -> Create Credentials -> API Key**. | **Paling direkomendasikan & 100% aman.** Resmi dari Google dengan kuota gratis 10.000 unit/hari (cukup untuk mengambil ribuan komentar tanpa risiko blokir). |
| **3. X / Twitter** *(Pencarian kata kunci `"sampah palembang"`)* | `TWITTER_AUTH_TOKEN` | 1. Login ke [x.com](https://x.com) di browser Chrome/Edge menggunakan akun riset<br>2. Tekan **F12 (Inspect Element)** -> pilih tab **Application**<br>3. Di menu kiri, buka **Cookies -> `https://x.com`**<br>4. Cari baris bernama **`auth_token`**, lalu salin nilai (*Value*) kode heksadesimalnya. | Membutuhkan **Node.js (`npx`)** terinstal di komputer karena menggunakan *Tweet-Harvest*. Gunakan akun X sekunder/riset. |
| **4. Meta Threads** *(Utas warga Palembang & akun berita lokal di `threads.net`)* | `THREADS_SESSION_ID`<br>*(atau)*<br>`THREADS_USERNAME` & `THREADS_PASSWORD`<br>*(atau)*<br>`APIFY_API_TOKEN` | **Opsi 1 (Cookie Session):** Login ke [threads.net](https://www.threads.net) di browser -> tekan **F12 (Inspect)** -> tab **Application -> Cookies -> `https://www.threads.net`** -> salin nilai cookie **`sessionid`**.<br>**Opsi 2 (Via Apify):** Gunakan `APIFY_API_TOKEN` yang sama dengan Instagram untuk memanggil actor `apify/threads-scraper`. | Sangat potensial untuk jurnal terbaru karena banyak warga Palembang beralih menyampaikan keluhan publik di **Threads** sejak 2024–2026. Gunakan akun dummy/riset. |

### C. Kebutuhan Model Transformer Lokal (IndoBERT & BERTopic)
| Parameter `.env` | Apa yang Dibutuhkan? | Keterangan |
| :--- | :--- | :--- |
| `USE_TRANSFORMERS` | `true` atau `false` | Ubah menjadi `true` jika Anda ingin mengaktifkan model Neural Network **IndoBERT** & **BERTopic** secara lokal di laptop atau di GPU Google Colab. Jika `false`, program memakai model *Lexicon & Taxonomy Baseline* lokal yang ringan. |
| `INDOBERT_MODEL_PATH` | `mdhugol/indonesia-bert-sentiment-classification` | Nama repositori model IndoBERT di HuggingFace yang sudah di-*fine-tune* untuk klasifikasi Sentimen Bahasa Indonesia (`Positif`, `Netral`, `Negatif`). |

### D. Kebutuhan Geocoding & Cara Mendapatkan `GOOGLE_MAPS_API_KEY` (Jurnal 2)
Untuk **Jurnal 2 (Pemetaan GIS)**, program sebenarnya **sudah dilengkapi Database Koordinat Lokal Kota Palembang (`config/gazetteer_palembang.json`)** dan peta interaktif berbasis **OpenStreetMap / Leaflet.js** yang **100% GRATIS tanpa perlu API Key dan tanpa kartu kredit**.

Namun, jika ada nama jalan/gang baru di Palembang yang belum terdaftar di `gazetteer_palembang.json`, Anda dapat mengisi `GOOGLE_MAPS_API_KEY` agar sistem otomatis mencari titik koordinatnya ke server Google Maps:

| Parameter `.env` | Langkah demi Langkah Cara Mendapatkan `GOOGLE_MAPS_API_KEY` |
| :--- | :--- |
| `GOOGLE_MAPS_API_KEY` | 1. Buka [Google Cloud Console](https://console.cloud.google.com/) dan login dengan akun Google Anda.<br>2. Pilih project yang sama saat Anda membuat `YOUTUBE_API_KEY` (atau klik **New Project**).<br>3. Buka menu **APIs & Services -> Library** di sebelah kiri.<br>4. Ketik **`Geocoding API`** pada kolom pencarian, klik **Geocoding API**, lalu klik tombol **Enable**.<br>*(Catatan: Google Maps Platform mewajibkan akun Billing aktif, namun memberikan kuota gratis senilai \$200/bulan atau sekitar 40.000 request geocoding gratis per bulan).*<br>5. Buka menu **APIs & Services -> Credentials** -> klik **+ Create Credentials -> API key**.<br>6. Salin API Key yang muncul (diawali dengan `AIzaSy...`) lalu tempelkan ke baris `GOOGLE_MAPS_API_KEY=` di dalam file `.env` Anda. |
| **Alternatif Tanpa Kartu Kredit (100% Gratis)** | Jika tidak ingin mengaktifkan Billing Google Cloud, biarkan `GOOGLE_MAPS_API_KEY` kosong/default. Anda cukup menambahkan nama lokasi baru beserta koordinat `lat` dan `lon`-nya (bisa dilihat dari klik kanan di Google Maps biasa) ke dalam file [`config/gazetteer_palembang.json`](config/gazetteer_palembang.json). |

---

## 4. Tutorial Lengkap Cara Menjalankan di Google Colab (GPU T4 Gratis)

Menjalankan riset ini di **Google Colab** sangat direkomendasikan karena Anda mendapat fasilitas **GPU NVIDIA T4 Gratis** untuk menjalankan model Deep Learning **IndoBERT** dan **BERTopic** tanpa membebani laptop:

### Tahap 1: Upload Proyek ke Google Drive
1. Buka [Google Drive](https://drive.google.com/) di browser Anda.
2. Klik tombol **+ Baru (+ New) -> Upload Folder**.
3. Pilih folder `C:\laragon\www\riset_sampah_palembang` (yang sekarang sudah bersih dan hanya berisi ~45 file ringan).
4. Tunggu beberapa detik hingga folder `riset_sampah_palembang` masuk ke halaman utama Google Drive Anda (`MyDrive/riset_sampah_palembang`).

### Tahap 2: Menjalankan Jurnal 1 di Google Colab (IndoBERT & BERTopic)
1. Di dalam Google Drive Anda, buka folder `riset_sampah_palembang` -> buka folder **`colab`**.
2. Klik 2 kali pada file **`Colab_Jurnal_1_IndoBERT_BERTopic.ipynb`** (pilih **Open with -> Google Colaboratory**).
3. **Aktifkan GPU Gratis:** Di menu bagian atas Google Colab, klik **Runtime -> Change runtime type** -> pada bagian *Hardware accelerator* pilih **T4 GPU** -> klik **Save**.
4. Jalankan tiap sel (*cell*) dari atas ke bawah dengan menekan tombol **Play (▶)** di sebelah kiri sel:
   * **Sel #1 (Mount Drive):** Akan muncul pop-up izin akses Google Drive -> klik **Connect to Google Drive** -> pilih akun Google Anda -> klik **Allow**.
   * **Sel #2 (Install Library):** Menginstal `bertopic`, `python-dotenv`, `instaloader`, dan `apify-client` (bebas konflik *protobuf*).
   * **Sel #3 (Konfigurasi AI):** Secara otomatis menyalakan `USE_TRANSFORMERS = 'true'` agar Jurnal 1 menggunakan **IndoBERT** dan **BERTopic**.
   * **Sel #4 (Eksekusi Pipeline Jurnal 1):** Menjalankan 15 unit test dan memproses **360 dokumen keluhan sampah Palembang**.
   * **Sel #5 (Tabel Visual):** Menampilkan tabel hasil analisis Jurnal 1 langsung di layar Colab.
5. **Cara Mengunduh Hasil Jurnal 1:** Hasil CSV (`hasil_analisis_jurnal1.csv`) dan JSON (`ringkasan_jurnal1.json`) otomatis tersimpan di Google Drive Anda pada folder `riset_sampah_palembang/data/outputs/jurnal_1/`.

### Tahap 3: Menjalankan Jurnal 2 di Google Colab (NER Lokasi, Skor Urgensi & Peta GIS)
1. Kembali ke folder `riset_sampah_palembang/colab/` di Google Drive Anda.
2. Klik 2 kali pada file **`Colab_Jurnal_2_NER_GIS_Palembang.ipynb`**.
3. Jalankan tombol **Play (▶)** berurutan mulai dari **Sel #1 hingga Sel #5**:
   * **Sel #1 & #2:** Menghubungkan Google Drive dan menyiapkan library.
   * **Sel #3:** Menjalankan `python main_jurnal2.py` untuk mengekstrak titik lokasi Palembang, menghitung skor urgensi (`0–100`), dan membuat file peta GIS HTML.
   * **Sel #4:** Menampilkan tabel prioritas penanganan darurat sampah untuk DLHK Kota Palembang.
   * **Sel #5:** **Menampilkan Peta Interaktif Hotspot Sampah Kota Palembang langsung di dalam halaman Google Colab!** (Anda bisa melakukan *zoom-in/out*, klik titik merah/oranye/hijau untuk melihat detail keluhan & rekomendasi AI, lalu di-*screenshot* untuk gambar publikasi Jurnal 2).

---

## 5. Tutorial Menjalankan Secara Lokal di Laptop (CMD / PowerShell)

**Jika menggunakan Command Prompt (CMD):**
```cmd
cd C:\laragon\www\riset_sampah_palembang
copy .env.example .env
python -m unittest discover -s tests -v
python main_jurnal1.py
python main_jurnal2.py
```

**Jika menggunakan PowerShell:**
```powershell
cd C:\laragon\www\riset_sampah_palembang
Copy-Item .env.example .env
python -m unittest discover -s tests -v
python main_jurnal1.py
python main_jurnal2.py
```

---

### Langkah 3: Menjalankan Pengujian Otomatis (Unit Testing)
Sebelum menjalankan riset penuh, pastikan seluruh modul berjalan normal dengan menjalankan 14 *unit test* bawaan:

```powershell
python -m unittest discover -s tests -v
```

Jika seluruh konfigurasi kode baik, terminal akan menampilkan:
```text
Ran 14 tests in 0.073s
OK
```

---

### Langkah 4: Menjalankan Pipeline Jurnal 1 (NLP, Sentimen & Pemodelan Topik)
Jalankan perintah berikut untuk memproses data keluhan untuk kebutuhan **Jurnal 1**:

```powershell
python main_jurnal1.py
```

**Hasil yang didapat untuk Jurnal 1 (`data/outputs/jurnal_1/`):**
1. `hasil_analisis_jurnal1.csv` — Berisi teks asli, username yang sudah dianonimisasi (`USER_xxxx`), hasil normalisasi Bahasa Palembang, label sentimen (`Negatif`/`Positif`/`Netral`), kategori emosi (`Marah_Kecewa`, `Khawatir_Darurat`, `Harapan_Saran`, `Apresiasi`), serta klaster topik keluhan.
2. `ringkasan_jurnal1.json` — Berisi rekapitulasi jumlah distribusi sentimen, distribusi topik, serta nilai **Accuracy, Macro Precision, Macro Recall, Macro F1-Score, dan Cohen's Kappa** yang siap dimasukkan ke dalam Tabel Bab 4 Jurnal 1.

---

### Langkah 5: Menjalankan Pipeline Jurnal 2 (NER Geospasial, Urgensi & Peta GIS)
Jalankan perintah berikut untuk memproses data keluhan untuk kebutuhan **Jurnal 2**:

```powershell
python main_jurnal2.py
```

**Hasil yang didapat untuk Jurnal 2 (`data/outputs/jurnal_2/`):**
1. `hasil_geospasial_urgensi_jurnal2.csv` — Berisi hasil deteksi lokasi spesifik di Kota Palembang (misal: *Pasar 16 Ilir, Simpang Patal, TPA Sukawinatan, Sungai Bendung*), nama Kecamatan, koordinat (`latitude`, `longitude`), skor urgensi (`0–100`), level urgensi (`TINGGI_KRITIS`, `SEDANG`, `RENDAH`), target SLA penanganan, dan rekomendasi tindakan otomatis untuk DLHK Palembang.
2. `ringkasan_jurnal2.json` — Statistik sebaran keluhan per kecamatan, tipe kawasan (Pasar Tradisional, Sungai/Drainase, TPA, Jalan), dan **Top 3 Prioritas Darurat**.
3. `peta_hotspot_sampah_palembang.html` — **Peta Interaktif GIS Kota Palembang**. Buka file ini langsung di browser (Chrome/Edge) untuk melihat titik merah/oranye/hijau lokasi keluhan sampah di Palembang beserta *popup* detail rekomendasinya. Peta ini dapat langsung di-*screenshot* sebagai gambar visualisasi spasial pada naskah Jurnal 2.

---

## 5. Cara Mengambil Data Baru (Live Scraping) ke Dalam Pipeline

Contoh skrip singkat jika Anda sudah mengisi `YOUTUBE_API_KEY` atau `IG_USERNAME` di `.env` dan ingin mengambil data baru lalu langsung memasukkannya ke Jurnal 1 dan Jurnal 2:

```python
from pathlib import Path
from src.scrapers.youtube_scraper import YouTubeScraper
from src.scrapers.threads_scraper import ThreadsScraper
from src.jurnal_1_nlp.pipeline_jurnal1 import PipelineJurnal1
from src.jurnal_2_geospasial.pipeline_jurnal2 import PipelineJurnal2

# Contoh A: Tarik komentar dari video berita sampah Palembang di YouTube
yt = YouTubeScraper()
data_komentar = yt.fetch_comments(video_id="MASUKKAN_ID_VIDEO_YOUTUBE", limit=100)

# Contoh B: Atau tarik utas keluhan sampah Palembang dari Meta Threads
th = ThreadsScraper()
data_threads = th.fetch_comments(keyword_or_post_url="sampah palembang", limit=100)
data_komentar.extend(data_threads)

# 2. Simpan ke folder data/raw/
raw_csv_path = Path("data/raw/hasil_scraping_gabungan.csv")
yt.save_to_csv(data_komentar, raw_csv_path)

# 3. Jalankan analisis untuk Jurnal 1 dan Jurnal 2 menggunakan data baru tersebut
PipelineJurnal1().run(input_csv=raw_csv_path)
PipelineJurnal2().run(input_csv=raw_csv_path)
```

---

## 6. Tips Tambahan untuk Menembus Jurnal SINTA

1. **Kamus Bahasa Palembang (`config/kamus_palembang.json`):** Terus tambahkan kosakata *slang* Palembang baru yang Anda temukan saat proses *scraping*. Di dalam naskah jurnal, tonjolkan keberadaan kamus normalisasi lokal ini sebagai salah satu kontribusi orisinal (*novelty*).
2. **Validasi Ahli (Human-in-the-loop):** Ambil sampel sekitar 200–300 baris dari `hasil_analisis_jurnal1.csv`, berikan label manual oleh 2 orang anotator, lalu gunakan modul `EvaluatorJurnal1.evaluate_predictions(label_manusia, label_ai)` di `src/jurnal_1_nlp/evaluator.py` untuk mendapatkan skor **Cohen's Kappa** riil. Reviewer jurnal sangat menyukai validasi ini.
3. **Kepatuhan Etika Penelitian:** Sebutkan di bagian *Methodology* bahwa seluruh identitas akun warga telah dianonimisasi menggunakan algoritma *one-way cryptographic hashing* (`SHA-256`) pada modul `BaseScraper.anonymize_username()`.
