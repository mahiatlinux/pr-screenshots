# PR 11160 review evidence

PR: https://github.com/unslothai/unsloth/pull/11160

- Base: `f6cf06dece62234d2a79cc4b4852dd6ed3c309c2`
- Head: `ed65282cbc9e701c4acdb286a352ab80c696416a`
- Prospective merge: `42a008d9b8c851b436a034941df46a0f8a575850`

The failure model was a caller-controlled remote image reaching llama-server without destination validation. The patch moves fetching to Studio and leaves only bytes downstream. Reviewed risks: alternate API routes and tool passthrough bypassing normalization; redirects or DNS rebinding bypassing address validation; a slow response outliving its deadline; count-token requests performing a fetch; regressions to inline images and Gemini's existing fetch behavior.

## Results

- Base affected tests: 2,085 passed. Head and merge affected tests: 2,121 passed each.
- The independent 25-case route probe found 20 failures of the new safety contract on base, zero on head and merge. Inline-image compatibility controls pass on all three.
- HTTP loopback, HTTPS loopback and HTTP metadata URLs reach downstream dispatch on base. Generation rejects them with 400 on head and merge. HTTPS count-token requests carry a placeholder; disallowed schemes are refused.
- Public HTTPS images are fetched live by head and merge. Their four generation routes dispatch the same 30,343-byte PNG, SHA-256 `4b69699aab174d8bcb5f1c57cbf41b14cece83f4c001ad72f5ce3ca9492b1bf3`.
- Real socket drip test, 0.2-second deadline: base takes approximately 0.95 seconds; head stops at approximately 0.20 seconds.
- Native Linux, macOS and Windows public HTTPS, private-address refusal and socket A/B checks pass: https://github.com/mahiatlinux/unsloth/actions/runs/35165949644
- Ruff 0.6.9 passes on all eight changed files. The repository's formatting wrapper leaves the writable head copy unchanged. `git diff --check` passes.
- Identical JPEG-to-PNG expansion on base and head: 2,799,419 to 12,581,871 bytes, identical output hash. Download caps do not redefine the existing inline image conversion contract.

The route probe uses real FastAPI handlers, a backend double for model generation/counting, and a real local HTTP capture server for tool passthrough. Public image downloads and the socket deadline test use real network I/O. These results establish request processing and transport behavior; they are not model inference results.

Local execution used Ubuntu 26.04 x86_64, CPython 3.13.14, uv 0.12.1 and the attached package resolution. Bubblewrap isolated the filesystem, process namespace and credentials. Each tested checkout had its own uv environment. Offline suites used a separate network namespace. Live checks ran with an empty credential environment. Hosted jobs used disposable runners and checkout with `persist-credentials: false`.

## Commands

Run from each exact checkout with the attached dependencies:

```sh
python -m pytest studio/backend/tests/test_remote_image_url_fetch_behaviour.py studio/backend/tests/test_gemini_provider.py studio/backend/tests/test_web_fetch_extraction.py studio/backend/tests/test_anthropic_messages.py studio/backend/tests/test_openai_tool_passthrough.py -q --timeout=30
python probe.py head --live
python fetch_probe.py head
```

On base, omit the newly added `test_remote_image_url_fetch_behaviour.py` from the existing suite. The route probe expects its artifacts directory at `/task/artifacts`; its `base`, `head` or `merge` argument labels the output. `fetch_probe.py` takes a checkout directory whose final component is `base` or `head`, and asserts the negative control on base and the bounded result on head.

Primary references checked: [Python HTTP client](https://docs.python.org/3/library/http.client.html), [Pillow image decoding](https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.open).

## Resumed verification, 2026-09-18 UTC

Source head `485fa2b2a613391e99225925ea94b24d4eefc1e6` includes the maintainer's URL-padding and User-Agent fixes. The original writable checkout remains unchanged. Mirror merge `3ed4695ffb19386879a5d67fd7f1c95e9accedae` combines that head with upstream `c7d8980a2`.

- The same affected suite passes: 2,128 tests on source head; 2,139 on the mirror merge.
- All 25 independent route safety assertions pass on both revisions, including live public HTTPS downloads. The generated PNG hash remains identical to the earlier run.
- Repeated live public HTTPS/private-address checks pass; the 0.2-second socket-drip deadline completes at 0.20 seconds on head and 0.95 seconds on the exact original base.
- Ruff passes on all eight changed Python files; `git diff --check` passes.
- Environment and pinned package resolution are unchanged from the original run.

The original PR has three failed GitHub checks. Their historical run-log endpoints returned HTTP 410 during this resumption; these failures are not represented as successful checks here.

## Historical CI gap resolved, 2026-09-18 UTC

[Fresh scoped staging CI](https://github.com/mahiatlinux/unsloth/actions/runs/35402633351) compared the same immutable base and head using the original three job selections. The workflow is preserved in commit `729555fb4` on mahiatlinux/unsloth.

| Job group | Base | Head | Comparison |
| --- | --- | --- | --- |
| Backend a-k plus serial tests | 16,071 passed, 1 failed, 43 skipped | 16,072 passed, 1 failed, 43 skipped | Same test and traceback; no head-only failure |
| Repository Python plus CLI | 6,544 passed, 128 skipped | 6,544 passed, 128 skipped | Both pass |
| Extra browser UI | FLUX.2 picker timeout in download-only cancel/retry | All selected steps pass | Base-only failure |

The shared backend failure is `test_base_model_dir_name_fallback.py::test_the_transcribed_repo_id_rule_is_never_looser_than_the_hubs`: `assert ['Café-8B'] == []`. Dependency versions match between each pair; the repository test environments differ only in the editable Unsloth commit. Every serial backend test passed.

The browser base failed to keep the FLUX.2-klein-4B picker open across five attempts. Head passed that exact scenario and the remaining extra UI checks, including model settings, memory estimates and IME behavior. Two head screenshots were inspected and preserved in `ci-gap/`.

The staging workflow remains red because it faithfully reports the shared backend failure and the base-only UI failure. No new PR defect was found. The historical logs remain unavailable; no claim is made about their exact original cause. Full JUnit and browser artifacts are attached to the fresh run. Structured results and package versions are preserved here. The cancelled first staging attempt is excluded because its application-home override did not match the official UI harness.
