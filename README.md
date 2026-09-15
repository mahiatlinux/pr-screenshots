LGTM. Reviewed and tested `9717fb14604d7face9e2ebdd3e8878012cb1a52b` in isolated temporary checkouts. No additional defects confirmed within this PR's scope.

**Before:** Merge base `03af220ac` forwarded the named choice object and the full catalog. Fresh Qwen3-0.6B Q4_K_M inference called the wrong tool in all 18 forced requests across `/v1/messages`, `/v1/chat/completions`, and `/v1/responses`, covering streaming and non-streaming.

**After:** Head sends only the selected tool under `required`. Across the same 18 requests, it called the selected tool 10 times and never called another tool. The other eight responses explicitly reached the 512-token limit. Anthropic prompt counts fell from 216 to 159 and matched generation usage; `auto` counts stayed at 216.

**Verdict:** The reported bug is real and this patch fixes the request construction. A token limit can still stop generation before a tool call.

**Regression risk:** The expanded 22-file suite passed 2,591 tests on base and 2,600 on head. The earlier four-file suite passed 1,613 tests on head and the prospective merge. The independent 16-case catalog probe passed on head. Restoring the code before the count correction made both dropped-tool count regressions fail; current head passed both.

**Compatibility:** Linux x86_64, Python 3.14.4, llama.cpp b10970, identical pinned dependencies on both sides. Completed 27 live requests per side, including `auto`, `none`, and `required` controls. Lint, repository formatting, and diff checks passed. The existing Windows GGUF and UI CI runs also passed on this head.

**UI evidence:** Built both frontends separately and captured the API monitor in Chromium 151 and Firefox 153. Both show `get_time` / 216 tokens before and `get_weather` / 159 tokens after.

**Fixes:** None needed. Source checkouts remain unchanged.

**Gaps:** Two full-inference tests were skipped in each expanded run. A separate CPU dependency check remained blocked by missing Triton. No fresh native macOS/Safari, Edge, or GPU inference run. Existing Core zoo CI failures are outside the changed Studio paths; this approval does not claim all repository CI is green.

## Evidence capture

Base: `03af220ac0023ab846727397b3a1de9efa0aec42` (PR merge base).
Head: `9717fb14604d7face9e2ebdd3e8878012cb1a52b`.

Both Studio frontends were built separately, with separate app homes and caches. Screenshots use Linux x86_64, Chromium 151.0.7922.34 and Firefox 153.0, viewport 1500 × 1000, light theme, en-US locale, and reduced motion. The images show the API monitor after actual CPU inference, with the same prompt and a named `get_weather` choice against a two-tool catalog.

- [Chromium before/after](fresh-chromium-before-after.png)
- [Firefox before/after](fresh-firefox-before-after.png)
- [Live request results](live-summary.json)
- [Test suite results](test-results.json)
- [Expanded test file list](expanded-test-files.json)

The expanded suite used `run_expanded.py` from each checkout root, with that checkout's `studio/backend` on `PYTHONPATH`, in separate isolated environments. The runner imports `utils.paths` before calling `pytest.main` with `-q -rs -p no:cacheprovider --timeout=60 --junitxml=<output>` and the 22 paths in `expanded-test-files.json`. Test output paths are chosen by the runner; runtime dependencies and the DeepSeek tokenizer fixture must be present.

Live inference used Qwen3-0.6B-Q4_K_M, model revision `50968a4468ef4233ed78cd7c3de230dd1d61a56b`, llama.cpp b10970 (`bfdc32183`), CPU inference with two threads, a 4096-token context, a 512-token output limit, temperature 0.6, thinking disabled, and seeds 3407, 3408, 3409. The prompt was `What time is it in Tokyo right now?`, with `get_weather` and `get_time` available and `get_weather` forced. Each side received 18 forced requests plus nine controls across Messages, Chat Completions and Responses.

The screenshots show a successful forced-call case. Across all head forced requests, ten called the selected tool and eight stopped at the output limit; none called the wrong tool. Timing in the screenshots is illustrative and is not a performance benchmark.
