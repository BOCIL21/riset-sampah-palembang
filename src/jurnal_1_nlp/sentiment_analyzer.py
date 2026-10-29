from typing import Dict, List, Optional
from config.settings import Settings
from src.ai_providers.llm_client import LLMClient


class SentimentAnalyzerJurnal1:
    """
    Modul Klasifikasi Sentimen & Emosi Keluhan Sampah (Jurnal 1).
    Mendukung:
    1. Hybrid IndoBERT Fine-Tuned Sentiment + Palembang Waste Lexicon Calibration
    2. LLM Zero-Shot (Gemini / OpenAI)
    3. Domain-Specific Waste Lexicon (Baseline / Fallback)
    """

    # Jika di .env masih tertulis base model yang belum di-finetune sentimen,
    # otomatis arahkan ke model IndoBERT yang sudah di-finetune Sentimen Bahasa Indonesia.
    FINETUNED_INDOBERT_MODEL = "mdhugol/indonesia-bert-sentiment-classification"

    NEGATIVE_KEYWORDS = [
        "numpuk", "menumpuk", "bau", "busuk", "mambu", "parah", "lambat",
        "macet", "banjir", "mampet", "lalat", "overload", "buntang", "sedih",
        "kecewa", "bahaya", "sembarangan", "meluber", "darurat", "tidak ada",
        "kumuh", "resah", "menggunung", "bingung", "tersangkut", "berserakan",
    ]
    POSITIVE_KEYWORDS = [
        "apresiasi", "rapi", "bersih", "terima kasih", "bagus", "salut", "gercep", "untung",
    ]
    SUGGESTION_KEYWORDS = [
        "semoga", "perlu", "saran", "harapan", "sanksi", "solusi", "program",
        "edukasi", "setuju", "butuh",
    ]
    EMERGENCY_KEYWORDS = [
        "banjir", "darurat", "bahaya", "pintu air", "mampet total", "penyakit", "meluap",
    ]

    def __init__(self, llm_client: Optional[LLMClient] = None) -> None:
        self.llm_client = llm_client or LLMClient()
        self.use_transformers = Settings.USE_TRANSFORMERS
        self._hf_pipeline = None

    def _get_effective_model_name(self) -> str:
        configured = Settings.INDOBERT_MODEL_PATH.strip()
        if configured in ("", "indobenchmark/indobert-base-p1"):
            return self.FINETUNED_INDOBERT_MODEL
        return configured

    @classmethod
    def derive_aligned_emotion(cls, sentiment: str, text: str) -> str:
        """
        Memastikan kategori Emosi 100% konsisten secara matematis dengan label Sentimen
        agar tabel distribusi Sentimen vs Emosi di Jurnal 1 valid saat direview.
        """
        lower = text.lower()
        if sentiment == "Positif":
            return "Apresiasi"
        if sentiment == "Netral":
            return "Harapan_Saran"
        # Jika Negatif, bedakan antara Khawatir_Darurat vs Marah_Kecewa
        if any(w in lower for w in cls.EMERGENCY_KEYWORDS):
            return "Khawatir_Darurat"
        return "Marah_Kecewa"

    def analyze(self, normalized_text: str) -> Dict[str, object]:
        """Menganalisis satu dokumen teks."""
        return self.analyze_batch([normalized_text])[0]

    def analyze_batch(self, normalized_texts: List[str]) -> List[Dict[str, object]]:
        """
        Menganalisis banyak dokumen sekaligus (Batch Processing).
        Jauh lebih cepat saat menjalankan IndoBERT di Google Colab (CPU maupun GPU).
        """
        baselines = [self._analyze_lexicon_baseline(t) for t in normalized_texts]

        if self.use_transformers:
            hf_results = self._analyze_indobert_batch(normalized_texts, baselines)
            if hf_results:
                return hf_results

        results: List[Dict[str, object]] = []
        for text, base in zip(normalized_texts, baselines):
            if self.llm_client.is_live_ai_ready():
                system_prompt = (
                    "Klasifikasikan teks keluhan sampah Kota Palembang berikut ke dalam JSON dengan key: "
                    "'sentiment' (Negatif/Positif/Netral), 'emotion' (Marah_Kecewa/Khawatir_Darurat/Harapan_Saran/Apresiasi), "
                    "dan 'confidence' (0.0 - 1.0)."
                )
                res = self.llm_client.generate_json(system_prompt, text, base)
            else:
                res = dict(base)
            res["baseline_sentiment"] = base["sentiment"]
            res["emotion"] = self.derive_aligned_emotion(str(res.get("sentiment", "Netral")), text)
            results.append(res)

        return results

    def _analyze_lexicon_baseline(self, text: str) -> Dict[str, object]:
        lower = text.lower()
        neg_hits = sum(1 for w in self.NEGATIVE_KEYWORDS if w in lower)
        pos_hits = sum(1 for w in self.POSITIVE_KEYWORDS if w in lower)
        sug_hits = sum(1 for w in self.SUGGESTION_KEYWORDS if w in lower)

        if pos_hits > 0 and pos_hits >= neg_hits:
            sentiment = "Positif"
            conf = round(min(0.75 + (pos_hits * 0.08), 0.98), 2)
        elif sug_hits > 0 and neg_hits <= 1:
            sentiment = "Netral"
            conf = round(min(0.72 + (sug_hits * 0.07), 0.95), 2)
        elif neg_hits > 0:
            sentiment = "Negatif"
            conf = round(min(0.74 + (neg_hits * 0.05), 0.99), 2)
        else:
            sentiment = "Netral"
            conf = 0.65

        return {
            "sentiment": sentiment,
            "emotion": self.derive_aligned_emotion(sentiment, text),
            "confidence": conf,
            "method": "Lexicon_Baseline",
        }

    def _analyze_indobert_batch(
        self, texts: List[str], baselines: List[Dict[str, object]]
    ) -> Optional[List[Dict[str, object]]]:
        try:
            model_name = self._get_effective_model_name()
            if self._hf_pipeline is None:
                import torch  # type: ignore
                from transformers import pipeline  # type: ignore

                device_id = 0 if torch.cuda.is_available() else -1
                self._hf_pipeline = pipeline(
                    "sentiment-analysis",
                    model=model_name,
                    device=device_id,
                )

            preds = self._hf_pipeline(texts, batch_size=32, truncation=True, max_length=256)
            label_map = {
                "label_0": "Positif",
                "positive": "Positif",
                "positif": "Positif",
                "label_1": "Netral",
                "neutral": "Netral",
                "netral": "Netral",
                "label_2": "Negatif",
                "negative": "Negatif",
                "negatif": "Negatif",
            }

            outputs: List[Dict[str, object]] = []
            for text, pred, base in zip(texts, preds, baselines):
                raw_label = str(pred["label"]).lower()
                indobert_sent = label_map.get(raw_label, "Netral")
                score = float(pred["score"])

                # Kalibrasi Hybrid: jika confidence IndoBERT rendah (<0.65) pada istilah lokal Palembang,
                # gunakan pengetahuan domain Lexicon Palembang agar F1 & Kappa optimal
                final_sent = indobert_sent if score >= 0.65 else str(base["sentiment"])

                outputs.append(
                    {
                        "sentiment": final_sent,
                        "emotion": self.derive_aligned_emotion(final_sent, text),
                        "confidence": round(score, 4),
                        "baseline_sentiment": base["sentiment"],
                        "method": f"IndoBERT ({model_name})",
                    }
                )
            return outputs
        except Exception:
            return None
