"""The video-editing pipeline's scene-edit branch: what each step sends, with no provider.

Spec: hq/projects/hyper/workspace/specs/2026-09-24-video-editing-scene-edit.md, chunk 3 rows 1-4.
"""

import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.test_video_editing_pipeline import FakeBridge, ffmpeg_exe, job_for, load_pipeline

CLINIC = "replace the kitchen background with the bright reception area of a modern dental clinic"


def make_clip(path: Path, seconds: float, size: str = "720x1280") -> None:
    subprocess.run(
        [
            ffmpeg_exe(), "-y", "-loglevel", "error",
            "-f", "lavfi", "-i", f"testsrc=size={size}:rate=24:duration={seconds}",
            "-f", "lavfi", "-i", f"sine=frequency=440:duration={seconds}",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(path),
        ],
        check=True,
    )


class EditBridge(FakeBridge):
    """Chunk 1's bridge plus canned answers for the edit tools; a stand-in clip lands at every copy."""

    def __init__(self, stand_in_seconds: float, **kwargs):
        super().__init__(**kwargs)
        self.stand_in_seconds = stand_in_seconds
        self.edits = 0

    async def __call__(self, tool_name, **kwargs):
        if tool_name == "videos_edit":
            self.calls.append((tool_name, kwargs))
            self.edits += 1
            return {
                "file_id": f"file_omni_{self.edits}",
                "url": f"https://files.example/omni_{self.edits}.mp4",
                "interaction_id": f"v1_interaction_{self.edits}",
                "resolution": kwargs.get("resolution"),
                "input_tokens": 14228,
                "video_output_tokens": 15448,
                "cost_usd": 0.2917,
            }
        if tool_name == "files_copy_to_sandbox":
            self.calls.append((tool_name, kwargs))
            make_clip(Path(kwargs["destination"]), self.stand_in_seconds, size="360x640")
            return {"success": True}
        return await super().__call__(tool_name, **kwargs)


def edit_job(clip: Path, **fields) -> dict:
    job = job_for(clip, caption_language="en", outputs="captions_only")
    job.update({"edit_instruction": CLINIC, "strip_text": "no", "edit_part": "whole", "edit_resolution": "auto", "extend_seconds": 0, "previous_interaction_id": None, "captions": "yes"})
    job.update(fields)
    return job


def names(calls) -> list[str]:
    return [name for name, _ in calls]


class PlanTests(unittest.TestCase):
    def test_plan_lists_every_omni_call_as_it_will_be_sent_and_sends_nothing(self):
        bridge = EditBridge(8)
        pipeline = load_pipeline(bridge)
        with tempfile.TemporaryDirectory() as tmp:
            tall, small, long = Path(tmp) / "tall.mp4", Path(tmp) / "small.mp4", Path(tmp) / "long.mp4"
            make_clip(tall, 8)
            make_clip(small, 8, size="360x640")
            make_clip(long, 15)

            lines = pipeline.render_plan(edit_job(tall, strip_text="yes"), pipeline.probe_clip(tall)).splitlines()
            first = lines[0]
            for expected in ("1. videos_edit", pipeline.OMNI_MODEL, "720p", "9:16", "8.0 s", CLINIC):
                self.assertIn(expected, first)
            self.assertTrue(first.rstrip().endswith(pipeline.STRIP_TEXT_SENTENCE))
            self.assertIn("audio_words_transcribe", lines[1])
            self.assertTrue(lines[-1].startswith("Total: $"))

            small_lines = pipeline.render_plan(edit_job(small), pipeline.probe_clip(small)).splitlines()
            self.assertIn("360p", small_lines[0])

            long_lines = pipeline.render_plan(edit_job(long), pipeline.probe_clip(long)).splitlines()
            omni_lines = [line for line in long_lines if "videos_edit" in line]
            self.assertEqual(len(omni_lines), 2)
            for line in omni_lines:
                self.assertIn("7.5 s", line)
            self.assertEqual(pipeline.edit_pieces(pipeline.parse_job(edit_job(long)), pipeline.probe_clip(long)), [(0.0, 7.5), (7.5, 15.0)])
            self.assertEqual(pipeline.edit_pieces(pipeline.parse_job(edit_job(tall)), pipeline.probe_clip(tall)), [(0.0, 8.0)])
            self.assertEqual(pipeline.edit_pieces(pipeline.parse_job(edit_job(long, edit_part="2-9")), pipeline.probe_clip(long)), [(2.0, 9.0)])
            with self.assertRaises(RuntimeError):
                pipeline.render_plan(edit_job(long, edit_part="12-20"), pipeline.probe_clip(long))

            wide, square = Path(tmp) / "wide.mp4", Path(tmp) / "square.mp4"
            make_clip(wide, 8, size="1280x720")
            make_clip(square, 8, size="640x640")
            self.assertIn("16:9", pipeline.render_plan(edit_job(wide), pipeline.probe_clip(wide)).splitlines()[0])
            self.assertIn("360p", pipeline.render_plan(edit_job(tall, edit_resolution="360p"), pipeline.probe_clip(tall)).splitlines()[0])
            with self.assertRaises(RuntimeError):
                pipeline.render_plan(edit_job(square), pipeline.probe_clip(square))
        self.assertEqual(bridge.calls, [])


