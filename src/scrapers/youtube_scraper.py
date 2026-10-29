from typing import Dict, List
from config.settings import Settings
from src.scrapers.base_scraper import BaseScraper


class YouTubeScraper(BaseScraper):
    """
    Scraper komentar YouTube menggunakan YouTube Data API v3 resmi.
    Cocok untuk mengambil komentar berita lokal Palembang (PALTV, Sriwijaya TV, KompasTV Sumsel).
    """

    def __init__(self) -> None:
        self.api_key = Settings.YOUTUBE_API_KEY

    def fetch_comments(self, video_id: str, limit: int = 50) -> List[Dict[str, object]]:
        """Mengambil komentar dari video YouTube berdasarkan video_id."""
        if not Settings.credential_status()["youtube_api_ready"]:
            raise RuntimeError(
                "YOUTUBE_API_KEY belum diatur pada file .env. "
                "Dapatkan gratis di Google Cloud Console (YouTube Data API v3)."
            )

        from googleapiclient.discovery import build  # type: ignore

        youtube = build("youtube", "v3", developerKey=self.api_key)
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=min(limit, 100),
            textFormat="plainText",
        )
        response = request.execute()

        results: List[Dict[str, object]] = []
        for idx, item in enumerate(response.get("items", []), start=1):
            snippet = item["snippet"]["topLevelComment"]["snippet"]
            results.append(
                {
                    "id": str(item.get("id", idx)),
                    "platform": "YouTube",
                    "username": self.anonymize_username(snippet.get("authorDisplayName", "anon")),
                    "timestamp": snippet.get("publishedAt", ""),
                    "raw_text": snippet.get("textDisplay", ""),
                    "likes_count": int(snippet.get("likeCount", 0)),
                    "source_account": video_id,
                }
            )
        return results
