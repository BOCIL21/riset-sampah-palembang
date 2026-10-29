import json
import re
from pathlib import Path
from typing import Dict, Optional
from config.settings import Settings
from src.ai_providers.llm_client import LLMClient
from src.preprocessing.text_cleaner import TextCleaner


class PalembangNormalizer:
    """
    Modul Novelty Penelitian:
    Menormalisasi kosakata Bahasa Palembang (Baso Palembang) ke Bahasa Indonesia baku
    menggunakan pendekatan Hybrid (Kamus Leksikon Palembang + Large Language Model).
    """

    def __init__(
        self,
        kamus_path: Optional[Path] = None,
        llm_client: Optional[LLMClient] = None,
    ) -> None:
        self.kamus_path = kamus_path or Settings.KAMUS_PALEMBANG_PATH
        self.kamus: Dict[str, str] = self._load_kamus()
        self.llm_client = llm_client or LLMClient()

    def _load_kamus(self) -> Dict[str, str]:
        if not self.kamus_path.exists():
            return {}
        return json.loads(self.kamus_path.read_text(encoding="utf-8"))

    def normalize_lexicon(self, text: str) -> str:
        """
        Tahap 1: Mengganti frasa dan kata Bahasa Palembang berdasarkan kamus JSON.
        Mengurutkan frasa terpanjang lebih dulu (misal 'cak mano' sebelum 'cak').
        """
        cleaned = TextCleaner.clean(text, lowercase=True)
        sorted_keys = sorted(self.kamus.keys(), key=len, reverse=True)
        for slang in sorted_keys:
            baku = self.kamus[slang]
            pattern = re.compile(rf"\b{re.escape(slang)}\b", flags=re.IGNORECASE)
            cleaned = pattern.sub(baku, cleaned)
        return re.sub(r"\s+", " ", cleaned).strip()

    def normalize_hybrid(self, text: str) -> Dict[str, str]:
        """
        Tahap 2: Menggabungkan normalisasi kamus dengan LLM (jika API aktif)
        untuk memperbaiki struktur kalimat Bahasa Palembang ke Bahasa Indonesia baku.
        """
        lexicon_result = self.normalize_lexicon(text)
        system_prompt = (
            "Anda adalah ahli linguistik Bahasa Palembang (Sumatera Selatan). "
            "Ubah kalimat keluhan warga berikut ke dalam Bahasa Indonesia baku tanpa mengubah nama lokasi. "
            "Kembalikan dalam JSON dengan key: 'normalized_text'."
        )
        fallback = {"normalized_text": lexicon_result}
        ai_resp = self.llm_client.generate_json(system_prompt, lexicon_result, fallback)
        return {
            "original_text": text,
            "lexicon_normalized": lexicon_result,
            "final_normalized": str(ai_resp.get("normalized_text", lexicon_result)),
        }
