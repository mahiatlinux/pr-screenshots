# Fabric group and lambda factory approval repair

Exact head `1f8c52328d9b7347534d0da51236dba43890aec4`. Six external regression assertions fail on preceding merge fad5753ddd4e36a5d75322636c0cfe0b0d292198, containing head 1406f84a2174bc2bdc7a702e6efdb52426ea0a33. Actual SerialGroup, ThreadingGroup, assigned lambda and inline lambda clients connect before approval in the negative control. After repair all are blocked before approval and succeed afterward. Every group member requires approval. Library behavior and forwarded constructor configuration were checked in installed Fabric 3.2.3 group.py.

Policy/sandbox/permission suites plus six external controls: 2,813 passed, one platform skip, including 199 repository SSH policy cases. Thirty approved real SSH connections succeed. Ruff 0.6.9 and diff checks pass. Python 3.14.4, credential-free Bubblewrap namespace; Paramiko 5.0.0, Fabric 3.2.3, AsyncSSH 2.24.0. No model inference.

```sh
python -m pytest /evidence/round11_regressions.py studio/backend/tests/test_ssh_policy.py studio/backend/tests/test_sandbox_tools.py studio/backend/tests/test_permission_mode.py -q --tb=short --timeout=90 -p no:cacheprovider
python /evidence/round11_live.py
python -m ruff check studio/backend/core/inference/ssh_policy.py studio/backend/tests/test_ssh_policy.py
```
