---
name: argentine-voiceover
description: Generate local Spanish voiceovers with an Argentine voice using the exact historical Piper-plus-ffmpeg workflow used to create LINIERS 2500_slow_mixed_voice_up.mp4. Use this when the user wants the same Argentine female narration pipeline for a real-estate walkthrough or similar narrated promo video.
---

# Argentine Voiceover

## Overview

This skill turns text into Argentine Spanish narration with Piper and reproduces the same real-estate video pipeline recovered from Codex logs, but with an intelligent sync step so it can choose the right final duration without hardcoding multiple fixed WAV variants.

Default voice: `es_AR-daniela-high`.

## When To Use It

- The user wants the same pipeline previously used for the house walkthrough video.
- The user wants an Argentine female narrator voice from Piper.
- The user has a property-tour script and wants the same final-style narration, but synced intelligently to the current target video.
- The user wants the final `mixed` and `mixed_voice_up` MP4s created with the original mix filters.

## Workflow

1. Bootstrap the runtime:
   Run `scripts/bootstrap.py` to create `.venv`, install Piper dependencies, and download the exact Piper voice assets used in the original workflow.
2. Render the final narration:
   Run `scripts/render_property_pipeline.py`. It starts from the historical final preset and adjusts `length-scale` based on the target video duration.
3. Inspect durations:
   The render script prints the target video duration, the attempts it made, and the final WAV duration.
4. Produce the final assets:
   Run `scripts/mix_video_pipeline.py` to create the exact `mixed` and `mixed_voice_up` MP4 outputs with the original `ffmpeg` filter graphs.

## Operational Rules

- Prefer the bundled scripts over improvising new filter graphs.
- Keep the text in a UTF-8 `.txt` file and render from that file.
- If the voice model is missing, run `scripts/bootstrap.py`.
- If `ffmpeg` is missing, stop and say the skill requires it.
- The original pipeline used Piper regeneration, not `ffmpeg atempo`, to approach the target duration.
- Seed from the recovered final preset: `length-scale 1.09`, `sentence-silence 0.36`.
- Preserve the original mix filters unless the user explicitly asks to change them.

## Commands

Bootstrap:

```bash
python3 scripts/bootstrap.py
```

Render the synced final WAV:

```bash
python3 scripts/render_property_pipeline.py \
  --input-text assets/examples/property-tour.txt \
  --output-dir output/tts \
  --video "/path/to/video.mp4"
```

Mix back into video with the recovered filters:

```bash
python3 scripts/mix_video_pipeline.py \
  --video "/path/to/video.mp4" \
  --voiceover output/tts/property-tour-video-final.wav \
  --output-dir output/video
```

## Resources

### scripts/

- `bootstrap.py`: creates the venv, installs runtime dependencies, downloads the exact Piper assets used in the historical pipeline.
- `render_property_pipeline.py`: starts from the historical final Piper preset and adjusts against the target video duration until it converges.
- `mix_video_pipeline.py`: reproduces the original `mixed` and `mixed_voice_up` ffmpeg recipes.

### assets/

- `assets/examples/property-tour.txt`: example narration text for a property walkthrough.