class RunTests(unittest.IsolatedAsyncioTestCase):
    async def test_edit_run_sends_each_step_the_right_thing_in_order(self):
        bridge = EditBridge(7.5)
        pipeline = load_pipeline(bridge)
        with tempfile.TemporaryDirectory() as tmp:
            clip = Path(tmp) / "long.mp4"
            make_clip(clip, 15)
            job = edit_job(clip)
            result = await pipeline.run(job, Path(tmp) / "out")

            sent = names(bridge.calls)
            piece_downloads = [kw for name, kw in bridge.calls if name == "files_copy_from_sandbox" and "piece." in kw["sources"][0]]
            self.assertEqual(len(piece_downloads), 2)
            edits = [kw for name, kw in bridge.calls if name == "videos_edit"]
            self.assertEqual([Path(kw["file_id"]).name for kw in edits], ["piece.1.mp4", "piece.2.mp4"])
            self.assertTrue(all(kw["file_id"].startswith("/files/video-editing/") for kw in edits))
            self.assertEqual(edits[0]["instruction"], CLINIC)
            self.assertTrue(edits[1]["instruction"].startswith(CLINIC) and edits[1]["instruction"].endswith(pipeline.ANCHOR_SENTENCE))
            self.assertNotIn("reference_image_file_id", edits[0])
            self.assertEqual(Path(edits[1]["reference_image_file_id"]).name, "anchor.1.png")
            self.assertEqual({kw["resolution"] for kw in edits}, {"720p"})
            self.assertEqual({kw["aspect_ratio"] for kw in edits}, {"9:16"})
            copies = [kw for name, kw in bridge.calls if name == "files_copy_to_sandbox"]
            self.assertEqual([kw["sources"] for kw in copies], [["file_omni_1"], ["file_omni_2"]])
            words = [kw for name, kw in bridge.calls if name == "audio_words_transcribe"]
            self.assertEqual([kw["file_id"] for kw in words], ["file_source"])
            self.assertLess(max(i for i, n in enumerate(sent) if n == "files_copy_from_sandbox" and "piece." in bridge.calls[i][1]["sources"][0]), sent.index("videos_edit"))
            first_edit, first_copy = sent.index("videos_edit"), sent.index("files_copy_to_sandbox")
            anchor = next(i for i, (n, kw) in enumerate(bridge.calls) if n == "files_copy_from_sandbox" and "anchor." in kw["sources"][0])
            second_edit = [i for i, n in enumerate(sent) if n == "videos_edit"][1]
            self.assertTrue(first_edit < first_copy < anchor < second_edit)
            output_downloads = [Path(kw["sources"][0]).name for name, kw in bridge.calls if name == "files_copy_from_sandbox" and "piece." not in kw["sources"][0] and "anchor." not in kw["sources"][0]]
            self.assertEqual(output_downloads, ["edited.mp4", "final.en.mp4", "captions.en.srt", "check.en.png"])
            self.assertEqual({name: Path(path).name for name, path in result.items() if name != "interaction_ids"}, {name: name for name in output_downloads})
            self.assertEqual(result["interaction_ids"], ["v1_interaction_1", "v1_interaction_2"])

        bridge = EditBridge(8)
        pipeline = load_pipeline(bridge)
        with tempfile.TemporaryDirectory() as tmp:
            clip = Path(tmp) / "short.mp4"
            make_clip(clip, 8)
            result = await pipeline.run(edit_job(clip, captions="no"), Path(tmp) / "out")
            self.assertNotIn("audio_words_transcribe", names(bridge.calls))
            self.assertNotIn("ai_functions_run", names(bridge.calls))
            self.assertEqual(sorted(result), ["check.edit.png", "edited.mp4", "interaction_ids"])

    async def test_refinement_sends_the_ids_and_no_pieces(self):
        bridge = EditBridge(7.5)
        pipeline = load_pipeline(bridge)
        with tempfile.TemporaryDirectory() as tmp:
            clip = Path(tmp) / "long.mp4"
            make_clip(clip, 15)
            job = edit_job(clip, edit_instruction="now make the light warmer", previous_interaction_id=["v1_first", "v1_second"])
            result = await pipeline.run(job, Path(tmp) / "out")

            edits = [kw for name, kw in bridge.calls if name == "videos_edit"]
            self.assertEqual([kw.get("previous_interaction_id") for kw in edits], ["v1_first", "v1_second"])
            self.assertEqual([kw.get("file_id") for kw in edits], [None, None])
            self.assertEqual([kw for name, kw in bridge.calls if name == "files_copy_from_sandbox" and "piece." in kw["sources"][0]], [])
            self.assertEqual(sorted(result), ["captions.en.srt", "check.en.png", "edited.mp4", "final.en.mp4", "interaction_ids"])
            self.assertEqual(result["interaction_ids"], ["v1_interaction_1", "v1_interaction_2"])

    async def test_extension_sends_the_extend_instruction_and_reads_words_from_the_extended_clip(self):
        bridge = EditBridge(4)
        pipeline = load_pipeline(bridge)
        with tempfile.TemporaryDirectory() as tmp:
            clip = Path(tmp) / "short.mp4"
            make_clip(clip, 8)
            job = edit_job(clip, edit_instruction="she smiles and waves", extend_seconds=4)
            plan_first = pipeline.render_plan(job, pipeline.probe_clip(clip)).splitlines()[0]
            self.assertIn("extend", plan_first)
            self.assertIn("4 s", plan_first)
            result = await pipeline.run(job, Path(tmp) / "out")

            edits = [kw for name, kw in bridge.calls if name == "videos_edit"]
            self.assertEqual(len(edits), 1)
            self.assertTrue(edits[0]["instruction"].startswith("Continue the scene for 4 seconds."))
            sent = names(bridge.calls)
            extended_download = next(i for i, (n, kw) in enumerate(bridge.calls) if n == "files_copy_from_sandbox" and Path(kw["sources"][0]).name == "extended.mp4")
            self.assertLess(extended_download, sent.index("audio_words_transcribe"))
            words = [kw for name, kw in bridge.calls if name == "audio_words_transcribe"]
            self.assertEqual(Path(words[0]["file_id"]).name, "extended.mp4")
            self.assertEqual(sorted(result), ["captions.en.srt", "check.en.png", "extended.mp4", "final.en.mp4", "interaction_ids"])


if __name__ == "__main__":
    unittest.main()
