#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


START_LENGTH_SCALE = 1.09
SENTENCE_SILENCE = 0.36


def skill_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def venv_python() -> Path:
    return skill_dir() / ".venv" / "bin" / "python"


def ffprobe_duration(path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=nw=1:nk=1",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return float(result.stdout.strip())


def run_piper(
    python_path: Path,
    model_path: Path,
    input_text: Path,
    output_wav: Path,
    length_scale: float,
    sentence_silence: float,
) -> None:
    cmd = [
        str(python_path),
        "-m",
        "piper",
        "-m",
        str(model_path),
        "-c",
        str(model_path.with_suffix(".onnx.json")),
        "-i",
        str(input_text),
        "-f",
        str(output_wav),
        "--length-scale",
        str(length_scale),
        "--sentence-silence",
        str(sentence_silence),
    ]
    subprocess.run(cmd, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the recovered Argentine property voiceover pipeline")
    parser.add_argument("--input-text", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--base-name", default="property-tour")
    parser.add_argument("--voice", default="es_AR-daniela-high")
    parser.add_argument("--video", type=Path)
    parser.add_argument("--tolerance-seconds", type=float, default=1.0)
    parser.add_argument("--max-passes", type=int, default=4)
    args = parser.parse_args()

    if shutil.which("ffprobe") is None:
        print("ffprobe is required.", file=sys.stderr)
        return 1

    python_path = venv_python()
    if not python_path.exists():
        print("Missing skill virtualenv. Run scripts/bootstrap.py first.", file=sys.stderr)
        return 1

    if not args.input_text.exists():
        print(f"Input text file not found: {args.input_text}", file=sys.stderr)
        return 1

    model_path = skill_dir() / "models" / f"{args.voice}.onnx"
    if not model_path.exists():
        print(f"Voice model not found: {model_path}", file=sys.stderr)
        print("Run scripts/bootstrap.py to download it.", file=sys.stderr)
        return 1

    args.output_dir.mkdir(parents=True, exist_ok=True)
    final_output = args.output_dir / f"{args.base_name}-video-final.wav"

    target_duration = None
    if args.video:
        if not args.video.exists():
            print(f"Video not found: {args.video}", file=sys.stderr)
            return 1
        target_duration = ffprobe_duration(args.video)
        print(f"video_duration={target_duration:.6f}")

    length_scale = START_LENGTH_SCALE
    best_duration = None
    previous_temp_output: Path | None = None
    for attempt in range(1, args.max_passes + 1):
        temp_output = args.output_dir / f"{args.base_name}-video-final-pass{attempt}.wav"
        run_piper(
            python_path=python_path,
            model_path=model_path,
            input_text=args.input_text,
            output_wav=temp_output,
            length_scale=length_scale,
            sentence_silence=SENTENCE_SILENCE,
        )
        best_duration = ffprobe_duration(temp_output)
        print(
            f"attempt={attempt} length_scale={length_scale:.6f} "
            f"sentence_silence={SENTENCE_SILENCE:.2f} duration={best_duration:.6f}"
        )

        if target_duration is None:
            temp_output.replace(final_output)
            print(final_output)
            return 0

        if abs(best_duration - target_duration) <= args.tolerance_seconds:
            temp_output.replace(final_output)
            print(final_output)
            return 0

        if previous_temp_output and previous_temp_output.exists():
            previous_temp_output.unlink()
        previous_temp_output = temp_output

        proposed_length = length_scale * (target_duration / best_duration)
        length_scale = min(max(proposed_length, 0.85), 1.35)

    if best_duration is None:
        print("Render failed before producing audio.", file=sys.stderr)
        return 1

    last_attempt = args.output_dir / f"{args.base_name}-video-final-pass{args.max_passes}.wav"
    if last_attempt.exists():
        last_attempt.replace(final_output)
    print(final_output)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
