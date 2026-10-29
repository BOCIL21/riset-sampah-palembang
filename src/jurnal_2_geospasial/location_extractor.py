import json
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional
from config.settings import Settings
from src.ai_providers.llm_client import LLMClient


class LocationExtractorJurnal2:
    """
    Modul Named Entity Recognition (NER) Geospasial Kota Palembang (Jurnal 2).
    Mengekstrak nama lokasi, kecamatan, tipe kawasan, dan koordinat (lat, lon)
    dari teks keluhan tidak terstruktur menggunakan Gazetteer Palembang + LLM.
    """

    def __init__(
        self,
        gazetteer_path: Optional[Path] = None,
        llm_client: Optional[LLMClient] = None,
    ) -> None:
        self.gazetteer_path = gazetteer_path or Settings.GAZETTEER_PALEMBANG_PATH
        self.gazetteer: Dict[str, Dict[str, object]] = self._load_gazetteer()
        self.llm_client = llm_client or LLMClient()

    def _load_gazetteer(self) -> Dict[str, Dict[str, object]]:
        if not self.gazetteer_path.exists():
            return {}
        return json.loads(self.gazetteer_path.read_text(encoding="utf-8"))

    @staticmethod
    def _format_place_name(place: str) -> str:
        """Memformat nama tempat dengan mempertahankan singkatan & angka Romawi tetap kapital."""
        upper_tokens = {"ii", "iii", "iv", "vi", "km", "tpa", "tps", "psel", "bkb", "jsc", "rs"}
        words = []
        for w in place.split():
            if w.lower() in upper_tokens:
                words.append(w.upper())
            else:
                words.append(w.capitalize())
        return " ".join(words)

    def extract_location(self, text: str) -> Dict[str, object]:
        """
        Mendeteksi entitas lokasi spesifik di Palembang dari kalimat warga.
        Memprioritaskan entitas spesifik (Pasar, Sungai, TPA, Jalan, Simpang, Taman)
        dibanding nama Kecamatan umum, kemudian mengurutkan dari frasa terpanjang.
        """
        lower = text.lower()
        matched_locations: List[str] = []
        primary_meta: Optional[Dict[str, object]] = None

        def _sort_key(place_key: str) -> tuple:
            tipe = str(self.gazetteer[place_key].get("tipe", ""))
            is_specific = 0 if tipe in {"Kecamatan", "Kawasan"} else 1
            return (is_specific, len(place_key))

        sorted_places = sorted(self.gazetteer.keys(), key=_sort_key, reverse=True)
        for place in sorted_places:
            if place in lower:
                matched_locations.append(self._format_place_name(place))
                if primary_meta is None:
                    primary_meta = self.gazetteer[place]

        if primary_meta is not None:
            fallback = {
                "detected_location": matched_locations[0],
                "all_locations": ", ".join(matched_locations),
                "kecamatan": str(primary_meta["kecamatan"]),
                "tipe_kawasan": str(primary_meta["tipe"]),
                "latitude": float(primary_meta["lat"]),  # type: ignore
                "longitude": float(primary_meta["lon"]),  # type: ignore
                "geocoding_status": "TERPETAKAN_SPESIFIK",
            }
        else:
            # Titik tengah Kota Palembang jika lokasi spesifik tidak disebutkan
            fallback = {
                "detected_location": "Kota Palembang (Umum)",
                "all_locations": "Kota Palembang",
                "kecamatan": "Tidak Spesifik",
                "tipe_kawasan": "Umum",
                "latitude": -2.9761,
                "longitude": 104.7754,
                "geocoding_status": "DEFAULT_KOTA",
            }

        system_prompt = (
            "Ekstrak entitas lokasi di Kota Palembang dari teks keluhan berikut. "
            "Kembalikan JSON dengan key: 'detected_location', 'kecamatan', 'tipe_kawasan'."
        )
        ai_res = self.llm_client.generate_json(system_prompt, text, fallback)
        fallback["detected_location"] = ai_res.get("detected_location", fallback["detected_location"])
        fallback["kecamatan"] = ai_res.get("kecamatan", fallback["kecamatan"])

        # Jika lokasi belum ada di Gazetteer lokal tapi GOOGLE_MAPS_API_KEY aktif, panggil Google Maps Geocoding API
        if (
            fallback["geocoding_status"] == "DEFAULT_KOTA"
            and Settings.credential_status().get("google_maps_api_ready")
            and fallback["detected_location"] != "Kota Palembang (Umum)"
        ):
            gmaps_coords = self._geocode_via_google_maps(str(fallback["detected_location"]))
            if gmaps_coords:
                fallback["latitude"] = gmaps_coords["lat"]
                fallback["longitude"] = gmaps_coords["lon"]
                fallback["geocoding_status"] = "TERPETAKAN_GOOGLE_MAPS_API"

        return fallback

    def _geocode_via_google_maps(self, location_name: str) -> Optional[Dict[str, float]]:
        """Mencari koordinat (lat, lon) lokasi Palembang melalui Google Maps Geocoding API."""
        try:
            query = urllib.parse.quote(f"{location_name}, Palembang, Sumatera Selatan, Indonesia")
            url = (
                f"https://maps.googleapis.com/maps/api/geocode/json"
                f"?address={query}&key={Settings.GOOGLE_MAPS_API_KEY}"
            )
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            if data.get("status") == "OK" and data.get("results"):
                loc = data["results"][0]["geometry"]["location"]
                return {"lat": float(loc["lat"]), "lon": float(loc["lng"])}
        except Exception:
            return None
        return None
