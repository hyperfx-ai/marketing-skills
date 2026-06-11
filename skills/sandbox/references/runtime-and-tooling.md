---
name: Runtime and Tooling
description: Use this reference when you need to verify sandbox runtime/tooling before project work.
---

## Expected Baseline

- `node` / `npx`
- `pnpm`
- `bun`
- `uv` (Python package manager)
- `vp` (Vite+ unified frontend toolchain: dev, build, lint, format)
- `python` (with venv at `/home/user/.venv`)
- `agent-browser` (snapshots, screenshots, interactions)

Do not assume all are present in every environment version. Verify first.

## Verification Commands

```bash
node --version
pnpm --version
bun --version
uv --version
vp --version
python --version
agent-browser --version
```

If any command fails, install the missing tool before continuing.

## Sandbox Start Pattern

```python
sandbox_start()
```

Use the current thread's sandbox working directory as the app root for cloned repositories. In practice this is the active directory attached to the thread, typically under `/home/user/sessions/<shortid>`.

## UI Modes

The product now has two sandbox UI modes:

- Python/data-analysis mode: native `python(code)` / `javascript(code)` results show logs, charts, and file artifacts in the sandbox results surface.
- App-builder mode: IDE + preview stay rooted to the current thread's sandbox working directory.

Do not try to put Python analysis outputs into the app IDE tree. Keep app source in the current thread's sandbox working directory, and let analysis outputs surface through the sandbox results UI or explicit file sharing.

## Pre-installed Python Libraries

The sandbox venv includes data science libraries out of the box:

- pandas, numpy, scipy
- matplotlib, seaborn, plotly
- httpx, aiohttp, openpyxl
- Pillow, markdown
- reportlab, pdf2image, weasyprint

PDF helpers available in the template:
- `poppler-utils` for `pdf2image`
- Cairo/Pango/GDK Pixbuf libraries for `weasyprint`

## Guardrails

- Check runtime health before clone/build commands.
- Keep commands deterministic and non-interactive.
- If a tool is missing, install explicitly and then re-verify with `--version`.
- Use `pnpm` for package installation (not npm or yarn).
- Use `vp dev` to start frontend dev servers (not `pnpm dev`, `npx vite`, or raw `vite`).
- Use `vp build` to build frontend projects, `vp check` for linting and formatting.
- **NEVER** start dev servers with shell `&` (e.g. `vp dev &`). Use `shell(command, background=True)` instead. Shell `&` freezes the thread.
- Use direct shell checks like `curl` and `lsof` for app health and port validation.
- For app work, keep file browsing scoped to the current thread's sandbox working directory.
- Hidden files should be treated as out of scope for normal file-tree browsing unless explicitly requested.
