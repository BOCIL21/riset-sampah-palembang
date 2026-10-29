import unittest
from pathlib import Path
from src.jurnal_1_nlp.evaluator import EvaluatorJurnal1
from src.jurnal_1_nlp.pipeline_jurnal1 import PipelineJurnal1
from src.jurnal_1_nlp.sentiment_analyzer import SentimentAnalyzerJurnal1
from src.jurnal_1_nlp.topic_modeler import TopicModelerJurnal1


class TestJurnal1NLP(unittest.TestCase):
    def test_sentiment_analyzer_negative_and_positive(self) -> None:
        analyzer = SentimentAnalyzerJurnal1()
        neg = analyzer.analyze("Sampah sudah menumpuk sekali dan bau busuk di pasar")
        pos = analyzer.analyze("Apresiasi petugas kebersihan sudah rapi dan bersih")
        self.assertEqual(neg["sentiment"], "Negatif")
        self.assertEqual(pos["sentiment"], "Positif")

    def test_topic_modeler_clustering(self) -> None:
        modeler = TopicModelerJurnal1()
        docs = [
            "Sampah di Pasar 16 Ilir penuh lalat dan sayur busuk",
            "Drainase dan got mampet di Sungai Sekanak bikin banjir",
            "Truk petugas DLHK belum angkut kontainer selama 4 hari",
        ]
        topics = modeler.assign_topics(docs)
        self.assertEqual(topics[0]["topic_id"], "T1_Sampah_Pasar_Tradisional")
        self.assertEqual(topics[1]["topic_id"], "T2_Sungai_Drainase_Banjir")
        self.assertEqual(topics[2]["topic_id"], "T3_Keterlambatan_Angkut_DLHK")

    def test_evaluator_cohens_kappa_and_f1(self) -> None:
        y_true = ["Negatif", "Negatif", "Positif", "Netral"]
        y_pred = ["Negatif", "Negatif", "Positif", "Netral"]
        metrics = EvaluatorJurnal1.evaluate_predictions(y_true, y_pred)
        self.assertEqual(metrics["accuracy"], 1.0)
        self.assertEqual(metrics["cohens_kappa"], 1.0)

    def test_full_pipeline_jurnal1(self) -> None:
        pipeline = PipelineJurnal1()
        report = pipeline.run()
        self.assertGreaterEqual(report["total_dokumen"], 900)
        self.assertTrue(Path(str(report["file_output_csv"])).exists())


if __name__ == "__main__":
    unittest.main()
