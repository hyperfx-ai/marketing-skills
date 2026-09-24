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
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from seti.sandbox import call_tool

CUE_MAX_WORDS = 4
CUE_MAX_CHARS = 26
CUE_GAP_SECONDS = 0.6
CUE_MIN_SECONDS = 0.3
FONT_SIZE_DIVISOR = 20
SRT_CANVAS_HEIGHT = 288
MARGIN_BOTTOM_RATIO = 0.12
MARGIN_ABOVE_TEXT_RATIO = 0.19
WHISPER_USD_PER_MINUTE = 0.006
TRANSLATION_TIER = "fast"
TRANSLATION_USD_PER_1K_CHARS = 0.0025
TTS_MODEL = "gemini-3.8-flash-tts"
TEMPO_MIN = 0.9
TEMPO_MAX = 1.1
TTS_USD_PER_M_INPUT_TOKENS = 0.5
TTS_USD_PER_M_OUTPUT_TOKENS = 9.0
VOICE_CREATE_USD = 0.01
KARAOKE_HIGHLIGHT_COLOUR = "&H0000FFFF"
TTS_OUTPUT_TOKENS_PER_SECOND = 32
ESTIMATED_CHARS_PER_SECOND = 12
OMNI_MODEL = "gemini-omni-1.1-flash"
OMNI_MAX_PIECE_SECONDS = 10.0
OMNI_USD_PER_M_INPUT_TOKENS = 1.50
OMNI_USD_PER_M_VIDEO_OUTPUT_TOKENS = 17.50
OMNI_OUTPUT_TOKENS_PER_SECOND = {"360p": 1931, "720p": 5792}
OMNI_INPUT_TOKENS_PER_SECOND = 1771
STRIP_TEXT_SENTENCE = "Remove every piece of on-screen text and every caption, and do not add any text."
TIKTOK_MUSIC_POLICY_URL = "https://www.tiktok.com/legal/page/global/music-usage-confirmation/en"
TIKTOK_CAPTION_MAX_CHARS = 2200
TIKTOK_MIN_SECONDS = 3.0
TIKTOK_MIN_SHORT_SIDE = 720
TIKTOK_SAME_MINUTE_SPACING_S = 15
ANCHOR_SENTENCE = "The attached image is the previous part of this same video after the same edit: match its scene, furniture, lighting and colour grading exactly."

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


def plain_text(text: str) -> str:
    """Translated text with any JSON escape codes for letters turned back into the letters."""
    return re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), text)


def function_output(result: dict) -> dict:
    """The JSON an ai_functions_run call produced, or the error it reported."""
    first = (result.get("results") or [{}])[0]
    output = first.get("output_json")
    if output is None:
        raise RuntimeError(f"the translation function returned no JSON: {first.get('error') or result.get('error') or result}")
    return output


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
    texts = {item["i"]: plain_text(item["text"]) for item in function_output(result)["cues"]}
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


def has_edit(job: dict) -> bool:
    """An edit or an extension is asked for."""
    return bool(job.get("edit_instruction")) or int(job.get("extend_seconds") or 0) > 0


def is_extension(job: dict) -> bool:
    return int(job.get("extend_seconds") or 0) > 0


def captions_wanted(job: dict) -> bool:
    return job.get("captions", "yes") != "no"


def with_edited(edited: dict | None, ids: dict[str, str]) -> dict[str, str]:
    return {edited["name"]: edited["file_id"], **ids} if edited else ids


def edit_span(job: dict, probe: Probe) -> tuple[float, float]:
    """The seconds to edit: the whole clip, or the user's part."""
    part = str(job.get("edit_part") or "whole")
    if part == "whole":
        return (0.0, probe.duration_s)
    start, end = (float(value) for value in part.split("-", 1))
    if start < 0 or end <= start or end > probe.duration_s + 0.05:
        raise RuntimeError(f"edit_part {part} is outside the clip, which is {probe.duration_s:.1f} s long")
    return (start, min(end, probe.duration_s))


