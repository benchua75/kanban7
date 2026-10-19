---
description: Security-scan, push to GitHub, write README/About, enable Pages, add CI/CD
argument-hint: [owner/repo or repo URL] [public|private]
allowed-tools: Bash(git:*), Bash(gh:*), Bash(grep:*), Bash(curl:*), Bash(gitleaks:*), Bash(command:*), Bash(ls:*), Bash(mkdir:*), Bash(rm:*), Read, Write, Edit, Glob, Grep, mcp__playwright__browser_navigate, mcp__playwright__browser_resize, mcp__playwright__browser_wait_for, mcp__playwright__browser_take_screenshot, mcp__playwright__browser_close
---

# Publish this project to GitHub

Arguments: `$ARGUMENTS`

Take this repo from local to a published GitHub repository by running the steps below **in order**. Every step is idempotent: check the existing state before you change anything, and update what's there instead of duplicating it.

Hard rules for the whole command:
- **The security scan (step 1) gates every push.** If it finds anything, stop and report it.
- Never ask for, print or store tokens or passwords. Use the existing `gh` login.
- Stage files only by explicit path. Never use `git add -A` / `git add .`.
- Never force-push, rewrite history or delete a remote repo without asking.
- Pushing and making a repo public are outward-facing. Confirm the target repo and visibility once before the first push.
- Respect the constraints in `CLAUDE.md`. Don't change `index.html` behaviour.

---

## Step 0: Collect the GitHub info

1. Parse `$ARGUMENTS` for:
   - the target repo, as `owner/repo` or a `https://github.com/owner/repo(.git)` URL
   - the visibility, `public` or `private`
2. Gather context: `git remote -v`, `git branch --show-current`, `git status --short`, `gh auth status`.
3. If `gh` isn't logged in, stop and tell the user to run `gh auth login` themselves.
4. If the repo or visibility is missing, or differs from the existing `origin`, ask with AskUserQuestion. Offer the `origin` repo as the default. Also ask whether to create the repo if `gh repo view <owner/repo>` says it doesn't exist.
5. Record `OWNER`, `REPO` and `PAGES_URL=https://<owner>.github.io/<repo>/` (lower-case the owner) for later steps.

## Step 1: Security scan (gate)

Make sure nothing sensitive is, or will be, uploaded to the internet.

