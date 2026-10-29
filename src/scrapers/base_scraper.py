import csv
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List


class BaseScraper(ABC):
    """
    Kelas dasar (Abstract Base Class) untuk seluruh scraper sosial media.
    Menyediakan format username yang tetap mudah dibaca manusia (readable)
    sekaligus memiliki opsi penyamaran ringan untuk publikasi jurnal.
    """

    @staticmethod
    def anonymize_username(username: str) -> str:
        """
        Menyamarkan sebagian karakter tengah username namun tetap mudah dibaca
        (Contoh: 'wong_palembang01' -> '@wong_pal***01').
        """
        if not username:
            return "@warga_anonim"
        clean = username.strip().lstrip("@")
        if len(clean) <= 5:
            return f"@{clean[:2]}***"
        prefix = clean[: min(8, len(clean) - 3)]
        suffix = clean[-2:]
        return f"@{prefix}***{suffix}"

    @staticmethod
    def format_readable_username(username: str) -> str:
        """Memastikan username diawali simbol '@' agar rapi dan mudah dibaca di tabel CSV."""
        if not username:
            return "@palembang.terkini"
        clean = username.strip().lstrip("@")
        return f"@{clean}"

    @staticmethod
    def build_profile_url(platform: str, username: str) -> str:
        """Membentuk URL langsung ke profil akun media sosial berdasarkan platform dan username."""
        clean = (username or "").strip().lstrip("@")
        plat = (platform or "").strip().lower()
        if plat == "instagram":
            return f"https://www.instagram.com/{clean}/"
        if plat == "tiktok":
            return f"https://www.tiktok.com/@{clean}"
        if plat == "threads":
            return f"https://www.threads.net/@{clean}"
        if plat == "youtube":
            return f"https://www.youtube.com/@{clean.replace(' ', '')}"
        if plat in {"x", "twitter"}:
            return f"https://x.com/{clean}"
        return f"https://www.instagram.com/{clean}/"

    @staticmethod
    def load_from_csv(csv_path: Path, anonymize: bool = True) -> List[Dict[str, str]]:
        """Memuat dataset dari file CSV dengan mempertahankan username, profile_url, dan post_url."""
        records: List[Dict[str, str]] = []
        if not csv_path.exists():
            raise FileNotFoundError(f"File dataset tidak ditemukan: {csv_path}")

        with csv_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                item = dict(row)
                raw_user = item.get("username", "")
                platform = item.get("platform", "Instagram")
                item["username"] = BaseScraper.format_readable_username(raw_user)
                if anonymize:
                    item["username_masked"] = BaseScraper.anonymize_username(raw_user)
                if not item.get("profile_url"):
                    item["profile_url"] = BaseScraper.build_profile_url(platform, raw_user)
                if not item.get("post_url"):
                    item["post_url"] = BaseScraper.build_profile_url(
                        platform, item.get("source_account", raw_user)
                    )
                records.append(item)
        return records

    @staticmethod
    def save_to_csv(records: List[Dict[str, object]], output_path: Path) -> None:
        """Menyimpan hasil scraping atau pemrosesan ke dalam file CSV."""
        if not records:
            return
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = list(records[0].keys())
        with output_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)

    @abstractmethod
    def fetch_comments(self, query_or_target: str, limit: int = 50) -> List[Dict[str, object]]:
        """Metode abstrak yang wajib diimplementasikan oleh setiap scraper platform."""
        raise NotImplementedError
