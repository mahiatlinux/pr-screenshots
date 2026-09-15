# PR 7701 verification

Tested original head d168257c0fe70dcba5f6f5bfc35d95c6911a2862 and repaired head fab1c3a7d1132f91ce186628e23cd1478aa74afc. Screenshot and live API controls use current merge base 0ab40feeb4cc77400a4abc4afd0bc7b111607213; the persistence negative control uses original merge base 8ee07d6ae61e92544f63a733daf86f9b6a6b0ef2.

Linux x86_64, Python 3.12.13, Node 26.8.2, Pydantic 2.13.4, Transformers 5.4.0, CPU PyTorch 2.14.0, llama.cpp b10909. Separate worktrees, venvs, homes, caches and browser contexts; every PR process ran inside a credential-free bubblewrap sandbox.

## Commands

- `python -m pytest studio/backend/tests/test_openai_auto_switch.py studio/backend/tests/test_model_override_schema_compatibility.py studio/backend/tests/test_validate_diffusion_unknown.py studio/backend/tests/test_llama_server_args.py studio/backend/tests/test_llama_cpp_mtp_detection.py studio/backend/tests/test_gguf_reload_inheritance.py tests/studio/test_chat_preset_load_config.py tests/studio/test_model_picker_contracts.py -q --tb=short --timeout=60`: 1673 passed, 1 skipped, 3 subtests passed.
- `cd studio/frontend && npm run typecheck && npm test && npm run build`: passed, 7609 tests.
- `python -m ruff check studio/backend/core/inference/llama_cpp.py studio/backend/utils/openai_auto_switch_settings.py`: passed.
- `git diff --check`: passed.

## Real API scenario

Qwen3-0.6B-Q4_K_M.gguf, context 2048, manual GPU layers 0, one parallel slot, speculation off. POST `/api/inference/validate`, POST `/api/inference/load` with budget 32 and padded exhaustion message, GET `/api/inference/status`, then POST `/v1/chat/completions` with temperature 0, max_tokens 128 and the prompt “What is 7 times 8? Think briefly.” Base ignored the new settings and used all 128 completion tokens on reasoning. Repaired head echoed the requested/effective pair, inserted the exhaustion message, and answered 56 in 52 completion tokens. These are single smoke observations, not benchmarks.

## UI scenario

Chromium 145.0.7632.6, Playwright 1.58.2, 1440x1100, en-US, light theme. Open run settings for the same locally loaded model. Base has neither control; repaired head displays budget 32 and the message. Edit to zero and Stop., enable Remember for this model, reload the real model, refresh the browser: both settings remain intact. Screenshots were inspected manually.

## Compatibility probe

Official llama.cpp b6000 and b10909 CPU binaries: defaults and zero parse successfully on both; b6000 rejects positive budgets before launch, while b10909 accepts 32. Sources: https://github.com/ggml-org/llama.cpp/releases/tag/b6000 and https://github.com/ggml-org/llama.cpp/releases/tag/b10909; flag contract: https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md.

## Final repair round

Head `8e24c8c8c741a9d8ef1f38846299648b65c6e88a`, base `f7ab2098fa27d73e5f2e0645b5a9c4bb0b6f5c3e`. Merged the current base to reproduce GitHub's merge result, then corrected its installer test formatting without changing the AST. The full Python lint pass succeeded. The backend command above plus `studio/backend/tests/test_video_chat_completions_behaviour.py tests/python/test_installer_differential_comparer.py` passed: 1833 tests, 5 skipped, 3 subtests passed. The frontend suite passed 7609 tests before the six-line summary fix; after that fix, the four new summary tests, typecheck and production build passed.

The saved API settings summary previously showed App defaults for both a zero reasoning budget and a message-only override. The focused test had three failures before repair and four passes after. Run `cd studio/frontend && node --experimental-strip-types --test tests/saved-reasoning-settings-summary.test.ts`. Chromium screenshots `summary-before.png` and `summary-after.png` capture the actual settings API and rendered panel before and after the repair. Both were manually inspected.

Repeated the real Studio CPU API experiment on the final base and repaired head with the same inputs and observed the same 128-token reasoning-only base result versus a completed 52-token answer. Firefox 146.0.1 passed the visible controls, edit, remember, actual model reload and page-refresh scenario on the final head. Existing screenshots labeled fab1c3a7d retain their original tested SHA.

## Requested intent and managed wrapper repair

