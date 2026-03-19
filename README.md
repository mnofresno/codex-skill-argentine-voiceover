# Codex Skill: Argentine Voiceover

`argentine-voiceover` is a Codex skill for generating Spanish voiceovers with an Argentine voice using Piper, then mixing that narration into a video with the same historical pipeline that was used on `LINIERS 2500_slow_mixed_voice_up.mp4`.

This repo packages the historical workflow recovered from Codex logs on `2026-03-12`, but collapses the multi-variant trial process into a single intelligent renderer: it starts from the same final Piper preset that was chosen in that session and adjusts `length-scale` against the target video duration until the narration fits well.

## What It Does

- Bootstraps a local Python virtualenv for Piper.
- Downloads the `es_AR-daniela-medium` and `es_AR-daniela-high` voice assets on demand.
- Renders narration from a `.txt` file to `.wav` with the original Piper settings.
- Measures the target video duration and converges on a synced final narration with Piper.
- Produces `mixed` and `mixed_voice_up` MP4 outputs with the original `ffmpeg` mix recipes.

## Repo Layout

```text
skills/
  argentine-voiceover/
    SKILL.md
    agents/openai.yaml
    scripts/
```

## Prerequisites

- `python3`
- `ffmpeg`

On macOS with Homebrew:

```bash
brew install ffmpeg
```

## Install In Codex

From the local Codex helper:

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo mnofresno/codex-skill-argentine-voiceover \
  --path skills/argentine-voiceover
```

Then restart Codex.

## Manual Workflow

Bootstrap the runtime and download the voice assets:

```bash
python3 skills/argentine-voiceover/scripts/bootstrap.py
```

Render the synced final narration:

```bash
python3 skills/argentine-voiceover/scripts/render_property_pipeline.py \
  --input-text skills/argentine-voiceover/assets/examples/property-tour.txt \
  --output-dir output/tts \
  --video "LINIERS 2500_slow.mp4"
```

Create the exact video mix outputs:

```bash
python3 skills/argentine-voiceover/scripts/mix_video_pipeline.py \
  --video "LINIERS 2500_slow.mp4" \
  --voiceover output/tts/property-tour-video-final.wav \
  --output-dir output/video
```

## Notes

- The skill defaults to `es_AR-daniela-high` because that is the voice used in the final historical pipeline.
- The intelligent renderer seeds from the final historical preset:
  - `--length-scale 1.09`
  - `--sentence-silence 0.36`
- Then it probes the target video duration and adjusts `length-scale` until the narration lands within tolerance.
- The bootstrap script installs `piper-tts` and `pathvalidate`, matching what was needed in this environment.
