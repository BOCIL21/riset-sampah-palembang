import os
from pathlib import Path
from typing import Dict

BASE_DIR = Path(__file__).resolve().parent.parent


def _load_dotenv_manual(dotenv_path: Path) -> None:
    """Membaca file .env tanpa bergantung penuh pada library eksternal jika belum terinstal."""
    if not dotenv_path.exists():
        return
    for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_dotenv_manual(BASE_DIR / ".env")


class Settings:
    """Konfigurasi terpusat untuk aplikasi scraping & AI jurnal."""

    PROJECT_ROOT: Path = BASE_DIR
    DATA_RAW_DIR: Path = BASE_DIR / "data" / "raw"
    DATA_PROCESSED_DIR: Path = BASE_DIR / "data" / "processed"
    OUTPUT_JURNAL1_DIR: Path = BASE_DIR / "data" / "outputs" / "jurnal_1"
    OUTPUT_JURNAL2_DIR: Path = BASE_DIR / "data" / "outputs" / "jurnal_2"

    KAMUS_PALEMBANG_PATH: Path = BASE_DIR / "config" / "kamus_palembang.json"
    GAZETTEER_PALEMBANG_PATH: Path = BASE_DIR / "config" / "gazetteer_palembang.json"

    # AI Settings
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "offline_fallback")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    AI_MODEL_NAME: str = os.getenv("AI_MODEL_NAME", "gemini-1.5-flash")

    # Scraping Credentials
    IG_USERNAME: str = os.getenv("IG_USERNAME", "")
    IG_PASSWORD: str = os.getenv("IG_PASSWORD", "")
    APIFY_API_TOKEN: str = os.getenv("APIFY_API_TOKEN", "")
    YOUTUBE_API_KEY: str = os.getenv("YOUTUBE_API_KEY", "")
    TWITTER_AUTH_TOKEN: str = os.getenv("TWITTER_AUTH_TOKEN", "")
    THREADS_USERNAME: str = os.getenv("THREADS_USERNAME", "")
    THREADS_PASSWORD: str = os.getenv("THREADS_PASSWORD", "")
    THREADS_SESSION_ID: str = os.getenv("THREADS_SESSION_ID", "")

    # NLP & GIS Settings
    USE_TRANSFORMERS: bool = os.getenv("USE_TRANSFORMERS", "false").lower() == "true"
    INDOBERT_MODEL_PATH: str = os.getenv("INDOBERT_MODEL_PATH", "mdhugol/indonesia-bert-sentiment-classification")
    OSM_USER_AGENT: str = os.getenv("OSM_USER_AGENT", "RisetSampahPalembang_Jurnal/1.0")
    GOOGLE_MAPS_API_KEY: str = os.getenv("GOOGLE_MAPS_API_KEY", "")
    DATA_START_YEAR: int = int(os.getenv("DATA_START_YEAR", "2024"))
    DATA_END_YEAR: int = int(os.getenv("DATA_END_YEAR", "2026"))

    @classmethod
    def ensure_directories(cls) -> None:
        """Memastikan seluruh direktori data dan output tersedia."""
        for folder in [
            cls.DATA_RAW_DIR,
            cls.DATA_PROCESSED_DIR,
            cls.OUTPUT_JURNAL1_DIR,
            cls.OUTPUT_JURNAL2_DIR,
        ]:
            folder.mkdir(parents=True, exist_ok=True)

    @classmethod
    def credential_status(cls) -> Dict[str, bool]:
        """Mengecek status ketersediaan kredensial untuk laporan diagnostik."""
        apify_ready = bool(cls.APIFY_API_TOKEN and "masukkan_" not in cls.APIFY_API_TOKEN)
        return {
            "gemini_api_key_ready": bool(cls.GEMINI_API_KEY and "masukkan_" not in cls.GEMINI_API_KEY),
            "openai_api_key_ready": bool(cls.OPENAI_API_KEY and "masukkan_" not in cls.OPENAI_API_KEY),
            "instagram_login_ready": bool(
                apify_ready
                or (cls.IG_USERNAME and cls.IG_PASSWORD and "username_" not in cls.IG_USERNAME)
            ),
            "apify_token_ready": apify_ready,
            "youtube_api_ready": bool(cls.YOUTUBE_API_KEY and "masukkan_" not in cls.YOUTUBE_API_KEY),
            "twitter_token_ready": bool(cls.TWITTER_AUTH_TOKEN and "masukkan_" not in cls.TWITTER_AUTH_TOKEN),
            "threads_ready": bool(
                apify_ready
                or (cls.THREADS_SESSION_ID and "masukkan_" not in cls.THREADS_SESSION_ID)
                or (cls.THREADS_USERNAME and cls.THREADS_PASSWORD and "username_" not in cls.THREADS_USERNAME)
            ),
            "google_maps_api_ready": bool(
                cls.GOOGLE_MAPS_API_KEY and "opsional_" not in cls.GOOGLE_MAPS_API_KEY
            ),
        }