Latest tested head: `a0a32013278e56d37f7ca85efdd034d6ce07a236`. Control: `8e24c8c8c741a9d8ef1f38846299648b65c6e88a` in a separate install, environment and application home. Both used `LLAMA_ARG_THINK_BUDGET=32` and `LLAMA_ARG_THINK_BUDGET_MESSAGE=Conclude now.` with an initial request of -1 and an empty message.

The actual Chromium UI on the control turned an unrelated batch-size edit into a request and saved override for budget 32/message Conclude now. The repaired UI sends -1/empty, reports effective budget 32 and saves only the unrelated edit. `inherited-merge.png` and `inherited-fix.png` were manually inspected. Both installs also completed real Qwen3-0.6B CPU inference with the inherited budget.

- `python -m pytest studio/backend/tests/test_openai_auto_switch.py studio/backend/tests/test_llama_cpp_mtp_detection.py studio/backend/tests/test_gguf_reload_inheritance.py studio/backend/tests/test_llama_server_args.py -q --tb=short --timeout=60`: 1420 passed, 1 skipped.
- `node --experimental-strip-types --test tests/active-reasoning-intent.test.ts tests/saved-reasoning-settings-summary.test.ts tests/reasoning-budget-config.test.ts tests/reasoning-budget-rollback.test.ts`: 16 passed. Typecheck and production build passed afterward.
- The active-config negative control fails two tests; the positive-budget wrapper negative control raises the reproduced false rejection. The repaired tests pass.
- Real official b6000 and b10909 CPU binary probes pass the same version matrix after the wrapper-path correction. The wrapper regression uses controlled subprocess outcomes on Linux, not a native macOS execution claim. Apple documents why launching a protected shell purges DYLD variables: https://developer.apple.com/library/archive/documentation/Security/Conceptual/System_Integrity_Protection_Guide/RuntimeProtections/RuntimeProtections.html.

The initial scoped backend invocation overlapped the formatter and invalidated inspect-source line offsets in six source-inspection tests; the recorded successful run above started after formatting completed. No test was weakened.

## Resident adoption and shared snapshots

Head `4b912408e44f48c01c40e749432e423911424bcd` includes the requested-value resident comparison (`bb859566a`) and the corresponding snapshot used by ordinary re-selection, presets and failed-switch restoration. The old comparator failed two focused tests; the shared snapshot failed all three parity scenarios before repair. Older backends without request echoes retain their effective-value fallback.

The full frontend suite passed 7620 tests after the comparator change. After the shared snapshot change, `node --experimental-strip-types --test tests/active-reasoning-intent.test.ts tests/reasoning-budget-config.test.ts tests/reasoning-budget-rollback.test.ts tests/resident-config-match.test.ts tests/model-config-instance-key.test.ts` passed 129 tests, followed by typecheck and production build.

The real Studio CPU-loaded model reported requested budget -1 and effective budget 32. Its actual status was passed to the production comparator with the matching load config: the unchanged comparator at control 8e24c8c8c rejected reuse, and the repaired comparator accepted it. These logs demonstrate the reuse decision; they do not claim a browser-driven external-provider roundtrip.

The full frontend suite was then rerun on exact latest head `4b912408e44f48c01c40e749432e423911424bcd`: **7620 passed, zero failed** (`frontend-latest.log`).

## Preset subscription repair

Latest head: `27791b6ce84993d7b19c85a6d9927d6e91d4b0bd`. The preset summary and dirty-state subscriptions now select the same requested pair as preset capture, so a same-effective-value reload from another client still updates them when its request changes. Both subscription regression cases fail before repair; 14 focused tests, typecheck, production build and the full frontend suite pass afterward. Latest full frontend count: **7622 passed, zero failed** (`frontend-preset-final.log`).

Review decision: the combined Windows command-limit report was not taken under the strict normal-input correctness scope. It requires both near-limit extra arguments and an 8 KiB exhaustion message. This boundary-hardening rejection does not dispute Microsoft's documented 32767-character CreateProcessW limit. The rationale is recorded on the original review thread: https://github.com/unslothai/unsloth/pull/7701#discussion_r4021083341.

## Completion

Squash-merged as `af4e98e2f63f1907eb4b5d5f8b9375311d9b667a` on 2026-09-15 at 23:32:20 UTC. The clean final review explicitly names tested head `27791b6ce8`: https://github.com/unslothai/unsloth/pull/7701#issuecomment-5689583997. Exact final approval: https://github.com/unslothai/unsloth/pull/7701#pullrequestreview-5216931639. Pre-commit passed; GitHub reported no required check contexts. The normal squash merge used an exact-head guard and no protection bypass.
