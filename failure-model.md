# PR 12433 failure model

## Claimed behavior

- Base: viewport dialogs blur/dim the page, but the Windows/Linux custom titlebar remains sharp because it paints above Radix overlays.
- Head: a pointer-transparent titlebar pseudo-element mirrors the viewport backdrop while native minimize, maximize, and close controls remain sharp and clickable above it.

## Assumptions to falsify

- `body:has([data-viewport-backdrop="true"][data-state="open"])` matches every supported viewport dialog, alert, and sheet while open and clears after the final one closes.
- The titlebar forms the expected stacking context: pseudo-element z=90 above its surface, controls z=100 above the pseudo-element, and the existing Radix overlay remains z=50.
- Pointer transparency preserves titlebar dragging and native window actions.
- Absolute panel-local dialogs and menus never trigger the viewport effect.
- Web and native macOS configurations do not render the custom titlebar.
- Modern supported browser/WebView implementations support `:has()` and backdrop filtering sufficiently for this rule.

## Regression boundaries

- media viewer, generic dialog, alert dialog, sheet, nested dialogs, dismissal order, panel-local dialog, dropdown menu;
- light/dark themes, narrow viewport, transition start/end, multiple open viewport overlays;
- minimize/maximize/close dispatch and titlebar dragging;
- frontend build/type checks, workflow wiring, formatting, and production component imports.

## Security and performance

- No new privileged data path or native command is introduced.
- The broad `body:has(...)` selector could add style-recalculation work; verify normal interaction remains responsive and the selector is scoped to a rare open-modal state.

## Observable tests

- A/B fixed-state assertions: base has no titlebar pseudo-element; head has opacity 1, blur 2px, pointer-events none, and controls above backdrop.
- Repeat identical production-fixture interactions across base/head and capture labelled screenshots plus computed-style facts.
- Run all branch checks in the added Playwright scene and frontend build/type/unit gates.
- Inspect every overlay primitive and caller for an unmarked supported viewport path.
