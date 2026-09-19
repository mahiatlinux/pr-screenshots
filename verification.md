# MCP image replay verification

Base: c7d8980a206d9724630f7081e29d64dd6141c538
Original PR head: 4589fbbaebf5036c4fbee478f3d2c4bb82b654ee
Repaired original tree: 888c1be68fe39dae8c98d5710d67993ca8e50c86
Review mirror: 5c8751b94d40759f8897ad75dfe11eb0d1d9218d

Linux x86_64, Python 3.13.14, PyTorch 2.10.0+cpu for backend tests, RTX 5060 Ti for live llama.cpp vision inference. Browser: Chromium 151.0.7922.34, Playwright 1.62.0, viewport 1400 x 1000.

Live Qwen3.5-0.8B Q4_K_M plus F16 vision projector, pinned to unsloth/Qwen3.5-0.8B-GGUF revision 6ab461498e2023f6e3c1baea90a8f0fe38ab64d0. Base never receives image parts and cannot identify red, blue, or green. Head receives one image part and identifies all three correctly.

Browser experiment: separate production builds and Studio homes, seeded saved MCP screenshot result containing a real red PNG, then a real follow-up chat request through Studio to the GPU-backed OpenAI-compatible endpoint. Base answers NO_IMAGE; repaired code answers RED. This tests saved-result replay, not a live MCP server invocation. Both Chromium pages have zero page errors.

Repairs:
- Correct three stale image-result assertions.
- Preserve an MCP image between two caller image attachments on the multiple-image local route, with tool support enabled or disabled. Before: red, blue. After: red, green, blue, in marker order. Added cases for caller-image reservation and the eight-image cap.
- Add an assistant boundary for synthetic image turns only when the loaded Ministral template has the tool-skipping alternation check. Original head fails local rendering, processor rendering, llama-server token counting and streaming; repaired code passes all four. The image markers stay in place. The strict template comes from the official supported model revision below. The Qwen weights are used only to exercise llama-server request/template handling with this template, not to claim Ministral model quality.

Official template: https://huggingface.co/mistralai/Ministral-3-3B-Instruct-2512/blob/7046a0e237b436c8fb4927061ab3773772e53741/chat_template.jinja

Executed tests:
- Original affected suite: 2053 passed, 70 skipped, 3 stale-assertion failures.
- Repaired original: 1921 passed, 70 skipped across image, route, external provider, MLX backend contract, local tool-loop, orchestrator and template suites.
- Repaired mirror: 1924 passed, 70 skipped across the same modules, including three upstream-added tests.
- Focused llama.cpp and Studio image tool-loop tests: 6 passed.
- Frontend MCP image tests: 33 passed; TypeScript and production builds passed.
- Regression negative controls: both multi-attachment routes fail before the repair; both strict-template tests fail when their repair is disabled.
- Ruff and git diff checks pass.

The local MLX checks are backend contract tests; live vision execution used llama.cpp on CUDA.

Additional execution: a disposable FastMCP 4.0.5 HTTP server returned real ImageContent blocks. Studio's production call_tool_sync and replay builder fed those results to the GPU model. Base passed zero image parts and could not see any of the three colors; repaired code passed one image part and identified all three correctly. Firefox 153.0 reproduced the browser NO_IMAGE to RED result with zero page errors. The repository Python-floor check also passed for Python 3.10.

Final test-only follow-up:
- Original task branch: 34bd20102f3f5565856721534f2ce292216b595e.
- Mirror: 9b8fad07152ec40579306d39244f971e21c05c07.
- Video-routing and CI-sharding guards: 56 passed on each branch. The video guard detects mutations removing the video gate, replacing image-or-video with image-and-video, or inverting the image condition.
- Stream cancellation, GGUF slot-release ordering and context-refusal suites: 10 passed.

Commands, run from studio/backend with the isolated environment:

```
python -m pytest tests/test_chat_template_tool_arguments.py tests/test_chat_template_continuation.py tests/test_mcp_images.py tests/test_mcp_flatten_result.py tests/test_sf_client_tools_passthrough.py tests/test_vision_client_tools.py tests/test_openai_tool_passthrough.py tests/test_anthropic_messages.py tests/test_external_tool_call_id_replay.py tests/test_mlx_inference_backend.py tests/test_safetensors_tool_loop.py tests/test_orchestrator_unload_cancel.py -q
python -m pytest tests/test_llama_cpp_tool_loop.py tests/test_studio_tool_loop.py -q -k 'mcp or image'
python -m pytest tests/test_video_attachment_part.py ../../tests/test_ci_backend_pytest_shards.py -q
python -m pytest tests/test_llama_cpp_stream_cancel.py tests/test_gguf_stream_slot_release_ordering.py tests/test_context_refusal_units.py -q
```

WebKit 26.5 also reproduces NO_IMAGE to RED with zero page errors. Its runtime libraries were extracted into the disposable task directory; the host was unchanged.

Review finding 4051743629 was rejected after verification on exact mirror head 9b8fad07152ec40579306d39244f971e21c05c07. The async-generator closure is defined at line 4236, messages is initialized at line 4918, and the only calls to the generator are at lines 7760 and 7778. TypeScript and the production build pass. An executed probe of the actual lookup block returns the user message with the correct parent ID after initialization. All 17 research frontend contract tests pass. No code change was required.

Final MLX note repair: 536f7535d on the original-based branch, 67f4b941e9df774ed46c59d8778c843d876f3711 on the mirror. Both new omission-note regressions fail before repair. Final affected suites: original-based 1923 passed, 70 skipped; mirror 1926 passed, 70 skipped. Shared trimming keeps the selected image, removes emptied synthetic turns and relabels notes beside preserved user text.

Completed: all six fixes landed at 05d69cf4f7d45ee9c1e822cb19e0765f5a4c50ce with an exact tree match to the verified original-based branch. Final Codex verdict on mirror 67f4b941e9df774ed46c59d8778c843d876f3711 found no major issues. Original PR approved and squash-merged as 992849427e930b505b7e1293e513b5448fb17fdb. Mirror closed without merging.