def edit_pieces(job: dict, probe: Probe) -> list[tuple[float, float]]:
    """The spans Omni edits, each at most 10 s: the whole clip or the user's part, cut into the fewest equal pieces."""
    if is_extension(job):
        return [(max(0.0, probe.duration_s - OMNI_MAX_PIECE_SECONDS), probe.duration_s)]
    start, end = edit_span(job, probe)
    count = max(1, math.ceil((end - start) / OMNI_MAX_PIECE_SECONDS - 1e-9))
    length = (end - start) / count
    return [(round(start + i * length, 3), round(start + (i + 1) * length, 3)) for i in range(count)]


def edit_resolution(job: dict, probe: Probe) -> str:
    """360p or 720p: the sheet's value, or auto from the clip's short side."""
    wanted = job.get("edit_resolution") or "auto"
    if wanted != "auto":
        return wanted
    return "720p" if min(probe.width, probe.height) >= 720 else "360p"


def aspect_ratio(probe: Probe) -> str:
    """9:16 or 16:9 from the clip; a square clip is refused."""
    if probe.width == probe.height:
        raise RuntimeError("Omni edits portrait (9:16) or landscape (16:9) clips only")
    return "9:16" if probe.height > probe.width else "16:9"


def edit_instruction(job: dict) -> str:
    """The text sent to Omni: the strip sentence or the extend prefix, then the user's words."""
    words = (job.get("edit_instruction") or "").strip()
    if is_extension(job):
        return f"Continue the scene for {int(job['extend_seconds'])} seconds. {words}".strip()
    if job.get("strip_text") == "yes":
        return f"{words} {STRIP_TEXT_SENTENCE}".strip()
    return words


def omni_usd(seconds: float, resolution: str) -> float:
    """Estimated dollars for one Omni call of that many output seconds."""
    output = seconds * OMNI_OUTPUT_TOKENS_PER_SECOND[resolution] * OMNI_USD_PER_M_VIDEO_OUTPUT_TOKENS
    inputs = seconds * OMNI_INPUT_TOKENS_PER_SECOND * OMNI_USD_PER_M_INPUT_TOKENS
    return (output + inputs) / 1_000_000


def edit_plan_lines(job: dict, probe: Probe) -> tuple[list[str], float]:
    """One plan line per Omni call and their total; sends nothing."""
    pieces = edit_pieces(job, probe)
    resolution = edit_resolution(job, probe)
    ratio = aspect_ratio(probe)
    text = edit_instruction(job)
    lines: list[str] = []
    total = 0.0
    for n, (start, end) in enumerate(pieces, start=1):
        seconds = int(job["extend_seconds"]) if is_extension(job) else end - start
        usd = omni_usd(seconds, resolution)
        what = f"extend by {seconds} s from the last {end - start:.1f} s" if is_extension(job) else f"edit piece {n} of {len(pieces)}, {end - start:.1f} s"
        lines.append(f"videos_edit ({OMNI_MODEL}) {what} at {resolution} {ratio}, about ${usd:.4f}, instruction: {text}")
        total += usd
    return lines, total


def probe_fps(path: Path) -> float:
    text = subprocess.run([ffmpeg_exe(), "-i", str(path)], capture_output=True, text=True).stderr
    for line in text.splitlines():
        if "Video:" in line:
            tokens = line.replace(",", " ").split()
            for token, following in zip(tokens, tokens[1:]):
                if following == "fps":
                    return float(token)
    return 24.0


