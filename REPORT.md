# PR #10940 review

Reviewed [unslothai/unsloth#10940](https://github.com/unslothai/unsloth/pull/10940), authored by NilayYadav, on 2026-09-15.

## Before

Exact merge base: `03af220ac0023ab846727397b3a1de9efa0aec42`.

The actual Studio application called a deterministic stdio MCP server and sent the resulting tool messages to a local OpenAI-compatible provider. The audio response used the filesystem server's shape: an audio block mirrored in `structuredContent`. The PDF response used an embedded binary resource.

In all five tested browsers, the provider received 1,197 characters containing encoded WAV data and an empty PDF result. The expanded tool cards displayed the same payload dump and blank result. The same scene's attachment assertions failed on base for those exact reasons, after confirming that both tools ran, three provider completions occurred, and two tool cards appeared.

## After

Original head: `5c91199048eceb37bc8da16d67f322c1578ed855`.

All five browsers passed the identical scene. Provider inputs and expanded tool cards contained the 53-character audio note and 91-character PDF note. Neither encoded payload reached the provider.

The fetched prospective merge `7f35cab7ea17148e3d50119c4d7dccafcbc328d2` also passed the focused regression suite and independent stdio A/B probe. Its actual first parent is `8760d44374e5f094707d5c0e9e75560200db26b9`; GitHub's initial PR metadata reported base tip `d5846921772942997e92d2faeae4e201bc08946b`. Tests use the recorded immutable commits, not mutable branch names. There is no repaired head because no further defect was confirmed.

## Verdict

Real bug. The PR fixes the tested attachment-loss and structured binary-payload cases. No additional correctness defect was confirmed.

Audio and embedded resources are valid tool-result types in the [MCP specification](https://modelcontextprotocol.io/specification/2025-11-25/server/tools). The audit traced `call_tool_sync` through `_flatten_result` and `strip_result_for_model`, then verified both the provider request and the rendered tool result.

The compact failure model was: base discards non-image blocks and falls back to raw structured output; head must replace those attachments with notes, prune mirrored binary data, retain independent structured fields, preserve text/link/image behavior, and retain error classification. No persisted schema or public interface changes were found.

## Regression risk

The four focused suites were `test_mcp_flatten_result.py`, `test_tool_loop_controller.py`, `test_mcp_stdio_real_server.py`, and `test_mcp_upgrade_compat.py`.

| Snapshot/runtime | Result |
| --- | --- |
| Merge base, Python 3.14 | 122 passed, 1 skipped |
| Original head, Python 3.14 | 131 passed, 1 skipped |
| Prospective merge, Python 3.14 | 131 passed, 1 skipped |
| Original head, Python 3.11 / FastMCP floor | 131 passed, 1 skipped |
| Original head, Python 3.10.20 / FastMCP floor | 131 passed, 1 skipped |
| Original head, Python 3.12.13 / FastMCP floor | 131 passed, 1 skipped |
| Original head, Python 3.13.14 / FastMCP floor | 131 passed, 1 skipped |

The expanded run selected every `test_mcp*.py` and `test_*tool*.py` file from `studio/backend` with the same pinned dependencies on both snapshots. Head: **4,171 passed, 7 failed, 9 skipped** in 718 seconds. Base: **4,162 passed, 7 failed, 9 skipped** in 704 seconds. All seven failure identities matched.

Targeted rechecks resolved six failures after supplying sandbox localhost resolution and the `awk` alternative, and removing the live-scene stdio override for the URL-validation test. Both snapshots then had 11 passes and the same remaining failure in that recheck group: `test_nesting_deep_enough_to_exhaust_the_stack_is_unsplittable`. That unchanged test fails on Python 3.14 and passes on Python 3.13. No source or test assertions were weakened. Exploratory collection failures from missing Torch/PEFT and an incorrect working directory were resolved before the complete expanded run.

An additional 20,000 seeded mixed-attachment cases passed checks for payload omission, independent-field retention, input immutability, error classification, and image counts. Another 500 results across eight threads matched serial execution.

The actual `@modelcontextprotocol/server-filesystem` **2026.8.31** package passed nine cases through Studio's real stdio client: WAV, PDF, CSV, ZIP, empty CSV/WAV, PNG, plain text, and a missing-file error. Encoded payloads were absent from head's model-facing results; plain text and image display semantics were preserved.

The focused suite's single skip requires native Windows batch-launch semantics. Covered paths include text and text resources, resource links, independent and partially mirrored structured output, image envelopes and payload budgets, mixed attachments, zero-byte attachments, error prefixes, MIME aliases, and real stdio command execution.

An independent real stdio probe exercised nine result shapes. A separate seeded comparison generated 10,000 attachment-free results and checked both flattened and model-facing strings. Base, head, merge, and the older SDK configuration produced the same digest: `142a9c7e0a8b5a76cd3324839360d1b549cc3fa5a9600f5b7ff211307377ff1e`. Seed: 10940. Original head and merge stdio outputs matched.

Ruff passed on both changed files. The final PR diff passed `git diff --check`. Both frontend builds passed. No source changes remain in any review worktree.

## Compatibility

Host: Ubuntu 26.04.1 LTS, x86_64, kernel 7.0.0-31-generic. uv 0.12.1. PR code ran in bubblewrap with cleared environment, isolated process/network namespaces, and no credential directories. Each tested checkout used its own uv environment. Application homes, caches, frontend builds, ports, and browser contexts were isolated.

| Configuration | Versions |
| --- | --- |
| Current dependency comparison and UI | Python 3.14.4, FastMCP 4.0.3, MCP 2.2.0, Pydantic 2.13.4, AnyIO 4.13.0, FastAPI 0.141.1 |
| Minimum declared FastMCP | Python 3.11.15, FastMCP 3.0.2, MCP 1.30.0, Pydantic 2.13.5, AnyIO 4.13.0 |
| Browser automation | Playwright 1.62.0, Chromium 151.0.7922.34, Firefox 153.0, Chrome 153.0.8010.36, Edge 153.0.4234.32, WebKit 26.5 |

The expanded comparison also installed Torch 2.14.0+cpu and PEFT 0.20.0 into the isolated environments for token/vision unit tests. Additional Python resolutions are retained in `requirements-3.10.lock`, `requirements-3.12.lock`, and `requirements-3.13.lock`; `requirements-expanded.lock` records the full expanded test environment.

A separate real-model smoke replayed the exact observed Studio tool messages into cached Ling-3.0-tiny-Q6_K using llama-server build 10909 (`329b6160f`), first on CPU and then on an RTX 5060 Ti with driver 595.91.07. The CUDA run offloaded **25/25 layers**, with a 6,327 MiB model buffer. All four base/head audio/PDF requests returned nonempty answers. The head audio answer identified the WAV attachment; the PDF answer said it could not read the file. The audio prompt decreased from 402 to 89 tokens. This small deterministic smoke does not establish a hallucination rate or guarantee how every model responds. No weights were downloaded and no training was run.

The measured provider input reduction is 1,197 to 53 characters for mirrored WAV and 0 to 91 for PDF. This is payload-size evidence, not an inference-speed or memory benchmark.

Pinned package resolutions are in `requirements.lock` and `requirements-floor.lock`; selected test logs and result JSON files are beside this report. Standalone repro scripts and complete original artifacts remain in the isolated review workspace.

## UI evidence

Used the `pr-ui-evidence` workflow, its authentication/scene helpers, and the author's deterministic provider fixture after inspection. The application was launched directly from each exact source checkout with separately installed backend dependencies and separately built frontend assets. The fixture substitutes only the external provider and MCP server; Studio's chat, tool execution, flattening, provider serialization, and rendering run normally.

- [Chromium before/after](before-after.png): payload dump and blank PDF become attachment notes.
- [Firefox before/after](before-after-firefox.png): same observed change.
- [Chrome before/after](before-after-chrome.png): same observed change.
- [Edge before/after](before-after-edge.png): same observed change.
- [WebKit before/after](before-after-webkit.png): same observed change; this is not native Safari.

All five composites were opened and visually inspected. Browser facts and immutable source identities are published in [evidence.json](evidence.json). Original browser captures and provider inputs remain in the isolated review workspace. Viewport: 1280 by 1300, light theme, en-US, reduced motion. When the provider quotes the PDF note in its reply, the existing Markdown renderer marks the file URI as blocked; the tool card retains the readable note. Chrome, Edge, and WebKit compatibility libraries were extracted under the temp workspace without altering the system installation.

## Fixes

None. No added repository tests, source edits, or commits were necessary. The writable review branch remains at the original head. No source changes were pushed, merged, or closed. This branch contains only the published verification evidence. The user subsequently requested reviewer assignment and an approval comment; `mahiatlinux` was added as a requested reviewer, preserving the existing reviewer. Published [approval review 5205104925](https://github.com/unslothai/unsloth/pull/10940#pullrequestreview-5205104925) as `mahiatlinux`, with “LGTM!” and the verified results and gaps. GitHub returned `APPROVED` for the reviewed head.

Active GitHub identity was verified as `mahiatlinux`. The original head is `NilayYadav/unsloth:fix-mcp-non-image-results`. Direct fork permission is read-only, while the account has upstream push permission and the PR permits maintainer edits. No remote source branch was modified.

## Gaps

- Native Windows, WSL, macOS, and arm64 were not available in this local Linux run. The Windows UI failure was re-run as attempt 2 but remained queued at the final local check.
- Native Safari was not run. WebKit evidence does not establish the Safari/macOS cell.
- Browser screenshots cover successful audio/PDF results and the pre-fix empty/payload states. Separate screenshots for error, oversized image, mixed image/audio, zero-byte, mobile, keyboard, stale storage, and network-failure states were not captured; applicable result semantics were covered by focused tests.
- The live Studio provider is deterministic; the separate CPU/CUDA smoke uses a real model. Neither experiment establishes a general hallucination rate. No training or full GPU performance benchmark was needed or performed.
- This was a source-runtime review. Clean installer, wheel, upgrade, rollback, the full dependency matrix, and full-repository tests were not independently executed. Python 3.10 through 3.14 received focused coverage; the complete expanded base/head comparison ran on Python 3.14. Python 3.9 was not tested, consistent with the backend workflow's stated 3.10 floor despite the broader package metadata.
- The expanded suite's nine skips were two optional `data_designer` tests, three Windows launcher cases, two per-user runtime-directory cases absent inside the sandbox, one no-confinement case skipped because this kernel has Landlock, and one case-insensitive-filesystem case. These unrelated native/optional states were not emulated to manufacture passes.
- One pre-existing Python 3.14 deep-nesting test failure remains after environmental rechecks. It fails identically on base/head and passes on 3.13. The full expanded suite was not redundantly repeated after the six isolated environment corrections.
- [Windows UI CI](https://github.com/unslothai/unsloth/actions/runs/34898040914) initially timed out waiting for “Loaded models”; its retry remains pending. [Core CI](https://github.com/unslothai/unsloth/actions/runs/34898040617) fails zoo tests for Gemma4 on the older Transformers lane and the vLLM FlashInfer opt-out assertion. The exact same failures were verified in [upstream main run 34882416498](https://github.com/unslothai/unsloth/actions/runs/34882416498). They were not repaired in this PR. This approval does not claim all repository CI is green.
- The reused UI fixture's `tools_offered` summary compares unprefixed names with Studio-prefixed names and therefore records an empty list. Verification uses the actual two returned tool messages, three provider requests, two rendered cards, and exact payload assertions instead. The immutable source identities are recorded here and in the screenshot labels because the fixture's GitHub-only `ref` field is empty in a local run.

## Commands and artifact index

Focused suite, from each repository root:

```bash
.venv/bin/python -m pytest -q studio/backend/tests/test_mcp_flatten_result.py studio/backend/tests/test_tool_loop_controller.py studio/backend/tests/test_mcp_stdio_real_server.py studio/backend/tests/test_mcp_upgrade_compat.py
```

Expanded suite, from `studio/backend`:

```bash
../../.venv/bin/python -m pytest tests/test_mcp*.py tests/test_*tool*.py -q --tb=short -o faulthandler_timeout=120 --durations=15
```

UI scene command, inside the prepared sandbox for each source snapshot:

```bash
python artifacts/ui_review.py base chromium
python artifacts/ui_review.py head chromium
```

The same scene ran with `firefox`, `chrome`, `edge`, and `webkit`. It used the inspected [deterministic provider/MCP fixture](https://github.com/NilayYadav/unsloth-staging/blob/e626d3cf6bef317ed6cb87c98b9c8a8f90a13203/.github/scripts/pr10940-ui-probe.py), separate Studio installs, and isolated application homes. Base assertion failures were the expected negative control; head assertions passed. These commands describe the test invocation; the scene also requires the fixture, browser server, and authentication helpers described above.

Published logs preserve failures and warnings. Workspace and temporary filesystem paths were replaced with placeholders, and trailing whitespace was removed. Screenshots contain synthetic fixture data only.

- [base-ab.json](base-ab.json)
- [base-regression.log](base-regression.log)
- [base-ui-build.log](base-ui-build.log)
- [evidence.json](evidence.json)
- [expanded-base-final.log](expanded-base-final.log)
- [expanded-head-final.log](expanded-head-final.log)
- [head-ab.json](head-ab.json)
- [head-floor-ab.json](head-floor-ab.json)
- [head-floor-regression.log](head-floor-regression.log)
- [head-regression.log](head-regression.log)
- [head-ui-build.log](head-ui-build.log)
- [merge-ab.json](merge-ab.json)
- [merge-regression.log](merge-regression.log)
- [nesting-python313.log](nesting-python313.log)
- [official-filesystem-base.json](official-filesystem-base.json)
- [official-filesystem-head.json](official-filesystem-head.json)
- [python-3.10.log](python-3.10.log)
- [python-3.12.log](python-3.12.log)
- [python-3.13.log](python-3.13.log)
- [real-model-cpu.json](real-model-cpu.json)
- [real-model.json](real-model.json)
- [recheck-base.log](recheck-base.log)
- [recheck-head.log](recheck-head.log)
- [requirements-3.10.lock](requirements-3.10.lock)
- [requirements-3.12.lock](requirements-3.12.lock)
- [requirements-3.13.lock](requirements-3.13.lock)
- [requirements-expanded.lock](requirements-expanded.lock)
- [requirements-floor.lock](requirements-floor.lock)
- [requirements.lock](requirements.lock)
- [stress.log](stress.log)
