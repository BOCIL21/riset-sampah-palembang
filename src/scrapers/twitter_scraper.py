import subprocess
from pathlib import Path
from typing import Dict, List
from config.settings import Settings
from src.scrapers.base_scraper import BaseScraper


class TwitterScraper(BaseScraper):
    """
    Scraper untuk X (Twitter) menggunakan integrasi Tweet-Harvest (Node.js)
    atau pembacaan CSV hasil ekspor pencarian kata kunci (misal: 'sampah palembang').
    """

    def __init__(self) -> None:
        self.auth_token = Settings.TWITTER_AUTH_TOKEN

    def fetch_comments(self, search_keyword: str, limit: int = 50) -> List[Dict[str, object]]:
        """
        Menjalankan Tweet-Harvest CLI jika auth_token tersedia,
        atau mengarahkan pengguna ke impor CSV.
        """
        if not Settings.credential_status()["twitter_token_ready"]:
            raise RuntimeError(
                "TWITTER_AUTH_TOKEN belum diatur pada file .env. "
                "Masukkan cookie auth_token dari akun X/Twitter riset Anda."
            )

        output_filename = "tweets_palembang.csv"
        cmd = [
            "npx",
            "-y",
            "tweet-harvest@latest",
            "-o",
            output_filename,
            "-s",
            search_keyword,
            "-l",
            str(limit),
            "--token",
            self.auth_token,
        ]
        subprocess.run(cmd, check=True)
        csv_result = Path("tweets-data") / output_filename
        if csv_result.exists():
            return self.load_from_csv(csv_result, anonymize=True)
        return []
