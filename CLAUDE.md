# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A demo/training IT Project Management Kanban board for a **fictitious** bank ("Northbridge Bank IT PMO"). The whole app is one file: `index.html` (markup + `<style>` + one `<script>` IIFE).

## Hard constraints (from the original brief — do not violate)

- Vanilla HTML/CSS/JS only. No frameworks, libraries, build step, bundler or npm.
- Single file `index.html`; must work by double-clicking (`file://`), no server.
- No external resources: no CDNs, web fonts or image files. System font stack; icons are inline SVG or Unicode glyphs.
- **No persistence.** State lives only in the in-memory `projects` array. Never use localStorage, sessionStorage, IndexedDB, cookies or any storage API. A refresh resets to `SEED`; this is intended, and the UI notice bar says so.
- The only backend is FormSubmit (`https://formsubmit.co/ajax/<email>`) for the "New project request" form.
- No real bank branding: no UOB logo, trademarks or imitation of official systems. Text wordmark + corporate blue palette only.

## Running / checking

There is no build, lint or test tooling. Open the file directly:

```bash
open index.html
```

Constraint check (should print nothing):

```bash
grep -nE 'localStorage|sessionStorage|indexedDB|document\.cookie|<link|src="http|innerHTML|@import' index.html
```

## Script architecture

- **Config at top:** `FORMSUBMIT_EMAIL` (currently the placeholder `pmo-demo@example.com`). While it equals `FORMSUBMIT_PLACEHOLDER`, the form never sends. It shows a warning and offers "Add to board without sending" instead.
- **Domain constants:** `COLUMNS` (stage keys/names; `wip` limit on In Progress), `PRIORITIES`, `RAGS`, `DEPARTMENTS`. Selects in the filters and dialogs are populated from these via `fillSelect`, so add values here, not in markup.
- **State:** `projects` (cloned from `SEED`), `filters`, `nextIdNum` (IDs are `PRJ-<n>`), `draggedId`, `editingId`.
- **Rendering:** `render(focusId?)` rebuilds the whole board and summary from `projects` on every change; there's no diffing. Order of cards within a column = order in the `projects` array. DOM is built with `el()` + `textContent` (no `innerHTML`, to avoid XSS from user input).
- **Moves:** all stage changes go through `moveProject(id, status, beforeId)`, which reorders the array, forces progress to 100 for Done, and toasts. Used by HTML5 drag-and-drop (delegated listeners on `#board`), Alt+←/→ keyboard moves, and the detail dialog.
- **Dialogs:** native `<dialog>` with `showModal()`; `[data-close]` elements and backdrop clicks close them; focus returns to the trigger card (re-found by `editingId` after re-render).
- **FormSubmit flow:** `formNew` submit → validate → JSON POST with `_subject`, `_template: 'table'`, `_captcha: 'false'`, `_honey` honeypot. On `success === "true"` → `addRequestToBoard(d, true)` (adds to Backlog). On error/network failure → `showSubmitError` and reveal the local-add button. FormSubmit may reject `file://` (null origin) requests; the error path covers this.

## Testing notes

- The Claude desktop Browser pane renders `file://` pages as a static `data:` snapshot. `location.reload()` and re-navigating in the same tab do **not** reload it, so to verify the reset-on-refresh behaviour, open a new tab.
- The first real FormSubmit submission to a new address triggers an activation email that must be confirmed before deliveries arrive.
