import json
from config.settings import Settings
from src.jurnal_1_nlp.pipeline_jurnal1 import PipelineJurnal1


def main() -> None:
    print("=" * 75)
    print("EKSEKUSI PIPELINE JURNAL 1 (SENTIMEN INDOBERT/LLM & TOPIC MODELING BERTOPIC)")
    print("=" * 75)
    print("Status Kredensial Saat Ini:", json.dumps(Settings.credential_status(), indent=2))

    pipeline = PipelineJurnal1()
    summary = pipeline.run()

    print("\n[SUKSES] Ringkasan Hasil Jurnal 1:")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
