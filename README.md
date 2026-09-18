Verification evidence for unslothai/unsloth#11172.

The `live_probe.py` experiment first classifies each script, then deliberately executes it directly in an isolated network namespace to verify the actual destination. Its HTTP 200 results prove client behavior; they do not mean that Studio bypassed its repaired policy gate. The real Studio gate is exercised separately by the UI captures and `ui-*.json` connection counts.

Run the scripts with `PYTHONPATH=studio/backend` and the dependencies in `final-requirements.txt`, inside an isolated credential-free environment. Compare the merge base `16408b25fdef12133be49e117cdd5f9a3382cb3a`, original head `6e2f3da93999d1726ef6136d68896b658eb6fa73`, and repaired source `570ffdac9`.

The focused test command was:

```sh
python -m pytest studio/backend/tests/test_sandbox_tools.py studio/backend/tests/test_permission_mode.py studio/backend/tests/test_bypass_permissions.py studio/backend/tests/test_consent_gate.py studio/backend/tests/test_tool_confirm_loop.py studio/backend/tests/test_tool_confirm_stream.py studio/backend/tests/test_outbound_network_guard.py -q --disable-warnings
```

`merge-tests.log` runs `test_sandbox_tools.py` on the reviewed prospective merge tree `78743ffc8`.
