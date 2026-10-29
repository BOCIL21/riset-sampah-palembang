from collections import Counter
from typing import Dict, List
from config.settings import Settings


class TopicModelerJurnal1:
    """
    Modul Pemodelan Topik Keluhan Sampah (Jurnal 1).
    Mengelompokkan dokumen ke dalam topik utama pengelolaan sampah Kota Palembang
    menggunakan Hybrid BERTopic + Domain Taxonomy (tanpa outlier -1 yang terbuang).
    """

    INDONESIAN_STOPWORDS = [
        "yang", "di", "dan", "ini", "itu", "ke", "dari", "untuk", "dengan", "pada",
        "sudah", "sekali", "tidak", "ada", "sama", "saja", "jadi", "karena", "kalau",
        "bisa", "terus", "banyak", "tolong", "min", "pak", "nih", "pas", "tiap",
        "pagi", "sore", "malam", "kemarin", "sini", "situ", "masih", "belum", "harus",
        "biar", "jangan", "sampai", "dekat", "bawah", "atas", "tengah", "pinggir",
        "kota", "palembang", "sampah",
    ]

    TOPIC_TAXONOMY: Dict[str, Dict[str, object]] = {
        "T1_Sampah_Pasar_Tradisional": {
            "label": "Tumpukan Sampah Pasar Tradisional",
            "keywords": [
                "pasar", "sayur", "lalat", "meluber", "pedagang", "16 ilir",
                "lemabang", "jakabaring", "palimo", "cinde", "kuto", "tangga takat", "basement",
            ],
        },
        "T2_Sungai_Drainase_Banjir": {
            "label": "Pencemaran Sungai Musi, Anak Sungai & Drainase Rawan Banjir",
            "keywords": [
                "sungai", "musi", "sekanak", "bendung", "buah", "lambidaro",
                "kapitan", "banjir", "got", "mampet", "drainase", "pintu air", "air", "trash trap",
            ],
        },
        "T3_Keterlambatan_Angkut_DLHK": {
            "label": "Keterlambatan Jadwal Pengangkutan & Armada DLHK",
            "keywords": [
                "angkut", "diambil", "petugas", "dlhk", "truk", "jadwal",
                "hari", "seminggu", "kontainer", "armada", "iuran", "telat",
            ],
        },
        "T4_Kapasitas_TPS_TPA_Overload": {
            "label": "Kapasitas TPS Kurang, TPA Sukawinatan Overload & PSEL Keramasan",
            "keywords": [
                "tpa", "tps", "sukawinatan", "overload", "penuh", "perumahan",
                "resmi", "keramasan", "psel", "gunungan", "penggantinya",
            ],
        },
        "T5_Perilaku_Warga_Dan_Kebijakan": {
            "label": "Perilaku Buang Sampah Sembarangan, Komunitas & Regulasi",
            "keywords": [
                "sembarangan", "sadar", "sanksi", "denda", "bank sampah",
                "apresiasi", "taman", "warga", "relawan", "clean vibes", "kamera", "edukasi",
            ],
        },
    }

    def assign_topics(self, texts: List[str]) -> List[Dict[str, object]]:
        """Menetapkan topik dominan dan kata kunci pemicu untuk setiap dokumen."""
        domain_results = self._assign_domain_taxonomy(texts)

        if Settings.USE_TRANSFORMERS and len(texts) >= 15:
            bertopic_results = self._run_bertopic_hybrid(texts, domain_results)
            if bertopic_results:
                return bertopic_results

        return domain_results

    def _assign_domain_taxonomy(self, texts: List[str]) -> List[Dict[str, object]]:
        results: List[Dict[str, object]] = []
        for text in texts:
            lower = text.lower()
            best_topic_id = "T5_Perilaku_Warga_Dan_Kebijakan"
            best_score = 0
            matched_words: List[str] = []

            for topic_id, info in self.TOPIC_TAXONOMY.items():
                kw_list: List[str] = list(info["keywords"])  # type: ignore
                hits = [kw for kw in kw_list if kw in lower]
                if len(hits) > best_score:
                    best_score = len(hits)
                    best_topic_id = topic_id
                    matched_words = hits

            results.append(
                {
                    "topic_id": best_topic_id,
                    "topic_label": self.TOPIC_TAXONOMY[best_topic_id]["label"],
                    "matched_keywords": ", ".join(matched_words) if matched_words else "umum",
                    "topic_score": best_score,
                }
            )
        return results

    def summarize_topic_distribution(self, topic_records: List[Dict[str, object]]) -> Dict[str, int]:
        """Menghitung distribusi frekuensi tiap topik untuk grafik/tabel Jurnal 1."""
        counts = Counter(str(item["topic_id"]) for item in topic_records)
        return dict(counts.most_common())

    def _run_bertopic_hybrid(
        self, texts: List[str], domain_results: List[Dict[str, object]]
    ) -> List[Dict[str, object]]:
        """
        Menjalankan BERTopic dengan CountVectorizer bebas stopword Bahasa Indonesia
        serta mereduksi outlier (-1) agar tidak ada dokumen yang terbuang di tabel jurnal.
        """
        try:
            from bertopic import BERTopic  # type: ignore
            from sklearn.feature_extraction.text import CountVectorizer  # type: ignore

            vectorizer = CountVectorizer(stop_words=self.INDONESIAN_STOPWORDS, ngram_range=(1, 2))
            topic_model = BERTopic(
                language="multilingual",
                vectorizer_model=vectorizer,
                min_topic_size=8,
                nr_topics=6,
                calculate_probabilities=False,
            )
            topics, _ = topic_model.fit_transform(texts)

            # Reduksi outlier -1 menggunakan strategi c-tf-idf bawaan BERTopic
            if -1 in topics:
                try:
                    topics = topic_model.reduce_outliers(texts, topics, strategy="c-tf-idf")
                except Exception:
                    pass

            output: List[Dict[str, object]] = []
            for t_id, dom in zip(topics, domain_results):
                words = topic_model.get_topic(t_id) or []
                clean_words = [w[0] for w in words[:5] if w[0]]
                kw_str = ", ".join(clean_words) if clean_words else str(dom["matched_keywords"])
                # Gabungkan ID topik domain dengan representasi kata kunci c-TF-IDF BERTopic
                output.append(
                    {
                        "topic_id": dom["topic_id"],
                        "topic_label": dom["topic_label"],
                        "matched_keywords": kw_str,
                        "bertopic_cluster": int(t_id),
                        "topic_score": dom["topic_score"],
                    }
                )
            return output
        except Exception:
            return []
