"""The video-editing pipeline script: cues, translation, plan and run, with no provider.

Spec: hq/projects/hyper/workspace/specs/2026-09-24-video-editing-captions.md, chunk 1 rows 3-6.
"""

import importlib.util
import json
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


class FakeBridge:
    """Stands in for seti.sandbox.call_tool: canned answers, every call recorded."""

    def __init__(self, translation_texts=None, fail_on=None):
        self.calls: list[tuple[str, dict]] = []
        self.translation_texts = translation_texts
        self.fail_on = fail_on

    async def __call__(self, tool_name, **kwargs):
        self.calls.append((tool_name, kwargs))
        if self.fail_on and self.fail_on(tool_name, kwargs):
            raise RuntimeError(f"fake failure in {tool_name}")
        if tool_name == "audio_words_transcribe":
            return {"file_id": kwargs.get("file_id"), "language": "en", "duration_s": 8.0, "words": WORDS}
        if tool_name == "ai_functions_run":
            items = kwargs["input"]["cues"]
            texts = self.translation_texts or [f"[{item['i']}] traducido" for item in items]
            return {
                "success": True,
                "results": [{"success": True, "output_json": {"cues": [{"i": item["i"], "text": text} for item, text in zip(items, texts)]}}],
            }
        if tool_name == "sandbox_download_file":
            return {"file_id": f"file_{Path(kwargs['path']).name}", "url": f"https://files.example/{Path(kwargs['path']).name}"}
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


def job_for(clip: Path, *, caption_language="es", outputs="both") -> dict:
    return {
        "source_file_id": "file_source",
        "source_path": str(clip),
        "spoken_language": "auto",
        "caption_language": caption_language,
        "caption_style": "plain",
        "caption_position": "bottom",
        "outputs": outputs,
        "delivery": "chat",
    }


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


class TranslationTests(unittest.IsolatedAsyncioTestCase):
    async def test_translation_keeps_every_cue_in_place(self):
        bridge = FakeBridge(translation_texts=["uno", "dos", "tres", "cuatro", "cinco"])
        pipeline = load_pipeline(bridge)
        cues = pipeline.group_words_into_cues(WORDS)

        translated = await pipeline.translate_cues(cues, "Spanish")

        self.assertEqual(len(translated), len(cues))
        self.assertEqual([c.index for c in translated], [c.index for c in cues])
        self.assertEqual([(c.start, c.end) for c in translated], [(c.start, c.end) for c in cues])
        self.assertEqual([c.text for c in translated], ["uno", "dos", "tres", "cuatro", "cinco"])
        self.assertNotEqual([c.text for c in translated], [c.text for c in cues])
        tool_name, kwargs = bridge.calls[0]
        self.assertEqual(tool_name, "ai_functions_run")
        self.assertIn("output_json_schema", kwargs)


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
    async def test_run_lands_every_output_in_files_with_an_id(self):
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
                self.assertEqual(result[name], f"file_{name}")
                self.assertTrue((out / name).exists(), name)
            downloads = [kwargs["path"] for tool, kwargs in bridge.calls if tool == "sandbox_download_file"]
            self.assertEqual(sorted(Path(p).name for p in downloads), sorted(expected))
            self.assertTrue((out / "ledger.jsonl").exists())

    async def test_run_names_the_failed_stage_when_a_burn_dies(self):
        bridge = FakeBridge(fail_on=lambda tool, kwargs: tool == "sandbox_download_file" and kwargs["path"].endswith("final.es.mp4"))
        pipeline = load_pipeline(bridge)
        with tempfile.TemporaryDirectory() as tmp:
            clip = Path(tmp) / "clip.mp4"
            make_fixture_clip(clip, seconds=3)
            out = Path(tmp) / "out"

            with self.assertRaises(RuntimeError) as raised:
                await pipeline.run(job_for(clip), out)

            self.assertIn("final.es.mp4", str(raised.exception))
            ledger = [json.loads(line) for line in (out / "ledger.jsonl").read_text(encoding="utf-8").splitlines()]
            self.assertEqual(ledger[-1]["stage"], "land")
            self.assertEqual(ledger[-1]["status"], "failed")


if __name__ == "__main__":
    unittest.main()
