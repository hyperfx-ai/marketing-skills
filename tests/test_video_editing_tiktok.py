"""The video-editing pipeline's TikTok delivery: what the plan prints and what each slot sends, with no provider.

Spec: hq/projects/hyper/workspace/specs/2026-09-24-video-editing-tiktok.md, chunk 4 rows 1-2.
"""

import asyncio
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from tests.test_video_editing_edit import CLINIC, make_clip
from tests.test_video_editing_pipeline import FakeBridge, job_for, load_pipeline

CAPTION = (
    "Mystery slabs that are starting at ONE dollar for hits like these! Join our stream by clicking "
    "the red bubble around our profile to get hits 🔥 #gamerschoice #stream #mysteryslabs #pokemontcg #tcg"
)
ZONE = "Europe/Amsterdam"
TIMES = [
    "2026-09-29 12:00",
    "2026-09-29 15:00",
    "2026-09-29 19:00",
    "2026-09-30 12:00",
    "2026-09-30 15:00",
    "2026-09-30 19:00",
]
PRIVATE = "private until the app is audited"


def utc_iso(local: str) -> str:
    return datetime.strptime(local, "%Y-%m-%d %H:%M").replace(tzinfo=ZoneInfo(ZONE)).astimezone(ZoneInfo("UTC")).isoformat()


class TikTokBridge(FakeBridge):
    """Chunk 1's bridge plus a trigger id per schedule call and one publish result."""

    def __init__(self):
        super().__init__()
        self.scheduled = 0

    async def __call__(self, tool_name, **kwargs):
        if tool_name == "tiktok_posts_schedule":
            self.calls.append((tool_name, kwargs))
            self.scheduled += 1
            return {"trigger_id": f"trigger_{self.scheduled}", "run_at": kwargs["run_at"]}
        if tool_name == "tiktok_posts_publish":
            self.calls.append((tool_name, kwargs))
            return {"publish_id": "v_pub_1", "status": "PUBLISH_COMPLETE", "fail_reason": None, "processing_time_seconds": 12}
        return await super().__call__(tool_name, **kwargs)


def tiktok_job(clip: Path, **fields) -> dict:
    job = job_for(clip, caption_language="en", outputs="captions_only")
    job.update({"delivery": "tiktok", "tiktok_caption": CAPTION, "tiktok_times": list(TIMES), "tiktok_timezone": ZONE, "tiktok_account": "hypertest"})
    job.update(fields)
    return job


def edited(job: dict) -> dict:
    job.update({"edit_instruction": CLINIC, "strip_text": "yes", "edit_part": "whole", "edit_resolution": "auto", "extend_seconds": 0, "previous_interaction_id": None, "captions": "yes"})
    return job


def names(calls) -> list[str]:
    return [name for name, _ in calls]


class PlanTests(unittest.TestCase):
    def test_plan_lists_one_tiktok_line_per_slot_after_the_captions_and_sends_nothing(self):
        bridge = TikTokBridge()
        pipeline = load_pipeline(bridge)
        with tempfile.TemporaryDirectory() as tmp:
            clip = Path(tmp) / "clip.mp4"
            make_clip(clip, 8)
            probe = pipeline.probe_clip(clip)

            lines = pipeline.render_plan(tiktok_job(clip), probe).splitlines()
            tiktok = [line for line in lines if "TikTok post" in line]
            self.assertEqual(len(tiktok), 6)
            last_caption = max(i for i, line in enumerate(lines) if "ffmpeg burn" in line)
            first_tiktok = lines.index(tiktok[0])
            music = next(i for i, line in enumerate(lines) if pipeline.TIKTOK_MUSIC_POLICY_URL in line)
            self.assertLess(last_caption, first_tiktok)
            self.assertLess(lines.index(tiktok[-1]), music)
            self.assertLess(music, len(lines) - 1)
            self.assertTrue(lines[-1].startswith("Total: $"))
            for line, local in zip(tiktok, TIMES):
                for expected in ("@hypertest", CAPTION, local, ZONE, PRIVATE, "AI label: no", "$0"):
                    self.assertIn(expected, line)

            lines = pipeline.render_plan(edited(tiktok_job(clip)), probe).splitlines()
            self.assertEqual(sum("AI label: yes" in line for line in lines), 6)

            lines = pipeline.render_plan(tiktok_job(clip, tiktok_times=[]), probe).splitlines()
            now_lines = [line for line in lines if "TikTok post" in line]
            self.assertEqual(len(now_lines), 1)
            self.assertIn("post now", now_lines[0])
            self.assertIn(CAPTION, now_lines[0])

            with self.assertRaises(RuntimeError):
                pipeline.render_plan(tiktok_job(clip, tiktok_times=["2020-01-01 12:00"]), probe)
            with self.assertRaises(RuntimeError):
                pipeline.render_plan(tiktok_job(clip, tiktok_account=None), probe)
            self.assertEqual(bridge.calls, [])


class RunTests(unittest.TestCase):
    def test_run_schedules_one_post_per_slot_after_landing_in_time_order(self):
        bridge = TikTokBridge()
        pipeline = load_pipeline(bridge)
        with tempfile.TemporaryDirectory() as tmp:
            clip = Path(tmp) / "clip.mp4"
            make_clip(clip, 8)

            result = asyncio.run(pipeline.run(tiktok_job(clip), Path(tmp) / "out"))

            sent = names(bridge.calls)
            self.assertNotIn("tiktok_posts_publish", sent)
            self.assertEqual(sent.count("tiktok_posts_schedule"), 6)
            self.assertLess(max(i for i, n in enumerate(sent) if n == "sandbox_download_file"), sent.index("tiktok_posts_schedule"))
            for name in ("final.en.mp4", "captions.en.srt", "check.en.png"):
                self.assertIn(name, result)
            for (_, kwargs), local in zip([c for c in bridge.calls if c[0] == "tiktok_posts_schedule"], TIMES):
                self.assertEqual(kwargs["file"], result["final.en.mp4"])
                self.assertEqual(kwargs["caption"], CAPTION)
                self.assertIs(kwargs["is_aigc"], False)
                self.assertEqual(kwargs["run_at"], utc_iso(local))
                self.assertEqual(kwargs["timezone"], ZONE)
            self.assertEqual(result["tiktok"], [f"trigger_{n}" for n in range(1, 7)])

    def test_run_with_no_times_publishes_once_and_ends_with_the_publish_id(self):
        bridge = TikTokBridge()
        pipeline = load_pipeline(bridge)
        with tempfile.TemporaryDirectory() as tmp:
            clip = Path(tmp) / "clip.mp4"
            make_clip(clip, 8)

            result = asyncio.run(pipeline.run(tiktok_job(clip, tiktok_times=[]), Path(tmp) / "out"))

            sent = names(bridge.calls)
            self.assertNotIn("tiktok_posts_schedule", sent)
            self.assertEqual(sent.count("tiktok_posts_publish"), 1)
            _, kwargs = next(c for c in bridge.calls if c[0] == "tiktok_posts_publish")
            self.assertEqual(kwargs["file"], result["final.en.mp4"])
            self.assertEqual(kwargs["caption"], CAPTION)
            self.assertIs(kwargs["is_aigc"], False)
            self.assertEqual(result["tiktok"][0]["publish_id"], "v_pub_1")
            self.assertEqual(result["tiktok"][0]["status"], "PUBLISH_COMPLETE")


if __name__ == "__main__":
    unittest.main()
