import unittest
from src.preprocessing.palembang_normalizer import PalembangNormalizer
from src.preprocessing.text_cleaner import TextCleaner


class TestPreprocessingPalembang(unittest.TestCase):
    def setUp(self) -> None:
        self.normalizer = PalembangNormalizer()

    def test_text_cleaner_removes_url_and_mentions(self) -> None:
        raw = "Tolong @palembang.terkini cek https://t.co/xyz123 sampah di #Pasar16Ilir!!"
        cleaned = TextCleaner.clean(raw)
        self.assertNotIn("https", cleaned)
        self.assertNotIn("@palembang", cleaned)
        self.assertIn("pasar16ilir", cleaned)

    def test_palembang_lexicon_normalization(self) -> None:
        kalimat_plg = "La numpuk nian sampah ini, cak mano pemkot katek yang ambek"
        hasil = self.normalizer.normalize_lexicon(kalimat_plg)
        self.assertIn("sudah", hasil)
        self.assertIn("sekali", hasil)
        self.assertIn("bagaimana", hasil)
        self.assertIn("tidak ada", hasil)
        self.assertIn("ambil", hasil)

    def test_hybrid_normalizer_structure(self) -> None:
        res = self.normalizer.normalize_hybrid("Banyu pasang sampah mambu nian")
        self.assertIn("original_text", res)
        self.assertIn("lexicon_normalized", res)
        self.assertIn("final_normalized", res)
        self.assertIn("air", res["final_normalized"])


if __name__ == "__main__":
    unittest.main()
