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
import math
import shutil
import subprocess
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
TRANSLATION_TIER = "fast"
TRANSLATION_USD_PER_1K_CHARS = 0.0025
ESTIMATED_CHARS_PER_SECOND = 12

LANGUAGE_CODES = {
    "english": "en",
    "spanish": "es",
    "french": "fr",
    "german": "de",
    "italian": "it",
    "portuguese": "pt",
    "dutch": "nl",
    "japanese": "ja",
    "korean": "ko",
    "chinese": "zh",
    "arabic": "ar",
    "hindi": "hi",
}

TRANSLATION_SCHEMA = {
    "type": "object",
    "properties": {
        "cues": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"i": {"type": "integer"}, "text": {"type": "string"}},
                "required": ["i", "text"],
            },
        }
    },
    "required": ["cues"],
}


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


def language_code(name: str) -> str:
    """Whisper names languages ("english"); outputs are named by ISO code ("en")."""
    return LANGUAGE_CODES.get(name.strip().lower(), name.strip().lower())


def target_language(job: dict) -> str | None:
    """The second caption language, or None when the job wants captions in the spoken one."""
    wanted = language_code(job.get("caption_language") or "")
    spoken = language_code(job.get("spoken_language") or "auto")
    if job.get("outputs") != "both" or not wanted or wanted == spoken:
        return None
    return wanted


def split_into_groups(words: list[dict], max_words: int, max_chars: int, gap_s: float) -> list[list[dict]]:
    groups: list[list[dict]] = []
    current: list[dict] = []
    for word in words:
        text = " ".join(w["word"].strip() for w in [*current, word])
        gap = word["start"] - current[-1]["end"] if current else 0.0
        too_long = len(current) >= max_words or len(text) > max_chars
        if current and (too_long or gap > gap_s):
            groups.append(current)
            current = []
        current.append(word)
    if current:
        groups.append(current)
    return groups


def group_words_into_cues(
    words: list[dict],
    *,
    max_words: int = CUE_MAX_WORDS,
    max_chars: int = CUE_MAX_CHARS,
    gap_s: float = CUE_GAP_SECONDS,
) -> list[Cue]:
    """Group timed words into short caption cues that follow the speech."""
    cues: list[Cue] = []
    for index, group in enumerate(split_into_groups(words, max_words, max_chars, gap_s), start=1):
        start = group[0]["start"]
        end = max(group[-1]["end"], start + CUE_MIN_SECONDS)
        cues.append(Cue(index, start, end, " ".join(w["word"].strip() for w in group)))
    for cue, following in zip(cues, cues[1:]):
        cue.end = min(cue.end, following.start)
    return cues


async def translate_cues(cues: list[Cue], target_language: str) -> list[Cue]:
    """Translate cue text through ai_functions_run, keeping every index and timing."""
    result = await call_tool(
        "ai_functions_run",
        instructions=(
            f"Translate the text of every cue into {target_language}. Keep each cue's i, keep the "
            "count and the order, and keep each translation short enough to read as a caption "
            "in the same time as the original."
        ),
        input={"cues": [{"i": cue.index, "text": cue.text} for cue in cues]},
        output_json_schema=TRANSLATION_SCHEMA,
        performance=TRANSLATION_TIER,
    )
    texts = {item["i"]: item["text"] for item in result["results"][0]["output_json"]["cues"]}
    return [Cue(cue.index, cue.start, cue.end, texts[cue.index]) for cue in cues]


def ffmpeg_exe() -> str:
    found = shutil.which("ffmpeg")
    if found:
        return found
    import imageio_ffmpeg

    return imageio_ffmpeg.get_ffmpeg_exe()


def ensure_ffmpeg() -> str:
    try:
        return ffmpeg_exe()
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "imageio-ffmpeg"], check=True)
        return ffmpeg_exe()


