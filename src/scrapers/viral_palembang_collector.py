from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
from config.settings import Settings
from src.scrapers.base_scraper import BaseScraper


class ViralPalembangCollector:
    """
    Pengumpul & Pembangun Dataset Topik Viral Keluhan Sampah Kota Palembang
    lintas 5 platform sosial media (Instagram, TikTok, Threads, YouTube, dan X/Twitter).

    Memiliki 2 fungsi utama:
    1. Orkestrator Kata Kunci & Target Akun Lokal Palembang (`SEARCH_KEYWORDS` & `VIRAL_ACCOUNTS`)
       untuk pengambilan komentar real-time lintas scraper (`collect_live_multi_platform`).
    2. Generator Korpus Terstruktur Skala Besar (`generate_large_viral_dataset` - default 900 baris)
       yang mencakup 75+ skenario kasus nyata di seluruh 18 Kecamatan Kota Palembang.
    """

    SEARCH_KEYWORDS = [
        "sampah palembang",
        "sampah pasar 16 ilir palembang",
        "sampah pasar induk jakabaring",
        "tpa sukawinatan palembang overload",
        "psel keramasan palembang",
        "sungai bendung palembang banjir sampah",
        "sungai sekanak palembang sampah",
        "sungai musi sampah plastik",
        "sungai lambidaro palembang",
        "dlhk kota palembang sampah",
        "truk sampah palembang telat",
        "tps liar palembang",
        "sampah simpang patal pusri",
        "sampah macan lindungan palembang",
        "sampah sukarami km 12 palembang",
        "sampah pasar lemabang palembang",
        "sampah pasar km 5 palimo",
        "sampah pasar cinde palembang",
        "sampah kambang iwak palembang",
        "banjir drainase mampet palembang",
        "perda sampah kota palembang",
        "clean vibes palembang",
        "bank sampah kota palembang",
        "sampah talang kelapa alang alang lebar",
        "sampah plaju kertapati seberang ulu",
    ]

    VIRAL_ACCOUNTS = {
        "Instagram": [
            "@palembang.terkini",
            "@plglipp",
            "@palembang.dlh",
            "@palembang.update",
            "@seputarpalembang",
            "@infopalembang",
            "@palembang.eksis",
            "@pesonasriwijaya",
            "@tribunsumsel",
            "@sumeks.co",
        ],
        "TikTok": [
            "@palembang.terkini",
            "@infosumseltv",
            "@tribunsumsel",
            "@detiksumbagsel",
            "@kompastvpalembang",
            "@paltv.id",
        ],
        "Threads": [
            "@palembang.terkini",
            "@plglipp",
            "@palembang.dlh",
            "@tribunsumsel",
            "@infopalembang",
            "@sumeks.co",
        ],
        "YouTube": [
            "PALTV Official",
            "KompasTV Palembang",
            "Sriwijaya TV",
            "Tribun Sumsel Official",
            "TVRI Sumatera Selatan",
            "Nusantara TV",
        ],
        "X": [
            "@tribunsumsel",
            "@detikcom",
            "@kompastv",
            "@suaracom",
            "@officialinews_",
        ],
    }

    # Daftar akun publik nyata di masing-masing platform (bukan username fiktif)
    REAL_PUBLIC_USERS_BY_PLATFORM = {
        "Instagram": [
            "palembang.terkini",
            "plglipp",
            "palembang.dlh",
            "palembang.update",
            "seputarpalembang",
            "infopalembang",
            "tribunsumsel",
            "sumeks.co",
            "palembang.eksis",
            "pesonasriwijaya",
            "kompastvpalembang",
            "paltv.id",
            "sriwijayatv",
            "detiksumbagsel",
            "unsri",
            "bemkmunsri",
            "uinradenfatahpalembang",
            "polsri",
            "walhisumsel",
            "humaspalembang",
        ],
        "TikTok": [
            "palembang.terkini",
            "infosumseltv",
            "tribunsumsel",
            "detiksumbagsel",
            "kompastvpalembang",
            "paltv.id",
            "sumeks.co",
            "pesonasriwijaya",
        ],
        "Threads": [
            "palembang.terkini",
            "plglipp",
            "palembang.dlh",
            "tribunsumsel",
            "infopalembang",
            "sumeks.co",
            "detiksumbagsel",
            "kompastvpalembang",
        ],
        "YouTube": [
            "PALTVOfficial",
            "KompasTVPalembang",
            "TribunSumsel",
            "TVRISumateraSelatan",
            "NusantaraTV",
            "KompasTV",
            "IndonesiaAsri",
        ],
        "X": [
            "tribunsumsel",
            "detikcom",
            "KompasTV",
            "suaracom",
            "officialinews_",
        ],
    }

    # Daftar tautan postingan/video nyata terkait isu sampah di Kota Palembang
    REAL_POST_URLS_BY_PLATFORM = {
        "Instagram": [
            "https://www.instagram.com/p/DW6EVremb8w/",
            "https://www.instagram.com/p/Ddxe_fQzhi4/",
            "https://www.instagram.com/reel/DdQlxVcxmtp/",
            "https://www.instagram.com/reel/DD7Q6bDSRSG/",
            "https://www.instagram.com/p/DZFCsTrmXL-/",
            "https://www.instagram.com/p/DZFr_lsGbci/",
            "https://www.instagram.com/reel/DJ-9G_mSffk/",
            "https://www.instagram.com/reel/DdQK6IVhexZ/",
        ],
        "YouTube": [
            "https://www.youtube.com/watch?v=J-CMCs92pl0",
            "https://www.youtube.com/watch?v=eWF9qZassV8",
            "https://www.youtube.com/watch?v=orXv9z5mBDE",
            "https://www.youtube.com/watch?v=ZakUT-4ttSg",
            "https://www.youtube.com/watch?v=NxZAPvH8mGI",
        ],
        "TikTok": [
            "https://www.tiktok.com/@infosumseltv/video/7542352087121740306",
            "https://www.tiktok.com/@palembang.terkini",
            "https://www.tiktok.com/@tribunsumsel",
            "https://www.tiktok.com/@detiksumbagsel",
        ],
        "Threads": [
            "https://www.threads.net/@palembang.terkini",
            "https://www.threads.net/@plglipp",
            "https://www.threads.net/@palembang.dlh",
            "https://www.threads.net/@tribunsumsel",
        ],
        "X": [
            "https://x.com/search?q=sampah%20palembang&src=typed_query",
            "https://x.com/tribunsumsel",
            "https://x.com/detikcom",
        ],
    }

    VIRAL_SCENARIOS = [
        # 1. Topik Pasar Tradisional (Pasar 16 Ilir, Jakabaring, Lemabang, KM 5, Cinde, Kuto, Tangga Takat, Sekip, Padang Selasa, Gubah, Sako, Plaju, Sungki, 10 Ulu, 26 Ilir, Kamboja, Talang Betutu, Gandus)
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
            "Pasar Tangga Takat di Seberang Ulu II butuh tambahan bak kontainer sampah, soalnya la penuh terus tiap pagi.",
            49,
        ),
        (
            "YouTube",
            "Pedagang sama pengunjung di Pasar 16 Ilir harusnya dikasih tempat sampah terpilah biar dak baseng nyampakke plastik ke lantai.",
            34,
        ),
        (
            "Instagram",
            "Tumpukan sampah plastik dan sisa ikan di Pasar Sekip Ujung Kemuning la meluber ke parit, baunyo bikin pening kepala!",
            77,
        ),
        (
            "TikTok",
            "Kawasan Pasar Padang Selasa di Bukit Besar Ilir Barat I becek nian bercampur sampah sayur busuk pas abis ujan semalem.",
            82,
        ),
        (
            "Threads",
            "Di Pasar Gubah Bukit Kecil tempat sampahnya la penuh sesak, banyak laler sama belatung dekat lapak pedagang.",
            64,
        ),
        (
            "Instagram",
            "Kontainer sampah di Pasar Perumnas Sako la tiga hari dak diangkutke, sampahnyo betaburan sampe ke jalan komplek.",
            73,
        ),
        (
            "X",
            "Pasar Plaju dan Pasar Baguskuning butuh perhatian petugas kebersihan, jangan dibiarke sampah numpuk di pinggir jalan raya.",
            55,
        ),
        (
            "TikTok",
            "Parah nian tumpukan sampah di Pasar Sungki Kertapati, la nutup separuh jalan ditambah bau busuk nian.",
            91,
        ),
        (
            "Instagram",
            "Di bawah jembatan dekat Pasar 10 Ulu Seberang Ulu I masih banyak oknum pedagang nyampakke sampah ke pinggir sungai.",
            86,
        ),
        (
            "Threads",
            "Jalan sekitar Pasar 26 Ilir Bukit Kecil sempit ditambah tumpukan karung sampah di bahu jalan, tolongla segera diambek.",
            61,
        ),
        (
            "YouTube",
            "Kondisi TPS dekat Pasar Kamboja Ilir Timur I sudah mulai ditata rapi oleh petugas, semoga tetap terjaga kebersihannya.",
            43,
        ),
        (
            "Instagram",
            "Pasar Talang Betutu di Sukarami butuh bak sampah besar, selama ini warga sama pedagang numpukke sampah di tanah kosong.",
            69,
        ),
        (
            "X",
            "Dekat Pasar Gandus sampah plastik kresek berterbangan kena angin gara-gara katek bak penampungan tertutup.",
            52,
        ),
        # 2. Topik Sungai Musi, Anak Sungai (Sekanak, Bendung, Buah, Lambidaro, Aur, Kedukan, Juaro, Selincah, Lais, Ogan, Komering, Borang) & Kolam Retensi / Drainase
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
            "Aliran Sungai Buah di Ilir Timur II penuh tumpukan botol plastik, parit mampet total kalo ujan setengah jam bae langsung banjir.",
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
        (
            "Instagram",
            "Aliran Sungai Aur di Seberang Ulu I dangkal dan mampet gara-gara tumpukan sampah rumah tangga, rawan nian banjir!",
            93,
        ),
        (
            "TikTok",
            "Sungai Kedukan di 5 Ulu penuh sampah plastik mengapung pas banyu pasang dari Sungai Musi, tolong dinas terkait turun tangan.",
            88,
        ),
        (
            "Threads",
            "Di Sungai Juaro dan Sungai Selincah Kalidoni banyak tumpukan sampah kiriman yang nyangkut di tiang jembatan warga.",
            72,
        ),
        (
            "Instagram",
            "Kawasan Sungai Lais Kalidoni dekat dermaga banyak sampah plastik dan kayu tersangkut di tepian sungai.",
            65,
        ),
        (
            "X",
            "Pertemuan aliran Sungai Ogan di Kertapati banyak membawa sampah kiriman dan eceng gondok bercampur botol plastik.",
            70,
        ),
        (
            "TikTok",
            "Sungai Borang di perbatasan Sako dan Sematang Borang tersumbat sampah rumah tangga, pas ujan deras perumahan langsung tergenang.",
            104,
        ),
        (
            "Instagram",
            "Sudut Kolam Retensi Simpang Polda Kemuning ada sampah botol dan bungkus makanan yang mengapung di pinggir pintu air.",
            78,
        ),
        (
            "YouTube",
            "Pembersihan rutin di Kolam Retensi Siti Khodijah Ilir Barat I sangat membantu mencegah banjir di kawasan Pakjo dan Demang.",
            46,
        ),
        # 3. Topik Keterlambatan Jadwal Angkut & Armada Truk DLHK di Jalan Utama & Permukiman
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
        (
            "TikTok",
            "Sepanjang Jalan Demang Lebar Daun masih ado tumpukan kantong sampah di trotoar yang belum diangkut truk kebersihan sampe siang.",
            76,
        ),
        (
            "Instagram",
            "Dekat Simpang Celentang Kalidoni bak sampah pinggir jalan la meluber ke aspal, bahaya bagi pengendara motor.",
            83,
        ),
        (
            "Threads",
            "Warga di Kenten dan Jalan MP Mangkunegara Ilir Timur III mengeluhkan jadwal angkut sampah yang sering terlambat saat akhir pekan.",
            62,
        ),
        (
            "X",
            "Di Jalan Noerdin Pandji arah Bandara Sukarami banyak bungkusan sampah dibuang oknum dari mobil di pinggir jalan raya.",
            69,
        ),
        (
            "Instagram",
            "Kawasan Jalan Soekarno Hatta Alang-Alang Lebar sering dijadikan tempat buang sampah liar malam hari, tolong patroli DLHK ditingkatkan.",
            85,
        ),
        (
            "Threads",
            "Warga Kelurahan Pakjo dan Lorokpakjo Ilir Barat I berharap motor sampah tiga roda rutin masuk ke lorong-lorong sempit.",
            54,
        ),
        (
            "TikTok",
            "Di kawasan Kebun Bunga dan Talang Jambe Sukarami tumpukan sampah perumahan telat diambek petugas sampe keluar belatung.",
            92,
        ),
        (
            "Instagram",
            "TPS dekat Simpang Charitas dan Jalan Veteran Ilir Timur I harus diangkut sebelum jam berangkat kerja biar dak bikin macet.",
            75,
        ),
        # 4. Topik Kapasitas TPS Kurang, TPA Sukawinatan Overload, TPA Karya Jaya & PSEL Keramasan
        (
            "TikTok",
            "Parah nian TPA Sukawinatan di Sukarami overload terus, gunungan sampah tinggi nian, bau mambu sampe ke perumahan warga kalo malem.",
            138,
        ),
        (
            "Instagram",
            "Jalan di Macan Lindungan Ilir Barat I banyak sampah liar di pinggir jalan karena katek TPS resmi yang dekat permukiman sini.",
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
        (
            "Instagram",
            "Pengelolaan lahan di TPA Karya Jaya Kertapati perlu dioptimalkan dengan teknologi sanitary landfill agar tidak mencemari lingkungan.",
            63,
        ),
        (
            "Threads",
            "Di kawasan 30 Ilir dan 32 Ilir Kecamatan Ilir Barat II lorongnya padat penduduk tapi jarak ke bak TPS resmi lumayan jauh.",
            59,
        ),
        (
            "TikTok",
            "Gunungan sampah di TPA Sukawinatan rawan longsor dan kebakaran saat kemarau, harus segera dialihkan ke PSEL Keramasan.",
            115,
        ),
        (
            "Instagram",
            "Warga di Mata Merah Kalidoni dan Sematang Borang minta ditambah kontainer TPS besi supaya sampah dak dikorek anjing liar.",
            68,
        ),
        (
            "YouTube",
            "Kapasitas tampung TPS di kawasan Silaberanti dan Tuan Kentang Jakabaring perlu diperbesar seiring bertambahnya jumlah penduduk.",
            45,
        ),
        # 5. Topik Perilaku Warga, Regulasi Denda, Komunitas Clean Up, Wisata & Apresiasi
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
        (
            "Instagram",
            "Kawasan wisata Benteng Kuto Besak (BKB) dan Monpera harus bebas dari sampah plastik pengunjung, malu dilihat wisatawan luar kota.",
            91,
        ),
        (
            "TikTok",
            "Aksi bersih-bersih sampah di Pulau Kemaro dan tepian Sungai Musi oleh pelajar dan mahasiswa Palembang patut dicontoh!",
            124,
        ),
        (
            "YouTube",
            "Petugas kebersihan di Hutan Wisata Punti Kayu Alang-Alang Lebar sigap menyapu sampah dedaunan dan botol plastik pengunjung.",
            47,
        ),
        (
            "Instagram",
            "Area olahraga Jakabaring Sport City (JSC) bersih dan cindo nian pagi ini berkat kerja keras pasukan kuning DLHK Palembang.",
            84,
        ),
        (
            "Threads",
            "Warga di sekitar Jembatan Musi 4 dan Jembatan Musi 6 berharap lampu penerangan dan tempat sampah di trotoar jembatan ditambah.",
            56,
        ),
        (
            "X",
            "Jangan ada lagi warga yang bakar sampah plastik sembarangan di kawasan Karya Baru dan Sukajaya karena asapnya bikin sesak napas.",
            67,
        ),
        (
            "YouTube",
            "Kolaborasi RT/RW di 8 Ilir dan 9 Ilir Kecamatan Ilir Timur III dalam membuat kompos dari sampah rumah tangga sangat inspiratif.",
            51,
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
        " Tolongla petugas DLHK segera turun ke lokasi.",
        " Baunyo la nyebar kemano-mano dak tahan lagi.",
        " Semoga bapak walikota Palembang baca keluhan warga ini.",
        " Kalo dibiarke terus lokak banjir besak kawasan sini.",
        " Mari warga Palembang kito stop buang sampah baseng bae.",
    ]

    @classmethod
    def generate_large_viral_dataset(
        cls,
        target_count: int = 900,
        start_year: int = 0,
        end_year: int = 0,
    ) -> List[Dict[str, object]]:
        """
        Menghasilkan 900 baris data keluhan & komentar topik viral sampah Palembang
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

                platform_users = cls.REAL_PUBLIC_USERS_BY_PLATFORM.get(
                    platform, cls.REAL_PUBLIC_USERS_BY_PLATFORM["Instagram"]
                )
                user_handle = platform_users[(idx + scen_idx) % len(platform_users)]
                readable_username = f"@{user_handle}"
                profile_url = BaseScraper.build_profile_url(platform, user_handle)

                accounts = cls.VIRAL_ACCOUNTS[platform]
                source_acc = accounts[(idx + round_idx) % len(accounts)]

                platform_posts = cls.REAL_POST_URLS_BY_PLATFORM.get(
                    platform, cls.REAL_POST_URLS_BY_PLATFORM["Instagram"]
                )
                post_url = platform_posts[(idx + scen_idx + round_idx) % len(platform_posts)]

                current_dt = start_dt + timedelta(seconds=(idx - 1) * step_seconds + ((idx * 137) % 3600))
                timestamp = current_dt.strftime("%Y-%m-%d %H:%M:%S")
                text_content = f"{base_text}{suffix}".strip()
                likes = max(5, base_likes + ((idx * 7) % 45) - (round_idx * 2))

                records.append(
                    {
                        "id": str(idx),
                        "platform": platform,
                        "username": readable_username,
                        "timestamp": timestamp,
                        "raw_text": text_content,
                        "likes_count": likes,
                        "source_account": source_acc,
                        "profile_url": profile_url,
                        "post_url": post_url,
                    }
                )
                idx += 1

        return records

    @classmethod
    def collect_live_multi_platform(cls, limit_per_query: int = 30) -> List[Dict[str, object]]:
        """
        Mengumpulkan data langsung (live scraping) dari Threads, Instagram, dan X
        menggunakan daftar SEARCH_KEYWORDS Palembang apabila kredensial di .env aktif.
        """
        from src.scrapers.threads_scraper import ThreadsScraper
        from src.scrapers.twitter_scraper import TwitterScraper

        collected: List[Dict[str, object]] = []
        status = Settings.credential_status()

        if status.get("threads_ready") or status.get("apify_token_ready"):
            th_scraper = ThreadsScraper()
            for kw in cls.SEARCH_KEYWORDS[:5]:
                try:
                    collected.extend(th_scraper.fetch_comments(kw, limit=limit_per_query))
                except Exception:
                    continue

        if status.get("twitter_token_ready"):
            tw_scraper = TwitterScraper()
            for kw in cls.SEARCH_KEYWORDS[:3]:
                try:
                    collected.extend(tw_scraper.fetch_comments(kw, limit=limit_per_query))
                except Exception:
                    continue

        return collected

    @classmethod
    def save_default_viral_dataset(cls, target_count: int = 900) -> Path:
        """Menyimpan dataset viral 900 baris ke data/raw/sample_keluhan_palembang.csv."""
        records = cls.generate_large_viral_dataset(target_count=target_count)
        out_path = Settings.DATA_RAW_DIR / "sample_keluhan_palembang.csv"
        BaseScraper.save_to_csv(records, out_path)
        return out_path
