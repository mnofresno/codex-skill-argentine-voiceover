#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import venv
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen


VOICE_URLS = {
    "es_AR-daniela-medium": [
        "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_AR/daniela/medium/es_AR-daniela-medium.onnx",
        "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_AR/daniela/medium/es_AR-daniela-medium.onnx.json",
    ],
    "es_AR-daniela-high": [
        "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_AR/daniela/high/es_AR-daniela-high.onnx",
        "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_AR/daniela/high/es_AR-daniela-high.onnx.json",
    ],
}


def skill_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def venv_python_path(skill_root: Path) -> Path:
    return skill_root / ".venv" / "bin" / "python"


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def ensure_venv(skill_root: Path) -> Path:
    python_path = venv_python_path(skill_root)
    if python_path.exists():
        return python_path

    venv.EnvBuilder(with_pip=True).create(skill_root / ".venv")
    return python_path


def install_requirements(python_path: Path, skill_root: Path) -> None:
    requirements = skill_root / "scripts" / "requirements.txt"
    run([str(python_path), "-m", "pip", "install", "-r", str(requirements)])


def download_file(url: str, destination: Path, force_redownload: bool, required: bool) -> None:
    if destination.exists() and destination.stat().st_size > 0 and not force_redownload:
        return
    try:
        with urlopen(url) as response, open(destination, "wb") as out:
            out.write(response.read())
    except HTTPError:
        if required:
            raise


def ensure_voice(skill_root: Path, voice: str, force_redownload: bool) -> None:
    model_dir = skill_root / "models"
    model_dir.mkdir(parents=True, exist_ok=True)
    voices = [("es_AR-daniela-medium", False), (voice, True)]
    for voice_name, required in voices:
        urls = VOICE_URLS.get(voice_name)
        if not urls:
            if required:
                raise ValueError(f"No download URLs configured for {voice_name}")
            continue
        for url in urls:
            destination = model_dir / Path(url).name
            download_file(url, destination, force_redownload, required)


def main() -> int:
    parser = argparse.ArgumentParser(description="Bootstrap Argentine Voiceover skill")
    parser.add_argument("--voice", default="es_AR-daniela-high")
    parser.add_argument("--force-redownload", action="store_true")
    args = parser.parse_args()

    if shutil.which("ffmpeg") is None:
        print("ffmpeg is required but was not found in PATH.", file=sys.stderr)
        return 1

    root = skill_dir()
    python_path = ensure_venv(root)
    install_requirements(python_path, root)
    ensure_voice(root, args.voice, args.force_redownload)

    print(f"Bootstrap complete.")
    print(f"Skill dir: {root}")
    print(f"Python: {python_path}")
    print(f"Voices: es_AR-daniela-medium, {args.voice}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
