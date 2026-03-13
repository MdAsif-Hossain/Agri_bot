"""
ASR evaluation: WER/CER from local audio manifest.

Loads eval/datasets/asr_manifest.jsonl with local audio paths and
reference transcriptions, runs STT, computes Word Error Rate and
Character Error Rate.

Usage:
    python -m eval.eval_asr --dataset eval/datasets/asr_manifest.jsonl --output eval/results/asr.json
    python -m eval.eval_asr --smoke  # CI-safe mock mode
"""

import json
import argparse
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _get_git_sha() -> str:
    """Get current git commit SHA, or 'unknown'."""
    try:
        import subprocess
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT),
        )
        return result.stdout.strip()[:12] if result.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


def _wer(reference: str, hypothesis: str) -> float:
    """Compute Word Error Rate (Levenshtein on words)."""
    ref_words = reference.strip().lower().split()
    hyp_words = hypothesis.strip().lower().split()

    if not ref_words:
        return 0.0 if not hyp_words else 1.0

    # Dynamic programming
    d = [[0] * (len(hyp_words) + 1) for _ in range(len(ref_words) + 1)]
    for i in range(len(ref_words) + 1):
        d[i][0] = i
    for j in range(len(hyp_words) + 1):
        d[0][j] = j

    for i in range(1, len(ref_words) + 1):
        for j in range(1, len(hyp_words) + 1):
            cost = 0 if ref_words[i - 1] == hyp_words[j - 1] else 1
            d[i][j] = min(
                d[i - 1][j] + 1,      # deletion
                d[i][j - 1] + 1,      # insertion
                d[i - 1][j - 1] + cost,  # substitution
            )

    return d[len(ref_words)][len(hyp_words)] / len(ref_words)


def _cer(reference: str, hypothesis: str) -> float:
    """Compute Character Error Rate (Levenshtein on chars)."""
    ref_chars = list(reference.strip().lower())
    hyp_chars = list(hypothesis.strip().lower())

    if not ref_chars:
        return 0.0 if not hyp_chars else 1.0

    d = [[0] * (len(hyp_chars) + 1) for _ in range(len(ref_chars) + 1)]
    for i in range(len(ref_chars) + 1):
        d[i][0] = i
    for j in range(len(hyp_chars) + 1):
        d[0][j] = j

    for i in range(1, len(ref_chars) + 1):
        for j in range(1, len(hyp_chars) + 1):
            cost = 0 if ref_chars[i - 1] == hyp_chars[j - 1] else 1
            d[i][j] = min(
                d[i - 1][j] + 1,
                d[i][j - 1] + 1,
                d[i - 1][j - 1] + cost,
            )

    return d[len(ref_chars)][len(hyp_chars)] / len(ref_chars)


def evaluate_asr_smoke() -> dict:
    """CI-safe smoke test with mock STT (no models/audio needed)."""
    mock_pairs = [
        ("ধানের রোগ কি", "ধানের রোগ কি"),
        ("rice blast disease", "rice blast disease"),
        ("বীজ বপন সময়", "বীজ বপন সময়ে"),
    ]

    per_sample = []
    for ref, hyp in mock_pairs:
        per_sample.append({
            "reference": ref,
            "hypothesis": hyp,
            "wer": round(_wer(ref, hyp), 4),
            "cer": round(_cer(ref, hyp), 4),
        })

    wers = [s["wer"] for s in per_sample]
    cers = [s["cer"] for s in per_sample]

    return _build_result(
        metrics={"avg_wer": sum(wers) / len(wers), "avg_cer": sum(cers) / len(cers)},
        counts={"n_samples": len(per_sample), "perfect_wer": sum(1 for w in wers if w == 0)},
        per_sample=per_sample,
        notes=["smoke_test", "mock_transcriptions"],
    )


def evaluate_asr(dataset_path: str) -> dict:
    """Run ASR eval with actual STT on local audio files."""
    dataset = Path(dataset_path)
    entries = [json.loads(line) for line in dataset.read_text(encoding="utf-8").strip().split("\n")]

    from config import settings
    from agribot.voice.stt import get_stt
    from agribot.voice.audio_preprocess import preprocess_audio

    stt = get_stt(
        model_size=settings.WHISPER_MODEL_SIZE, device="cpu",
        beam_size=settings.WHISPER_BEAM_SIZE,
    )

    per_sample = []
    skipped = 0

    for entry in entries:
        audio_path = Path(entry["audio_path"])
        ref_text = entry.get("reference_text_bn", "") or entry.get("reference_text_en", "")

        if not audio_path.exists():
            skipped += 1
            continue

        try:
            canonical, _ = preprocess_audio(str(audio_path), max_duration_s=120)
            result = stt.transcribe(str(canonical))
            hyp_text = result["text"]
            canonical.unlink(missing_ok=True)
        except Exception as e:
            per_sample.append({"reference": ref_text, "hypothesis": "", "error": str(e), "wer": 1.0, "cer": 1.0})
            continue

        per_sample.append({
            "reference": ref_text,
            "hypothesis": hyp_text,
            "wer": round(_wer(ref_text, hyp_text), 4),
            "cer": round(_cer(ref_text, hyp_text), 4),
            "confidence": result.get("confidence", 0),
            "language": result.get("language", ""),
        })

    wers = [s["wer"] for s in per_sample]
    cers = [s["cer"] for s in per_sample]

    return _build_result(
        metrics={
            "avg_wer": sum(wers) / len(wers) if wers else 0,
            "avg_cer": sum(cers) / len(cers) if cers else 0,
        },
        counts={
            "n_samples": len(per_sample),
            "skipped": skipped,
            "perfect_wer": sum(1 for w in wers if w == 0),
        },
        per_sample=per_sample,
        notes=[f"skipped {skipped} missing audio files"] if skipped else [],
    )


def _build_result(metrics: dict, counts: dict, per_sample: list, notes: list) -> dict:
    """Build standardized eval result JSON."""
    return {
        "run_id": str(uuid.uuid4())[:8],
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_sha": _get_git_sha(),
        "config_snapshot": {
            "whisper_model": "base",
            "beam_size": 5,
        },
        "metrics": metrics,
        "counts": counts,
        "per_sample": per_sample,
        "notes": notes,
    }


def main():
    parser = argparse.ArgumentParser(description="Evaluate ASR (WER/CER)")
    parser.add_argument("--dataset", default="eval/datasets/asr_manifest.jsonl")
    parser.add_argument("--output", default="eval/results/asr.json")
    parser.add_argument("--smoke", action="store_true", help="CI-safe smoke test")
    args = parser.parse_args()

    if args.smoke:
        results = evaluate_asr_smoke()
    else:
        results = evaluate_asr(args.dataset)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\n🎤 ASR Results ({results['counts']['n_samples']} samples):")
    for k, v in results["metrics"].items():
        print(f"   {k}: {v:.4f}")
    print(f"\n   Saved to: {output_path}")


if __name__ == "__main__":
    main()
