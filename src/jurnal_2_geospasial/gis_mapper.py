import json
import math
from pathlib import Path
from typing import Dict, List


class GISMapperJurnal2:
    """
    Generator Peta Interaktif Hotspot Keluhan Sampah Kota Palembang (Jurnal 2).
    Kompatibel 100% baik saat dibuka langsung di Browser (Chrome/Edge) maupun
    saat di-render langsung di dalam sel Google Colab menggunakan IPython.display.HTML.
    """

    COLOR_MAP = {
        "TINGGI_KRITIS": "#dc2626",  # Merah Kritis
        "SEDANG": "#f59e0b",         # Oranye/Kuning Sedang
        "RENDAH": "#16a34a",         # Hijau Rendah
    }

    @classmethod
    def generate_interactive_map(cls, records: List[Dict[str, object]], output_html_path: Path) -> Path:
        """Membuat file HTML peta interaktif titik keluhan sampah Kota Palembang."""
        output_html_path.parent.mkdir(parents=True, exist_ok=True)

        markers_data: List[Dict[str, object]] = []
        for idx, row in enumerate(records, start=1):
            base_lat = float(row.get("latitude", -2.9761))  # type: ignore
            base_lon = float(row.get("longitude", 104.7754))  # type: ignore

            # Tambahkan sebaran mikro (spatial jitter ~50-250 meter) agar 360 titik
            # tidak menumpuk di satu piksel yang sama dan terlihat jelas di peta
            angle = idx * 2.39996  # Golden angle dalam radian
            radius_deg = 0.0004 * math.sqrt(idx % 35)
            lat = round(base_lat + radius_deg * math.cos(angle), 6)
            lon = round(base_lon + radius_deg * math.sin(angle), 6)

            level = str(row.get("urgency_level", "RENDAH"))
            score = int(row.get("urgency_score", 20))  # type: ignore
            color = cls.COLOR_MAP.get(level, "#2563eb")

            markers_data.append(
                {
                    "lat": lat,
                    "lon": lon,
                    "color": color,
                    "score": score,
                    "id": str(row.get("id", idx)),
                    "platform": f"{row.get('platform', '')} ({row.get('source_account', '')})",
                    "username": str(row.get("username", "")),
                    "tanggal": str(row.get("timestamp", "")),
                    "lokasi": str(row.get("detected_location", "")),
                    "kecamatan": str(row.get("kecamatan", "")),
                    "urgensi": f"{level} (Skor: {score}/100)",
                    "sla": str(row.get("sla_target", "")),
                    "keluhan": str(row.get("normalized_text", "")),
                    "real_comment": str(row.get("real_comment", "")),
                    "tindakan": str(row.get("recommended_action", "")),
                    "profile_url": str(row.get("profile_url", "")),
                    "post_url": str(row.get("post_url", "")),
                }
            )

        markers_json = json.dumps(markers_data, ensure_ascii=False)
        html_content = f"""<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <title>Peta GIS Hotspot Keluhan Sampah Kota Palembang (Jurnal 2)</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="referrer" content="no-referrer-when-downgrade">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <style>
        .palembang-map-wrapper {{ margin: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; border: 1px solid #cbd5e1; border-radius: 8px; overflow: hidden; }}
        #palembang-header {{ background: #0f172a; color: #fff; padding: 12px 20px; display: flex; justify-content: space-between; align-items: center; }}
        #palembang-header h2 {{ margin: 0; font-size: 17px; color: #fff; }}
        #palembang-map {{ height: 600px; min-height: 600px; width: 100%; background: #e2e8f0; }}
        .legend-plg {{ background: white; color: #0f172a; padding: 12px 14px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.2); font-size: 13px; line-height: 22px; }}
        .dot-plg {{ display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 6px; vertical-align: middle; }}
    </style>
</head>
<body style="margin:0;">
    <div class="palembang-map-wrapper">
        <div id="palembang-header">
            <h2>Peta Spasial & Tingkat Urgensi Keluhan Sampah Kota Palembang (Jurnal 2)</h2>
            <span>Total Titik Laporan: {len(records)} (2017–2026)</span>
        </div>
        <div id="palembang-map"></div>
    </div>
    <script>
        (function() {{
            function initPalembangMap() {{
                var container = document.getElementById('palembang-map');
                if (!container) return;
                if (container._leaflet_id) {{
                    container._leaflet_id = null;
                    container.innerHTML = '';
                }}

                var petaJalan = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
                    maxZoom: 19,
                    attribution: 'Tiles &copy; Esri World Street Map | Riset Smart Environment Palembang'
                }});

                var petaJurnalTerang = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
                    maxZoom: 19,
                    attribution: 'Tiles &copy; Esri World Topo Map'
                }});

                var petaOsmHot = L.tileLayer('https://{{s}}.tile.openstreetmap.fr/hot/{{z}}/{{x}}/{{y}}.png', {{
                    maxZoom: 19,
                    attribution: '&copy; OpenStreetMap contributors, Tiles style by HOT'
                }});

                var petaSatelit = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
                    maxZoom: 18,
                    attribution: 'Tiles &copy; Esri World Imagery'
                }});

                var map = L.map(container, {{
                    center: [-2.9761, 104.7650],
                    zoom: 12,
                    layers: [petaJalan]
                }});

                var baseMaps = {{
                    "Peta Jalan Utama (Esri Street Map)": petaJalan,
                    "Peta Topografi & Jalan (Esri Topo)": petaJurnalTerang,
                    "Peta OpenStreetMap (OSM HOT)": petaOsmHot,
                    "Citra Satelit (Esri Imagery)": petaSatelit
                }};
                L.control.layers(baseMaps, null, {{position: 'topright'}}).addTo(map);

                var points = {markers_json};
                for (var i = 0; i < points.length; i++) {{
                    var info = points[i];
                    var radius = Math.max(6, Math.min(13, info.score / 8));
                    var circle = L.circleMarker([info.lat, info.lon], {{
                        radius: radius,
                        fillColor: info.color,
                        color: '#0f172a',
                        weight: 1.2,
                        opacity: 0.95,
                        fillOpacity: 0.82
                    }}).addTo(map);

                    var realCommentRow = info.real_comment ? ("<b>Komentar Asli (" + info.username + "):</b> <span style='color:#1e40af;'>&quot;" + info.real_comment + "&quot;</span><br><br>") : "";
                    var popupHtml = "<div style='min-width:275px;font-size:13px;color:#0f172a;'>" +
                               "<b>Lokasi:</b> " + info.lokasi + " (" + info.kecamatan + ")<br>" +
                               "<b>Postingan Sumber:</b> " + info.platform + "<br>" +
                               "<b>Akun Pengomentar:</b> <a href='" + info.profile_url + "' target='_blank' rel='noopener noreferrer'><b>" + info.username + "</b></a><br>" +
                               "<b>Waktu:</b> " + info.tanggal + " | <a href='" + info.post_url + "' target='_blank' rel='noopener noreferrer'><b>Lihat Postingan &amp; Komentar</b></a><br>" +
                               "<b>Tingkat Urgensi:</b> <span style='color:" + info.color + ";font-weight:bold;'>" + info.urgensi + "</span><br>" +
                               "<b>Target SLA:</b> " + info.sla + "<br><hr style='margin:6px 0;'>" +
                               realCommentRow +
                               "<b>Konteks Laporan Spasial:</b> <i>&quot;" + info.keluhan + "&quot;</i><br><br>" +
                               "<b>Rekomendasi AI:</b> " + info.tindakan + "</div>";
                    circle.bindPopup(popupHtml);
                }}

                var legend = L.control({{position: 'bottomright'}});
                legend.onAdd = function () {{
                    var div = L.DomUtil.create('div', 'legend-plg');
                    div.innerHTML = "<b>Tingkat Urgensi Penanganan (DLHK)</b><br>" +
                                    "<span class='dot-plg' style='background:#dc2626'></span>Tinggi / Kritis (Rawan Banjir/Macet)<br>" +
                                    "<span class='dot-plg' style='background:#f59e0b'></span>Sedang (TPS Penuh / Telat Angkut)<br>" +
                                    "<span class='dot-plg' style='background:#16a34a'></span>Rendah (Edukasi / Terkendali)";
                    return div;
                }};
                legend.addTo(map);

                setTimeout(function() {{ map.invalidateSize(); }}, 250);
                setTimeout(function() {{ map.invalidateSize(); }}, 800);
            }}

            if (typeof window.L !== 'undefined') {{
                initPalembangMap();
            }} else {{
                var script = document.createElement('script');
                script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
                script.onload = initPalembangMap;
                document.head.appendChild(script);
            }}
        }})();
    </script>
</body>
</html>
"""
        output_html_path.write_text(html_content, encoding="utf-8")
        return output_html_path
