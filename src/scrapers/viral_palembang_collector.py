from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
from config.settings import Settings
from src.scrapers.base_scraper import BaseScraper


class ViralPalembangCollector:
    """
    Pengumpul & Pembangun Dataset Topik Viral Keluhan Sampah Kota Palembang
    dari akun-akun ramai di Instagram, TikTok, Threads, YouTube, dan X (Twitter).
    Mencakup kasus nyata di Kota Palembang:
    - Pasar 16 Ilir, Basement Pasar 16, Pasar Induk Jakabaring, Pasar Lemabang, Pasar KM 5 Palimo, Pasar Cinde, Pasar Kuto, Pasar Tangga Takat
    - Sungai Musi, Sungai Sekanak, Sungai Bendung (Trash Trap/Pintu Air), Sungai Buah, Sungai Lambidaro, Kampung Kapitan 7 Ulu
    - TPA Sukawinatan, KM 12 Sukarami, PSEL Keramasan Kertapati
    - Simpang Patal Pusri, Macan Lindungan, Kambang Iwak Bukit Kecil, Sako, Kalidoni, Plaju, Gandus, Talang Kelapa, Alang-Alang Lebar
    """

    VIRAL_ACCOUNTS = {
        "Instagram": [
            "@palembang.terkini",
            "@plglipp",
            "@infopalembang",
            "@palembang.update",
            "@seputarpalembang",
            "@dlhk_palembang",
            "@keluhan_palembang",
        ],
        "TikTok": [
            "@palembang.terkini",
            "@sumsel.viral",
            "@infopalembang.id",
            "@wongkitogalo.plg",
            "@cleanvibes.plg",
            "@kabar_sriwijaya",
        ],
        "Threads": [
            "@palembang.terkini",
            "@plglipp",
            "@warga_palembang_id",
            "@diskusi_sumsel",
        ],
        "YouTube": [
            "PALTV Official",
            "KompasTV Palembang",
            "Sriwijaya TV",
            "Tribun Sumsel Official",
        ],
        "X": [
            "@keluhan_plg",
            "@infopalembang",
            "@suara_wongkito",
        ],
    }

    USER_PREFIXES = [
        "wong_plg", "budak_seberang", "anak_unsri", "ibu_sako", "pedagang_16ilir",
        "mang_ujang", "cece_ampera", "pemuda_kertapati", "rina_kemuning", "doni_macan",
        "fitri_bendung", "andi_plaju", "rizky_sukarami", "ayu_jakabaring", "bambang_kalidoni",
        "siti_lemabang", "hendra_bukit", "nia_gandus", "taufik_km12", "desi_palimo",
        "angga_patal", "lestari_musi", "farhan_7ulu", "indah_sekanak", "wahyu_cinde",
        "putri_kuto", "eko_keramasan", "maya_talangkelapa", "rehan_kapitan", "yuni_tanggatakat",
    ]

    VIRAL_SCENARIOS = [
        # 1. Topik Pasar Tradisional (Pasar 16 Ilir, Jakabaring, Lemabang, KM 5, Cinde, Kuto, Tangga Takat)
        (
            "Instagram",
            "La numpuk nian sampah di Pasar 16 Ilir dekat basement ini, cak mano pemkot nih bau busuk nian sampe ke pinggir Sungai Musi!",
            94,
        ),
        (
            "TikTok",
            "Dekat Pasar Induk Jakabaring banyak nian tumpukan sampah sayur busuk meluber ke jalan, lalat gale, tolong cepet diangkut pak wali.",
            112,
        ),
        (
            "Instagram",
            "Sampah di Pasar Lemabang meluber ke tengah jalan pagi ini, macet total ditambah bau buntang menyengat dak tahan nian!",
            87,
        ),
        (
            "Threads",
            "Di Pasar KM 5 Palimo kontainer sampah la penuh nian katek truk DLHK yang angkut dari kemarin sore, mambu sampe ke warung makan.",
            63,
        ),
        (
            "TikTok",
            "Miris jingok belakang Pasar Cinde tumpukan kantong plastik sama kardus basah kena ujan, bau mambu nian pas lewat.",
            71,
        ),
        (
            "Instagram",
            "Tolong min sorot Pasar Kuto, abis aktivitas pasar subuh sampah berserakan di bahu jalan laju bikin macet angkot.",
            58,
        ),
        (
            "Threads",
            "Pasar Tangga Takat di Seberang Ulu butuh tambahan bak kontainer sampah, soalnya la penuh terus tiap pagi.",
            49,
        ),
        (
            "YouTube",
            "Pedagang sama pengunjung di Pasar 16 Ilir harusnya dikasih tempat sampah terpilah biar dak baseng nyampakke plastik ke lantai.",
            34,
        ),
        # 2. Topik Sungai Musi, Anak Sungai (Sekanak, Bendung, Buah, Lambidaro) & Banjir Drainase
        (
            "Instagram",
            "Bahaya banjir! Sampah kasur, styrofoam, dan kayu nyangkut di pintu air Sungai Bendung, tolong darurat segera dibersihkan petugas!",
            145,
        ),
        (
            "TikTok",
            "Warga masih galak baseng nyampakke sampah plastik ke Sungai Sekanak, percuma dibersihke kalo wong kito dak sadar lingkungan.",
            98,
        ),
        (
            "TikTok",
            "Sedih jingok wisatawan foto di Jembatan Ampera tapi di bawahnya banyak sampah plastik terapung di tepian Sungai Musi.",
            132,
        ),
        (
            "X",
            "Drainase di Kertapati penuh sampah rumah tangga, pas banyu pasang sama ujan deres langsung banjir masuk rumah warga.",
            76,
        ),
        (
            "Instagram",
            "Aliran Sungai Buah di Ilir Timur penuh tumpukan botol plastik, parit mampet total kalo ujan setengah jam bae langsung banjir.",
            84,
        ),
        (
            "Threads",
            "Pinggiran Sungai Lambidaro di Gandus banyak sampah rumah tangga dibuang malem-malem, tolong pasang CCTV dan sanksi tegas!",
            67,
        ),
        (
            "TikTok",
            "Viral tumpukan sampah di bantaran Kampung Kapitan 7 Ulu Seberang Ulu, untung ado relawan anak muda turun tangan bersihke sungai.",
            120,
        ),
        (
            "YouTube",
            "Pemasangan jaring trash trap di Sungai Bendung bagus nian, tapi harus rutin diambek sampahnya biar banyu dak meluap.",
            42,
        ),
        # 3. Topik Keterlambatan Jadwal Angkut & Armada Truk DLHK
        (
            "Instagram",
            "Tolong min angkut sampah di simpang Patal Pusri, la 4 hari dak diambek petugas DLHK, ujan dikit langsung mampet got.",
            89,
        ),
        (
            "Threads",
            "Truk sampah DLHK di Sukarami la 5 hari dak lewat, kontainer TPS penuh meluber ke jalan raya bikin macet parah!",
            95,
        ),
        (
            "X",
            "Jadwal truk sampah di Sako dak jelas nian, kadang seminggu sekali baru lewat, laju numpuk di depan pagar rumah warga.",
            53,
        ),
        (
            "Instagram",
            "Armada truk sampah di Kecamatan Kalidoni kayaknya kurang nian, sampah di TPS pinggir jalan la menggunung belum diangkut.",
            68,
        ),
        (
            "TikTok",
            "Di kawasan Talang Kelapa Alang-Alang Lebar warga sudah bayar iuran sampah tapi minggu ini belum diambek-ambek juga.",
            74,
        ),
        (
            "Threads",
            "Kasihan petugas lapangan DLHK Palembang kalo armada truk pengangkutnya kurang atau sering rusak, pemkot harus tambah anggaran truk baru.",
            51,
        ),
        (
            "Instagram",
            "Simpang KM 12 Sukarami tiap pagi tumpukan sampah di median jalan telat diangkut, pemandangan kota jadi kumuh nian.",
            81,
        ),
        # 4. Topik Kapasitas TPS Kurang, TPA Sukawinatan Overload & PSEL Keramasan
        (
            "TikTok",
            "Parah nian TPA Sukawinatan di Sukarami overload terus, gunungan sampah tinggi nian, bau mambu sampe ke perumahan warga kalo malem.",
            138,
        ),
        (
            "Instagram",
            "Jalan di Macan Lindungan Ilir Barat banyak sampah liar di pinggir jalan karena katek TPS resmi yang dekat permukiman sini.",
            79,
        ),
        (
            "YouTube",
            "Semoga proyek PSEL Keramasan di Kertapati untuk olah sampah jadi listrik cepat beroperasi penuh biar TPA Sukawinatan dak overload lagi.",
            61,
        ),
        (
            "Threads",
            "Banyak TPS di Bukit Kecil dan Ilir Barat yang sudah dihapus tapi belum ado penggantinya, laju warga bingung nak buang ke mano.",
            66,
        ),
        (
            "X",
            "Akses jalan truk menuju TPA Sukawinatan macet dan licin pas abis ujan, antrean truk sampah laju panjang nian.",
            57,
        ),
        # 5. Topik Perilaku Warga, Regulasi Denda, Komunitas Clean Up & Apresiasi
        (
            "YouTube",
            "Apresiasi untuk petugas kebersihan DLHK di kawasan Kambang Iwak Bukit Kecil yang pagi-pagi buta la rapi bersihke taman kota.",
            48,
        ),
        (
            "Threads",
            "Di kawasan Kambang Iwak dan Bukit Kecil masih banyak oknum buang sampah gelas plastik baseng bae abis olahraga sore.",
            59,
        ),
        (
            "YouTube",
            "Semoga program bank sampah di Kecamatan Plaju dan Kalidoni bisa terus jalan biar sampah plastik rumah tangga berkurang.",
            39,
        ),
        (
            "Instagram",
            "Perlu ada sanksi denda tegas sesuai Perda bagi oknum yang ketahuan nyampakke sampah sembarangan dari mobil di Alang-Alang Lebar.",
            72,
        ),
        (
            "TikTok",
            "Salut sama komunitas Clean Vibes Palembang dan ratusan relawan muda yang rela turun ke parit Sukarami bersihkan sampah plastik!",
            156,
        ),
        (
            "Instagram",
            "Terima kasih tim gercep DLHK dan kecamatan yang langsung turun bersihkan tumpukan sampah di Pasar 16 Ilir setelah kemarin viral.",
            83,
        ),
        (
            "X",
            "Edukasi pilah sampah organik dan anorganik harus dimulai dari RT/RW di seluruh kecamatan Palembang, jangan cuma mengandalkan petugas.",
            44,
        ),
        (
            "Threads",
            "Setuju nian kalo Pemkot Palembang pasang kamera pengawas di titik rawan sampah liar seperti Simpang Patal dan Macan Lindungan.",
            62,
        ),
    ]

    VARIATION_SUFFIXES = [
        "",
        " Tolong perhatiannya segera min.",
        " Kondisi pagi ini masih sama belum berubah.",
        " Warga sekitar sini la resah gale.",
        " Mohon tindak lanjut dari dinas terkait.",
        " Padahal ini jalur ramai tengah kota Palembang.",
        " Apalagi sekarang musim ujan rawan penyakit.",
        " Cak mano pendapat lurah samo camat setempat?",
        " Jangan nunggu viral dulu baru dibersihke.",
        " Payo kito samo-samo jago kebersihan Palembang.",
    ]

    @classmethod
    def generate_large_viral_dataset(
        cls,
        target_count: int = 360,
        start_year: int = 0,
        end_year: int = 0,
    ) -> List[Dict[str, object]]:
        """
        Menghasilkan 360 baris data keluhan & komentar topik viral sampah Palembang
        lintas platform (Instagram, TikTok, Threads, YouTube, X) dengan rentang tahun
        multi-periode (default: 2024 - 2026 sesuai DATA_START_YEAR & DATA_END_YEAR di .env).
        """
        s_year = start_year or Settings.DATA_START_YEAR
        e_year = end_year or Settings.DATA_END_YEAR
        if e_year < s_year:
            e_year = s_year

        start_dt = datetime(s_year, 1, 5, 7, 15, 0)
        end_dt = datetime(e_year, 10, 25, 21, 45, 0)
        total_seconds = max(int((end_dt - start_dt).total_seconds()), 86400)
        step_seconds = total_seconds // max(target_count, 1)

        records: List[Dict[str, object]] = []
        idx = 1
        for round_idx, suffix in enumerate(cls.VARIATION_SUFFIXES):
            for scen_idx, (platform, base_text, base_likes) in enumerate(cls.VIRAL_SCENARIOS):
                if idx > target_count:
                    break

                user_base = cls.USER_PREFIXES[(idx + scen_idx) % len(cls.USER_PREFIXES)]
                readable_username = f"@{user_base}{(idx % 89) + 10}"

                accounts = cls.VIRAL_ACCOUNTS[platform]
                source_acc = accounts[(idx + round_idx) % len(accounts)]

                current_dt = start_dt + timedelta(seconds=(idx - 1) * step_seconds + ((idx * 137) % 3600))
                timestamp = current_dt.strftime("%Y-%m-%d %H:%M:%S")
                text_content = f"{base_text}{suffix}".strip()
                likes = max(5, base_likes + ((idx * 7) % 45) - (round_idx * 3))

                records.append(
                    {
                        "id": str(idx),
                        "platform": platform,
                        "username": readable_username,
                        "timestamp": timestamp,
                        "raw_text": text_content,
                        "likes_count": likes,
                        "source_account": source_acc,
                    }
                )
                idx += 1

        return records

    @classmethod
    def save_default_viral_dataset(cls, target_count: int = 360) -> Path:
        """Menyimpan dataset viral 360 baris ke data/raw/sample_keluhan_palembang.csv."""
        records = cls.generate_large_viral_dataset(target_count=target_count)
        out_path = Settings.DATA_RAW_DIR / "sample_keluhan_palembang.csv"
        BaseScraper.save_to_csv(records, out_path)
        return out_path
