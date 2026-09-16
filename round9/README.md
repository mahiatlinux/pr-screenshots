# SSH user separators and Bash coprocess repair

Tested head: `0691ee43db0bc03e12c1faa60565b46ede091469`. Four regression assertions fail on previous head `c367f81d4007e62d2c4a6417f82175ef22170407`. Its merge e9d7610c6e70b9fc69c016dc419345c090656106 permits both actual terminal commands without approving the real destination: a username containing an extra at-sign and a simple Bash coprocess. Both are blocked before approval and succeed afterward after repair.

OpenSSH effective configuration confirms the final at-sign separates user from host. Fabric 3.2.3 source uses the same rsplit. Bash help coproc confirms its command operand executes asynchronously. The shared command walk now handles this keyword. Literal echo text remains unchanged; user-info shell expansion still fails closed. The stale-review Paramiko submodule wildcard example is already blocked by the previous registry fix.

Repository policy/sandbox/permission suites plus four external controls: 2,186 passed, one platform skip, including 182 repository SSH-policy cases. Twenty approved real SSH connections succeed. Ruff 0.6.9 and diff checks pass. Credential-free Bubblewrap namespace, Python 3.14.4. No model inference.

```sh
python -m pytest /evidence/round9_regressions.py studio/backend/tests/test_ssh_policy.py studio/backend/tests/test_sandbox_tools.py studio/backend/tests/test_permission_mode.py -q --tb=short --timeout=90 -p no:cacheprovider
python /evidence/round9_live.py
python /evidence/round9_probes.py
python -m ruff check studio/backend/core/inference/ssh_policy.py studio/backend/core/inference/tools.py studio/backend/tests/test_ssh_policy.py
```
