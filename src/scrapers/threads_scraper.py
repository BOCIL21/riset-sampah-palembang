from datetime import datetime
from typing import Dict, List
from config.settings import Settings
from src.scrapers.base_scraper import BaseScraper


class ThreadsScraper(BaseScraper):
    """
    Scraper untuk Meta Threads (threads.net).
    Sangat relevan karena banyak warga Palembang dan akun portal berita lokal
    (@palembang.terkini, @plglipp, @infopalembang) aktif berdiskusi di Threads.
    Mendukung pengambilan data melalui Apify Threads Scraper atau Session Cookie Threads.
    """

    def __init__(self) -> None:
        self.username = (
            Settings.THREADS_USERNAME
            if (Settings.THREADS_USERNAME and "username_" not in Settings.THREADS_USERNAME)
            else Settings.IG_USERNAME
        )
        self.password = (
            Settings.THREADS_PASSWORD
            if (Settings.THREADS_PASSWORD and "password_" not in Settings.THREADS_PASSWORD)
            else Settings.IG_PASSWORD
        )
        self.session_id = Settings.THREADS_SESSION_ID
        self.apify_token = Settings.APIFY_API_TOKEN

    def fetch_comments(self, keyword_or_post_url: str, limit: int = 50) -> List[Dict[str, object]]:
        """
        Mengambil postingan/balasan (replies) dari Threads berdasarkan kata kunci
        (misal: 'sampah palembang') atau URL post Threads spesifik.
        """
        status = Settings.credential_status()
        if not status["threads_ready"] and not status["apify_token_ready"]:
            raise RuntimeError(
                "Kredensial Threads belum diatur. Isi THREADS_SESSION_ID (atau THREADS_USERNAME & "
                "THREADS_PASSWORD) maupun APIFY_API_TOKEN pada file .env terlebih dahulu."
            )

        if status["apify_token_ready"]:
            return self._fetch_via_apify(keyword_or_post_url, limit)

        return self._fetch_via_graphql_session(keyword_or_post_url, limit)

    def _fetch_via_apify(self, keyword_or_post_url: str, limit: int) -> List[Dict[str, object]]:
        from apify_client import ApifyClient  # type: ignore

        client = ApifyClient(self.apify_token)
        run_input = {
            "queries": [keyword_or_post_url],
            "maxItems": limit,
        }
        run = client.actor("apify/threads-scraper").call(run_input=run_input)
        dataset_items = client.dataset(run["defaultDatasetId"]).list_items().items

        results: List[Dict[str, object]] = []
        for idx, item in enumerate(dataset_items, start=1):
            author = str(item.get("username") or item.get("ownerUsername") or "anon")
            results.append(
                {
                    "id": str(item.get("id", f"th_{idx}")),
                    "platform": "Threads",
                    "username": self.anonymize_username(author),
                    "timestamp": str(item.get("publishedAt", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))),
                    "raw_text": str(item.get("text", "")),
                    "likes_count": int(item.get("likeCount", 0)),
                    "source_account": f"@{author}",
                }
            )
        return results

    def _fetch_via_graphql_session(self, keyword_or_post_url: str, limit: int) -> List[Dict[str, object]]:
        """
        Mengambil data pencarian Threads menggunakan HTTP Request dengan cookie sessionid
        dari akun riset Threads/Instagram.
        """
        import requests  # type: ignore

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "X-IG-App-ID": "238260118697367",
            "Cookie": f"sessionid={self.session_id};",
        }
        response = requests.get(
            "https://www.threads.net/search",
            params={"q": keyword_or_post_url, "serp_type": "default"},
            headers=headers,
            timeout=15,
        )
        response.raise_for_status()

        # Jika memerlukan ekstraksi JSON terstruktur dari SSR Threads atau library threads-api
        return []
