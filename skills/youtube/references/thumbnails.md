
# Thumbnail Creator

Create high click-through YouTube thumbnails and the SEO assets that go with them. This skill orchestrates existing Hyper tools (YouTube research, image generation, AI extraction) through small Python scripts that run in the Hyper sandbox.

## How this skill works

Every workflow is a sandbox script under `scripts/`. The agent reads the matching reference doc, calls the script via the `sandbox` toolkit, and presents the JSON result back to the user. Generated images are persisted as `DBFile`s automatically and shown in chat.

You do **not** chain individual image-generation or YouTube tools yourself unless the user asks for something the scripts don't cover. The scripts are the contract.

## Routing Table

| User intent | Run this script | Reference |
|-------------|-----------------|-----------|
| "Make me a thumbnail for X" | `scripts/generate_thumbnail.py` | Direct generation, optional face/brand/style references |
| "What thumbnails work for `<niche>`?" | `scripts/research_top_thumbnails.py` | Returns top videos + downloaded thumbnails |
| "Make me a thumbnail like the top videos for `<niche>`" | `scripts/clone_top_thumbnail_style.py` | Research → user picks rank → style-cloned generation |
| "Analyse this video's thumbnail concepts" (URL given) | `scripts/analyze_thumbnail_concepts.py` | Returns 5 ready-to-render thumbnail concepts |
| "Give me good titles for this video" | `scripts/generate_seo_titles.py` | Returns 10 styled SEO title options |
| "Write the description for this video" | `scripts/generate_seo_description.py` | Returns hook, summary, takeaways, timestamps, hashtags |

## Composed Workflows

### A. Thumbnail from idea (no face)

1. Confirm the video topic / hook in one sentence with the user.
2. Run `scripts/generate_thumbnail.py` with `prompt=<your refined prompt>`.
3. Show the resulting `file_id` in chat (it renders automatically).

### B. Thumbnail with the user's face

1. Ask the user to upload a clean photo of their face if they haven't already in the thread. Tell them a head-and-shoulders, well-lit photo works best.
2. Once they upload, grab the file's `file_id` from the message attachments (it will look like `file_...`).
3. Run `scripts/generate_thumbnail.py` with `prompt=<refined prompt>` and `face_file_ids=["<file_id>"]`.

### C. Style-cloned thumbnail

1. Run `scripts/clone_top_thumbnail_style.py` with `query=<niche search term>`, `my_topic=<their video idea>`, optional `face_file_id`, and `top_k=5`.
2. The script returns the top `top_k` thumbnails so the user can pick the rank they like.
3. Re-run with `chosen_rank=<n>` to actually generate the cloned thumbnail.

### D. Full YouTube upload package

For users prepping to publish. Run sequentially and present each result before moving to the next:

1. `scripts/research_top_thumbnails.py` — what's working in the niche.
2. `scripts/clone_top_thumbnail_style.py` — pick a winning style, generate the thumbnail.
3. `scripts/generate_seo_titles.py` — 10 title options.
4. `scripts/generate_seo_description.py` — full description with hashtags.

## Rules

1. Treat the user's face like a sensitive asset: only use file_ids the user explicitly uploaded in this thread, and never invent or reuse them across users.
2. When the user mentions a niche or competitor channel, run `research_top_thumbnails` first — never guess what's working.
3. Don't dump base64 image data or thumbnail URLs into the chat. Pass the `file_id` and let the platform render it.
4. For style-cloning, always show the user the top thumbnails first and let them pick the rank. Style-cloning a low-ranked or off-topic video produces bad results.
5. If the user uploads multiple face photos, prefer the most recent and ignore the rest unless they ask you to compose them.
6. Use `images_generate_nano_banana` (flash) for cheap iteration and `pro` only when the thumbnail needs strong rendered text inside the image. Use `images_edit_openai` when composing multiple reference images (face + brand + product).

## Reference

- `references/composition-tips.md` — universal composition rules (rule of thirds, contrast, eye-line).
- `references/youtube-thumbnail-best-practices.md` — YouTube-specific patterns (16:9, mobile-safe text, CTR triggers).
