import unittest
from pathlib import Path
from src.jurnal_2_geospasial.location_extractor import LocationExtractorJurnal2
from src.jurnal_2_geospasial.pipeline_jurnal2 import PipelineJurnal2
from src.jurnal_2_geospasial.urgency_classifier import UrgencyClassifierJurnal2


class TestJurnal2Geospasial(unittest.TestCase):
    def test_location_extractor_palembang_landmarks(self) -> None:
        extractor = LocationExtractorJurnal2()
        loc1 = extractor.extract_location("Tumpukan sampah di Pasar 16 Ilir dekat Sungai Musi")
        self.assertEqual(loc1["detected_location"], "Pasar 16 Ilir")
        self.assertEqual(loc1["kecamatan"], "Ilir Timur I")
        self.assertEqual(loc1["geocoding_status"], "TERPETAKAN_SPESIFIK")

        loc2 = extractor.extract_location("TPA Sukawinatan overload terus")
        self.assertEqual(loc2["kecamatan"], "Sukarami")

    def test_urgency_classifier_levels(self) -> None:
        classifier = UrgencyClassifierJurnal2()
        crit = classifier.classify_urgency(
            "Bahaya banjir! Sampah nyangkut di pintu air Sungai Bendung darurat",
            likes_count=90,
        )
        low = classifier.classify_urgency(
            "Semoga program bank sampah di Plaju berjalan lancar",
            likes_count=5,
        )
        self.assertEqual(crit["urgency_level"], "TINGGI_KRITIS")
        self.assertGreaterEqual(int(crit["urgency_score"]), 70)  # type: ignore
        self.assertEqual(low["urgency_level"], "RENDAH")

    def test_full_pipeline_jurnal2_generates_csv_and_html_map(self) -> None:
        pipeline = PipelineJurnal2()
        report = pipeline.run()
        self.assertEqual(report["total_laporan"], 360)
        self.assertTrue(Path(str(report["file_output_csv"])).exists())
        map_path = Path(str(report["file_peta_interaktif_html"]))
        self.assertTrue(map_path.exists())
        map_content = map_path.read_text(encoding="utf-8")
        self.assertIn("leaflet", map_content.lower())
        self.assertNotIn('<i>"" +', map_content)

        # Validasi sintaks JavaScript di dalam HTML menggunakan node --check
        import re
        import subprocess

        scripts = re.findall(r"<script>(.*?)</script>", map_content, flags=re.S)
        self.assertEqual(len(scripts), 1)
        tmp_js = map_path.parent / "_syntax_check.js"
        tmp_js.write_text(scripts[0], encoding="utf-8")
        proc = subprocess.run(["node", "--check", str(tmp_js)], capture_output=True, text=True)
        tmp_js.unlink(missing_ok=True)
        self.assertEqual(proc.returncode, 0, msg=f"JS Syntax Error: {proc.stderr}")


if __name__ == "__main__":
    unittest.main()
