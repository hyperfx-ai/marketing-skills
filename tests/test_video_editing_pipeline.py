"""The video-editing pipeline script: cues, translation, plan and run, with no provider.

Spec: hq/projects/hyper/workspace/specs/2026-09-24-video-editing-captions.md (chunk 1) and
2026-09-24-video-editing-voice.md (chunk 2): one test per piece of the pipeline, input and output only.
"""

import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/video-editing/scripts/pipeline.py"
WORDS = json.loads((ROOT / "tests/fixtures/words_en_dental.json").read_text(encoding="utf-8"))
WORDS_ES = json.loads((ROOT / "tests/fixtures/words_es_dental.json").read_text(encoding="utf-8"))
TRANSCRIPT_ES = "Lo pospuse por dos años esperando en listas de espera. Llamé a Northgate y me atendieron esa misma semana."


class FakeBridge:
    """Stands in for seti.sandbox.call_tool: canned answers, every call recorded."""

    def __init__(self, speak_seconds=None):
        self.calls: list[tuple[str, dict]] = []
        self.speak_seconds = list(speak_seconds or [])

    async def __call__(self, tool_name, **kwargs):
        self.calls.append((tool_name, kwargs))
        if tool_name == "audio_words_transcribe":
            if "dubbed" in str(kwargs.get("file_id", "")):
                return {"file_id": kwargs.get("file_id"), "language": "spanish", "duration_s": 8.0, "words": WORDS_ES}
            return {"file_id": kwargs.get("file_id"), "language": "en", "duration_s": 8.0, "words": WORDS}
        if tool_name == "voices_create":
            return {"name": kwargs["name"], "voice_id": "voice_fake", "voice_type": "designed"}
        if tool_name == "voices_speak":
            seconds = self.speak_seconds.pop(0) if self.speak_seconds else 3.0
            return {"file_id": f"file_speech_{seconds}", "audio_url": "", "duration_s": seconds, "voice": kwargs["voice"]}
        if tool_name == "ai_functions_run" and "transcript" in kwargs["input"]:
            return {"success": True, "results": [{"success": True, "output_json": {"transcript": TRANSCRIPT_ES}}]}
        if tool_name == "ai_functions_run":
            items = kwargs["input"]["cues"]
            texts = [f"[{item['i']}] traducido" for item in items]
            return {
                "success": True,
                "results": [{"success": True, "output_json": {"cues": [{"i": item["i"], "text": text} for item, text in zip(items, texts)]}}],
            }
        if tool_name == "files_copy_from_sandbox":
            return f"Copied {kwargs['sources'][0]} -> {kwargs['destination']}"
        raise AssertionError(f"unexpected tool {tool_name}")


def load_pipeline(bridge):
    sandbox = types.ModuleType("seti.sandbox")
    sandbox.call_tool = bridge
    spec = importlib.util.spec_from_file_location("pipeline", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {"seti": types.ModuleType("seti"), "seti.sandbox": sandbox, "pipeline": module}):
        spec.loader.exec_module(module)
    return module


def ffmpeg_exe() -> str:
    import imageio_ffmpeg

    return imageio_ffmpeg.get_ffmpeg_exe()


def make_fixture_clip(path: Path, seconds: int = 3) -> None:
    subprocess.run(
        [
            ffmpeg_exe(), "-y", "-loglevel", "error",
            "-f", "lavfi", "-i", f"testsrc=size=360x640:rate=24:duration={seconds}",
            "-f", "lavfi", "-i", f"sine=frequency=440:duration={seconds}",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(path),
        ],
        check=True,
    )


def job_for(clip: Path, *, caption_language="es", outputs="both", dub="none", voice="designed", caption_style="plain") -> dict:
    return {
        "source_file_id": "file_source",
        "source_path": str(clip),
        "spoken_language": "auto",
        "caption_language": caption_language,
        "caption_style": caption_style,
        "caption_position": "bottom",
        "outputs": outputs,
        "delivery": "chat",
        "dub": dub,
        "voice": voice,
        "consent_file_id": None,
    }


def make_tone(path: Path, seconds: float) -> None:
    subprocess.run(
        [ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"sine=frequency=440:duration={seconds}", "-c:a", "pcm_s16le", str(path)],
        check=True,
    )


async def fake_fetch_audio(file_id: str, target: Path) -> None:
    make_tone(target, float(file_id.rsplit("_", 1)[1]))


