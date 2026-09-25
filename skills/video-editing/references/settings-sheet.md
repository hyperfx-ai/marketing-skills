# The settings sheet

The sheet is the whole job: `pipeline.py plan job.json` prices it and prints the calls it would make,
`pipeline.py run job.json` executes exactly that. The agent fills every field it can from the request and
the attachment and asks only for the rest.

| Field | Values | Default | Source | Priced |
| --- | --- | --- | --- | --- |
| `source_file_id` | a `/files/...` path from `files_list` | — | The attachment as stored, found by `files_list`; never its signed link, never the sandbox copy under `/home/user`. Required. | Whisper is billed on its audio length |
| `source_path` | a sandbox path | `/home/user/video-editing/source.mp4` | Where `files_copy_to_sandbox` put the clip | No |
| `spoken_language` | `auto` or an ISO 639-1 code (`en`, `es`, `fr`, …) | `auto` | Whisper detects it. When the user names the spoken language, use their code; it overrides detection (a short clip with music can be misread). | No |
| `caption_language` | an ISO 639-1 code | the spoken language | The user's request. When they ask for a translation and name no language, ask this one question. | Yes, when it differs from the spoken language |
| `caption_style` | `plain`, `karaoke` | `plain` | `plain` is bold white text with a black outline; `karaoke` lights each word up as it is spoken (yellow on white). | No |
| `caption_position` | `bottom`, `above_text` | `bottom` | `above_text` when the user says the clip has on-screen text at the bottom; the captions sit higher so they do not cover it. | No |
| `outputs` | `captions_only`, `both` | `captions_only` | `both` when a second language is asked for: one captioned MP4 per language. Ignored when `dub` is set. | Yes: `both` adds one translation and one burn |
| `dub` | `none` or an ISO 639-1 code | `none` | The user asks for a dub. The output is the dubbed language only. | Yes: a voice creation when none is on file, one translation, one speech call, one more Whisper pass |
| `voice` | `designed`, `replicated`, or a record name | `designed` | `designed`: the run makes a voice that resembles the clip's speaker (no recording). `replicated`: a clone, needs `consent_file_id`. A name: a record in `/files/voices/`, reused as is. | `designed` and `replicated` cost one voice creation |
| `consent_file_id` | a file id | — | Only for `replicated`: a clip of the speaker saying the consent sentence. | No |
| `delivery` | `chat`, `tiktok` | `chat` | `tiktok` when the user wants the result posted or scheduled on TikTok. | No: TikTok charges nothing |
| `tiktok_caption` | text, at most 2200 characters | — | The user's caption and hashtags, verbatim. Ask for it when `delivery` is `tiktok` and none was given. | No |
| `tiktok_times` | a list of `YYYY-MM-DD HH:MM` local times | `[]` | The times the user named; empty means post now. Never guessed: "schedule it" with no times is a question. | No |
| `tiktok_timezone` | an IANA zone name (`Europe/Amsterdam`) | the user's profile zone | The profile zone when the platform has one, else asked once. Printed beside every time in the plan. | No |
| `tiktok_account` | the connected account's display name, or empty | — | Copied from the workspace's TikTok connections; asked only when there are several. Empty makes the plan refuse with "connect TikTok in Set up". | No |
| `edit_instruction` | text | empty | The user's words for what should change in the picture; for an extension, what happens next. An edit runs when this or `extend_seconds` is set. | Yes: one Omni call per piece |
| `strip_text` | `no`, `yes` | `no` | `yes` when the user wants the on-screen text gone; the script adds one fixed sentence to the instruction. Omni redraws text it is not told to remove. | No |
| `edit_part` | `whole`, `start-end` seconds | `whole` | Only when the user asks for a part of the clip ("just the first five seconds"). Never asked for. | Yes: fewer seconds |
| `edit_resolution` | `auto`, `360p`, `720p` | `auto` | `auto` is 720p when the clip's short side is 720 px or more, else 360p. 1080p and 4K are not offered: Omni publishes no rate for them. | Yes: 720p is about three times 360p |
| `extend_seconds` | `0`, or 3 to 10 | `0` | The seconds the user wants added; Omni continues the scene and the script appends the new seconds after the whole clip. | Yes: priced on the seconds asked for |
| `previous_interaction_id` | the ids from the last completion | empty | When the user refines the edit they just got. One id per piece, in order; the clip is not uploaded again. | Yes: one Omni call per piece |
| `captions` | `yes`, `no` | `yes` | `no` when the user wants only the edit and no captions. | No: `no` skips Whisper |

