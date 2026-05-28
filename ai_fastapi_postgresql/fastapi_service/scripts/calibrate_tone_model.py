import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.pronunciation_model import evaluate_audio_tone_segment
from app.tone_calibration import build_calibration_from_error_samples, reset_tone_calibration_cache


def main() -> None:
    args = parse_args()
    database_url = args.database_url or os.getenv("DATABASE_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL is required. Pass --database-url or export DATABASE_URL.")

    output_path = Path(args.output).resolve()
    samples_path = Path(args.samples_output).resolve()
    project_root = Path(__file__).resolve().parents[3]
    media_root = Path(args.media_root).resolve() if args.media_root else project_root / "backend_node"

    os.environ["TONE_CALIBRATION_PATH"] = str(output_path.with_suffix(".neutral.json"))
    reset_tone_calibration_cache()

    rows = fetch_tone_annotations(database_url)
    samples = collect_error_samples(rows=rows, media_root=media_root)
    calibration = build_calibration_from_error_samples(samples)
    calibration.update(
        {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_annotation_count": len(rows),
            "media_root": str(media_root),
        }
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    samples_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(calibration, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    samples_path.write_text(json.dumps(samples, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "calibration": str(output_path),
                "samples": str(samples_path),
                "source_annotation_count": len(rows),
                "calibration_sample_count": len(samples),
                "score_bias_by_expected_tone": calibration["score_bias_by_expected_tone"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def parse_args() -> argparse.Namespace:
    default_models_dir = Path(__file__).resolve().parents[1] / "models"
    parser = argparse.ArgumentParser(description="Calibrate tone scoring from corpus_annotation rows.")
    parser.add_argument("--database-url", default=None)
    parser.add_argument("--media-root", default=None, help="Directory that contains the /uploads path.")
    parser.add_argument("--output", default=str(default_models_dir / "tone_calibration.json"))
    parser.add_argument("--samples-output", default=str(default_models_dir / "tone_calibration_samples.json"))
    return parser.parse_args()


def fetch_tone_annotations(database_url: str) -> list[dict[str, Any]]:
    try:
        import psycopg
        from psycopg.rows import dict_row
    except ModuleNotFoundError as error:
        raise SystemExit("Install dependencies first: python -m pip install -r requirements.txt") from error

    query = """
        SELECT
            ca.id AS annotation_id,
            ca.practice_record_id,
            ca.error_type,
            ca.start_ms,
            ca.end_ms,
            ci.hanzi,
            ci.pinyin,
            ci.item_type,
            aa.storage_path
        FROM corpus_annotation ca
        JOIN practice_record pr ON pr.id = ca.practice_record_id
        JOIN corpus_item ci ON ci.id = pr.corpus_item_id
        LEFT JOIN audio_asset aa ON aa.id = pr.learner_audio_id
        WHERE ca.error_type = 'tone'
          AND ca.start_ms IS NOT NULL
          AND ca.end_ms IS NOT NULL
          AND aa.storage_path IS NOT NULL
        ORDER BY ca.created_at ASC
    """
    with psycopg.connect(database_url, row_factory=dict_row) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            return list(cursor.fetchall())


def collect_error_samples(*, rows: list[dict[str, Any]], media_root: Path) -> list[dict[str, Any]]:
    samples: list[dict[str, Any]] = []
    for row in rows:
        audio_path = media_root / str(row["storage_path"]).lstrip("/")
        if not audio_path.exists():
            continue
        audio_content = audio_path.read_bytes()
        result = evaluate_audio_tone_segment(
            audio_content=audio_content,
            corpus_type=row["item_type"],
            hanzi=row["hanzi"],
            pinyin=row["pinyin"],
        )
        annotation_start = int(row["start_ms"])
        annotation_end = int(row["end_ms"])
        for segment in result.syllable_analysis:
            overlap_ms = _overlap_ms(annotation_start, annotation_end, segment.start_ms, segment.end_ms)
            segment_duration = max(1, segment.end_ms - segment.start_ms)
            if overlap_ms < 80 and overlap_ms / segment_duration < 0.25:
                continue
            sample = segment.model_dump()
            sample.update(
                {
                    "annotation_id": str(row["annotation_id"]),
                    "practice_record_id": str(row["practice_record_id"]),
                    "annotation_start_ms": annotation_start,
                    "annotation_end_ms": annotation_end,
                    "overlap_ms": overlap_ms,
                    "hanzi_full": row["hanzi"],
                    "pinyin_full": row["pinyin"],
                    "audio_path": str(audio_path),
                }
            )
            samples.append(sample)
    return samples


def _overlap_ms(first_start: int, first_end: int, second_start: int, second_end: int) -> int:
    return max(0, min(first_end, second_end) - max(first_start, second_start))


if __name__ == "__main__":
    main()
