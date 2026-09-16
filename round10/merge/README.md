# Prospective merge verification

Merge and parents: `fad5753ddd4e36a5d75322636c0cfe0b0d292198 71d85d5bb5fec3806efc428c6d2a264f4d00d60d 1406f84a2174bc2bdc7a702e6efdb52426ea0a33`.

Repository policy/sandbox/permission suites: 2,801 passed, one platform skip. All 26 real SSH connection controls pass. Fresh frontend production build passes. Authenticated Chromium 153 and Firefox 155 captures were manually inspected; they restore executed tool output through chat history, without model inference or a browser-driven Allow click.

Additional tool-loop, streaming, bypass-permission and folder suites on source head 1406f84a2174bc2bdc7a702e6efdb52426ea0a33: 610 passed, one failure. The failing folder test expects Path.is_dir() to raise PermissionError, but Python 3.14 returns False. The identical test fails on the original base 9bef060ea4200fb679067c4fca406087c1c14a4b with six neighboring folder tests passing. It is unrelated to SSH changes and remains visible in both logs.

```sh
python -m pytest studio/backend/tests/test_ssh_policy.py studio/backend/tests/test_sandbox_tools.py studio/backend/tests/test_permission_mode.py -q --tb=short --timeout=90 -p no:cacheprovider
python /evidence/round10_complete_live.py
python /evidence/live_ssh.py
cd studio/frontend && npm run build
python /evidence/ui_scene.py
```