def ffmpeg(*args: str) -> None:
    proc = subprocess.run([ffmpeg_exe(), "-y", "-loglevel", "error", *args], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {proc.stderr[-1500:]}")


def probe_clip(path: Path) -> Probe:
    """Read duration, size and audio presence with ffmpeg."""
    text = subprocess.run([ffmpeg_exe(), "-i", str(path)], capture_output=True, text=True).stderr
    duration, width, height, has_audio = 0.0, 0, 0, False
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("Duration:"):
            h, m, s = line.split()[1].rstrip(",").split(":")
            duration = int(h) * 3600 + int(m) * 60 + float(s)
        if "Video:" in line:
            for token in line.replace(",", " ").split():
                if "x" in token and token.replace("x", "").isdigit():
                    width, height = (int(part) for part in token.split("x"))
        if "Audio:" in line:
            has_audio = True
    if duration <= 0:
        raise RuntimeError(f"ffmpeg found no duration for {path}")
    return Probe(duration, width, height, has_audio)


def whisper_usd(duration_s: float) -> float:
    return max(1, math.ceil(duration_s / 60)) * WHISPER_USD_PER_MINUTE


def translation_usd(duration_s: float) -> float:
    return duration_s * ESTIMATED_CHARS_PER_SECOND / 1000 * TRANSLATION_USD_PER_1K_CHARS


def output_names(spoken: str, target: str | None) -> list[str]:
    names = []
    for lang in [spoken, *([target] if target else [])]:
        names += [f"final.{lang}.mp4", f"captions.{lang}.srt", f"check.{lang}.png"]
    return names


def render_plan(job: dict, probe: Probe) -> str:
    """Render every call the run would make, one line each, with a total line. Sends nothing."""
    if not probe.has_audio:
        raise RuntimeError("the clip has no audio track, so there is nothing to caption")
    spoken = language_code(job.get("spoken_language") or "auto")
    spoken_name = "<spoken>" if spoken == "auto" else spoken
    target = target_language(job)
    lines = [
        f"audio_words_transcribe (whisper-1) on {probe.duration_s:.1f} s of audio, "
        f"billed per started minute: ${whisper_usd(probe.duration_s):.4f}"
    ]
    total = whisper_usd(probe.duration_s)
    if target:
        chars = round(probe.duration_s * ESTIMATED_CHARS_PER_SECOND)
        lines.append(
            f"ai_functions_run ({TRANSLATION_TIER}) translating the cues to {target}, "
            f"priced from about {chars} characters of text: ${translation_usd(probe.duration_s):.4f}"
        )
        total += translation_usd(probe.duration_s)
    for lang in [spoken_name, *([target] if target else [])]:
        lines.append(
            f"ffmpeg burn of captions.{lang}.srt into final.{lang}.mp4 "
            f"({job.get('caption_style', 'plain')}, {job.get('caption_position', 'bottom')}) "
            f"and one check frame check.{lang}.png: $0"
        )
    lines.append(f"sandbox_download_file for {len(output_names(spoken_name, target))} outputs into files: $0")
    numbered = [f"{n}. {line}" for n, line in enumerate(lines, start=1)]
    return "\n".join([*numbered, f"Total: ${total:.4f}"])


def srt_time(seconds: float) -> str:
    total_ms = int(round(max(seconds, 0) * 1000))
    h, rem = divmod(total_ms, 3_600_000)
    m, rem = divmod(rem, 60_000)
    s, ms = divmod(rem, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def write_srt(cues: list[Cue], path: Path) -> None:
    blocks = [f"{cue.index}\n{srt_time(cue.start)} --> {srt_time(cue.end)}\n{cue.text}\n" for cue in cues]
    path.write_text("\n".join(blocks), encoding="utf-8")


def burn(source: Path, subs: Path, target: Path, probe: Probe, position: str) -> None:
    font_size = max(12, round(probe.height / FONT_SIZE_DIVISOR))
    ratio = MARGIN_ABOVE_TEXT_RATIO if position == "above_text" else MARGIN_BOTTOM_RATIO
    style = (
        f"FontName=DejaVu Sans,FontSize={font_size},PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,"
        f"Outline=2,Bold=1,Alignment=2,MarginV={round(probe.height * ratio)},MarginL=20,MarginR=20"
    )
    ffmpeg("-i", str(source), "-vf", f"subtitles='{subs.as_posix()}':force_style='{style}'", "-c:a", "copy", str(target))


def check_frame(video: Path, cue: Cue, target: Path) -> None:
    ffmpeg("-ss", f"{(cue.start + cue.end) / 2:.2f}", "-i", str(video), "-frames:v", "1", str(target))


def note(ledger: Path, stage: str, status: str, **fields) -> None:
    with ledger.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"stage": stage, "status": status, **fields}) + "\n")


