# PR 12433 review evidence

- Source PR: `unslothai/unsloth#12433`
- Merge base: `564e98902248871b7be83ceb0a21d594cf9bf7b3`
- Reviewed source head: `30d698708073cb1383bc2cb807489d15c4bef1ee`
- Reviewed mirror merge: `087c252ebfd83b344fbd9df96393103002dd5fea`
- Host: Ubuntu Linux, kernel `7.0.0-34-generic`, x86_64
- Node: `26.8.2`; npm: `11.19.1`
- Python: `3.13.14` in per-worktree uv environments; uv: `0.12.1`
- Playwright: `1.62.0`; Chromium for Testing: `151.0.7922.34`
- Browser contexts: isolated, non-persistent; viewport 1440x900 and 640x700; device scale factor 1

## A/B method

The immutable base worktree remained unchanged. A separate base-derived scene worktree received only the PR's deterministic smoke page and harness so that identical interactions could run against base production components/CSS. Base and head used separate Node installs, Python environments, Vite servers, ports, browser processes, and evidence directories. Tauri IPC was stubbed; no native OS window command was executed.

Expected difference: with a viewport media dialog open, base leaves the custom titlebar sharp; head dims/blurs the titlebar surface while keeping minimize/maximize/close sharp and pointer-accessible.

Commands:

```text
SMOKE_PORT=15491 SMOKE_EXPECT_BLUR=0 SMOKE_EVIDENCE_DIR=artifacts/base-ui python tests/studio/playwright_titlebar_blur.py
SMOKE_PORT=15492 SMOKE_EXPECT_BLUR=1 SMOKE_EVIDENCE_DIR=artifacts/head-ui python tests/studio/playwright_titlebar_blur.py
```

Both runs passed media, dialog, alert, sheet, nested-modal, dismissal, panel-local exclusion, menu exclusion, light/dark, narrow, web/macOS exclusion, minimize/maximize/close dispatch, and titlebar-drag assertions.

Computed styles:

- Base: generated content `none`, blur `none`, controls z-index `auto`, Radix overlay z-index `50`.
- Head: generated content present, opacity `1`, blur `blur(2px)`, pointer-events `none`, titlebar backdrop z-index `90`, controls z-index `100`, Radix overlay z-index `50`.

Pixel-difference bounding boxes were exactly the 40 CSS-pixel titlebar band:

- 1440x150 titlebar crop: `(0, 0, 1440, 40)`, 57,558 changed pixels.
- 1440x900 light frame: `(0, 0, 1440, 40)`, 57,558 changed pixels.
- 1440x900 dark frame: `(0, 0, 1440, 40)`, 57,525 changed pixels.
- 640x700 narrow frame: `(0, 0, 640, 40)`, 25,558 changed pixels.

Every composite was opened and manually inspected. The change matches the expected titlebar-only blur/dim; the dialog and page remain pixel-identical, and the three window-control glyphs remain sharp.

## Other executed checks

```text
npm run build
npm test
python scripts/run_ruff_format.py tests/studio/playwright_titlebar_blur.py  # fixed-point check on writable copy
python -m ruff check tests/studio/playwright_titlebar_blur.py
git diff --check 564e98902248..30d698708073
```

- Production frontend build passed.
- Frontend unit suite passed: 9,753 passed, 0 failed.
- Repository formatter left the committed Playwright file byte-identical; Ruff check passed.
- Net source diff passed `git diff --check`.
