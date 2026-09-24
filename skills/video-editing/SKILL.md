---
name: video-editing
description: Edit a video the user attaches — captions timed to the spoken words, captions translated into another language, and (coming) a dubbed voice, AI scene edits and TikTok delivery. Use when the user attaches or names a video and asks to caption it, subtitle it, translate its captions, dub it, edit it, or post it to TikTok.
use_cases:
  - Add captions to an attached video, timed word by word
  - Add captions and translate them into another language
  - Caption a clip that already has on-screen text, placing captions above it
requires_toolkits:
  - video_generation_toolkit
  - sandbox
suggested_toolkits:
  - file_manager
icon: video_generation
short_description: Caption and translate an attached video through a plan the user approves first.
---

# Video Editing

The user attaches a video and says what they want done to it. This skill fills one settings sheet,
runs a script in the sandbox that prints the exact plan with its price, and only after the user says
yes runs that same plan as a background job. Every output lands in the user's files with an id.

## Routing

| User intent | Status | Where to go |
| --- | --- | --- |
| Captions in the spoken language | Ready | This guide |
| Captions translated into another language | Ready | This guide (`outputs: both`) |
| A dubbed voice in another language | Coming | Tell the user it is not available yet |
| AI scene edits (remove text, change a scene) | Coming | Tell the user it is not available yet |
| Posting the result to TikTok | Coming | Tell the user it is not available yet; deliver in chat |
| Generating a new video from a prompt | Other skill | [`video-generation`](../video-generation) |

## Requirements

- **Hyper MCP installed.** [https://app.hyperfx.ai/mcp](https://app.hyperfx.ai/mcp)
- **Video Generation toolkit enabled** at [https://app.hyperfx.ai/apps](https://app.hyperfx.ai/apps) — provides `audio_words_transcribe` (Whisper word timestamps).
- **Sandbox toolkit enabled** — the pipeline runs there (`sandbox_shell`, `sandbox_python_run`, `files_copy_to_sandbox`, `sandbox_download_file`), and translation goes through `ai_functions_run` from inside it.
- **Background jobs enabled** for the workspace. The run is a background shell job; if `sandbox_shell(background=true)` is refused because background tools are off, tell the user that plainly and stop. Do not run the pipeline in the foreground.

### How to run the tools in this skill

Every tool in this skill is named by its canonical tool name. Run it with the call your surface gives you:

| Surface | Find a tool | Run it |
| --- | --- | --- |
| MCP client (Claude, Cursor, Codex, ChatGPT) | `search("<what you want to do>")`, then `describe("<name>")` | `call("<name>", {...})` |
| Hyper CLI | `hyperai search "<what you want to do>"`, then `hyperai describe <name>` | `hyperai call <name> --json '{...}'` |

If a tool is not found, its integration is not connected or not enabled for the workspace: stop and tell the user which integration to connect.

## Critical rules

1. **The script prices the job, never you.** Show the plan text exactly as the script printed it. Do not type, round, or restate a number.
2. **Nothing runs before a yes.** `plan` sends nothing. `run` starts only after the user answers yes to the plan. "Not now", silence, or a new question is not a yes.
3. **Ask only for what you cannot fill.** The file comes from the attachment, the spoken language from Whisper. Ask for the caption language only when the user named none and asked for a translation, or when "caption this" gives no language and you cannot tell whether they want the spoken one; one question, then proceed.
4. **Same job, both times.** `plan` and `run` read the same `job.json`. If the user changes anything after seeing the plan, rewrite the sheet and run `plan` again.
5. **Report ids, not paths.** The completion names each output with its file id. Those ids are what the user opens; a sandbox path is not a deliverable.

## The settings sheet

The sheet is the job. Every field, its default and where it comes from is in
[references/settings-sheet.md](references/settings-sheet.md). The short form:

| Field | Default | Filled from |
| --- | --- | --- |
| `source_file_id` | — | The attachment's file id |
| `source_path` | `/home/user/video-editing/source.mp4` | Where you copied the clip in the sandbox |
| `spoken_language` | `auto` | Whisper detects it; the user's word wins if they name it |
| `caption_language` | the spoken language | The user's request; ask if a translation is wanted and no language is named |
| `caption_style` | `plain` | Bold white with an outline (`karaoke` is coming) |
| `caption_position` | `bottom` | `above_text` when the user says the clip has text at the bottom |
| `outputs` | `captions_only` | `both` when a second language is asked for |
| `delivery` | `chat` | Always `chat` in this version |

## Flow

### 1. Set up the sandbox

Copy the clip and the script in, and make sure ffmpeg is available. The script is `scripts/pipeline.py`
beside this file; `files_list` shows its exact path under `/skills/` if you are unsure.

```python
files_copy_to_sandbox(sources=["<attachment file id>"], destination="/home/user/video-editing/source.mp4")
files_copy_to_sandbox(sources=["<path of this skill>/scripts/pipeline.py"], destination="/home/user/video-editing/pipeline.py")
sandbox_shell(command="python -m pip install -q imageio-ffmpeg")
```

The pip install is about 30 MB and happens once per fresh sandbox; tell the user it is preparing.

### 2. Write the sheet

```python
sandbox_python_run(code='''
import json
job = {
    "source_file_id": "<attachment file id>",
    "source_path": "/home/user/video-editing/source.mp4",
    "spoken_language": "auto",
    "caption_language": "es",
    "caption_style": "plain",
    "caption_position": "bottom",
    "outputs": "both",
    "delivery": "chat",
}
json.dump(job, open("/home/user/video-editing/job.json", "w"), indent=1)
''')
```

### 3. Show the plan and ask for a yes

```python
sandbox_shell(command="cd /home/user/video-editing && python pipeline.py plan job.json")
```

Paste the printed lines verbatim, then ask: "Shall I run this?" Stop there.

### 4. On yes, run it in the background

```python
sandbox_shell(command="cd /home/user/video-editing && python pipeline.py run job.json", background=true, timeout=1800)
```

Tell the user it is running and that you will report when it finishes. The job's completion message
carries the result: a JSON object mapping each output name to its file id.

### 5. Report the outputs

List every output with its id: `final.<lang>.mp4` per language, `captions.<lang>.srt` per language, and
`check.<lang>.png` (one frame with a caption on it, so the user can see the placement). If the completion
names a failed stage instead, say which stage failed and what it said; `out/ledger.jsonl` in the sandbox
holds one line per stage.

## What the script does

`pipeline.py run` inside the sandbox: `audio_words_transcribe` for the words, cues of at most 4 words or 26
characters that break at pauses over 0.6 s, `ai_functions_run` for the translation when a second language is
asked for, ffmpeg to burn each caption file and grab a check frame, and `sandbox_download_file` once per
output so each lands in the user's files with an id.

## Example

**Input:** "Add captions and translate to Spanish" with a clip attached.

**Flow:**
1. Copy the clip and the script into the sandbox, install ffmpeg.
2. Sheet: `caption_language: "es"`, `outputs: "both"`, everything else default. Nothing to ask.
3. Run `plan`, paste its lines, ask for a yes.
4. On yes, run `run` in the background.
5. On completion, report `final.en.mp4`, `final.es.mp4`, `captions.en.srt`, `captions.es.srt`, `check.en.png`, `check.es.png` with their ids.
