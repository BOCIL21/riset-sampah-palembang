import json
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional
from config.settings import Settings
from src.jurnal_2_geospasial.gis_mapper import GISMapperJurnal2
from src.jurnal_2_geospasial.location_extractor import LocationExtractorJurnal2
from src.jurnal_2_geospasial.urgency_classifier import UrgencyClassifierJurnal2
from src.preprocessing.palembang_normalizer import PalembangNormalizer
from src.scrapers.base_scraper import BaseScraper


class PipelineJurnal2:
    """
    Orchestrator utama untuk Jurnal 2:
    Memproses data keluhan -> Normalisasi Bahasa Palembang -> Ekstraksi Entitas Lokasi (NER) ->
    Klasifikasi Urgensi & Rekomendasi Kebijakan -> Pembuatan Peta GIS HTML Interaktif.
    """

    def __init__(self) -> None:
        Settings.ensure_directories()
        self.normalizer = PalembangNormalizer()
        self.location_extractor = LocationExtractorJurnal2()
        self.urgency_classifier = UrgencyClassifierJurnal2()

    def run(self, input_csv: Optional[Path] = None) -> Dict[str, object]:
        csv_path = input_csv or (Settings.DATA_RAW_DIR / "sample_keluhan_palembang.csv")
        if input_csv is None:
            from src.scrapers.viral_palembang_collector import ViralPalembangCollector

            if not csv_path.exists():
                ViralPalembangCollector.save_default_viral_dataset(900)
            else:
                existing = BaseScraper.load_from_csv(csv_path, anonymize=False)
                years = {str(r.get("timestamp", ""))[:4] for r in existing}
                has_real_post_url = bool(existing and "/p/" in str(existing[0].get("post_url", "")))
                if len(existing) < 900 or years == {"2026"} or not has_real_post_url:
                    ViralPalembangCollector.save_default_viral_dataset(900)

        raw_records = BaseScraper.load_from_csv(csv_path, anonymize=True)

        processed_rows: List[Dict[str, object]] = []
        for row in raw_records:
            raw_text = row.get("raw_text", "")
            likes_count = int(row.get("likes_count", 0) or 0)

            norm_info = self.normalizer.normalize_hybrid(raw_text)
            final_text = norm_info["final_normalized"]

            loc_info = self.location_extractor.extract_location(final_text)
            urg_info = self.urgency_classifier.classify_urgency(final_text, likes_count=likes_count)

            processed_rows.append(
                {
                    "id": row.get("id", ""),
                    "platform": row.get("platform", ""),
                    "source_account": row.get("source_account", ""),
                    "username": row.get("username", ""),
                    "username_masked": row.get("username_masked", ""),
                    "timestamp": row.get("timestamp", ""),
                    "likes_count": likes_count,
                    "raw_text": raw_text,
                    "normalized_text": final_text,
                    "detected_location": loc_info["detected_location"],
                    "kecamatan": loc_info["kecamatan"],
                    "tipe_kawasan": loc_info["tipe_kawasan"],
                    "latitude": loc_info["latitude"],
                    "longitude": loc_info["longitude"],
                    "geocoding_status": loc_info["geocoding_status"],
                    "urgency_level": urg_info["urgency_level"],
                    "urgency_score": urg_info["urgency_score"],
                    "sla_target": urg_info["sla_target"],
                    "risk_factors": urg_info.get("risk_factors", ""),
                    "recommended_action": urg_info["recommended_action"],
                    "profile_url": row.get("profile_url", ""),
                    "post_url": row.get("post_url", ""),
                }
            )

        # Urutkan berdasarkan urgency_score tertinggi untuk tabel prioritas DLHK
        processed_rows.sort(key=lambda r: int(r["urgency_score"]), reverse=True)  # type: ignore

        out_csv = Settings.OUTPUT_JURNAL2_DIR / "hasil_geospasial_urgensi_jurnal2.csv"
        BaseScraper.save_to_csv(processed_rows, out_csv)

        out_map = Settings.OUTPUT_JURNAL2_DIR / "peta_hotspot_sampah_palembang.html"
        GISMapperJurnal2.generate_interactive_map(processed_rows, out_map)

        kecamatan_counts = dict(Counter(str(r["kecamatan"]) for r in processed_rows))
        urgency_counts = dict(Counter(str(r["urgency_level"]) for r in processed_rows))
        kawasan_counts = dict(Counter(str(r["tipe_kawasan"]) for r in processed_rows))
        year_counts = dict(Counter(str(r["timestamp"])[:4] for r in processed_rows))

        top_unique_locations: List[Dict[str, object]] = []
        seen_locs = set()
        for r in processed_rows:
            loc_name = str(r["detected_location"])
            if loc_name not in seen_locs:
                seen_locs.add(loc_name)
                top_unique_locations.append(
                    {
                        "lokasi": loc_name,
                        "kecamatan": r["kecamatan"],
                        "skor_urgensi": r["urgency_score"],
                        "level": r["urgency_level"],
                        "rekomendasi": r["recommended_action"],
                    }
                )
            if len(top_unique_locations) >= 5:
                break

        summary_report = {
            "judul_jurnal_2": (
                "Ekstraksi Entitas Lokasi dan Klasifikasi Tingkat Urgensi Keluhan Sampah "
                "di Kota Palembang Berbasis Large Language Models (LLM) untuk Mendukung Smart Environment"
            ),
            "total_laporan": len(processed_rows),
            "distribusi_tahun": year_counts,
            "distribusi_urgensi": urgency_counts,
            "sebaran_kecamatan": kecamatan_counts,
            "sebaran_tipe_kawasan": kawasan_counts,
            "top_3_prioritas_darurat": top_unique_locations[:3],
            "top_5_prioritas_darurat": top_unique_locations[:5],
            "file_output_csv": str(out_csv),
            "file_peta_interaktif_html": str(out_map),
        }

        out_json = Settings.OUTPUT_JURNAL2_DIR / "ringkasan_jurnal2.json"
        out_json.write_text(json.dumps(summary_report, indent=2, ensure_ascii=False), encoding="utf-8")
        return summary_report
