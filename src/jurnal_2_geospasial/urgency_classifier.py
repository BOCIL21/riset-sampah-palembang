from typing import Dict, List, Optional
from src.ai_providers.llm_client import LLMClient


class UrgencyClassifierJurnal2:
    """
    Modul Klasifikasi Multi-Label & Skoring Tingkat Urgensi Keluhan Sampah (Jurnal 2).
    Digunakan sebagai Sistem Pendukung Keputusan (Decision Support) bagi DLHK Kota Palembang.
    """

    CRITICAL_TRIGGERS = [
        "banjir", "mampet", "pintu air", "drainase", "got", "meluber",
        "macet total", "darurat", "bahaya", "sungai", "buntang",
    ]
    MEDIUM_TRIGGERS = [
        "numpuk", "menumpuk", "overload", "penuh", "bau", "busuk",
        "mambu", "lalat", "hari", "seminggu", "tidak diambil", "belum diangkut",
    ]

    def __init__(self, llm_client: Optional[LLMClient] = None) -> None:
        self.llm_client = llm_client or LLMClient()

    def classify_urgency(self, normalized_text: str, likes_count: int = 0) -> Dict[str, object]:
        """
        Menentukan level urgensi (TINGGI_KRITIS, SEDANG, RENDAH), skor urgensi (0-100),
        serta rekomendasi tindakan operasional untuk DLHK Palembang.
        """
        lower = normalized_text.lower()
        crit_hits = [w for w in self.CRITICAL_TRIGGERS if w in lower]
        med_hits = [w for w in self.MEDIUM_TRIGGERS if w in lower]

        # Perhitungan Skor Urgensi Komposit (0 - 100)
        base_score = 20
        base_score += len(crit_hits) * 25
        base_score += len(med_hits) * 12
        # Bobot viralitas / dukungan warga (likes_count) maksimum 15 poin
        virality_bonus = min(int(likes_count // 5), 15)
        urgency_score = min(base_score + virality_bonus, 100)

        if crit_hits or urgency_score >= 70:
            level = "TINGGI_KRITIS"
            sla_target = "< 6 Jam (Respon Cepat / Darurat)"
            recommended_action = (
                "Kirim Satgas Kebersihan & Dinas PUPR/PSDA untuk pembersihan sumbatan "
                "drainase/sungai atau tumpukan yang menutup jalan utama."
            )
        elif med_hits or urgency_score >= 45:
            level = "SEDANG"
            sla_target = "1 x 24 Jam (Penjadwalan Armada Truk)"
            recommended_action = (
                "Tambahkan ritase armada truk pengangkut sampah DLHK dan lakukan "
                "penyemprotan disinfektan/deodoran di TPS terkait."
            )
        else:
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
