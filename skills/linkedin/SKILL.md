---
name: linkedin
description: Publish and manage LinkedIn content via the Hyper MCP — text posts, article / link previews, document and PDF posts, organization (company page) posts, and AI-generated text-to-carousel posts. Use when the user wants to post on LinkedIn, share an article on LinkedIn, post to a LinkedIn company page, upload a PDF / document to LinkedIn, or build a LinkedIn carousel from text.
requires_toolkits:
  - linkedin_toolkit
icon: linkedin
short_description: Publish LinkedIn text, article, document, company page, and carousel posts.
---

# LinkedIn

Skill for publishing to LinkedIn through the LinkedIn integration exposed by the Hyper MCP.

## Out of scope — defer to other skills

| Request | Send them to |
| --- | --- |
| Instagram post / Reel / Story | `instagram` |
| TikTok organic posting | `tiktok` |
| TikTok ad campaign | `tiktok-ads` |
| Meta (Facebook / Instagram) ads | `meta-ads` |
| Google Ads campaign | `google-ads` |
| Amazon Sponsored Products campaign | `amazon-ads` |

## Requirements

- **Hyper MCP installed and connected.** [https://app.hyperfx.ai/mcp](https://app.hyperfx.ai/mcp)
- **LinkedIn integration connected** at [https://app.hyperfx.ai/apps](https://app.hyperfx.ai/apps).
- For company-page posts, the connected member account must have permission to post for that organization.

If `search("linkedin_text_posts_create")` does not find `linkedin_text_posts_create`, stop and tell the user to enable Hyper MCP and connect LinkedIn.

### How to run the tools in this skill

Every tool in this skill is named by its canonical tool name. Run it with the call your surface gives you:

| Surface | Find a tool | Run it |
| --- | --- | --- |
| MCP client (Claude, Cursor, Codex, ChatGPT) | `search("<what you want to do>")`, then `describe("<name>")` | `call("<name>", {...})` |
| Hyper CLI | `hyperai search "<what you want to do>"`, then `hyperai describe <name>` | `hyperai call <name> --json '{...}'` |

If a tool is not found, its integration is not connected or not enabled for the workspace: stop and tell the user which integration to connect.

## Tool surface

| Tool | Purpose |
| --- | --- |
| `linkedin_text_posts_create` | Standard member or organization text post; also article / link posts via the article fields. |
| `linkedin_organization_posts_create` | Post explicitly as a company page (when you already know `organization_id`). |
| `linkedin_document_posts_create` | PDF / document post — LinkedIn renders pages as a swipeable document. |
| `linkedin_carousels_create_from_text` | AI text-to-carousel pipeline — generates slides + assembles a PDF + publishes as a document post. |

## Posting Rules

1. Use `linkedin_text_posts_create` for standard member or organization posts.
2. Use `linkedin_organization_posts_create` when the user explicitly wants to post as a company page **and** you already know the `organization_id`.
3. Use `linkedin_document_posts_create` for PDF / document uploads. LinkedIn renders PDF pages as a swipeable document post.
4. Use `linkedin_carousels_create_from_text` when the user wants a text-to-carousel workflow driven by AI-generated slides.

## Article / Link Posts

Do not rely on LinkedIn to scrape Open Graph metadata for API-created posts.

For reliable article posts:

- Provide `article_url`.
- Prefer explicit `article_title`, `article_description`, and `thumbnail_url`.
- If those fields are omitted, the backend may derive them from the shared page metadata, but explicit values are still more reliable.

Use this shape when editing or preparing a LinkedIn article post:

```python
linkedin_text_posts_create(
    text="Caption text",
    article_url="https://example.com/article",
    article_title="Explicit preview title",
    article_description="Explicit preview description",
    thumbnail_url="https://example.com/thumbnail.jpg",
    organization_id="123456789",  # optional
)
```

## Document and Carousel Posts

LinkedIn carousels are implemented as document posts backed by a PDF.

### Native PDF flow

Use `linkedin_document_posts_create` when you already have a PDF URL or stored file ID:

```python
linkedin_document_posts_create(
    text="Caption text",
    title="Deck title",
    document_url="https://example.com/deck.pdf",
    organization_id="123456789",  # optional
)
```

### Text-to-carousel flow

Use `linkedin_carousels_create_from_text` when the user wants the system to build the carousel from a block of source text:

```python
linkedin_carousels_create_from_text(
    text_content="Source content for the slides",
    title="Carousel title",
    caption="LinkedIn caption",
    num_slides=4,
    style="professional",
    color_scheme="blue",
    organization_id="123456789",  # optional
)
```

The current implementation:

- Parses the source text into slide content.
- Generates a single grid image with an image model.
- Splits the grid into individual slide images.
- Assembles a PDF.
- Publishes the PDF as a LinkedIn document post.
- Returns the live post URL — present this to the user to confirm the carousel is live.

Supported slide counts are `4`, `6`, and `9`.

## Manual Slide Editing

The current LinkedIn carousel pipeline is PDF-based. It does not provide a first-class live canvas editing loop before publish.

If a user wants manual refinement:

1. Generate the carousel assets first.
2. Review or edit the generated slide images / PDF externally.
3. Post the final PDF with `linkedin_document_posts_create`.

Do not promise an in-product editable canvas workflow unless the tool is actually available in the current environment.

## Organization Posting

When posting to a company page:

- If you don't know the `organization_id`, call `linkedin_managed_pages_list()` first — it returns all company pages the connected account can post to, with their IDs.
- Use `linkedin_organizations_posts_list_detailed(organization_id=...)` to preview recent posts before publishing — avoids accidental duplicates.
- Pass `organization_id` to whichever posting tool you're using.
- Expect LinkedIn org posting permissions to matter.
- If a post fails with a permissions error, verify that the authenticated account can post to that organization.

## Failure Modes & Recovery

- **Article preview is empty / wrong.** LinkedIn ignored the scraped metadata. Re-call `linkedin_text_posts_create` with explicit `article_title`, `article_description`, and `thumbnail_url`.
- **Permission error on organization post.** Confirm with the user that their LinkedIn account has page-posting permission for the target `organization_id`.
- **`linkedin_carousels_create_from_text` returned an unexpected slide count.** Only `num_slides` of `4`, `6`, or `9` are supported.
- **Document post fails with an invalid URL.** The `document_url` must be a directly-fetchable PDF (no auth, no HTML redirect page).
