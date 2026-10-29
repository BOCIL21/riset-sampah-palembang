from typing import Dict, List, Optional
from src.ai_providers.llm_client import LLMClient


class UrgencyClassifierJurnal2:
    """
    Modul Klasifikasi Multi-Label & Skoring Tingkat Urgensi Keluhan Sampah (Jurnal 2).
    Digunakan sebagai Sistem Pendukung Keputusan (Decision Support) bagi DLHK Kota Palembang.
    """

    CRITICAL_TRIGGERS = [
        "banjir", "mampet", "tersumbat", "pintu air", "drainase", "got", "meluber",
        "macet total", "nutup separuh jalan", "darurat", "bahaya", "buntang", "belatung",
    ]
    MEDIUM_TRIGGERS = [
        "numpuk", "menumpuk", "tumpukan", "overload", "penuh", "bau", "busuk",
        "mambu", "lalat", "hari", "seminggu", "tidak diambil", "belum diangkut",
        "cctv", "denda", "sanksi", "amdal", "polusi", "asap", "bak sampah", "kontainer",
    ]
    POSITIVE_SAFE_MARKERS = [
        "terima kasih", "apresiasi", "rapi sekali", "bersih sekali", "mulai ditata rapi",
        "sangat membantu", "patut dicontoh", "inovasi", "program bagus", "gotong royong warga",
        "berkurang drastis", "efektif mengurangi",
    ]
    NEGATIVE_PROBLEM_WORDS = [
        "numpuk", "menumpuk", "bau", "busuk", "mambu", "buntang", "mampet", "tersumbat",
        "meluber", "darurat", "bahaya", "parah", "keluhan", "belum diangkut", "tidak diambil",
        "macet", "penuh sampah", "sampah plastik mengapung", "krisis", "tercemar", "polusi",
    ]

    def __init__(self, llm_client: Optional[LLMClient] = None) -> None:
        self.llm_client = llm_client or LLMClient()

    def classify_urgency(self, normalized_text: str, likes_count: int = 0) -> Dict[str, object]:
        """
        Menentukan level urgensi (TINGGI_KRITIS, SEDANG, RENDAH), skor urgensi (0-100),
        serta rekomendasi tindakan operasional untuk DLHK Palembang.
        """
        lower = normalized_text.lower()
        is_positive_safe = any(p in lower for p in self.POSITIVE_SAFE_MARKERS) and not any(
            n in lower for n in self.NEGATIVE_PROBLEM_WORDS
        )

        if is_positive_safe:
            crit_hits: List[str] = []
            med_hits: List[str] = []
            urgency_score = min(15 + min(int(likes_count // 15), 10), 30)
            level = "RENDAH"
            sla_target = "Rutin / Terjadwal"
            recommended_action = (
                "Monitoring berkala, edukasi bank sampah, atau sosialisasi Perda Ketertiban Umum."
            )
        else:
            crit_hits = [w for w in self.CRITICAL_TRIGGERS if w in lower]
            if "sungai" in lower and any(n in lower for n in self.NEGATIVE_PROBLEM_WORDS):
                crit_hits.append("pencemaran sungai")
            med_hits = [w for w in self.MEDIUM_TRIGGERS if w in lower]

            virality_bonus = min(int(likes_count // 5), 15)
            if crit_hits:
                base_score = 55 + len(crit_hits) * 15 + len(med_hits) * 5
                urgency_score = min(max(base_score + virality_bonus, 72), 100)
                level = "TINGGI_KRITIS"
                sla_target = "< 6 Jam (Respon Cepat / Darurat)"
                recommended_action = (
                    "Kirim Satgas Kebersihan & Dinas PUPR/PSDA untuk pembersihan sumbatan "
                    "drainase/sungai atau tumpukan yang menutup jalan utama."
                )
            elif med_hits:
                base_score = 35 + len(med_hits) * 8
                urgency_score = min(max(base_score + virality_bonus, 45), 68)
                level = "SEDANG"
                sla_target = "1 x 24 Jam (Penjadwalan Armada Truk)"
                recommended_action = (
                    "Tambahkan ritase armada truk pengangkut sampah DLHK dan lakukan "
                    "penyemprotan disinfektan/deodoran di TPS terkait."
                )
            else:
                urgency_score = min(20 + min(int(likes_count // 10), 15), 35)
                level = "RENDAH"
                sla_target = "Rutin / Terjadwal"
                recommended_action = (
                    "Monitoring berkala, edukasi bank sampah, atau sosialisasi Perda Ketertiban Umum."
                )

        fallback = {
            "urgency_level": level,
            "urgency_score": urgency_score,
            "sla_target": sla_target,
            "risk_factors": ", ".join(crit_hits + med_hits) if (crit_hits or med_hits) else "reguler",
            "recommended_action": recommended_action,
        }

        system_prompt = (
            "Analisis tingkat urgensi laporan sampah Kota Palembang berikut. "
            "Kembalikan JSON dengan key: 'urgency_level' (TINGGI_KRITIS/SEDANG/RENDAH), "
            "'urgency_score' (0-100), 'sla_target', dan 'recommended_action'."
        )
        return self.llm_client.generate_json(system_prompt, normalized_text, fallback)