def media_duration(path: Path) -> float:
    text = subprocess.run([ffmpeg_exe(), "-i", str(path)], capture_output=True, text=True).stderr
    for line in text.splitlines():
        if "Duration:" in line:
            h, m, sec = line.strip().split()[1].rstrip(",").split(":")
            return int(h) * 3600 + int(m) * 60 + float(sec)
    raise AssertionError(f"no duration in {path}")


def audio_streams(path: Path) -> int:
    text = subprocess.run([ffmpeg_exe(), "-i", str(path)], capture_output=True, text=True).stderr
    return sum(1 for line in text.splitlines() if "Audio:" in line)


class CueTests(unittest.TestCase):
    def test_words_become_cues_that_follow_the_speech(self):
        pipeline = load_pipeline(FakeBridge())
        cues = pipeline.group_words_into_cues(WORDS)

        self.assertEqual(len(cues), 5)
        for cue in cues:
            self.assertLessEqual(len(cue.text.split()), 4)
            self.assertLessEqual(len(cue.text), 26)
            self.assertGreaterEqual(cue.end - cue.start, 0.3)
        starts = [c.start for c in cues]
        self.assertEqual(starts, sorted(starts))
        for a, b in zip(cues, cues[1:]):
            self.assertLessEqual(a.end, b.start)
        pause_index = next(i for i, w in enumerate(WORDS) if w["word"].strip() == "Called")
        pause_start = WORDS[pause_index]["start"]
        self.assertIn(pause_start, starts)
        self.assertEqual([c.index for c in cues], [1, 2, 3, 4, 5])


class PlanTests(unittest.TestCase):
    def test_plan_is_rendered_from_the_job_by_code_and_sends_nothing(self):
        bridge = FakeBridge()
        pipeline = load_pipeline(bridge)
        with tempfile.TemporaryDirectory() as tmp:
            clip = Path(tmp) / "clip.mp4"
            make_fixture_clip(clip, seconds=3)
            probe = pipeline.probe_clip(clip)

            plan = pipeline.render_plan(job_for(clip), probe)

        lines = [line for line in plan.splitlines() if line.strip()]
        self.assertEqual(len(bridge.calls), 0)
        self.assertRegex(lines[0], r"^1\. .*audio_words_transcribe.*3\.0 s")
        self.assertRegex(lines[1], r"^2\. .*ai_functions_run.*translat")
        self.assertRegex(lines[2], r"^3\. .*burn.*en")
        self.assertRegex(lines[3], r"^4\. .*burn.*es")
        self.assertRegex(lines[-1], r"^Total")


class RunTests(unittest.IsolatedAsyncioTestCase):
    async def test_run_lands_every_output_at_a_files_path(self):
        bridge = FakeBridge()
        pipeline = load_pipeline(bridge)
        with tempfile.TemporaryDirectory() as tmp:
            clip = Path(tmp) / "clip.mp4"
            make_fixture_clip(clip, seconds=3)
            out = Path(tmp) / "out"

            result = await pipeline.run(job_for(clip), out)

            expected = ["final.en.mp4", "final.es.mp4", "captions.en.srt", "captions.es.srt", "check.en.png", "check.es.png"]
            self.assertEqual(sorted(result), sorted(expected))
            for name in expected:
                self.assertRegex(result[name], rf"^/files/video-editing/file_source-\d{{8}}-\d{{6}}/{name}$")
                self.assertTrue((out / name).exists(), name)
            downloads = [kwargs["sources"][0] for tool, kwargs in bridge.calls if tool == "files_copy_from_sandbox"]
            self.assertEqual(sorted(Path(p).name for p in downloads), sorted(expected))
            self.assertTrue((out / "ledger.jsonl").exists())

class DubTranslationTests(unittest.IsolatedAsyncioTestCase):
    async def test_translation_is_asked_for_the_sources_spoken_length(self):
        bridge = FakeBridge()
        pipeline = load_pipeline(bridge)
        probe = pipeline.Probe(duration_s=8.0, width=360, height=640, has_audio=True)
        source_text = " ".join(w["word"].strip() for w in WORDS)

        speech_s, budget = pipeline.target_spoken_length(WORDS, probe)

        self.assertAlmostEqual(speech_s, WORDS[-1]["end"] - WORDS[0]["start"], places=3)
        self.assertEqual(budget, round(speech_s * (len(source_text) / speech_s)))

        transcript = await pipeline.translate_transcript(source_text, "Spanish", budget)

        self.assertEqual(transcript, TRANSCRIPT_ES)
        tool_name, kwargs = bridge.calls[0]
        self.assertEqual(tool_name, "ai_functions_run")
        self.assertIn(str(budget), kwargs["instructions"])
        self.assertIn("transcript", kwargs["input"])


