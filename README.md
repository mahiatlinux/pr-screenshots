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
