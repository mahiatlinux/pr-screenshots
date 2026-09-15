# PR 10980 verification

Tested original head `564e9d2ff48fb343cc701a501ad04fc56df3efb7`, original base `1811677f024a88b6cbe6d36e7d3d91b27c2c0190`, updated base `0ab40feeb4cc77400a4abc4afd0bc7b111607213`, prospective merge `48629e461`, and repair `6673a5b5d296f94f6a286318513868ca2b9a1627`.

Linux x86_64, Node 26.8.2, Python 3.12.13, identical npm lockfiles, Playwright 1.62.0. Commands ran inside a credential-free bubblewrap namespace with isolated checkouts, Python environments, caches, and browser contexts.

## Failure model and negative controls

Local-load follow-ups must retain their drafts through preparation and then queue without dispatching on the outgoing model. An explicit later hosted selection must own new prompts, including when the local load subsequently fails. Steering must cancel only its target; queue contents and captured settings must survive unrelated activity.

`ab-*.ts` extracts and executes the checked-out production queue functions with controlled stores and transport. The same three-prompt assertion fails on both base revisions because zero follow-ups are accepted; it passes on original head, prospective merge, and repair with three accepted and dispatched in the requested order. These are queue-engine simulations, not model inference.

`provider-negative.log` records both Queue and Steer failing on the original head because a hosted selection is classified as local. The repaired source passes the factory/dispatch regression and store tests, including switching away and back to the original provider and ignoring sampling-only changes.

## Executed commands

- `npm test`: 7,667 passed.
- `node --experimental-strip-types --test tests/composer-steering.test.ts tests/loading-model-selection.test.ts`: 67 passed.
- `python -m pytest tests/studio/test_multi_chat_prompt_queue_contract.py tests/studio/test_apt_steps_are_bounded.py tests/studio/test_playwright_suites_run_in_ci.py tests/studio/test_macos_slots_per_commit.py tests/studio/test_workflow_guards_run_unfiltered.py -q`: 321 passed.
- `node --experimental-strip-types --test tests/pasted-text-attachment.test.ts`: 34 passed.
- `npm run build`, `npm run typecheck`, `npm run i18n:check`, and `npm run bundle:check`: passed.
- Ruff 0.15.18 lint and repository formatting with Ruff 0.6.9 passed for the three changed Python files.
- ESLint comparison on thread.tsx and chat-runtime-store.ts: the same 62 diagnostics on original head and repair, zero additions.
- `python tests/studio/playwright_prompt_queue_actions.py` and `python tests/studio/playwright_composer_settings.py`: Chromium 151.0.7922.34 and Firefox 153.0 passed. The initial Firefox composer run exhausted its five-second cold-start allowance; the readiness wait passes without changing interaction assertions.

Local WebKit could not launch because the host lacks its required system libraries. Hosted compatibility checks cover the supported runner images and native Safari.

## UI evidence

Queue and settings screenshots render the production components from separate frontend installs at updated base and repair with identical deterministic state, viewport 1000x750, light theme, English, and isolated Chromium contexts. The queue has the same three prompts. Before has zero Steer controls; after has three. Composer preferences are absent before and present after. No model or backend transport is represented by these component screenshots. Composites show the changed surfaces at original scale; uncropped originals were inspected locally.

The identical-toolchain startup build increased from 5381.0 to 5384.0 KiB raw and 1609.0 to 1610.1 KiB compressed, with 84 eager chunks on both sides. The raw budget now covers this measured increase; the compressed budget is unchanged.
