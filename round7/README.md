# Direct Paramiko ProxyCommand repair

Tested head: `0f01d380e0e12cf8262dc750cc8681b463cb4a68`. Five approval assertions fail on previous head `fb6e4dcb5f93dee2b3dbd0b97c092a1779c6e2dc`. Constructing ProxyCommand directly reaches the unapproved disposable SSH server and returns the marker before the fix. The repaired policy blocks it with zero connections; approved direct proxies still succeed.

Repository policy/sandbox/permission suites plus five external controls: 2,164 passed, one platform skip, including 159 repository SSH-policy cases. Fourteen approved live connections return the marker. Ruff 0.6.9 and diff checks pass. Credential-free Bubblewrap namespace, Python 3.14.4, Paramiko 5.0.0. Imported/assigned aliases and dynamic commands are covered; a literal local echo remains allowed. No model inference.

```sh
python -m pytest /evidence/round7_regressions.py studio/backend/tests/test_ssh_policy.py studio/backend/tests/test_sandbox_tools.py studio/backend/tests/test_permission_mode.py -q --tb=short --timeout=90 -p no:cacheprovider
python /evidence/round7_live.py
python /evidence/proxy_command_live.py
python -m ruff check studio/backend/core/inference/ssh_policy.py studio/backend/core/inference/tools.py studio/backend/tests/test_ssh_policy.py
```

[Paramiko ProxyCommand API](https://docs.paramiko.org/en/stable/api/proxy.html) documents the command subprocess.

Wildcard ProxyCommand imports also fail the approval control on `32d7fe677d4db6c830ed53ea87f37c4d7213f1d7` and pass after the final repair. Final full-suite and live logs are round7-final-focused.log and round7-final-live.log; earlier logs retain the preceding repair evidence.
