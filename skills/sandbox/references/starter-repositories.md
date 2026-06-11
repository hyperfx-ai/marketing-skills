---
name: Starter Repositories
description: Use this reference when initializing projects in the sandbox.
---

## Clone-First Rule

Do not scaffold from pre-baked templates in the sandbox image. Always clone a starter repository.

Workspace root:

```bash
cd <thread-working-directory>
```

## Generic Clone Workflow

```bash
cd <thread-working-directory>
git clone <repo-url> app
cd <thread-working-directory>/app
pnpm install
```

Start the dev server with `shell()` using `background=True`:

```python
shell("cd <thread-working-directory>/app && vp dev", background=True)
```

`vp` (Vite+) is the standard frontend toolchain. It wraps Vite, Vitest, Oxlint, and Oxfmt into a single CLI. Use `vp dev` to start dev servers, `vp build` to build, `vp check` to lint and format.

**NEVER** start dev servers with shell `&` (e.g. `pnpm dev &`). This freezes the thread. Always use `background=True`.

## Verify the App is Running

After starting the dev server:

```python
sandbox_check_running_port(port=8080)
sandbox_health_check(port=8080)
sandbox_get_preview_url(port=8080)
```

The React Router + shadcn starter uses port 8080. Reveal.js uses port 3000.

## Available Starters

| Starter | Repo URL | Dev Port | Use Case |
|---------|----------|----------|----------|
| React Router + shadcn | `https://github.com/multigen-ai/hyper-sandbox-1.git` | 8080 | Marketing sites, landing pages, dashboards, websites, apps |
| Reveal.js Slides | `https://github.com/multigen-ai/reveal-slides-template.git` | 3000 | Presentations, slide decks, pitch decks |

The React Router + shadcn starter includes: React 19, React Router v7 (framework mode), Tailwind CSS v4, shadcn/ui (all components pre-installed), and Vite. Flat project structure — source files live in `app/`, routes in `app/routes/`, components in `app/components/`.

**Default**: The React Router + shadcn starter is the default for ALL web work (websites, landing pages, dashboards, apps). Use it unless the user explicitly requests a different stack. Never ask which starter to use.

## Notes

- Use `pnpm` for package installation (not npm/yarn/bun).
- Use `vp dev` to start dev servers (not `pnpm dev` or `npx vite`).
- For app work, always use the sandbox active directory rather than assuming a fixed app path.
- For monorepos, install from the relevant sub-directory (e.g. `cd client && pnpm install`).
- For Python projects, use `uv` to manage dependencies instead of pip.
