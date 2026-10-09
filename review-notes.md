# PR 13103 review evidence

## Scope and immutable refs

- Source PR: `unslothai/unsloth#13103`
- Source author/head: `NilayYadav/unsloth:add-mcp-support-deep-research`
- Source merge base: `6d3af3c332dc4eb1942a21d4d690677207152be5`
- Original source head: `0101eac9100369f8d6e72e9eef5af535dafd9edc`
- Source merge ref observed: `551d381adb` (source head merged into `63988fd030`)
- Mirror PR: `mahiatlinux/unsloth-staging-review#177`
- Mirror base/head observed: `5333c969f08a40493b8427583516a606355ddfb2` / `01305e371c85832dc5a085ead7e171ca3f191c71`
- Host: Linux x86_64, kernel `7.0.0-38-generic`
- GitHub identity: `mahiatlinux`

## Failure model written before execution

Pre-PR, Deep Research runs web and optional knowledge-base searches only. The PR intends to discover enabled, model-visible MCP tools whose schema has exactly one required string input, let the user opt into those tools, execute every selected tool for each search step, persist returned text as document sources, restore those sources after a lease recovery, and expose citations and source badges without changing runs that select nothing.

The patch assumes cached MCP schemas remain valid through a run, the existing MCP safety classifier is sufficient to identify read-only searches, the request/account context follows discovery and background execution, selected source identifiers remain stable, and fixed evidence budgets preserve useful evidence from every selected tool. It also assumes the frontend cannot build a request rejected by the backend's 20-source limit.

Material risks and observable checks:

1. Discovery/safety: reject multi-required, enum-only, mutating, destructive, credential, hidden, disabled, cross-account and stdio-in-disallowed-context tools; accept ordinary single-query tools. Exercise malformed schemas and camelCase/separator variants.
2. Execution: each selected eligible tool runs once per search step with the exact sanitized query; fetch steps do not run MCP searches; tool errors/timeouts do not fail a step when another evidence source succeeds.
3. Source bounds: source caps are enforced, duplicate/retried steps upsert deterministically, and evidence from later selected tools is not starved by an earlier large result.
4. Persistence/version skew: fresh schema creation and migration from a database without `kind` both succeed; ordinary knowledge-base sources read back as `knowledge_base`; MCP sources survive recovery and remain citable.
5. Citation safety: only catalogued MCP citations survive validation; brackets/newlines/duplicate display labels cannot forge attribution or swallow neighboring prose/code.
6. Account/security: discovery, configuration sanitization, worker execution, tool caches and persisted rows remain in the acting account context; stale or disabled selections cannot execute.
7. Cancellation/concurrency: cancellation and lease loss stop persistence; concurrent tools do not suppress successful peers; partial failures are observable but do not abort the research run.
8. Frontend contract: no MCP source is selected by default; loading/empty/error/populated states are visible; selections save only on dialog confirmation, persist, reach the create-run payload, and never exceed the backend limit.
9. UI/accessibility: configuration controls show the expected MCP source section, labels identify server and tool, switches have accessible names and keyboard behavior, and the source group is visible after a completed run. Check narrow and normal viewports plus failure/empty states.
10. Compatibility/regression: run focused backend tests on the exact base (negative control), original head and current prospective merge; run formatter/lint/type/build/focused frontend checks on the repaired merge; inspect current CI for native Windows/macOS/Linux and branded-browser evidence without converting unexecuted cells into passes.
11. Performance: discovery probes enabled servers concurrently; per-step MCP calls remain bounded by configured timeout and selected-source limit; record focused test duration and do not claim production load measurements without executing them.

PR code is treated as untrusted. Python/Node execution is confined with bubblewrap to the disposable task tree and a scrubbed environment; no GitHub configuration, SSH material or shared application home is visible inside the sandbox.

## Confirmed defects repaired

1. Discovery admitted mutating single-string tools because it rejected only a subset of unsafe names. Discovery now uses the MCP read-only safety classifier; the negative test exposed `schedule_meeting` and `complete_task` before the repair.
2. Credentialless discovery filtered stdio servers only after probing, so listing tools could spawn local commands. The stdio and selected-server filters now run before probes.
3. A run selecting one MCP server probed every enabled server. Discovery now accepts the selected server IDs and avoids touching unrelated servers.
4. Concatenating and truncating MCP evidence let one large result starve later selected sources. Evidence now uses the existing bounded fair-share helper; a three-source marker test failed before the repair and passes after it.
5. Untrusted MCP server/tool display names could forge malformed citation syntax. Persisted labels and citations are normalized, and MCP sources no longer accept the document-citation alias.
6. The frontend could persist and submit more than the backend's 20-source maximum, producing a 422. Hydration, setters, and the dialog now deduplicate, validate, and cap selections; unchecked switches disable at the limit.
7. Changing MCP sources did not advance the queued-settings epoch, so a delayed model-settings load could restore a stale selection. The setter now advances the epoch with the other mirrored research settings.

## Executed checks before UI evidence

- Negative control at merge base: importing the new `mcp_search_tools` helper fails, proving the focused feature tests distinguish the baseline.
- Original source head: the original focused backend suite passed (`4 passed`).
- Initial prospective merge: the original focused backend suite passed (`4 passed`).
- Repaired head focused backend suite: `8 passed in 5.63s`.
- Repaired head related backend regression suite: `765 passed`, no failures or skips (`56.697s` in JUnit).
- Repaired head focused frontend suite: `8 passed`.
- Repaired head full frontend suite: `11070 passed`, no failures or skips (`152.56s`).
- Repaired head frontend production build: passed (`vite build`, 9,800 modules); only pre-existing CSS/chunk-size warnings.
- Repaired head TypeScript build/test typecheck: passed.
- Repaired head ESLint for the changed component and new regression test: passed.
- Ruff 0.6.9 formatting/check over changed Python files: passed.
- Environment: Python 3.13.14, Node 26.8.2, npm 11.19.1, uv 0.12.1, Linux x86_64 kernel 7.0.0-38-generic.

