# The settings sheet

The sheet is the whole job: `pipeline.py plan job.json` prices it and prints the calls it would make,
`pipeline.py run job.json` executes exactly that. The agent fills every field it can from the request and
the attachment and asks only for the rest.

| Field | Values | Default | Source | Priced |
| --- | --- | --- | --- | --- |
| `source_file_id` | a file id | — | The attachment. Required. | Whisper is billed on its audio length |
| `source_path` | a sandbox path | `/home/user/video-editing/source.mp4` | Where `files_copy_to_sandbox` put the clip | No |
| `spoken_language` | `auto` or an ISO 639-1 code (`en`, `es`, `fr`, …) | `auto` | Whisper detects it. When the user names the spoken language, use their code; it overrides detection (a short clip with music can be misread). | No |
| `caption_language` | an ISO 639-1 code | the spoken language | The user's request. When they ask for a translation and name no language, ask this one question. | Yes, when it differs from the spoken language |
| `caption_style` | `plain` | `plain` | Bold white text with a black outline. `karaoke` (word highlighting) is coming. | No |
| `caption_position` | `bottom`, `above_text` | `bottom` | `above_text` when the user says the clip has on-screen text at the bottom; the captions sit higher so they do not cover it. | No |
| `outputs` | `captions_only`, `both` | `captions_only` | `both` when a second language is asked for: one captioned MP4 per language. | Yes: `both` adds one translation and one burn |
| `delivery` | `chat` | `chat` | Always `chat` in this version; TikTok delivery is coming. | No |

## What the plan prints

One numbered line per call the run will make, then a total:

1. `audio_words_transcribe` on the clip's audio length, billed per started minute.
2. `ai_functions_run` translating the cues into the caption language, priced from the estimated text length. Only when a translation is wanted.
3. One ffmpeg burn per language, with its check frame, at no charge.
4. `sandbox_download_file` for every output, at no charge.

The figures are computed by the script from the sheet and the clip. The agent shows them as printed.

## Outputs

| Name | One per | What it is |
| --- | --- | --- |
| `final.<lang>.mp4` | language | The clip with captions burned in |
| `captions.<lang>.srt` | language | The subtitle file, cue by cue |
| `check.<lang>.png` | language | One frame from the middle of the first cue, to see the placement |
| `words.<lang>.json` | spoken language | Whisper's words with their times (stays in the sandbox) |
| `ledger.jsonl` | run | One line per stage: started, done or failed, with its price (stays in the sandbox) |

## Cue rules the script applies

At most 4 words or 26 characters per cue; a new cue at a pause over 0.6 s; no cue shorter than 0.3 s;
cues never overlap. Font size is the frame height divided by 34; the bottom margin is 12 percent of the
height, or 19 percent for `above_text`.
