# Current upstream merge control

Locally constructed merge `f10b9da2d9014617177050a2282a9dbed096efd4`, tree `e0a060eb6d2d2d2821459315805c38e9e074ce7c`: upstream main `1066d16aff3b4a5dbaad1c4df85a3dd94bb3bb3c` and unchanged reviewed head `30f324518e7b342a279cd771d63ad134a9a48178`. git merge-tree reported no conflict. The official pull merge ref still pointed at the older round25 merge, so this detached task-only commit was created with git commit-tree and was never pushed to the contributor branch.

Python 3.14.4 focused policy, sandbox and permission suites: 2,962 passed, one platform skip. Actual tools: all 50 approved SSH connections and the separate authenticated reverse handshake pass; tested unapproved paths are blocked. Frontend npm run build passes with existing chunk-size/dynamic-import warnings. A clean scene run using real tool output produced Chromium 153 and Firefox 155 captures, both manually inspected. This is not model inference or a browser-driven Allow click.

Commands in the credential-free private-network/PID/filesystem sandbox:

```sh
cd studio/frontend && npm run build
python -m pytest studio/backend/tests/test_ssh_policy.py studio/backend/tests/test_sandbox_tools.py studio/backend/tests/test_permission_mode.py -q --tb=short --timeout=90 -p no:cacheprovider
python /evidence/round25_live.py
python /evidence/round21_reverse_live.py
python /evidence/live_ssh.py
python /evidence/ui_scene.py
```

No original PR code or history was changed for this control.