async def run_stage(ledger: Path, stage: str, work, **fields):
    """Await `work` between a started and a done ledger line; a failure is named and re-raised."""
    note(ledger, stage, "started", **fields)
    try:
        result = await work
    except Exception as error:
        note(ledger, stage, "failed", error=str(error), **fields)
        raise RuntimeError(f"stage {stage} failed on {fields.get('output', stage)}: {error}") from error
    note(ledger, stage, "done", **fields)
    return result


def caption_language_sync(job: dict, out: Path, lang: str, cues: list[Cue], probe: Probe) -> None:
    write_srt(cues, out / f"captions.{lang}.srt")
    burn(Path(job["source_path"]), out / f"captions.{lang}.srt", out / f"final.{lang}.mp4", probe, job.get("caption_position", "bottom"))
    check_frame(out / f"final.{lang}.mp4", cues[0], out / f"check.{lang}.png")


async def caption_language(job: dict, out: Path, ledger: Path, lang: str, cues: list[Cue], probe: Probe) -> None:
    await run_stage(ledger, "burn", asyncio.to_thread(caption_language_sync, job, out, lang, cues, probe), output=f"final.{lang}.mp4", usd=0.0)


async def transcribe(job: dict, out: Path, ledger: Path, probe: Probe) -> dict:
    spoken = job.get("spoken_language") or "auto"
    words = await run_stage(
        ledger,
        "words",
        call_tool("audio_words_transcribe", file_id=job["source_file_id"], language=None if spoken == "auto" else spoken),
        usd=whisper_usd(probe.duration_s),
    )
    lang = language_code(words["language"]) if spoken == "auto" else language_code(spoken)
    (out / f"words.{lang}.json").write_text(json.dumps(words["words"], ensure_ascii=False, indent=1), encoding="utf-8")
    return {"language": lang, "words": words["words"]}


async def run(job: dict, out: Path) -> dict[str, str]:
    """Run the job; return output names mapped to their file ids in /files."""
    out.mkdir(parents=True, exist_ok=True)
    ledger = out / "ledger.jsonl"
    ensure_ffmpeg()
    probe = probe_clip(Path(job["source_path"]))
    if not probe.has_audio:
        raise RuntimeError("the clip has no audio track, so there is nothing to caption")
    transcribed = await transcribe(job, out, ledger, probe)
    spoken = transcribed["language"]
    cues = group_words_into_cues(transcribed["words"])
    if not cues:
        raise RuntimeError("Whisper found no words in the clip")
    target = target_language({**job, "spoken_language": spoken})
    source_captions = caption_language(job, out, ledger, spoken, cues, probe)
    if target:
        translation = run_stage(ledger, "translate", translate_cues(cues, target), usd=translation_usd(probe.duration_s))
        translated, _ = await asyncio.gather(translation, source_captions)
        await caption_language(job, out, ledger, target, translated, probe)
    else:
        await source_captions
    ids: dict[str, str] = {}
    for name in output_names(spoken, target):
        landed = await run_stage(ledger, "land", call_tool("sandbox_download_file", path=str(out / name)), output=name, usd=0.0)
        ids[name] = landed["file_id"]
    return ids


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
