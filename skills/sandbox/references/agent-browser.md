---
name: Agent Browser
description: Use this reference for compact, ref-based browser automation in sandbox sessions.
---

## Typical Flow

```bash
agent-browser open https://example.com
agent-browser snapshot -i
agent-browser click @e2
agent-browser screenshot <thread-working-directory>/snapshots/page.png
agent-browser close
```

## Why Use It

- Compact output for agent context efficiency.
- Deterministic element refs from accessibility snapshots.
- Better repeatability for click/type/screenshot flows.

## Setup Checks

```bash
agent-browser --version
```

If browser binaries are missing, install Playwright browsers:

```bash
npx playwright install --with-deps chromium
```

## Artifact Handling

- Save screenshots to a known path, then move/copy to `/files/` when sharing.
- Do not leave generated screenshot/video artifacts tracked in git by default.
