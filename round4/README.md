# Fourth SSH repair round

Tested original PR head: `90c99e5fe1a3008b524222d35d97e40b446f68a2`. Negative control: `2d645a1addf73a50b26510beefdddee173033f7f`.

Twelve regression assertions fail before repair. The repaired policy, sandbox and permission suites pass 2,124 tests with one platform skip, including 124 SSH-policy tests. Ruff 0.6.9 and git diff checks pass. All local PR execution uses a credential-free Bubblewrap filesystem/network/PID namespace, Python 3.14.4 and separate local environments.

Actual OpenSSH, Paramiko 5.0.0, Fabric 3.2.3 and AsyncSSH 2.24.0 execute through the real terminal/Python tools against an ephemeral loopback SSH server. Eight connections return the expected marker after approval. Indirect subprocess, helper-returned client and qualified Transport calls make no connection before approval. No model inference is involved.

OpenSSH effective-configuration probes show canonicalization and options after the destination redirect the endpoint. The repaired policy blocks both. SFTP rejects trailing options itself; that control was not treated as a defect.

## Commands inside the isolated worktree

```sh
python -m pytest /evidence/round4_regressions.py -q --tb=short -p no:cacheprovider
python -m pytest studio/backend/tests/test_ssh_policy.py studio/backend/tests/test_sandbox_tools.py studio/backend/tests/test_permission_mode.py -q --tb=short --timeout=90 -p no:cacheprovider
python -m ruff check studio/backend/core/inference/ssh_policy.py studio/backend/core/inference/tools.py studio/backend/tests/test_ssh_policy.py
python /evidence/round4_live.py
python /evidence/canonical_probe.py
python /evidence/late_options_probe.py
```

The canonicalization probe mounts synthetic hosts entries for `approved.evil.example`; no real SSH configuration, credentials or external host is used.
