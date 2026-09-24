# The settings sheet

The sheet is the whole job: `pipeline.py plan job.json` prices it and prints the calls it would make,
`pipeline.py run job.json` executes exactly that. The agent fills every field it can from the request and
the attachment and asks only for the rest.

| Field | Values | Default | Source | Priced |
| --- | --- | --- | --- | --- |
| `source_file_id` | a file id or a `/files/...` path | — | The attachment as stored, never the sandbox copy under `/home/user`. Required. | Whisper is billed on its audio length |
| `source_path` | a sandbox path | `/home/user/video-editing/source.mp4` | Where `files_copy_to_sandbox` put the clip | No |
| `spoken_language` | `auto` or an ISO 639-1 code (`en`, `es`, `fr`, …) | `auto` | Whisper detects it. When the user names the spoken language, use their code; it overrides detection (a short clip with music can be misread). | No |
| `caption_language` | an ISO 639-1 code | the spoken language | The user's request. When they ask for a translation and name no language, ask this one question. | Yes, when it differs from the spoken language |
| `caption_style` | `plain`, `karaoke` | `plain` | `plain` is bold white text with a black outline; `karaoke` lights each word up as it is spoken (yellow on white). | No |
| `caption_position` | `bottom`, `above_text` | `bottom` | `above_text` when the user says the clip has on-screen text at the bottom; the captions sit higher so they do not cover it. | No |
| `outputs` | `captions_only`, `both` | `captions_only` | `both` when a second language is asked for: one captioned MP4 per language. Ignored when `dub` is set. | Yes: `both` adds one translation and one burn |
| `dub` | `none` or an ISO 639-1 code | `none` | The user asks for a dub. The output is the dubbed language only. | Yes: a voice creation when none is on file, one translation, one speech call, one more Whisper pass |
| `voice` | `designed`, `replicated`, or a record name | `designed` | `designed`: the run makes a voice that resembles the clip's speaker (no recording). `replicated`: a clone, needs `consent_file_id`. A name: a record in `/files/voices/`, reused as is. | `designed` and `replicated` cost one voice creation |
| `consent_file_id` | a file id | — | Only for `replicated`: a clip of the speaker saying the consent sentence. | No |
| `delivery` | `chat` | `chat` | Always `chat` in this version; TikTok delivery is coming. | No |

## What the plan prints

One numbered line per call the run will make, then a total:

1. `audio_words_transcribe` on the clip's audio length, billed per started minute.
2. `ai_functions_run` translating the cues into the caption language, priced from the estimated text length. Only when a translation is wanted.
3. For a dub: `voices_create` when no voice is named, the translation of the transcript with its character budget, `voices_speak` priced from the text length at the vendor's token rate, and `audio_words_transcribe` again on the dubbed track.
4. One ffmpeg burn per language, with its check frame, at no charge.
5. `files_copy_from_sandbox` for every output into the run's folder `/files/video-editing/<clip>-<time>/`, at no charge.

The figures are computed by the script from the sheet and the clip. The agent shows them as printed.

## Outputs

| Name | One per | What it is |
| --- | --- | --- |
| `final.<lang>.mp4` | language | The clip with captions burned in |
| `captions.<lang>.srt` | language | The subtitle file, cue by cue |
| `check.<lang>.png` | language | One frame from the middle of the first cue, to see the placement |
| `words.<lang>.json` | language | Whisper's words with their times, for the source and for the dubbed track (stays in the sandbox) |
| `transcript.<lang>.txt`, `speech.<lang>.wav`, `dubbed.<lang>.mp4` | dub | The translated transcript, the spoken audio, and the picture with the new audio before captions (stay in the sandbox) |
| `captions.<lang>.ass` | karaoke | The karaoke subtitle the burn used (stays in the sandbox) |
| `ledger.jsonl` | run | One line per stage: started, done or failed, with its price (stays in the sandbox) |

## Voice records

A created voice is saved as `/files/voices/<name>.json` with its Gemini voice id, type, language, the brief
it was made from, and the clip it came from. `voices_speak` only accepts a name that has a record, so a
voice is never referred to by id. Delete the file to forget the voice.

## The dub's length

The translation is asked to fit the clip's spoken length (the source's characters per second times its
speech seconds). The spoken take is tempo-fitted only within 0.9 to 1.1; outside that band the script asks
for one re-translation with the budget scaled by the miss, then fits. A second miss is fitted anyway and
noted in the ledger.

## Cue rules the script applies

At most 4 words or 26 characters per cue; a new cue at a pause over 0.6 s; no cue shorter than 0.3 s;
cues never overlap. Font size is the frame height divided by 34; the bottom margin is 12 percent of the
height, or 19 percent for `above_text`.