The defaults in this table are the `Job` defaults in `scripts/pipeline.py`: the script reads the sheet once
into that record, and an absent or empty field takes the default from there.

## What the plan prints

One numbered line per call the run will make, then a total:

1. `videos_edit` once per piece, naming the model, edit or extend, the piece's seconds, the resolution, the aspect ratio, the full instruction as it will be sent, and the estimated price: seconds × Omni's output tokens per second (5,792 at 720p, 1,931 at 360p) × $17.50 per million, plus the input estimate. Only when an edit is asked for. The run bills the actual usage Omni reports.
2. `speech_transcribe` on the clip's audio length, billed per started minute. Skipped when `captions` is `no`.
3. `ai_functions_run` translating the cues into the caption language, priced from the estimated text length. Only when a translation is wanted.
4. For a dub: `speech_voice_analyze` when no voice is named, the translation of the transcript with its character budget, `speech_create` priced from the text length at the vendor's token rate, and `speech_transcribe` again on the dubbed track.
5. One ffmpeg burn per language, with its check frame, at no charge.
6. `files_copy_from_sandbox` for every output into the run's folder `/files/video-editing/<clip>-<time>/`, at no charge.
7. With `delivery: tiktok`: one `TikTok post` line per time, or one `post now` line, each with the account, the caption as it will be sent, the local time and zone, `private until the app is audited`, `AI label: yes` or `no` (yes when the job edits, extends or dubs; code decides), and `$0`; then one line naming TikTok's Music Usage Confirmation, which the user's yes confirms. A time in the past, a caption over 2200 characters, a clip under 3 seconds or no connected account is a one-sentence refusal; an output under 720 px on its short side gets a warning line.

The figures are computed by the script from the sheet and the clip. The agent shows them as printed.

## Outputs

| Name | One per | What it is |
| --- | --- | --- |
| `edited.mp4` | edit | The clip with the edit in place, at the source's size, with the source's audio |
| `extended.mp4` | extension | The clip with the new seconds appended |
| `check.edit.png` | edit without captions | One frame from the middle of the first edited piece |
| `final.<lang>.mp4` | language | The clip (edited, when an edit ran) with captions burned in |
| `captions.<lang>.srt` | language | The subtitle file, cue by cue |
| `check.<lang>.png` | language | One frame from the middle of the first cue, to see the placement |
| `words.<lang>.json` | language | Whisper's words with their times, for the source and for the dubbed track (stays in the sandbox) |
| `transcript.<lang>.txt`, `speech.<lang>.wav`, `dubbed.<lang>.mp4` | dub | The translated transcript, the spoken audio, and the picture with the new audio before captions (stay in the sandbox) |
| `captions.<lang>.ass` | karaoke | The karaoke subtitle the burn used (stays in the sandbox) |
| `tiktok` (in the completion) | TikTok delivery | One scheduled-task id per scheduled post (the platform's deferred call, a row on the Scheduled tasks screen), or the publish id and status of a post made now |
| `ledger.jsonl` | run | One line per stage: started, done or failed, with its price (stays in the sandbox) |

## Voice records

A created voice is saved as `/files/voices/<name>.json` with its Gemini voice id, type, language, the brief
it was made from, and the clip it came from. `speech_create` only accepts a name that has a record, so a
voice is never referred to by id. Delete the file to forget the voice.

## The dub's length

The translation is asked to fit the clip's spoken length (the source's characters per second times its
speech seconds). The spoken take is tempo-fitted only within 0.9 to 1.1; outside that band the script asks
for one re-translation with the budget scaled by the miss, then fits. A second miss is fitted anyway and
noted in the ledger.

## Pieces the script cuts

Omni takes at most 10 s of input. A span of 10 s or less is one piece; a longer span is cut into the fewest
equal pieces of at most 10 s (15 s into two of 7.5 s, 30 s into three of 10 s). Every piece gets the same
instruction; the plan shows one line per piece. An extension feeds Omni the whole clip or its last 10 s.

## Cue rules the script applies

At most 4 words or 26 characters per cue; a new cue at a pause over 0.6 s; no cue shorter than 0.3 s;
cues never overlap. Font size is the frame height divided by 34; the bottom margin is 12 percent of the
height, or 19 percent for `above_text`.
