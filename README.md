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
