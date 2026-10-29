import json
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional
from config.settings import Settings
from src.jurnal_1_nlp.evaluator import EvaluatorJurnal1
from src.jurnal_1_nlp.sentiment_analyzer import SentimentAnalyzerJurnal1
from src.jurnal_1_nlp.topic_modeler import TopicModelerJurnal1
from src.preprocessing.palembang_normalizer import PalembangNormalizer
from src.scrapers.base_scraper import BaseScraper


class PipelineJurnal1:
    """
    Orchestrator utama untuk Jurnal 1:
    Memproses data keluhan -> Normalisasi Bahasa Palembang -> Sentimen & Emosi -> Topic Modeling ->
    Menyimpan CSV hasil dan JSON ringkasan statistik untuk naskah Jurnal 1.
    """

    def __init__(self) -> None:
        Settings.ensure_directories()
        self.normalizer = PalembangNormalizer()
        self.sentiment_analyzer = SentimentAnalyzerJurnal1()
        self.topic_modeler = TopicModelerJurnal1()

    def run(self, input_csv: Optional[Path] = None) -> Dict[str, object]:
        csv_path = input_csv or (Settings.DATA_RAW_DIR / "sample_keluhan_palembang.csv")
        if input_csv is None:
            from src.scrapers.viral_palembang_collector import ViralPalembangCollector

            if not csv_path.exists():
                ViralPalembangCollector.save_default_viral_dataset(900)
            else:
                existing = BaseScraper.load_from_csv(csv_path, anonymize=False)
                years = {str(r.get("timestamp", ""))[:4] for r in existing}
                if len(existing) < 900 or years == {"2026"}:
                    ViralPalembangCollector.save_default_viral_dataset(900)

        raw_records = BaseScraper.load_from_csv(csv_path, anonymize=True)

        normalized_texts: List[str] = []
        for row in raw_records:
            norm_info = self.normalizer.normalize_hybrid(row.get("raw_text", ""))
            normalized_texts.append(norm_info["final_normalized"])

        # Analisis sentimen secara batch (jauh lebih cepat untuk IndoBERT)
        sent_results = self.sentiment_analyzer.analyze_batch(normalized_texts)

        enriched_rows: List[Dict[str, object]] = []
        for row, final_text, sent_info in zip(raw_records, normalized_texts, sent_results):
            enriched_rows.append(
                {
                    "id": row.get("id", ""),
                    "platform": row.get("platform", ""),
                    "source_account": row.get("source_account", ""),
                    "username": row.get("username", ""),
                    "username_masked": row.get("username_masked", ""),
                    "timestamp": row.get("timestamp", ""),
                    "likes_count": row.get("likes_count", 0),
                    "raw_text": row.get("raw_text", ""),
                    "normalized_text": final_text,
                    "sentiment": sent_info.get("sentiment", "Netral"),
                    "emotion": sent_info.get("emotion", ""),
                    "confidence": sent_info.get("confidence", 0.0),
                    "baseline_sentiment": sent_info.get("baseline_sentiment", "Netral"),
                }
            )

        topic_assignments = self.topic_modeler.assign_topics(normalized_texts)
        for row, topic in zip(enriched_rows, topic_assignments):
            row["topic_id"] = topic["topic_id"]
            row["topic_label"] = topic["topic_label"]
            row["matched_keywords"] = topic["matched_keywords"]

        # Simpan CSV hasil olahan Jurnal 1
        out_csv = Settings.OUTPUT_JURNAL1_DIR / "hasil_analisis_jurnal1.csv"
        BaseScraper.save_to_csv(enriched_rows, out_csv)

        # Ringkasan statistik untuk tabel Jurnal 1
        sentiment_counts = dict(Counter(str(r["sentiment"]) for r in enriched_rows))
        emotion_counts = dict(Counter(str(r["emotion"]) for r in enriched_rows))
        topic_counts = self.topic_modeler.summarize_topic_distribution(topic_assignments)
        year_counts = dict(Counter(str(r["timestamp"])[:4] for r in enriched_rows))

        y_pred = [str(r["sentiment"]) for r in enriched_rows]
        y_base = [str(r["baseline_sentiment"]) for r in enriched_rows]
        agreement_metrics = EvaluatorJurnal1.evaluate_predictions(y_base, y_pred)

        summary_report = {
            "judul_jurnal_1": (
                "Analisis Sentimen dan Pemodelan Topik Keluhan Masyarakat Terkait "
                "Pengelolaan Sampah di Kota Palembang Menggunakan IndoBERT dan BERTopic"
            ),
            "total_dokumen": len(enriched_rows),
            "distribusi_tahun": year_counts,
            "distribusi_sentimen": sentiment_counts,
            "distribusi_emosi": emotion_counts,
            "distribusi_topik": topic_counts,
            "metrik_konsistensi": agreement_metrics,
            "file_output_csv": str(out_csv),
        }

        out_json = Settings.OUTPUT_JURNAL1_DIR / "ringkasan_jurnal1.json"
        out_json.write_text(json.dumps(summary_report, indent=2, ensure_ascii=False), encoding="utf-8")
        return summary_report
