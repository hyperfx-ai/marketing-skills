---
name: video-editing
description: Edit a video the user attaches — captions timed to the spoken words, captions translated into another language, a dub in another language in a voice like the speaker's, karaoke-style captions, AI scene edits with Gemini Omni (change a scene, remove on-screen text, extend the clip), and (coming) TikTok delivery. Use when the user attaches or names a video and asks to caption it, subtitle it, translate its captions, dub it, edit it, or post it to TikTok.
use_cases:
  - Add captions to an attached video, timed word by word
  - Add captions and translate them into another language
  - Caption a clip that already has on-screen text, placing captions above it
  - Dub a clip into another language in a voice that resembles the speaker, captions timed to the new voice
  - Karaoke captions, where each word lights up as it is spoken
  - Change the scene of an attached clip, or remove its on-screen text, with Gemini Omni
  - Extend an attached clip by a few seconds
requires_toolkits:
  - video_generation_toolkit
  - sandbox
suggested_toolkits:
  - file_manager
icon: video_generation
short_description: Caption, translate, dub and edit an attached video through a plan the user approves first.
---

# Video Editing

The user attaches a video and says what they want done to it. This skill fills one settings sheet,
runs a script in the sandbox that prints the exact plan with its price, and only after the user says
yes runs that same plan as a background job. Every output lands in the user's files in a folder for that
run, `/files/video-editing/<clip>-<time>/`, so a second run never overwrites the first.

## Routing

| User intent | Status | Where to go |
| --- | --- | --- |
| Captions in the spoken language | Ready | This guide |
| Captions translated into another language | Ready | This guide (`outputs: both`) |
| A dub in another language, in a voice like the speaker's | Ready | This guide (`dub: <language>`) |
| Karaoke captions (each word lights up as spoken) | Ready | This guide (`caption_style: karaoke`) |
| AI scene edits (remove text, change a scene) | Ready | This guide (`edit_instruction`) |
| Extend the clip by 3 to 10 seconds | Ready | This guide (`extend_seconds`) |
| Refine the last edit ("now make the light warmer") | Ready | This guide (`previous_interaction_id`) |
| Posting the result to TikTok | Coming | Tell the user it is not available yet; deliver in chat |
| Generating a new video from a prompt | Other skill | [`video-generation`](../video-generation) |

## Requirements

