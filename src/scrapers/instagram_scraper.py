from datetime import datetime
from typing import Dict, List
from config.settings import Settings
from src.scrapers.base_scraper import BaseScraper


class InstagramScraper(BaseScraper):
    """
    Scraper komentar Instagram untuk akun berita lokal Palembang
    (misal: @palembang.terkini, @plglipp, @infopalembang) menggunakan Instaloader atau Apify.
    """

    def __init__(self) -> None:
        self.username = Settings.IG_USERNAME
        self.password = Settings.IG_PASSWORD
        self.apify_token = Settings.APIFY_API_TOKEN

    def fetch_comments(self, post_shortcode: str, limit: int = 50) -> List[Dict[str, object]]:
        """
        Mengambil komentar dari satu postingan Instagram berdasarkan shortcode URL.
        Contoh URL: https://www.instagram.com/p/C9xyz123/ -> shortcode = 'C9xyz123'
        """
        status = Settings.credential_status()
        if not status["instagram_login_ready"] and not status["apify_token_ready"]:
            raise RuntimeError(
                "Kredensial Instagram belum diatur. Isi IG_USERNAME & IG_PASSWORD "
                "atau APIFY_API_TOKEN pada file .env terlebih dahulu."
            )

        if status["apify_token_ready"]:
            return self._fetch_via_apify(post_shortcode, limit)

        return self._fetch_via_instaloader(post_shortcode, limit)

    def _fetch_via_instaloader(self, post_shortcode: str, limit: int) -> List[Dict[str, object]]:
        import instaloader  # type: ignore

        loader = instaloader.Instaloader()
        loader.login(self.username, self.password)
        post = instaloader.Post.from_shortcode(loader.context, post_shortcode)

        results: List[Dict[str, object]] = []
        for idx, comment in enumerate(post.get_comments(), start=1):
            if idx > limit:
                break
            results.append(
                {
                    "id": str(comment.id),
                    "platform": "Instagram",
                    "username": self.anonymize_username(comment.owner.username),
                    "timestamp": comment.created_at_utc.strftime("%Y-%m-%d %H:%M:%S"),
                    "raw_text": comment.text,
                    "likes_count": comment.likes_count,
                    "source_account": f"@{post.owner_username}",
                }
            )
        return results

    def _fetch_via_apify(self, post_shortcode: str, limit: int) -> List[Dict[str, object]]:
        from apify_client import ApifyClient  # type: ignore

        client = ApifyClient(self.apify_token)
        run_input = {
            "directUrls": [f"https://www.instagram.com/p/{post_shortcode}/"],
            "resultsLimit": limit,
        }
        run = client.actor("apify/instagram-comment-scraper").call(run_input=run_input)
        dataset_items = client.dataset(run["defaultDatasetId"]).list_items().items

        results: List[Dict[str, object]] = []
        for idx, item in enumerate(dataset_items, start=1):
            results.append(
                {
                    "id": str(item.get("id", idx)),
                    "platform": "Instagram",
                    "username": self.anonymize_username(str(item.get("ownerUsername", "anon"))),
                    "timestamp": str(item.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))),
                    "raw_text": str(item.get("text", "")),
                    "likes_count": int(item.get("likesCount", 0)),
                    "source_account": post_shortcode,
                }
            )
        return results