def cut_piece(source: Path, span: tuple[float, float], target: Path) -> None:
    """Cut one span out of the source with a re-encode, frame-accurate."""
    ffmpeg("-i", str(source), "-ss", f"{span[0]:.3f}", "-to", f"{span[1]:.3f}", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", str(target))


def fitted(index: int, probe: Probe, fps: float, label: str) -> str:
    return f"[{index}:v]scale={probe.width}:{probe.height},fps={fps:g},setsar=1,setpts=PTS-STARTPTS[{label}]"


def assemble(source: Path, pieces: list[tuple[tuple[float, float], Path]], probe: Probe, target: Path) -> None:
    """Replace each span of the source with its edited piece at the source's size; the source's audio throughout."""
    fps = probe_fps(source)
    filters: list[str] = []
    labels: list[str] = []
    cursor = 0.0
    for n, ((start, end), _path) in enumerate(pieces, start=1):
        if start - cursor > 0.01:
            filters.append(f"[0:v]trim=start={cursor:.3f}:end={start:.3f},setpts=PTS-STARTPTS[s{n}]")
            labels.append(f"[s{n}]")
        filters.append(fitted(n, probe, fps, f"p{n}"))
        labels.append(f"[p{n}]")
        cursor = end
    if probe.duration_s - cursor > 0.01:
        filters.append(f"[0:v]trim=start={cursor:.3f},setpts=PTS-STARTPTS[tail]")
        labels.append("[tail]")
    filters.append(f"{''.join(labels)}concat=n={len(labels)}:v=1:a=0[v]")
    inputs: list[str] = ["-i", str(source)]
    for _span, path in pieces:
        inputs += ["-i", str(path)]
    ffmpeg(*inputs, "-filter_complex", ";".join(filters), "-map", "[v]", "-map", "0:a", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(target))


def append(source: Path, continuation: Path, probe: Probe, target: Path) -> None:
    """Append the continuation after the whole source at the source's size."""
    fps = probe_fps(source)
    filters = [
        "[0:v]setpts=PTS-STARTPTS[v0]",
        fitted(1, probe, fps, "v1"),
        "[v0][v1]concat=n=2:v=1:a=0[v]",
        "[0:a][1:a]concat=n=2:v=0:a=1[a]",
    ]
    ffmpeg("-i", str(source), "-i", str(continuation), "-filter_complex", ";".join(filters), "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", str(target))


def previous_ids(job: dict) -> list[str]:
    ids = job.get("previous_interaction_id") or []
    return [ids] if isinstance(ids, str) else list(ids)


async def land_piece(job: dict, out: Path, ledger: Path, n: int, span: tuple[float, float], whole: bool) -> str:
    """What Omni edits for piece n: the source itself, or the piece cut out and landed at a /files path."""
    if whole:
        return job["source_file_id"]
    piece = out / f"piece.{n}.mp4"
    await asyncio.to_thread(cut_piece, Path(job["source_path"]), span, piece)
    landed = await land(out, ledger, [piece.name], landing_folder(job))
    return landed[piece.name]


async def land_anchor(job: dict, out: Path, ledger: Path, edited_piece: Path, n: int) -> str:
    """Land the last frame of an edited piece so the next piece can be held to its scene."""
    anchor = out / f"anchor.{n}.png"
    duration = probe_clip(edited_piece).duration_s
    ffmpeg("-ss", f"{max(0.0, duration - 0.4):.2f}", "-i", str(edited_piece), "-frames:v", "1", str(anchor))
    landed = await land(out, ledger, [anchor.name], landing_folder(job))
    return landed[anchor.name]


async def edit(job: dict, out: Path, ledger: Path, probe: Probe) -> dict:
    """Run the edit or extension branch; return the edited clip's name, path, file id and interaction ids."""
    pieces = edit_pieces(job, probe)
    resolution = edit_resolution(job, probe)
    ratio = aspect_ratio(probe)
    text = edit_instruction(job)
    previous = previous_ids(job)
    if previous and len(previous) != len(pieces):
        raise RuntimeError(f"{len(previous)} previous interaction ids for {len(pieces)} pieces")
    whole = not is_extension(job) and pieces == [(0.0, probe.duration_s)]
    call_args = {"instruction": text, "resolution": resolution, "aspect_ratio": ratio}
    if previous:
        calls = [{**call_args, "previous_interaction_id": previous[n]} for n in range(len(pieces))]
    else:
        ids = await asyncio.gather(*(land_piece(job, out, ledger, n, span, whole) for n, span in enumerate(pieces, start=1)))
        calls = [{**call_args, "file_id": file_id} for file_id in ids]
    seconds = int(job["extend_seconds"]) if is_extension(job) else None
    results: list[dict] = []
    paths: list[Path] = []
    anchor_id: str | None = None
    for n, (span, args) in enumerate(zip(pieces, calls), start=1):
        if anchor_id:
            args = {**args, "instruction": f"{text} {ANCHOR_SENTENCE}", "reference_image_file_id": anchor_id}
        result = await run_stage(ledger, "edit", call_tool("videos_edit", **args), output=f"omni.{n}.mp4", usd=omni_usd(seconds or (span[1] - span[0]), resolution))
        path = out / f"omni.{n}.mp4"
        await run_stage(ledger, "fetch", call_tool("files_copy_to_sandbox", sources=[result["file_id"]], destination=str(path)), output=path.name, usd=0.0)
        results.append(result)
        paths.append(path)
        if n < len(pieces):
            anchor_id = await land_anchor(job, out, ledger, path, n)
    name = "extended.mp4" if is_extension(job) else "edited.mp4"
    if is_extension(job):
        await asyncio.to_thread(append, Path(job["source_path"]), paths[0], probe, out / name)
    else:
        await asyncio.to_thread(assemble, Path(job["source_path"]), list(zip(pieces, paths)), probe, out / name)
    first = pieces[0]
    check_frame(out / name, Cue(0, first[0], first[1], ""), out / "check.edit.png")
    landed = await land(out, ledger, [name], landing_folder(job))
    return {"name": name, "path": str(out / name), "file_id": landed[name], "interaction_ids": [result["interaction_id"] for result in results]}


def output_names(spoken: str, target: str | None, *, dub: str | None = None) -> list[str]:
    names = []
    for lang in [dub] if dub else [spoken, *([target] if target else [])]:
        names += [f"final.{lang}.mp4", f"captions.{lang}.srt", f"check.{lang}.png"]
    return names


def tiktok_wanted(job: dict) -> bool:
    return job.get("delivery") == "tiktok"


# TODO(HYP-1607 chunk 4): contract stubs; the build fills them in.
# spec: hq/projects/hyper/workspace/specs/2026-09-24-video-editing-tiktok.md, Design § The plan and § The run
# tests: tests/test_video_editing_tiktok.py
def tiktok_slots(job: dict) -> list[tuple[str, str]]:
    """UTC run times with the display zone, one per slot, spaced within a minute; raises on a past time."""
    raise NotImplementedError


def ai_label(job: dict) -> bool:
    raise NotImplementedError


def post_file(job: dict, names: list[str]) -> str:
    raise NotImplementedError


def tiktok_plan_lines(job: dict, probe: Probe) -> list[str]:
    raise NotImplementedError


async def deliver(job: dict, ledger: Path, ids: dict[str, str]) -> list:
    raise NotImplementedError


def tts_usd(duration_s: float, chars: int) -> float:
    tokens_in = chars / 4
    tokens_out = duration_s * TTS_OUTPUT_TOKENS_PER_SECOND
    return (tokens_in * TTS_USD_PER_M_INPUT_TOKENS + tokens_out * TTS_USD_PER_M_OUTPUT_TOKENS) / 1_000_000


def render_plan(job: dict, probe: Probe) -> str:
    """Render every call the run would make, one line each, with a total line. Sends nothing."""
    if not probe.has_audio:
        raise RuntimeError("the clip has no audio track, so there is nothing to caption")
    spoken = language_code(job.get("spoken_language") or "auto")
    spoken_name = "<spoken>" if spoken == "auto" else spoken
    dub = dub_language(job)
    target = None if dub else target_language(job)
    lines: list[str] = []
    total = 0.0
    if has_edit(job):
        lines, total = edit_plan_lines(job, probe)
    if not captions_wanted(job):
        lines.append("files_copy_from_sandbox for 2 outputs into files: $0")
        if tiktok_wanted(job):
            lines += tiktok_plan_lines(job, probe)
        numbered = [f"{n}. {line}" for n, line in enumerate(lines, start=1)]
        return "\n".join([*numbered, f"Total: ${total:.4f}"])
    lines.append(
        f"audio_words_transcribe (whisper-1) on {probe.duration_s:.1f} s of audio, "
        f"billed per started minute: ${whisper_usd(probe.duration_s):.4f}"
    )
    total += whisper_usd(probe.duration_s)
    if dub:
        dub_lines, dub_usd = dub_plan_lines(job, probe)
        lines += dub_lines
        total += dub_usd
    elif target:
        chars = round(probe.duration_s * ESTIMATED_CHARS_PER_SECOND)
        lines.append(
            f"ai_functions_run ({TRANSLATION_TIER}) translating the cues to {target}, "
            f"priced from about {chars} characters of text: ${translation_usd(probe.duration_s):.4f}"
        )
        total += translation_usd(probe.duration_s)
    for lang in [dub] if dub else [spoken_name, *([target] if target else [])]:
        lines.append(
            f"ffmpeg burn of captions.{lang}.srt into final.{lang}.mp4 "
            f"({job.get('caption_style', 'plain')}, {job.get('caption_position', 'bottom')}) "
            f"and one check frame check.{lang}.png: $0"
        )
    lines.append(f"files_copy_from_sandbox for {len(output_names(spoken_name, target, dub=dub)) + int(has_edit(job))} outputs into files: $0")
    if tiktok_wanted(job):
        lines += tiktok_plan_lines(job, probe)
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
    """Burn subtitles; an ASS file carries its own style, an SRT gets one sized for libass's 288-pixel canvas."""
    if subs.suffix == ".ass":
        ffmpeg("-i", str(source), "-vf", f"subtitles='{subs.as_posix()}'", "-c:a", "copy", str(target))
        return
    canvas = SRT_CANVAS_HEIGHT / probe.height
    font_size = max(4, round(probe.height / FONT_SIZE_DIVISOR * canvas))
    ratio = MARGIN_ABOVE_TEXT_RATIO if position == "above_text" else MARGIN_BOTTOM_RATIO
    style = (
        f"FontName=DejaVu Sans,FontSize={font_size},PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,"
        f"Outline=1,Bold=1,Alignment=2,MarginV={round(SRT_CANVAS_HEIGHT * ratio)},MarginL=8,MarginR=8"
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


def picture_path(job: dict) -> Path:
    return Path(job.get("dubbed_path") or job.get("edited_path") or job["source_path"])


def caption_language_sync(job: dict, out: Path, lang: str, cues: list[Cue], probe: Probe, words: list[dict] | None = None) -> None:
    write_srt(cues, out / f"captions.{lang}.srt")
    subs = out / f"captions.{lang}.srt"
    if job.get("caption_style") == "karaoke":
        subs = out / f"captions.{lang}.ass"
        write_ass(cues, words or [], subs, probe, job.get("caption_position", "bottom"))
    burn(picture_path(job), subs, out / f"final.{lang}.mp4", probe, job.get("caption_position", "bottom"))
    check_frame(out / f"final.{lang}.mp4", cues[0], out / f"check.{lang}.png")


async def caption_language(job: dict, out: Path, ledger: Path, lang: str, cues: list[Cue], probe: Probe, words: list[dict] | None = None) -> None:
    await run_stage(ledger, "burn", asyncio.to_thread(caption_language_sync, job, out, lang, cues, probe, words), output=f"final.{lang}.mp4", usd=0.0)


def dub_language(job: dict) -> str | None:
    wanted = job.get("dub")
    return None if not wanted or wanted == "none" else language_code(wanted)


def dub_plan_lines(job: dict, probe: Probe) -> tuple[list[str], float]:
    """The plan's lines for a dub: the voice to create when none is named, the translation with its budget, the speech, the second words pass."""
    target = dub_language(job)
    chars = round(probe.duration_s * ESTIMATED_CHARS_PER_SECOND)
    voice = job.get("voice") or "designed"
    lines = []
    usd = 0.0
    if voice in ("designed", "replicated"):
        lines.append(f"voices_create ({TTS_MODEL}) a {voice} voice from the clip's speaker, saved under /files/voices: ${VOICE_CREATE_USD:.4f}")
        usd += VOICE_CREATE_USD
    lines.append(
        f"ai_functions_run ({TRANSLATION_TIER}) translating the transcript to {target} to be spoken in "
        f"about {probe.duration_s:.1f} s, about {chars} characters: ${translation_usd(probe.duration_s):.4f}"
    )
    usd += translation_usd(probe.duration_s)
    lines.append(f"voices_speak ({TTS_MODEL}) in voice {voice}, priced from about {chars} characters at the vendor's token rate: ${tts_usd(probe.duration_s, chars):.4f}")
    usd += tts_usd(probe.duration_s, chars)
    lines.append(f"audio_words_transcribe (whisper-1) on the dubbed {probe.duration_s:.1f} s, billed per started minute: ${whisper_usd(probe.duration_s):.4f}")
    usd += whisper_usd(probe.duration_s)
    return lines, usd


async def ensure_voice(job: dict, ledger: Path) -> str:
    """Return the voice name to speak in, creating a designed voice from the clip when none is named."""
    voice = job.get("voice") or "designed"
    if voice not in ("designed", "replicated"):
        return voice
    name = job.get("voice_name") or f"{voice}-{Path(job['source_file_id']).stem}"
    record = await run_stage(
        ledger,
        "voice",
        call_tool(
            "voices_create",
            file_id=job["source_file_id"],
            name=name,
            voice_type=voice,
            consent_file_id=job.get("consent_file_id"),
        ),
        usd=VOICE_CREATE_USD,
    )
    return record["name"]


def target_spoken_length(words: list[dict], probe: Probe) -> tuple[float, int]:
    """Speech seconds of the source and the character budget for a translation spoken in that time."""
    speech_s = words[-1]["end"] - words[0]["start"] if words else probe.duration_s
    if speech_s <= 0:
        speech_s = probe.duration_s
    text = " ".join(w["word"].strip() for w in words)
    chars_per_second = len(text) / speech_s
    return speech_s, round(speech_s * chars_per_second)


async def translate_transcript(text: str, target_language: str, budget_chars: int) -> str:
    """One ai_functions_run call for a natural translation spoken in about budget_chars characters."""
    result = await call_tool(
        "ai_functions_run",
        instructions=(
            f"Translate the transcript into {target_language} as natural spoken language, keeping the "
            f"meaning and tone, in about {budget_chars} characters so that it is spoken in the same time "
            "as the original."
        ),
        input={"transcript": text},
        output_json_schema={"type": "object", "properties": {"transcript": {"type": "string"}}, "required": ["transcript"]},
        performance=TRANSLATION_TIER,
    )
    return plain_text(function_output(result)["transcript"])


async def fetch_audio(file_id: str, target: Path) -> None:
    """Copy the spoken audio into the sandbox; patched in tests."""
    await call_tool("files_copy_to_sandbox", sources=[file_id], destination=str(target))


async def speak(transcript: str, voice: str, target: Path) -> Path:
    """voices_speak through the bridge, the audio fetched to target."""
    spoken = await call_tool("voices_speak", text=transcript, voice=voice)
    await fetch_audio(spoken["file_id"], target)
    return target


def fit_audio(speech: Path, target_s: float, out: Path) -> tuple[Path, float]:
    """Tempo-fit the speech to target_s within the band; return the fitted file and the ratio applied."""
    ratio = probe_clip(speech).duration_s / target_s
    filters = []
    remaining = ratio
    while remaining < 0.5:
        filters.append("atempo=0.5")
        remaining /= 0.5
    while remaining > 2.0:
        filters.append("atempo=2.0")
        remaining /= 2.0
    filters.append(f"atempo={remaining:.4f}")
    ffmpeg("-i", str(speech), "-filter:a", ",".join(filters), "-c:a", "pcm_s16le", str(out))
    return out, ratio


def swap_audio(source: Path, fitted: Path, target: Path) -> None:
    """The source picture with the fitted speech as its only audio track."""
    ffmpeg("-i", str(source), "-i", str(fitted), "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-shortest", str(target))


def write_ass(cues: list[Cue], words: list[dict], path: Path, probe: Probe, position: str) -> None:
    """Karaoke subtitles: one dialogue line per cue, one highlight per word."""
    font_size = max(12, round(probe.height / FONT_SIZE_DIVISOR))
    ratio = MARGIN_ABOVE_TEXT_RATIO if position == "above_text" else MARGIN_BOTTOM_RATIO
    margin_v = round(probe.height * ratio)
    header = [
        "[Script Info]",
        "ScriptType: v4.00+",
        f"PlayResX: {probe.width}",
        f"PlayResY: {probe.height}",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: Karaoke,DejaVu Sans,{font_size},{KARAOKE_HIGHLIGHT_COLOUR},&H00FFFFFF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,2,0,2,20,20,{margin_v},1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    lines = []
    position_in_words = 0
    for cue in cues:
        count = len(cue.text.split())
        cue_words = words[position_in_words:position_in_words + count]
        position_in_words += count
        lines.append(f"Dialogue: 0,{ass_time(cue.start)},{ass_time(cue.end)},Karaoke,,0,0,0,,{karaoke_text(cue, cue_words)}")
    path.write_text("\n".join(header + lines) + "\n", encoding="utf-8")


def ass_time(seconds: float) -> str:
    centis = int(round(max(seconds, 0) * 100))
    h, rem = divmod(centis, 360_000)
    m, rem = divmod(rem, 6_000)
    s, cs = divmod(rem, 100)
    return f"{h}:{m:02}:{s:02}.{cs:02}"


def karaoke_text(cue: Cue, cue_words: list[dict]) -> str:
    total = int(round((cue.end - cue.start) * 100))
    parts = []
    spent = 0
    for index, word in enumerate(cue_words):
        if index == len(cue_words) - 1:
            centis = total - spent
        else:
            centis = int(round((cue_words[index + 1]["start"] - word["start"]) * 100))
            centis = max(1, min(centis, total - spent - (len(cue_words) - index - 1)))
        spent += centis
        parts.append(f"{{\\k{centis}}}{word['word'].strip()}")
    return " ".join(parts)


async def dub(job: dict, out: Path, ledger: Path, probe: Probe, transcribed: dict) -> dict:
    """Translate, speak, fit, swap, then transcribe the dubbed track; returns the dub's language, words and path."""
    target = dub_language(job)
    words = transcribed["words"]
    voice = await ensure_voice(job, ledger)
    text = " ".join(w["word"].strip() for w in words)
    speech_s, budget = target_spoken_length(words, probe)
    lead_in_s = words[0]["start"] if words else 0.0
    transcript = await run_stage(ledger, "translate", translate_transcript(text, target, budget), usd=translation_usd(probe.duration_s))
    speech = await run_stage(ledger, "speak", speak(transcript, voice, out / f"speech.{target}.wav"), usd=tts_usd(probe.duration_s, len(transcript)))
    ratio = probe_clip(speech).duration_s / speech_s
    if not TEMPO_MIN <= ratio <= TEMPO_MAX:
        budget = round(budget / ratio)
        transcript = await run_stage(ledger, "translate", translate_transcript(text, target, budget), usd=translation_usd(probe.duration_s), retry=True)
        speech = await run_stage(ledger, "speak", speak(transcript, voice, out / f"speech.{target}.wav"), usd=tts_usd(probe.duration_s, len(transcript)), retry=True)
        ratio = probe_clip(speech).duration_s / speech_s
    (out / f"transcript.{target}.txt").write_text(transcript, encoding="utf-8")
    fitted, applied = fit_audio(speech, speech_s, out / f"speech.{target}.fit.wav")
    note(ledger, "fit", "done", ratio=round(applied, 4), in_band=TEMPO_MIN <= applied <= TEMPO_MAX, usd=0.0)
    dubbed = out / f"dubbed.{target}.mp4"
    delayed = out / f"speech.{target}.delayed.wav"
    ffmpeg("-i", str(fitted), "-af", f"adelay={int(lead_in_s * 1000)}:all=1,apad=whole_dur={probe.duration_s}", "-c:a", "pcm_s16le", str(delayed))
    swap_audio(picture_path(job), delayed, dubbed)
    landed = await land(out, ledger, [dubbed.name], landing_folder(job))
    second = await run_stage(ledger, "words", call_tool("audio_words_transcribe", file_id=landed[dubbed.name], language=target), usd=whisper_usd(probe.duration_s))
    (out / f"words.{target}.json").write_text(json.dumps(second["words"], ensure_ascii=False, indent=1), encoding="utf-8")
    return {"language": target, "words": second["words"], "path": str(dubbed)}


async def transcribe(job: dict, out: Path, ledger: Path, probe: Probe) -> dict:
    spoken = job.get("spoken_language") or "auto"
    words = await run_stage(
        ledger,
        "words",
        call_tool("audio_words_transcribe", file_id=job.get("words_file_id") or job["source_file_id"], language=None if spoken == "auto" else spoken),
        usd=whisper_usd(probe.duration_s),
    )
    lang = language_code(words["language"]) if spoken == "auto" else language_code(spoken)
    (out / f"words.{lang}.json").write_text(json.dumps(words["words"], ensure_ascii=False, indent=1), encoding="utf-8")
    return {"language": lang, "words": words["words"]}


async def run(job: dict, out: Path) -> dict:
    """Run the job; output names mapped to their /files paths, one folder per run, plus the TikTok posts when asked."""
    ids = await produce(job, out)
    if tiktok_wanted(job):
        ids["tiktok"] = await deliver(job, out / "ledger.jsonl", ids)
    return ids


async def produce(job: dict, out: Path) -> dict[str, str]:
    """Make and land every output; return output names mapped to their /files paths."""
    out.mkdir(parents=True, exist_ok=True)
    ledger = out / "ledger.jsonl"
    ensure_ffmpeg()
    probe = probe_clip(Path(job["source_path"]))
    if not probe.has_audio:
        raise RuntimeError("the clip has no audio track, so there is nothing to caption")
    edited: dict | None = None
    edit_task = asyncio.create_task(edit(job, out, ledger, probe)) if has_edit(job) else None
    if edit_task and (is_extension(job) or not captions_wanted(job)):
        edited = await edit_task
        job["edited_path"], job["interaction_ids"] = edited["path"], edited["interaction_ids"]
        if not captions_wanted(job):
            return with_edited(edited, await land(out, ledger, ["check.edit.png"], landing_folder(job)))
        job["words_file_id"] = edited["file_id"]
    transcribed = await transcribe(job, out, ledger, probe)
    if edit_task and edited is None:
        edited = await edit_task
        job["edited_path"], job["interaction_ids"] = edited["path"], edited["interaction_ids"]
    if dub_language(job):
        dubbed = await dub(job, out, ledger, probe, transcribed)
        job["dubbed_path"] = dubbed["path"]
        cues = group_words_into_cues(dubbed["words"])
        await caption_language(job, out, ledger, dubbed["language"], cues, probe, dubbed["words"])
        return with_edited(edited, await land(out, ledger, output_names(dubbed["language"], None, dub=dubbed["language"]), landing_folder(job)))
    spoken = transcribed["language"]
    cues = group_words_into_cues(transcribed["words"])
    if not cues:
        raise RuntimeError("Whisper found no words in the clip")
    target = target_language({**job, "spoken_language": spoken})
    source_captions = caption_language(job, out, ledger, spoken, cues, probe, transcribed["words"])
    if target:
        translation = run_stage(ledger, "translate", translate_cues(cues, target), usd=translation_usd(probe.duration_s))
        translated, _ = await asyncio.gather(translation, source_captions)
        await caption_language(job, out, ledger, target, translated, probe, transcribed["words"])
    else:
        await source_captions
    return with_edited(edited, await land(out, ledger, output_names(spoken, target), landing_folder(job)))


def landing_folder(job: dict) -> str:
    """The run's folder, chosen once per job."""
    return job.setdefault("run_folder", run_folder(job))


def run_folder(job: dict) -> str:
    """Where this run's outputs land: /files/video-editing/<clip>-<time>, so runs never overwrite each other."""
    clip = Path(job["source_file_id"]).stem if "/" in job["source_file_id"] else job["source_file_id"]
    return f"/files/video-editing/{clip}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"


async def land(out: Path, ledger: Path, names: list[str], folder: str) -> dict[str, str]:
    ids: dict[str, str] = {}
    for name in names:
        await run_stage(ledger, "land", call_tool("files_copy_from_sandbox", sources=[str(out / name)], destination=f"{folder}/{name}"), output=name, usd=0.0)
        ids[name] = f"{folder}/{name}"
    return ids


def main(argv: list[str]) -> int:
    mode, job_path = argv[0], Path(argv[1])
    job = json.loads(job_path.read_text(encoding="utf-8"))
    source = str(job.get("source_file_id") or "")
    if not source or (source.startswith("/") and not source.startswith("/files/")):
        print(
            "source_file_id must be the attachment's file id or its /files path from files_list; "
            f"never the sandbox copy (got {source!r})",
            file=sys.stderr,
        )
        return 2
    if mode == "plan":
        print(render_plan(job, probe_clip(Path(job["source_path"]))))
        return 0
    if mode == "run":
        result = asyncio.run(run(job, (job_path.parent / "out").resolve()))
        print(json.dumps(result))
        return 0
    print(f"unknown mode {mode}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
