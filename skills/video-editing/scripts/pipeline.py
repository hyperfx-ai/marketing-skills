"""Video-editing pipeline for the Hyper sandbox: captions and translated captions.

Runs inside the user's sandbox. Provider calls go through the sandbox tool bridge
(`call_tool`); ffmpeg does the cutting, burning and frame capture locally.

    python pipeline.py plan job.json      # print every call the run would make, send nothing
    python pipeline.py run job.json       # run it; every output is landed in /files with an id

The job is the settings sheet the skill fills in. `plan` and `run` read the same file, so what
the user approved is what executes.
"""

from __future__ import annotations

import asyncio
import json
import sys
from dataclasses import dataclass
from pathlib import Path

from seti.sandbox import call_tool

CUE_MAX_WORDS = 4
CUE_MAX_CHARS = 26
CUE_GAP_SECONDS = 0.6
CUE_MIN_SECONDS = 0.3
FONT_SIZE_DIVISOR = 34
MARGIN_BOTTOM_RATIO = 0.12
MARGIN_ABOVE_TEXT_RATIO = 0.19
WHISPER_USD_PER_MINUTE = 0.006


@dataclass
class Probe:
    duration_s: float
    width: int
    height: int
    has_audio: bool


@dataclass
class Cue:
    index: int
    start: float
    end: float
    text: str


def group_words_into_cues(
    words: list[dict],
    *,
    max_words: int = CUE_MAX_WORDS,
    max_chars: int = CUE_MAX_CHARS,
    gap_s: float = CUE_GAP_SECONDS,
) -> list[Cue]:
    """Group timed words into short caption cues that follow the speech."""
    # TODO spec: hq/projects/hyper/workspace/specs/2026-09-24-video-editing-captions.md § Design (cue grouping)
    # TODO tests: tests/test_video_editing_pipeline.py
    raise NotImplementedError


async def translate_cues(cues: list[Cue], target_language: str) -> list[Cue]:
    """Translate cue text through ai_functions_run, keeping every index and timing."""
    # TODO spec: hq/projects/hyper/workspace/specs/2026-09-24-video-editing-captions.md § Design (the run)
    # TODO tests: tests/test_video_editing_pipeline.py
    raise NotImplementedError


def probe_clip(path: Path) -> Probe:
    """Read duration, size and audio presence with ffmpeg."""
    # TODO spec: hq/projects/hyper/workspace/specs/2026-09-24-video-editing-captions.md § Design (the plan)
    # TODO tests: tests/test_video_editing_pipeline.py
    raise NotImplementedError


def render_plan(job: dict, probe: Probe) -> str:
    """Render every call the run would make, one line each, with a total line. Sends nothing."""
    # TODO spec: hq/projects/hyper/workspace/specs/2026-09-24-video-editing-captions.md § Design (the plan)
    # TODO tests: tests/test_video_editing_pipeline.py
    raise NotImplementedError


async def run(job: dict, out: Path) -> dict[str, str]:
    """Run the job; return output names mapped to their file ids in /files."""
    # TODO spec: hq/projects/hyper/workspace/specs/2026-09-24-video-editing-captions.md § Design (the run)
    # TODO tests: tests/test_video_editing_pipeline.py
    raise NotImplementedError


def main(argv: list[str]) -> int:
    mode, job_path = argv[0], Path(argv[1])
    job = json.loads(job_path.read_text(encoding="utf-8"))
    if mode == "plan":
        print(render_plan(job, probe_clip(Path(job["source_path"]))))
        return 0
    if mode == "run":
        result = asyncio.run(run(job, job_path.parent / "out"))
        print(json.dumps(result))
        return 0
    print(f"unknown mode {mode}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
