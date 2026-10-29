import json
from config.settings import Settings
from src.jurnal_2_geospasial.pipeline_jurnal2 import PipelineJurnal2


def main() -> None:
    print("=" * 75)
    print("EKSEKUSI PIPELINE JURNAL 2 (NER GEOSPASIAL, SKOR URGENSI & PETA GIS PALEMBANG)")
    print("=" * 75)
    print("Status Kredensial Saat Ini:", json.dumps(Settings.credential_status(), indent=2))

    pipeline = PipelineJurnal2()
    summary = pipeline.run()

    print("\n[SUKSES] Ringkasan Hasil Jurnal 2:")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