## Resume and current source integration

After the host crash, source PR head had advanced to `9db12c44dd3b5fac2fd35c85bc0a7059aa4f516b`. The author's commits independently repaired stdio probing, per-tool evidence sharing, MCP-only dispatch, tool-policy checks, citation kinds, and dialog selection limits/stale choices. These commits were merged without rewriting their history. The remaining repair was reapplied as `a1fea3416b8cfc2c5d99ba96b68ed8c171d66dee`; the original evidence-sharing implementation from the author was retained.

Five isolated comment-cleaner passes produced comment-only patches. The Python AST/TypeScript printer gate passed on all 11 files before the separate cleanup commit `51bafb8072f28a9f45893ec00c92d5c723bb5380`. This is the current mirror head.

Current combined-head verification: related backend suite `770 passed in 59.22s`; focused frontend suite `8 passed`; TypeScript app and test typecheck passed; changed-component/test ESLint passed; Ruff 0.6.9 formatting/check passed; comment-only gate and diff checks passed. Detailed backend output and JUnit are in `backend-current.log` and `backend-current.xml`.

Mirror landing preview found exactly two new commits and no PR body change. Review and convergence remain routed to mirror #177; after convergence those two commits will be carried to the source using `mirror-pr.py land --confirm`.

## UI evidence

Completed: mirror `8cae33a143854ea182b5ee03e30d9849aadeb750` converged at https://github.com/mahiatlinux/unsloth-staging-review/pull/177#issuecomment-6071584791, with GitGuardian success and all five findings resolved. The watcher exited. `mirror-pr.py land 13103 --confirm` applied six commits without changing the PR body: `d7ee922d72`, `654ffa4172`, `5203bb883e`, `93eb6c8604`, `e897217266`, `f0c6cbe59d`. The landed source tree is byte-identical to the tested replay at `d28eba7e4e`. Source CI was newly queued, not awaited after convergence. Evidence: https://github.com/unslothai/unsloth/pull/13103#issuecomment-6071604992. Approval: https://github.com/unslothai/unsloth/pull/13103#pullrequestreview-5464345727. No merge or close performed; no blockers.

Citation follow-up: `bd01ee7a5e` distinguishes normalized source-label collisions using the unique MCP tool identifier. `8cae33a143` prevents MCP evidence, including stored reports, from supplying a RAG document preview target while retaining normal document previews. Both new regressions failed before implementation (one distinct label instead of two; MCP preview target present), then 70 backend tests and 10 focused frontend tests passed, along with app/test type checks, scoped ESLint and Ruff. The source replay applied cleanly and passed the same 70 backend tests. Final UI evidence is refreshed to `8cae33a143854ea182b5ee03e30d9849aadeb750`.

Discovery follow-up: `39d44d60af5d38d99a7b0cbc0015caa60540dd5c` retains selected sources absent from a discovery response, displays them as unavailable, counts them toward the 20-source limit, and provides explicit removal. The browser regression on `7e17de9921` failed with `AssertionError: incomplete discovery deleted the saved source` after an empty discovery response and Save. The test uses isolated settings initialization and an async response handler; earlier harness timeouts are not counted as negative proof. Focused frontend tests (5), type checks and scoped ESLint passed.

Final review follow-up: `7e17de99218e4f46e6c6edcba4bdfaf447e95712` fixes two confirmed findings: queued sends now snapshot MCP selections and installation settings sync includes their payload, normalization, persistence and hydration. Before implementation, both frontend regressions failed and the backend rejected the field as extra input. Afterward, all 11,072 frontend tests passed (102.19s), 69 focused backend tests passed (2.66s), app/test type checks, scoped ESLint, Ruff and diff checks passed. The source replay also applied cleanly. Final screenshots are refreshed against this SHA.

Two isolated full Studio installs were built at source merge base `6d3af3c332dc4eb1942a21d4d690677207152be5` and repaired mirror head `51bafb8072f28a9f45893ec00c92d5c723bb5380`. Installer CPU selection (`UNSLOTH_LLAMA_CPP_BACKEND=cpu`) resolved the sandbox's inaccessible NVIDIA runtime. The driver receives explicit refs, so its generic override warning is expected: BEFORE is still the actual source merge base, while AFTER is the repaired mirror merge.

Playwright 1.55.0, Chromium 140.0.7339.16, 1440x1200 and 390x844 viewports. Each side uses a fresh context and its own authenticated Studio home. MCP discovery response is a deterministic two-tool fixture; no external service credentials or user state are involved.

Observed and manually inspected: BEFORE has no MCP section or discovery request. AFTER shows both source names, accessible switches, and the 20-source limit. Keyboard selection/save persisted exactly one source, Cancel discarded a second selection, and Save stayed reachable on both narrow layouts. The repaired install's production frontend build completed as part of installation. `ui-diff/meta.json` contains structured facts; `ui-final.log` records the driver output.

Additional source-branch replay: both review commits cherry-picked cleanly onto `9db12c44dd`; focused tests passed (`13 passed in 3.36s`).
