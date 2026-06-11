---
name: Atifacts and Sharing
description: Use this reference for preview URLs, file exports, and clean artifact handling.
---

## Filesystem Roles

- `/home/user/` sandbox home
- Current thread sandbox working directory (typically under `/home/user/sessions/<shortid>/`) for cloned app code and working files
- `/tmp/` temporary files/logs
- `/files/` persistent shareable output

## Preview Running Apps

For local dev servers:

```bash
hyper-preview 3000
```

Use explicit ports and confirm server health before sharing preview URLs.

## Share Files with Users

Save deliverables under `/files/`, then generate URL:

```bash
hyper-url /files/report.pdf
```

## Artifact Hygiene

- Keep generated media (screenshots/videos) outside repository tracking unless explicitly requested.
- If needed for user download, copy from working path to a user-accessible destination (for example local Downloads or `/files/` URL).
- Verify git cleanliness before claiming completion when repository artifacts are involved.
