# PR 10933 verification evidence

Tested repair: `00fb4ee7b79f97ee6a80238eb789479675e43333`.

Separate Studio frontend builds, Python environments, application homes and browser contexts at the merge base, original head and repaired head. Real authentication, connection creation, live OpenRouter catalog requests, model selection, effort menus, image attachment and output-limit controls were exercised. UI screenshots were inspected before publication.

- 199 focused backend tests passed on repaired head and repaired prospective merge.
- 61 frontend checks passed; frontend builds, TypeScript checks and Ruff passed.
- 15 Chrome for Testing and 10 Firefox browser cases passed. PNG attachment decoding was asserted at 64 by 64 pixels.
- All 171 effort ladders from 445 live catalog models resolve after repair. Original head misses Gemini Pro latest.
- Both added regressions fail before repair and pass after repair.
- HTTP transport capture shows base drops minimal/xhigh/max; original and repaired head forward all six non-none levels.
- Three accelerator/NPU CI assertions fail identically on upstream alone and the repaired merge. See `ci-failures-upstream.log` and `ci-failures-merge-repaired.log`.

## Commands

From each relevant checkout:

```sh
python -m pytest studio/backend/tests/test_provider_model_capabilities.py studio/backend/tests/test_provider_reasoning_normalization.py studio/backend/tests/test_provider_max_output_tokens_contract.py studio/backend/tests/test_provider_base_url_validation.py studio/backend/tests/test_external_provider_sampling_over_the_wire.py -q
```

From `studio/frontend`:

```sh
npm run build
npm run typecheck
node --experimental-strip-types --test tests/model-catalog.test.ts tests/external-thinking-wire.test.ts tests/provider-capabilities-current-models.test.ts tests/provider-max-output-tokens.test.ts
node --experimental-strip-types --test tests/provider-catalog-refresh.test.ts tests/provider-capability-rollback.test.ts tests/provider-max-output-tokens-guards.test.ts tests/queued-model-capabilities.test.ts
```

Browser scenes: `node ui-scene.mjs base head fix` and `node ui-firefox.mjs base fix`; auth uses isolated test-account sessions. `metadata.json` records source commits and versions, and `chrome-facts.json` / `firefox-facts.json` record assertions. `comparison-*.png` and `firefox-comparison-*.png` are labelled merge-base/repaired-head pairs; uncropped screenshots are included.
