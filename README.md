# PR 10958 verification

The screenshots compare the exact merge base with commit 8621a4297566a7c1633bc81b8d99f9b28b425890. Originals, labelled composites, measured geometry, dependency versions and executed-check logs are included.

The application ran from separate production frontend builds and live FastAPI servers, each with its own virtual environment, SQLite database, authentication, caches and browser context. All test processes ran in a credential-free Bubblewrap sandbox. Conversations were seeded through the real chat-history API; no generation is involved in these layout checks.

## Commands

- `npm run typecheck`
- `npm run build`
- `npm run i18n:check:strict`
- `node --experimental-strip-types --test tests/appearance-accent-vars.test.ts tests/personalization-locale-hydration.test.ts tests/sidebar-nav-migration.test.ts tests/sidebar-nav-backend-parity.test.ts`
- `python -m pytest studio/backend/tests/test_personalization_settings.py -q`
- `python tests/studio/playwright_chat_width.py` against the running, authenticated Studio with a saved conversation. Set `BASE_URL`, `STUDIO_PW` and `CHAT_THREAD_ID` for the disposable instance.

## Negative controls

The browser regression fails on the original PR head and its prospective merge: at 390px Full makes messages 220px and the composer 270px, versus Wide at 340px and 366px. The repair restores Full to 340px and 366px. The same assertion passes in Chromium and Firefox and on the repaired merge.

The PR's personalization cases, run against the merge base, produce seven expected failures because the field, validation and presence metadata do not exist there; thirty existing cases pass. All 37 pass on the original head, final head and original merge.

## Observed UI behavior

At 1920px with the sidebar open, messages measure 744px on base, 1128px on Wide and 1470px on Full in Chromium. The composer measures 736px, 1152px and 1494px respectively. Editing and the welcome composer expand, the shared comparison composer expands, and collapsing the sidebar increases Full's message width to 1702px. All seven tested viewport widths retain Standard <= Wide <= Full and have no horizontal page overflow.

Live settings writes, reload persistence and reset to Standard passed. The settings screenshot shows the new control in Preferences. Full has no extra narrow-pane cost after the repair.

## Follow-up repair and merge conflict

Commit 8621a4297 removes the extra welcome padding for Wide and Full. The added transition assertion fails on 3120f1374 and passes on the final build in Chromium and Firefox. Wide remains 1152px when moving between empty and active threads. In Chromium, Full's welcome composer now matches the dock at 1494px.

Upstream 1811677f0 (#10966) landed during verification and conflicts with this PR in the comparison wrapper. The reviewed resolution keeps its symmetric padding and this PR's width cap. The candidate passes type checks, the production build and the complete Chromium scenario including the standalone regression. `merge-candidate.patch` applies the entire final PR plus that resolution to upstream 1811677f0; `conflict-resolution.diff` shows the conflict-marker resolution. The candidate is not pushed.
