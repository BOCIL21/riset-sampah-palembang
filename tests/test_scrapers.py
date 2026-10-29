import unittest
from config.settings import Settings
from src.scrapers.base_scraper import BaseScraper
from src.scrapers.instagram_scraper import InstagramScraper
from src.scrapers.threads_scraper import ThreadsScraper
from src.scrapers.youtube_scraper import YouTubeScraper


class TestScrapers(unittest.TestCase):
    def test_username_anonymization_consistency(self) -> None:
        masked1 = BaseScraper.anonymize_username("wong_plg01")
        masked2 = BaseScraper.anonymize_username("@wong_plg01")
        self.assertEqual(masked1, masked2)
        self.assertTrue(masked1.startswith("@wong_"))
        self.assertIn("***", masked1)

    def test_load_sample_dataset_csv(self) -> None:
        sample_csv = Settings.DATA_RAW_DIR / "sample_keluhan_palembang.csv"
        rows = BaseScraper.load_from_csv(sample_csv, anonymize=True)
        self.assertGreaterEqual(len(rows), 900)
        self.assertIn("username_masked", rows[0])
        self.assertTrue(rows[0]["username"].startswith("@"))
        platforms = {r["platform"] for r in rows}
        self.assertIn("Threads", platforms)
        self.assertIn("TikTok", platforms)
        self.assertIn("Instagram", platforms)

    def test_instagram_scraper_requires_credentials_when_unconfigured(self) -> None:
        scraper = InstagramScraper()
        scraper.username = ""
        scraper.password = ""
        scraper.apify_token = ""
        if not Settings.credential_status()["instagram_login_ready"] and not Settings.credential_status()["apify_token_ready"]:
            with self.assertRaises(RuntimeError):
                scraper.fetch_comments("C9xyz123", limit=5)

    def test_threads_scraper_requires_credentials_when_unconfigured(self) -> None:
        scraper = ThreadsScraper()
        scraper.username = ""
        scraper.password = ""
        scraper.session_id = ""
        scraper.apify_token = ""
        if not Settings.credential_status()["threads_ready"] and not Settings.credential_status()["apify_token_ready"]:
            with self.assertRaises(RuntimeError):
                scraper.fetch_comments("sampah palembang", limit=5)

    def test_youtube_scraper_requires_api_key_when_unconfigured(self) -> None:
        scraper = YouTubeScraper()
        if not Settings.credential_status()["youtube_api_ready"]:
            with self.assertRaises(RuntimeError):
                scraper.fetch_comments("dQw4w9WgXcQ", limit=5)


if __name__ == "__main__":
    unittest.main()
