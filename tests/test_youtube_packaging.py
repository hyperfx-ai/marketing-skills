"""Verify sandbox packaging contracts without a provider or credentials."""

import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

ROOT = Path(__file__).resolve().parents[1]
CASES = {
    "generate_seo_titles": ({"topic": "Marketing"}, {"titles": [{"title": "A title"}]}),
    "generate_seo_description": ({"topic": "Marketing"}, {"hook": "A hook"}),
    "analyze_thumbnail_concepts": (
        {"youtube_url": "https://youtube.com/watch?v=example"},
        {"concepts": [{"title": "A concept"}]},
    ),
}


class PackagingTests(unittest.IsolatedAsyncioTestCase):
    def load_script(self, name, rpc):
        sandbox = types.ModuleType("seti.sandbox")
        sandbox.call_tool = rpc
        spec = importlib.util.spec_from_file_location(
            name, ROOT / "skills/youtube/scripts" / f"{name}.py"
        )
        module = importlib.util.module_from_spec(spec)
        with patch.dict(
            sys.modules, {"seti": types.ModuleType("seti"), "seti.sandbox": sandbox}
        ):
            spec.loader.exec_module(module)
        return module

    async def test_structured_generation_uses_registered_name(self):
        for name, (inputs, output) in CASES.items():
            with self.subTest(script=name):
                response = {
                    "success": True,
                    "results": [{"success": True, "output_json": output}],
                }
                rpc = AsyncMock(
                    side_effect=[{"summary": "Video context"}, response]
                    if name.startswith("analyze")
                    else [response]
                )
                result = await self.load_script(name, rpc).run(**inputs)
                call = rpc.await_args_list[-1]
                self.assertEqual(call.args, ("ai_functions_run",))
                self.assertEqual(call.kwargs["output_format"], "json")
                self.assertEqual(call.kwargs["output_json_schema"]["type"], "object")
                field = (
                    "description"
                    if name.endswith("description")
                    else next(iter(output))
                )
                self.assertEqual(
                    result[field], output if field == "description" else output[field]
                )

    async def test_generation_failures_are_not_empty_successes(self):
        failures = [
            {"success": False, "error": "Provider failed", "results": []},
            {"success": True, "results": [{"success": False, "error": "Item failed"}]},
            {"success": True, "results": [{"success": True, "output_json": None}]},
        ]
        for name, (inputs, _) in CASES.items():
            for response in failures:
                with self.subTest(script=name, response=response):
                    rpc = AsyncMock(
                        side_effect=[{"summary": "Video context"}, response]
                        if name.startswith("analyze")
                        else [response]
                    )
                    with self.assertRaises(RuntimeError):
                        await self.load_script(name, rpc).run(**inputs)


if __name__ == "__main__":
    unittest.main()
