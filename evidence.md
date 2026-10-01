# PR 12433 review evidence

- Source PR: `unslothai/unsloth#12433`
- Merge base: `564e98902248871b7be83ceb0a21d594cf9bf7b3`
- Initial source head: `30d698708073cb1383bc2cb807489d15c4bef1ee`
- Final repaired source head: `20719ef0947044ca116352518669fd67b1a86c99`
- Final reviewed mirror head: `6918c39c3`
- Host: Ubuntu Linux, kernel `7.0.0-34-generic`, x86_64
- Node: `26.8.2`; npm: `11.19.1`
- Python: `3.13.14` in per-worktree uv environments; uv: `0.12.1`
- Playwright: `1.62.0`; Chromium for Testing: `151.0.7922.34`; Playwright Firefox: `153.0`
- Browser contexts: isolated, non-persistent; viewport 1440x900 and 640x700; device scale factor 1

## A/B method

The immutable base worktree remained unchanged. A separate base-derived scene worktree received only the PR's deterministic smoke page and harness so that identical interactions could run against base production components/CSS. Base and head used separate Node installs, Python environments, Vite servers, ports, browser processes, and evidence directories. Tauri IPC was stubbed; no native OS window command was executed.

Expected difference: with a viewport media dialog open, base leaves the custom titlebar sharp; head dims/blurs the titlebar surface while keeping minimize/maximize/close sharp and pointer-accessible.

Commands:

```text
SMOKE_PORT=5495 SMOKE_EXPECT_BLUR=0 SMOKE_EVIDENCE_DIR=artifacts/base-final-ui python tests/studio/playwright_titlebar_blur.py
SMOKE_PORT=5497 SMOKE_EXPECT_BLUR=1 SMOKE_EVIDENCE_DIR=artifacts/final-ui python tests/studio/playwright_titlebar_blur.py
```

Both runs passed media, dialog, alert, sheet, the real guided-tour component, nested-modal, dismissal, panel-local exclusion, menu exclusion, light/dark, narrow, web/macOS exclusion, minimize/maximize/close dispatch, and titlebar-drag assertions.

Computed styles:

- Base: generated content `none`, blur `none`, controls z-index `auto`, Radix overlay z-index `50`.
- Head: generated content present, opacity `1`, blur `blur(2px)`, pointer-events `none`, titlebar backdrop z-index `90`, controls z-index `100`, Radix overlay z-index `50`.
- Guided tour on base: generated content `none`, blur `none`.
- Guided tour on the repaired head: generated content present, opacity `1`, blur `blur(2px)`, pointer-events `none`, titlebar backdrop z-index `90`, controls z-index `100`.

Pixel-difference bounding boxes were exactly the 40 CSS-pixel titlebar band:

- 1440x150 titlebar crop: `(0, 0, 1440, 40)`, 57,558 changed pixels.
- 1440x900 light frame: `(0, 0, 1440, 40)`, 57,558 changed pixels.
- 1440x900 dark frame: `(0, 0, 1440, 40)`, 57,525 changed pixels.
- 640x700 narrow frame: `(0, 0, 640, 40)`, 25,558 changed pixels.

Every composite was opened and manually inspected. The change matches the expected titlebar-only blur/dim; the dialog and page remain pixel-identical, and the three window-control glyphs remain sharp.

The guided-tour composite was also manually inspected. Its animated spotlight and card are shown in both frames; the repaired frame adds the missing titlebar effect while retaining sharp native window controls.

The same A/B interaction matrix also passed in Playwright Firefox 153.0 with the same computed style facts. The 1440px Firefox captures differed only in the 40px titlebar band and were manually inspected; Chromium remains the primary evidence because the production smoke harness and CI target Chromium.

## Review findings and repairs

Codex reported three possible defects on the mirror. Two were confirmed and repaired:

- The document-wide descendant `body:has(...)` was replaced by a direct-child selector. In a synthetic 600,686-element DOM, 40 append-plus-forced-style samples measured 26.8 ms median, 33.2 ms p95 with the descendant selector versus 14.8 ms median, 16.7 ms p95 with the direct-child selector. The live Radix overlays were confirmed as direct children of `body`.
- `GuidedTour` uses a custom fixed Radix overlay rather than the shared dialog overlay. It now publishes `data-viewport-backdrop`, and the A/B browser scene opens the real component and asserts the computed titlebar effect.

The narrow-navbar report was not reachable. `Navbar` can take its mobile branch only when `useIsMobileShell()` returns `useIsMobile() && !isTauri`, while the custom titlebar requires `isTauri`. The 640 px Tauri browser fixture confirmed that no mobile sidebar trigger exists while the custom titlebar is active. The review thread records this evidence and was resolved without adding dead styling.

Fix commit `6918c39c3` was pushed to the mirror and landed back to the contributor branch with `mirror-pr.py`, producing source commit `20719ef0947044ca116352518669fd67b1a86c99`.

## Current-main mirror

The `mirror-pr.py` review target merged the initial source head onto upstream `c1e5a56fe626c060005c9671f95c388ef6bd6953`, then received fix commit `6918c39c3`. The GitGuardian-reported `studio/backend/tests/test_mcp_image.py` has no net diff from the mirror base.

- Production frontend build passed on the mirror tree.
- The four titlebar layering unit tests passed on the final source tree.
- The full Chromium interaction scene passed in an isolated mirror rerun with the same z-index and blur facts.
- One earlier mirror scene run, executed concurrently with the production build and full unit suite, timed out waiting for a stubbed window-command dispatch. No code changed; the immediate isolated rerun passed in 12 seconds, matching the source-head run. This was treated as CPU-saturation flake rather than a reachable product failure.

## Other executed checks

```text
npm run build
npm test
python scripts/run_ruff_format.py tests/studio/playwright_titlebar_blur.py  # fixed-point check on writable copy
python -m ruff check tests/studio/playwright_titlebar_blur.py
git diff --check 564e98902248..20719ef09470
```

- Production frontend build passed.
- Frontend unit suite passed: 9,759 passed, 0 failed.
- Repository formatter left the committed Playwright file byte-identical; Ruff check passed.
- Net source diff passed `git diff --check`.
