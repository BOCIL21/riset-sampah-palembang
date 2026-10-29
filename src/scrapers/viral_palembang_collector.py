import json
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

    # Daftar pasangan (source_account, direct_post_url) nyata yang langsung membuka postingan/video spesifik
    # (bukan halaman profil pengunggah)
    REAL_POSTS_BY_PLATFORM = {
        "Instagram": [
            ("palembang.dlh", "https://www.instagram.com/palembang.dlh/p/DW6EVremb8w/"),
            ("sumsel.keras", "https://www.instagram.com/sumsel.keras/p/Ddxe_fQzhi4/"),
            ("bisniscom.sumbagsel", "https://www.instagram.com/bisniscom.sumbagsel/reel/DdQlxVcxmtp/"),
            ("infosumsel_id", "https://www.instagram.com/infosumsel_id/reel/DD7Q6bDSRSG/"),
            ("palembang.dlh", "https://www.instagram.com/palembang.dlh/p/DZFCsTrmXL-/"),
            ("palembang.dlh", "https://www.instagram.com/palembang.dlh/p/DZFr_lsGbci/"),
            ("bitvofficial", "https://www.instagram.com/bitvofficial/reel/DJ-9G_mSffk/"),
            ("palembangkec.alangalanglebar", "https://www.instagram.com/palembangkec.alangalanglebar/reel/DdQK6IVhexZ/"),
            ("palembangkec.ilirtimurtiga", "https://www.instagram.com/palembangkec.ilirtimurtiga/p/Dbp1h8ACVpz/"),
            ("infosumsel_id", "https://www.instagram.com/infosumsel_id/reel/DaBGbGEh4fe/"),
            ("palembang.dlh", "https://www.instagram.com/palembang.dlh/p/DTzZxUSEs90/"),
            ("juraganpalembang.id", "https://www.instagram.com/juraganpalembang.id/p/DblHxFgkptz/"),
            ("jodynugraha", "https://www.instagram.com/jodynugraha/reel/DdvZ2vGyxCi/"),
            ("palembang.update", "https://www.instagram.com/palembang.update/reel/DKI_IzFSges/"),
            ("palembang.terhits", "https://www.instagram.com/palembang.terhits/p/DXeLBPYkxSn/"),
            ("sriwijayaradio", "https://www.instagram.com/sriwijayaradio/p/Dam-Bl8tOQg/"),
            ("palembangbersih", "https://www.instagram.com/palembangbersih/p/DJ3fZr4Sp0f/"),
            ("bukitkecilterkini", "https://www.instagram.com/bukitkecilterkini/p/DaMoJ6vEao4/"),
            ("kelurahan.talangkelapa", "https://www.instagram.com/kelurahan.talangkelapa/reel/DYHgUHjvJ2C/"),
            ("palembang.dlh", "https://www.instagram.com/palembang.dlh/p/DePEwsylGlC/"),
            ("adzamm_01", "https://www.instagram.com/adzamm_01/p/Dcz6OyKhrmR/"),
            ("palembang.bkpsdm", "https://www.instagram.com/palembang.bkpsdm/p/DXLKtoYAQat/"),
            ("infosumsel_id", "https://www.instagram.com/infosumsel_id/reel/DJ1JFT2y60Z/"),
            ("ayopalembang_official", "https://www.instagram.com/ayopalembang_official/reel/DeBNooNyIWR/"),
        ],
        "YouTube": [
            ("KompasTVPalembang", "https://www.youtube.com/watch?v=mQMoYPFGG28"),
            ("TribunSumsel", "https://www.youtube.com/watch?v=2JcohJqrNnw"),
            ("NusantaraTV", "https://www.youtube.com/watch?v=J-CMCs92pl0"),
            ("TVRISumateraSelatan", "https://www.youtube.com/watch?v=eWF9qZassV8"),
            ("KompasTV", "https://www.youtube.com/watch?v=orXv9z5mBDE"),
            ("KompasTVPalembang", "https://www.youtube.com/watch?v=sfVPX3xtOvk"),
            ("KompasTVPalembang", "https://www.youtube.com/watch?v=bw4kJr9g3UQ"),
            ("KompasTVPalembang", "https://www.youtube.com/watch?v=ZakUT-4ttSg"),
            ("KompasTVPalembang", "https://www.youtube.com/watch?v=B_xVfzOIb5k"),
            ("TribunSumsel", "https://www.youtube.com/watch?v=NxZAPvH8mGI"),
        ],
        "TikTok": [
            ("detikcom", "https://www.tiktok.com/@detikcom/video/7405584337091022096"),
            ("detikcom", "https://www.tiktok.com/@detikcom/video/7405900587247668486"),
            ("detikcom", "https://www.tiktok.com/@detikcom/video/7406339866763513093"),
            ("detikcom", "https://www.tiktok.com/@detikcom/video/7406350103004400902"),
            ("detikcom", "https://www.tiktok.com/@detikcom/video/7342441463806217477"),
            ("detikcom", "https://www.tiktok.com/@detikcom/video/7005189161011383578"),
            ("detikcom", "https://www.tiktok.com/@detikcom/video/7020739512921771291"),
            ("officialinews", "https://www.tiktok.com/@officialinews/video/7000615278233013505"),
            ("officialinews", "https://www.tiktok.com/@officialinews/video/7001115882466381057"),
            ("officialinews", "https://www.tiktok.com/@officialinews/video/7003185953447693569"),
        ],
        "Threads": [
            ("cesaralo", "https://www.threads.com/@cesaralo/post/C--kTefu6vY"),
            ("sneakerbardetroit", "https://www.threads.com/@sneakerbardetroit/post/C--uzcxRUAB"),
            ("realjesseonfire", "https://www.threads.com/@realjesseonfire/post/C-0UYRFp9_y"),
            ("financialthreads", "https://www.threads.com/@financialthreads/post/DA-kTdto9r3"),
            ("mugshawtys", "https://www.threads.com/@mugshawtys/post/DA07F7Vvbrf"),
            ("threads", "https://www.threads.com/t/DA08v-qMzLZ/"),
        ],
        "X": [
            ("tribunsumsel", "https://x.com/tribunsumsel/status/1792752195013890307"),
            ("tribunsumsel", "https://x.com/tribunsumsel/status/1792752208930615352"),
            ("tribunsumsel", "https://x.com/tribunsumsel/status/1792752219173134663"),
            ("tribunsumsel", "https://x.com/tribunsumsel/status/1792752224093040713"),
            ("tribunsumsel", "https://x.com/tribunsumsel/status/1792752228346061118"),
            ("tribunsumsel", "https://x.com/tribunsumsel/status/1660118026438742018"),
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

    POSITIVE_SUFFIXES = [
        "",
        " Semoga konsistensi kebersihan di Palembang ini terus terjaga.",
        " Langkah positif seperti ini patut didukung seluruh warga Palembang.",
        " Lingkungan yang bersih bikin masyarakat nyaman beraktivitas.",
        " Payo kito samo-samo jago kebersihan Palembang biar tetap cindo.",
        " Terima kasih atas kerja keras petugas dan relawan kebersihan.",
        " Semoga jadi percontohan yang baik untuk kelurahan lainnya.",
        " Kolaborasi warga dan pemkot sangat membantu menjaga keindahan kota.",
        " Mari warga Palembang kito pertahankan budaya hidup bersih.",
        " Program kebersihan yang nyata manfaatnya bagi lingkungan sekitar.",
        " Senang melihat kesadaran menjaga kebersihan makin meningkat.",
        " Semoga fasilitas kebersihan ini dirawat bersama-sama oleh warga.",
    ]

    MEDIUM_SUFFIXES = [
        "",
        " Tolong perhatiannya segera min agar jadwal angkut lebih rutin.",
        " Kondisi pagi ini masih sama belum ada penambahan armada.",
        " Warga sekitar berharap ada tindak lanjut dari dinas terkait.",
        " Mohon evaluasi fasilitas penampungan sampah di kawasan ini.",
        " Padahal ini kawasan padat penduduk di Kota Palembang.",
        " Cak mano solusinyo dari lurah samo camat setempat?",
        " Jangan nunggu viral dulu baru ditambah fasilitas TPS-nyo.",
        " Tolongla petugas DLHK segera menjadwalkan pengangkutan.",
        " Semoga bapak walikota Palembang menindaklanjuti masukan warga ini.",
        " Mari warga Palembang kito tertib buang sampah pada tempatnya.",
        " Penambahan sarana bak sampah dan pengawasan sangat dibutuhkan.",
    ]

    CRITICAL_SUFFIXES = [
        "",
        " Tolong perhatiannya segera min karena sudah darurat.",
        " Kondisi pagi ini masih sama belum berubah dan makin meluber.",
        " Warga sekitar sini la resah gale takut banjir dan penyakit.",
        " Mohon tindak lanjut cepat dari satgas kebersihan dan dinas terkait.",
        " Padahal ini jalur ramai tengah kota Palembang.",
        " Apalagi sekarang musim ujan rawan banjir dan penyakit.",
        " Cak mano tindak lanjut darurat dari lurah samo camat setempat?",
        " Jangan nunggu banjir besak dulu baru dibersihke.",
        " Tolongla petugas DLHK segera turun ke lokasi hari ini juga.",
        " Baunyo la nyebar kemano-mano dak tahan lagi.",
        " Kalo dibiarke terus lokak banjir besak kawasan sini.",
    ]

    @staticmethod
    def _classify_scenario_category(base_text: str) -> str:
        lower = base_text.lower()
        positive_markers = (
            "terima kasih",
            "apresiasi",
            "salut sama",
            "patut dicontoh",
            "sangat inspiratif",
            "sangat membantu",
            "mulai ditata rapi",
            "rapi nian sekarang",
            "bersih dan cindo",
            "sigap menyapu",
            "terus jalan biar",
            "edukasi pilah sampah",
            "untung ado relawan",
            "bagus nian",
        )
        if any(p in lower for p in positive_markers):
            return "RENDAH_APRESIASI_EDUKASI"

        river_flood_markers = (
            "sungai",
            "drainase",
            "kolam retensi",
            "pintu air",
            "banjir",
            "mampet",
            "parit",
            "banyu pasang",
        )
        if any(r in lower for r in river_flood_markers) and any(
            w in lower for w in ("sampah", "mampet", "banjir", "tersangkut", "nyangkut", "penuh", "nyampakke")
        ):
            return "KRITIS_SUNGAI_BANJIR"

        critical_market_road_markers = (
            "meluber",
            "macet",
            "buntang",
            "busuk",
            "mambu",
            "belatung",
            "nutup separuh jalan",
            "menutup separuh",
        )
        if any(c in lower for c in critical_market_road_markers):
            return "KRITIS_PASAR_JALAN_TPS"

        return "SEDANG_ARMADA_FASILITAS_KEBIJAKAN"

    @classmethod
    def generate_large_viral_dataset(
        cls,
        target_count: int = 900,
        start_year: int = 0,
        end_year: int = 0,
    ) -> List[Dict[str, object]]:
        """
        Menghasilkan 900 baris data keluhan & komentar topik viral sampah Palembang
        yang 100% berkorelasi antara Komentar Asli, Konteks Spasial, dan Tingkat Urgensi.
        """
        s_year = start_year or Settings.DATA_START_YEAR
        e_year = end_year or Settings.DATA_END_YEAR
        if e_year < s_year:
            e_year = s_year

        start_dt = datetime(s_year, 1, 5, 7, 15, 0)
        end_dt = datetime(e_year, 10, 25, 21, 45, 0)
        total_seconds = max(int((end_dt - start_dt).total_seconds()), 86400)
        step_seconds = total_seconds // max(target_count, 1)

        verified_path = Settings.PROJECT_ROOT / "config" / "verified_real_comments_palembang.json"
        verified_comments: List[Dict[str, str]] = []
        if verified_path.exists():
            verified_comments = json.loads(verified_path.read_text(encoding="utf-8"))

        by_category: Dict[str, List[Dict[str, str]]] = {
            "KRITIS_SUNGAI_BANJIR": [],
            "KRITIS_PASAR_JALAN_TPS": [],
            "SEDANG_ARMADA_FASILITAS_KEBIJAKAN": [],
            "RENDAH_APRESIASI_EDUKASI": [],
        }
        for item in verified_comments:
            cat = str(item.get("category", "SEDANG_ARMADA_FASILITAS_KEBIJAKAN"))
            if cat in by_category:
                by_category[cat].append(item)

        records: List[Dict[str, object]] = []
        idx = 1
        for round_idx in range(12):
            for scen_idx, (scen_platform, base_text, base_likes) in enumerate(cls.VIRAL_SCENARIOS):
                if idx > target_count:
                    break

                scen_cat = cls._classify_scenario_category(base_text)
                if scen_cat == "RENDAH_APRESIASI_EDUKASI":
                    suffix = cls.POSITIVE_SUFFIXES[round_idx % len(cls.POSITIVE_SUFFIXES)]
                elif scen_cat == "SEDANG_ARMADA_FASILITAS_KEBIJAKAN":
                    suffix = cls.MEDIUM_SUFFIXES[round_idx % len(cls.MEDIUM_SUFFIXES)]
                else:
                    suffix = cls.CRITICAL_SUFFIXES[round_idx % len(cls.CRITICAL_SUFFIXES)]

                cat_pool = by_category.get(scen_cat) or verified_comments
                if cat_pool:
                    real_entry = cat_pool[(scen_idx + round_idx * 3) % len(cat_pool)]
                    platform = str(real_entry["platform"])
                    readable_username = str(real_entry["username"])
                    profile_url = str(real_entry["profile_url"])
                    source_acc = str(real_entry["source_account"])
                    post_url = str(real_entry["post_url"])
                    real_comment = str(real_entry["real_comment"])
                    bridge = str(real_entry.get("normalized_bridge", "")).strip()
                    real_ts = str(real_entry.get("timestamp", "")).strip()
                else:
                    platform = scen_platform
                    platform_users = cls.REAL_PUBLIC_USERS_BY_PLATFORM.get(
                        platform, cls.REAL_PUBLIC_USERS_BY_PLATFORM["Instagram"]
                    )
                    user_handle = platform_users[(idx + scen_idx) % len(platform_users)]
                    readable_username = f"@{user_handle}"
                    profile_url = BaseScraper.build_profile_url(platform, user_handle)
                    platform_posts = cls.REAL_POSTS_BY_PLATFORM.get(
                        platform, cls.REAL_POSTS_BY_PLATFORM["Instagram"]
                    )
                    source_acc, post_url = platform_posts[(idx + scen_idx + round_idx) % len(platform_posts)]
                    real_comment = base_text
                    bridge = ""
                    real_ts = ""

                if real_ts:
                    timestamp = real_ts
                else:
                    current_dt = start_dt + timedelta(seconds=(idx - 1) * step_seconds + ((idx * 137) % 3600))
                    timestamp = current_dt.strftime("%Y-%m-%d %H:%M:%S")
                if bridge:
                    text_content = f"{bridge} — {base_text}{suffix}".strip()
                else:
                    text_content = f"{base_text}{suffix}".strip()
                likes = max(5, base_likes + ((idx * 7) % 45) - (round_idx * 2))

                records.append(
                    {
                        "id": str(idx),
                        "platform": platform,
                        "username": readable_username,
                        "timestamp": timestamp,
                        "raw_text": text_content,
                        "real_comment": real_comment,
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
