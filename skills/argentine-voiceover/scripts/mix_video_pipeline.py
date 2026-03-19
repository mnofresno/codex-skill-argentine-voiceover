#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


MIXED_FILTER = (
    "[0:a]volume=0.24[bg];"
    "[1:a]volume=1.55,highpass=f=110,lowpass=f=8500,"
    "acompressor=threshold=-18dB:ratio=2.2:attack=15:release=180[narr];"
    "[bg][narr]sidechaincompress=threshold=0.015:ratio=10:attack=12:release=280:makeup=1[ducked];"
    "[ducked][narr]amix=inputs=2:weights='1 1':normalize=0,alimiter=limit=0.93[aout]"
)

VOICE_UP_FILTER = (
    "[0:a]volume=0.08,aresample=44100[bg];"
    "[1:a]volume=3.2,highpass=f=120,lowpass=f=9000,"
    "acompressor=threshold=-24dB:ratio=3:attack=10:release=120,"
    "aresample=44100,pan=stereo|c0=c0|c1=c0[vox];"
    "[bg][vox]amix=inputs=2:weights='1 1':normalize=0,alimiter=limit=0.90[aout]"
)


def run_mix(video: Path, voiceover: Path, output: Path, filter_complex: str) -> None:
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(video),
        "-i",
        str(voiceover),
        "-filter_complex",
        filter_complex,
        "-map",
        "0:v",
        "-map",
        "[aout]",
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-shortest",
        str(output),
    ]
    subprocess.run(cmd, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the recovered ffmpeg mix pipeline")
    parser.add_argument("--video", required=True, type=Path)
    parser.add_argument("--voiceover", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--base-name", default=None)
    args = parser.parse_args()

    if shutil.which("ffmpeg") is None:
        print("ffmpeg is required.", file=sys.stderr)
        return 1

    if not args.video.exists():
        print(f"Video not found: {args.video}", file=sys.stderr)
        return 1
    if not args.voiceover.exists():
        print(f"Voiceover not found: {args.voiceover}", file=sys.stderr)
        return 1

    args.output_dir.mkdir(parents=True, exist_ok=True)
    base_name = args.base_name or args.video.stem
    mixed_output = args.output_dir / f"{base_name}_mixed.mp4"
    voice_up_output = args.output_dir / f"{base_name}_mixed_voice_up.mp4"

    run_mix(args.video, args.voiceover, mixed_output, MIXED_FILTER)
    run_mix(args.video, args.voiceover, voice_up_output, VOICE_UP_FILTER)

    print(mixed_output)
    print(voice_up_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
