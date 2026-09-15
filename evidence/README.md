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

Google Chrome 153.0.8010.47 and Microsoft Edge 153.0.4234.32 also pass both suites using official packages extracted inside the task sandbox. WebKit 26.5 passes after supplying its Ubuntu 24.04 runtime libraries inside that sandbox. Native Safari 26.6.2 passes on the hosted macOS runner: https://github.com/unslothai/unsloth/actions/runs/35030954725/job/104589078176. The macOS browser job still needs a retry: one Google Chrome 152 assertion received a truncated typed value, while the other nine suites passed.

## UI evidence

Queue and settings screenshots render the production components from separate frontend installs at updated base and repair with identical deterministic state, viewport 1000x750, light theme, English, and isolated Chromium contexts. The queue has the same three prompts. Before has zero Steer controls; after has three. Composer preferences are absent before and present after. No model or backend transport is represented by these component screenshots. Composites show the changed surfaces at original scale; uncropped originals were inspected locally.

The identical-toolchain startup build increased from 5381.0 to 5384.0 KiB raw and 1609.0 to 1610.1 KiB compressed, with 84 eager chunks on both sides. The raw budget now covers this measured increase; the compressed budget is unchanged.

## CI follow-up: 9e137a6c262d2921ad7115867c08cc7ab2cdacac

Merged main at f7ab2098 to resolve pre-commit's failed application of formatting to a newly added installer test. Applied only the reproduced five-line formatting change. Frontend tree identical to 6673a5b5; base frontend identical to 0ab40fee.

Reverification: 408 Python tests pass, 4 skip; 101 queue/store/pasted-text tests pass; TypeScript, production build, startup budget, Ruff lint and pinned formatting pass. Ten consecutive Chrome composer interaction suites pass locally with separate browser contexts. The new workflow run retains the macOS Chrome assertion unchanged.

### Queue form regression at 0739d854cc

Confirmed that clicking a reorder handle submitted the enclosing composer form and cleared an unsent draft. The new browser regression fails on `9e137a6c` with one unexpected submission. The three direct row controls now use `type="button"`; the menu trigger already receives that type from Radix. [Radix intentionally leaves the tooltip trigger type unset](https://github.com/radix-ui/primitives/blob/main/packages/react/tooltip/src/tooltip.tsx#L267-L269).

The complete queue browser suite passes in Chromium, Firefox, WebKit, Google Chrome and Microsoft Edge after the fix, including mouse and keyboard activation and rejected steering with an unsent draft. Also passed: 208 focused frontend tests, 25 Python guards, production/test TypeScript, production build, bundle budget, Ruff lint and pinned formatting. The component appearance is unchanged; the earlier screenshots still represent its layout.

Pre-commit and [all ten macOS browser suites](https://github.com/unslothai/unsloth/actions/runs/35032475357/job/104593917077) passed at `9e137a6c`, resolving the earlier intermittent Chrome typing failure without changing its assertion. A fresh review is required for `0739d854cc`.

### Completed

[Latest-head review](https://github.com/unslothai/unsloth/pull/10980#issuecomment-5689317709) found no major issues on `0739d854ccc496393fac1a99827b2ef908741b25`. [Final approval](https://github.com/unslothai/unsloth/pull/10980#pullrequestreview-5216736344) was recorded on that exact head. Pre-commit passed; no checks were failing and no review threads remained unresolved at approval. Other CI jobs were pending, and GitHub reported no required checks.

Squash-merged through GitHub without a protection bypass as [`f4958cee8`](https://github.com/unslothai/unsloth/commit/f4958cee8a92664899fd46ff764578bfe62887b0).