1. **Secret scan**
   - If `command -v gitleaks` succeeds, run `gitleaks detect --source . --no-banner --redact` and `gitleaks detect --source . --no-banner --redact --log-opts="--all"` for the history.
   - Otherwise, grep the working tree (`git ls-files` plus untracked files you're about to add) and the history (`git log -p --all`) case-insensitively for:
     - `-----BEGIN [A-Z ]*PRIVATE KEY-----`
     - `AKIA[0-9A-Z]{16}`
     - `gh[pousr]_[A-Za-z0-9]{36}`, `github_pat_[A-Za-z0-9_]{22,}`
     - `xox[baprs]-[A-Za-z0-9-]+`
     - `sk-[A-Za-z0-9]{20,}`, `sk_live_[A-Za-z0-9]+`
     - `(api[_-]?key|secret|passw(or)?d|token|bearer)\s*[:=]\s*['"][^'"]{8,}`
   - Review each hit. Placeholders and docs examples are fine. Real values are not.
2. **Sensitive files.** Check that none of these are tracked or about to be staged: `.env*`, `*.pem`, `*.key`, `*.p12`, `id_rsa*`, `*.log`, `.DS_Store`, `.claude/settings.local.json`, `node_modules/`, `*.sqlite`, backup or dump files. Make sure `.gitignore` lists them, and add missing entries.
3. **PII and emails.** List every email address in tracked files. `FORMSUBMIT_EMAIL` in `index.html` should be the placeholder `pmo-demo@example.com`. If it holds a real address, warn the user: publishing exposes it, and FormSubmit would send form data there. Ask before you continue.
4. **No unexpected network calls.** Run the project constraint check. It must print nothing:
   ```bash
   grep -nE 'localStorage|sessionStorage|indexedDB|document\.cookie|<link|src="http|innerHTML|@import' index.html
   ```
   List every `http(s)://` URL in `index.html`. The only outbound endpoint allowed is `https://formsubmit.co/...`. SVG namespace URLs (`http://www.w3.org/...`) are fine.
5. **Branding.** Confirm there are no real bank names, logos or trademarks (for example "UOB"). The bank must stay the fictitious "Northbridge Bank".
6. **Result.** Print a short scan report with the checks, PASS/FAIL and `file:line` for each finding. **If anything fails, stop here.** Don't push until the user fixes it or explicitly accepts the risk.

## Step 2: Create or update README.md

If `README.md` exists, read it first and keep sections the user wrote. Otherwise create it with:

- `# <Project title>` (take it from `<title>` in `index.html`) and a one-line description. Add a note that Northbridge Bank is **fictitious** and this is a demo/training app.
- **Badges** (shields.io, one line):
  - `![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white)`
  - `![CSS3](https://img.shields.io/badge/CSS3-1572B6?logo=css3&logoColor=white)`
  - `![JavaScript](https://img.shields.io/badge/JavaScript-vanilla-F7DF1E?logo=javascript&logoColor=black)`
  - `![No dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)`
  - CI status: `[![CI](https://github.com/OWNER/REPO/actions/workflows/ci-pages.yml/badge.svg)](https://github.com/OWNER/REPO/actions/workflows/ci-pages.yml)`
  - Pages: `[![GitHub Pages](https://img.shields.io/badge/demo-GitHub%20Pages-blue?logo=github)](PAGES_URL)`
  - License badge, only if a LICENSE file exists or the user wants one added
- **Live demo:** a link to `PAGES_URL`.
- **Screenshot:** `![<short description of the board>](docs/screenshot.png)` directly under the live demo link (captured in step 2b).
- **Features:** taken from `index.html` and `CLAUDE.md` (Kanban stages, WIP limit, drag-and-drop, Alt+←/→ keyboard moves, filters, RAG/priority, detail dialog, new project request form via FormSubmit, summary).
- **Tech stack:** a single `index.html` with vanilla HTML/CSS/JS, no frameworks, build, CDN or external assets.
- **Installation:**
  ```bash
  git clone https://github.com/OWNER/REPO.git
  cd REPO
  ```
  No npm install and no build step.
- **How to run:**
  - Double-click `index.html`, or `open index.html` (macOS), `start index.html` (Windows) or `xdg-open index.html` (Linux).
  - Or use the live demo at `PAGES_URL`.
  - Notes: there's no persistence, so a refresh resets to the seed data. To make the request form send email, set `FORMSUBMIT_EMAIL` in `index.html` and confirm FormSubmit's activation email.
- **Project structure:** a short tree, including `docs/screenshot.png` and `.mcp.json`.
- **CI/CD:** a short description of the workflow from step 3.
- **Disclaimer:** fictitious bank, not affiliated with any real institution.

## Step 2b: Capture the README screenshot (Playwright MCP)

Use the project's Playwright MCP server (`.mcp.json`) to capture the board and keep `docs/screenshot.png` current.

1. If the `mcp__playwright__*` tools aren't available, tell the user to install Node.js, restart the session and approve the `playwright` server. Skip this step (keep any existing screenshot) rather than failing the whole publish.
2. `mkdir -p docs`.
3. `mcp__playwright__browser_resize` to `width: 1440`, `height: 900`.
4. `mcp__playwright__browser_navigate` to `file://<absolute repo root>/index.html`, so the screenshot shows the code you're about to push. If `file://` is blocked, use `PAGES_URL` instead, but only once it serves the current version.
5. `mcp__playwright__browser_wait_for` with `time: 1` so the board finishes rendering.
6. `mcp__playwright__browser_take_screenshot` with `type: "png"` and `filename: "<absolute repo root>/docs/screenshot.png"`. Use the viewport, not `fullPage`.
7. `mcp__playwright__browser_close`.
8. Read the image back and check that it shows the board with all five columns and the seed data, and no error, blank page or open dialog. Delete any stray `page-*.yml` snapshot files the server wrote under the repo.
9. Make sure `README.md` embeds it as described in step 2.

## Step 3: CI/CD with GitHub Actions

Create or update `.github/workflows/ci-pages.yml`:

```yaml
name: CI & Pages

on:
  push:
    branches: [main]
  pull_request:
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: pages-${{ github.ref }}
  cancel-in-progress: true

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Secret scan (gitleaks)
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      - name: Project constraint check
        run: |
          if grep -nE 'localStorage|sessionStorage|indexedDB|document\.cookie|<link|src="http|innerHTML|@import' index.html; then
            echo "::error::Constraint violation in index.html (see CLAUDE.md)"; exit 1
          fi
      - name: HTML sanity check
        run: |
          test -f index.html
          grep -q '<!DOCTYPE html>' index.html || grep -qi '<!doctype html>' index.html
          grep -q '<title>' index.html

  deploy:
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    needs: check
    runs-on: ubuntu-latest
    permissions:
      pages: write
      id-token: write
      contents: read
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/checkout@v4
      - name: Stage site (index.html only)
        run: mkdir -p _site && cp index.html _site/
      - uses: actions/configure-pages@v5
      - uses: actions/upload-pages-artifact@v3
        with:
          path: _site
      - id: deployment
        uses: actions/deploy-pages@v4
```

Only `index.html` is published to Pages. `CLAUDE.md`, `.claude/` and other repo files are never deployed.

## Step 4: Commit and push

1. Stage only these files, by explicit path: `README.md`, `.github/workflows/ci-pages.yml`, `.gitignore`, `docs/screenshot.png`, `.mcp.json`, and any file the user asked for (for example `LICENSE`). Also stage `.claude/commands/publish-github.md` if it isn't committed yet.
2. Re-run the step 1 secret and sensitive-file checks on `git diff --cached`. Stop if anything turns up.
3. Commit with a clear message that ends with the attribution trailer the session requires.
4. Push:
   - If the repo doesn't exist and the user approved creating it, run `gh repo create OWNER/REPO --<visibility> --source . --remote origin --push`.
   - Otherwise, make sure `origin` points to `https://github.com/OWNER/REPO.git` (`git remote add` or `git remote set-url`), then run `git push -u origin <current-branch>`.
   - If the push is rejected as non-fast-forward, stop and ask. Never force-push.

## Step 5: Enable GitHub Pages (Actions build)

1. Check the current state: `gh api repos/OWNER/REPO/pages`. A 404 means Pages isn't enabled.
2. To enable it: `gh api -X POST repos/OWNER/REPO/pages -f build_type=workflow`. If Pages exists with another build type, run `gh api -X PUT repos/OWNER/REPO/pages -f build_type=workflow`.
3. Pages on a private repo needs a paid plan. If the API refuses, tell the user and suggest making the repo public, but don't change it without asking.
4. Trigger or watch the run: `gh run list --workflow ci-pages.yml -L 1`, then `gh run watch <id> --exit-status`. If the push ran before Pages was enabled and the deploy failed, re-run it with `gh workflow run ci-pages.yml` and watch again.
5. Read the final URL with `gh api repos/OWNER/REPO/pages --jq .html_url`. Use it as `PAGES_URL`, and fix the README if it differs.

## Step 6: Update the repo About section

```bash
gh repo edit OWNER/REPO \
  --description "IT PMO Kanban board demo for a fictitious bank: single-file vanilla HTML/CSS/JS, no dependencies" \
  --homepage "PAGES_URL" \
  --add-topic kanban --add-topic project-management --add-topic vanilla-js \
  --add-topic html --add-topic css --add-topic javascript \
  --add-topic github-pages --add-topic demo
```

## Step 7: Verify and report

1. `gh repo view OWNER/REPO --json url,visibility,description,homepageUrl,repositoryTopics`
2. `gh run list --workflow ci-pages.yml -L 1`. The latest run should be green.
3. `curl -sI PAGES_URL` should return HTTP 200 (allow a minute or two after the first deploy).
4. `git ls-files` lists everything that's public. Confirm none of it is sensitive (no `.claude/settings.local.json`, `.DS_Store`, `.env`, keys).
5. Finish with a short summary:
   - Repo URL and visibility
   - Live Pages URL
   - CI status
   - The About section: description, homepage and topics
   - The security scan result, and any warnings the user accepted