- **Hyper MCP installed.** [https://app.hyperfx.ai/mcp](https://app.hyperfx.ai/mcp)
- **Video Generation toolkit enabled** at [https://app.hyperfx.ai/apps](https://app.hyperfx.ai/apps) — provides `audio_words_transcribe` (Whisper word timestamps), `voices_create` and `voices_speak` (Gemini TTS voices), and `videos_edit` (Gemini Omni scene edits).
- **Sandbox toolkit enabled** — the pipeline runs there (`sandbox_shell`, `sandbox_python_run`, `files_copy_to_sandbox`, `files_copy_from_sandbox`), and translation goes through `ai_functions_run` from inside it.
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
6. **A dub is the dubbed language only.** "Dub this in Spanish" lands `final.es.mp4`, its captions and its check frame, nothing in the original language.
7. **A voice is made from the clip, not asked for.** With `voice: designed` the run itself creates a voice that resembles the speaker and saves it under `/files/voices/`. Reuse an existing record on the next run (see below). Ask about the voice only for a replicated (cloned) voice: it needs a consent clip, and the same question offers the designed voice as the no-recording alternative.
8. **Baked-in text gets stripped or mentioned.** Omni redraws on-screen text with mistakes when it is not told to remove it. When the clip has text on it and the user asks for an edit, set `strip_text: yes` if they want it gone; otherwise tell them the text may come out changed before they say yes.
9. **The whole clip is edited, in pieces.** Omni takes at most 10 seconds at a time; the script cuts a longer clip into equal pieces, edits each with the same instruction and stitches them back. Never ask which seconds to edit. Fill `edit_part` only when the user asks for a part themselves.

## The settings sheet

The sheet is the job. Every field, its default and where it comes from is in
[references/settings-sheet.md](references/settings-sheet.md). The short form:

| Field | Default | Filled from |
| --- | --- | --- |
| `source_file_id` | — | The attachment's file id, or its `/files/...` path from `files_list` |
| `source_path` | `/home/user/video-editing/source.mp4` | Where you copied the clip in the sandbox |
| `spoken_language` | `auto` | Whisper detects it; the user's word wins if they name it |
| `caption_language` | the spoken language | The user's request; ask if a translation is wanted and no language is named |
| `caption_style` | `plain` | `plain` (bold white with an outline) or `karaoke` (each word lights up as spoken) |
| `caption_position` | `bottom` | `above_text` when the user says the clip has text at the bottom |
| `outputs` | `captions_only` | `both` when a second language is asked for; ignored when `dub` is set |
| `dub` | `none` | A language code when the user asks for a dub; the output is that language only |
| `voice` | `designed` | `designed` (made from the clip's speaker by the run), `replicated` (a clone, needs `consent_file_id`), or the name of a record in `/files/voices/` |
| `consent_file_id` | — | Only for `replicated`: the file id of a clip in which the speaker says the consent sentence |
| `delivery` | `chat` | Always `chat` in this version |
| `edit_instruction` | empty | The user's words for the change; for an extension, what happens next |
| `strip_text` | `no` | `yes` when the user wants the on-screen text gone |
| `edit_part` | `whole` | `start-end` seconds only when the user asks for a part |
| `edit_resolution` | `auto` | 720p when the clip is 720 px or taller, else 360p; the user may name one |
| `extend_seconds` | `0` | 3 to 10 when the user wants the clip to go on |
| `previous_interaction_id` | empty | The ids from the last completion, when the user refines that edit |
| `captions` | `yes` | `no` when the user wants only the edit |

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

### 1b. Pick the voice (dub only)

Before writing the sheet for a dub, `files_list(path="/files/voices")`. If a record's `source_file_id` is
this clip, use its `name` as `voice`; otherwise use the newest record's name when the user wants the
same brand voice as before, else `designed` and the run makes one. If the user asks to clone their own
voice, ask one question, with the consent sentence to record, and offer `designed` in the same question:

> To clone your voice I need a short clip of you saying: "I am the owner of this voice and I consent to
> Google using this voice to create a synthetic voice model". Attach it, or say "designed" and I will
> make a voice that resembles the speaker without a recording.

Neither answer means the run does not start.

### 2. Write the sheet

```python
sandbox_python_run(code='''
import json
job = {
    "source_file_id": "<attachment file id, or its /files path>",
    "source_path": "/home/user/video-editing/source.mp4",
    "spoken_language": "auto",
    "caption_language": "es",
    "caption_style": "plain",
    "caption_position": "bottom",
    "outputs": "both",
    "dub": "none",
    "voice": "designed",
    "consent_file_id": None,
    "delivery": "chat",
    "edit_instruction": "",
    "strip_text": "no",
    "edit_part": "whole",
    "edit_resolution": "auto",
    "extend_seconds": 0,
    "previous_interaction_id": None,
    "captions": "yes",
}
json.dump(job, open("/home/user/video-editing/job.json", "w"), indent=1)
''')
```

### 3. Show the plan and ask for a yes

```python
sandbox_shell(command="cd /home/user/video-editing && python pipeline.py plan job.json")
```

Paste the printed lines verbatim in your own message, then ask: "Shall I run this?" Stop there. The user
cannot see tool output, so a reply that is only "Shall I run this?" with no plan lines above it shows
them nothing to approve; it is wrong.

### 4. On yes, run it in the background

```python
sandbox_shell(command="cd /home/user/video-editing && python pipeline.py run job.json", background=true, timeout=1800)
```

Tell the user it is running and that you will report when it finishes. The job's completion message
carries the result: a JSON object mapping each output name to its file id, plus `interaction_ids` when an
edit ran.

### 5. Report the outputs

List every output with its id: `final.<lang>.mp4` per language, `captions.<lang>.srt` per language, and
`check.<lang>.png` (one frame with a caption on it, so the user can see the placement). For a dub there is
one language: the dubbed one. If the completion
names a failed stage instead, say which stage failed and what it said; `out/ledger.jsonl` in the sandbox
holds one line per stage.

### 6. Refining an edit

When the user wants a change to the edit they just got ("now make the light warmer"), keep the sheet, put the
completion's `interaction_ids` into `previous_interaction_id`, put the new words into `edit_instruction`, and
go back to step 3: `plan`, a yes, `run`. Nothing is uploaded again; Omni continues from the last edit.

## What the script does

`pipeline.py run` inside the sandbox: when an edit is asked for, ffmpeg cuts the clip into pieces of at most 10 s,
`sandbox_download_file` lands each, `videos_edit` edits each with the same instruction (or extends the clip), `files_copy_to_sandbox`
brings the results back, and ffmpeg scales and stitches them into `edited.mp4` (or `extended.mp4`) with the clip's own audio.
Then, unless `captions` is `no`: `audio_words_transcribe` for the words, cues of at most 4 words or 26
characters that break at pauses over 0.6 s, `ai_functions_run` for the translation when a second language is
asked for, ffmpeg to burn each caption file and grab a check frame, and `files_copy_from_sandbox` once per
output so each lands in the user's files in the run's folder `/files/video-editing/<clip>-<time>/`. For a dub: `voices_create` when no voice is named, a
translation of the whole transcript asked to fit the clip's spoken length, `voices_speak` in that voice, a
tempo fit within 0.9 to 1.1 (one re-translation when the first take is outside it), the new audio swapped onto
the picture, `audio_words_transcribe` again on the dubbed track, and captions timed to it. `karaoke` writes
an ASS subtitle with one highlight per word instead of the plain SRT for the burn.

## Example: a dub

**Input:** "Dub this in Spanish" with a clip attached, no voice on file.

**Flow:** sheet `dub: "es"`, `voice: "designed"`, nothing to ask. `plan` shows the voice creation, the
translation with its character budget, the speech, the second transcription and the burn, with a total.
On yes, `run` in the background. On completion, report `final.es.mp4`, `captions.es.srt` and
`check.es.png` with their ids. A second run on the same clip finds the record in `/files/voices/` and
skips the creation.

## Example: a scene edit

**Input:** "Remove the text and change the background to our clinic reception" with an 8 s clip attached.

**Flow:**
1. Copy the clip and the script into the sandbox, install ffmpeg.
2. Sheet: `edit_instruction: "change the background to our clinic reception"`, `strip_text: "yes"`, everything else default. Nothing to ask.
3. Run `plan`: line 1 is the Omni call with the instruction and its price; paste the lines, ask for a yes.
4. On yes, run `run` in the background.
5. On completion, report `edited.mp4`, `final.en.mp4`, `captions.en.srt`, `check.en.png` with their ids, and keep the `interaction_ids` for a refinement.

## Example: captions

**Input:** "Add captions and translate to Spanish" with a clip attached.

**Flow:**
1. Copy the clip and the script into the sandbox, install ffmpeg.
2. Sheet: `caption_language: "es"`, `outputs: "both"`, everything else default. Nothing to ask.
3. Run `plan`, paste its lines, ask for a yes.
4. On yes, run `run` in the background.
5. On completion, report `final.en.mp4`, `final.es.mp4`, `captions.en.srt`, `captions.es.srt`, `check.en.png`, `check.es.png` with their ids.
