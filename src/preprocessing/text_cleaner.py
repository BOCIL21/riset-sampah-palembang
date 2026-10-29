import re


class TextCleaner:
    """
    Membersihkan teks mentah media sosial (menghapus URL, mention, hashtag berlebih,
    karakter non-ASCII/emoji berlebih, dan spasi ganda).
    """

    URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")
    MENTION_PATTERN = re.compile(r"@\w+")
    HASHTAG_PATTERN = re.compile(r"#(\w+)")
    MULTISPACE_PATTERN = re.compile(r"\s+")

    @classmethod
    def clean(cls, text: str, lowercase: bool = True) -> str:
        """Membersihkan teks komentar media sosial secara terstandar."""
        if not text:
            return ""

        cleaned = cls.URL_PATTERN.sub(" ", text)
        cleaned = cls.MENTION_PATTERN.sub(" ", cleaned)
        # Pertahankan kata di dalam hashtag karena sering memuat lokasi (misal #Pasar16Ilir)
        cleaned = cls.HASHTAG_PATTERN.sub(r"\1", cleaned)
        # Hanya izinkan huruf, angka, tanda baca dasar
        cleaned = re.sub(r"[^a-zA-Z0-9\s.,!?-]", " ", cleaned)
        cleaned = cls.MULTISPACE_PATTERN.sub(" ", cleaned).strip()

        return cleaned.lower() if lowercase else cleaned