class DubFitTests(unittest.IsolatedAsyncioTestCase):
    async def test_speech_is_fitted_within_the_band_and_retranslated_once_outside_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            near = out / "near.wav"
            make_tone(near, 7.7)
            pipeline = load_pipeline(FakeBridge())

            fitted, ratio = pipeline.fit_audio(near, 8.0, out / "near.fit.wav")

            self.assertAlmostEqual(ratio, 7.7 / 8.0, places=3)
            self.assertAlmostEqual(media_duration(fitted), 8.0, delta=0.15)

            bridge = FakeBridge(speak_seconds=[5.7, 7.9])
            pipeline = load_pipeline(bridge)
            clip = out / "clip.mp4"
            make_fixture_clip(clip, seconds=8)
            probe = pipeline.probe_clip(clip)
            job = job_for(clip, dub="es", voice="dental-presenter")
            ledger = out / "ledger.jsonl"
            transcribed = {"language": "en", "words": WORDS, "path": str(clip)}
            with patch.object(pipeline, "fetch_audio", new=fake_fetch_audio):
                dubbed = await pipeline.dub(job, out, ledger, probe, transcribed)

            translations = [k for t, k in bridge.calls if t == "ai_functions_run" and "transcript" in k["input"]]
            speaks = [k for t, k in bridge.calls if t == "voices_speak"]
            self.assertEqual(len(translations), 2)
            self.assertEqual(len(speaks), 2)
            self.assertEqual(dubbed["language"], "es")
            lines = [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines()]
            self.assertTrue(any(line.get("retry") for line in lines))


class DubRunTests(unittest.IsolatedAsyncioTestCase):
    async def test_dub_job_plans_by_code_then_lands_the_dubbed_language_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            clip = Path(tmp) / "clip.mp4"
            make_fixture_clip(clip, seconds=3)
            bridge = FakeBridge(speak_seconds=[2.9])
            pipeline = load_pipeline(bridge)
            probe = pipeline.probe_clip(clip)

            plan = pipeline.render_plan(job_for(clip, dub="es", voice="designed"), probe)

            self.assertEqual(len(bridge.calls), 0)
            order = [plan.index(key) for key in ("audio_words_transcribe", "voices_create", "translat", "voices_speak", "burn", "Total")]
            self.assertEqual(order, sorted(order))
            self.assertEqual(plan.count("audio_words_transcribe"), 2)
            self.assertRegex(plan, r"translat\w*[^\n]*\d+ characters")
            named = pipeline.render_plan(job_for(clip, dub="es", voice="dental-presenter"), probe)
            self.assertNotIn("voices_create", named)

            out = Path(tmp) / "out"
            with patch.object(pipeline, "fetch_audio", new=fake_fetch_audio):
                result = await pipeline.run(job_for(clip, dub="es", voice="designed"), out)

            self.assertEqual(sorted(result), ["captions.es.srt", "check.es.png", "final.es.mp4"])
            self.assertFalse((out / "final.en.mp4").exists())
            self.assertFalse((out / "captions.en.srt").exists())
            self.assertEqual(audio_streams(out / "final.es.mp4"), 1)
            self.assertAlmostEqual(media_duration(out / "final.es.mp4"), 3.0, delta=0.2)
            self.assertIn("pospuse", (out / "captions.es.srt").read_text(encoding="utf-8"))


class KaraokeTests(unittest.TestCase):
    def test_karaoke_captions_carry_one_highlight_per_word(self):
        pipeline = load_pipeline(FakeBridge())
        cues = pipeline.group_words_into_cues(WORDS)
        with tempfile.TemporaryDirectory() as tmp:
            clip = Path(tmp) / "clip.mp4"
            make_fixture_clip(clip, seconds=3)
            probe = pipeline.probe_clip(clip)
            ass = Path(tmp) / "captions.en.ass"

            pipeline.write_ass(cues, WORDS, ass, probe, "bottom")

            text = ass.read_text(encoding="utf-8")
            dialogue = [line for line in text.splitlines() if line.startswith("Dialogue:")]
            self.assertEqual(len(dialogue), len(cues))
            self.assertEqual(text.count("\\k"), len(WORDS))
            for cue, line in zip(cues, dialogue):
                centis = sum(int(m) for m in re.findall(r"\\k(\d+)", line))
                self.assertAlmostEqual(centis, round((cue.end - cue.start) * 100), delta=2)

            pipeline.burn(clip, ass, Path(tmp) / "final.en.mp4", probe, "bottom")
            self.assertTrue((Path(tmp) / "final.en.mp4").exists())


if __name__ == "__main__":
    unittest.main()
