# AsyncSSH helpers and context-manager clients

Tested head: `c367f81d4007e62d2c4a6417f82175ef22170407`. Six assertions fail on previous head `0f01d380e0e12cf8262dc750cc8681b463cb4a68`. Its merge 9d8c4ec49c4f83b47eb533527838635e970ae753 also executes four unapproved live paths: Paramiko context-manager client, AsyncSSH create_connection, host-key lookup and authentication-method lookup. All are blocked before approval after repair and work after approval.

The low-level create_connection client_factory is argument zero and its host is argument one. Context-manager optional bindings retain client identity. Known API symbols are shared across explicit, qualified and wildcard imports; wildcard create_connection fails the control before the registry repair at bc2e8c249. Supported signatures were checked in AsyncSSH 2.24.0 source and [API documentation](https://asyncssh.readthedocs.io/en/latest/api.html).

Repository policy/sandbox/permission suites plus six external controls: 2,180 passed, one platform skip, including 174 repository SSH-policy cases. Eighteen approved real connections succeed, including the two SSH metadata lookups. Ruff 0.6.9 and diff checks pass. Credential-free Bubblewrap namespace, Python 3.14.4. No model inference.

```sh
python -m pytest /evidence/round8_regressions.py studio/backend/tests/test_ssh_policy.py studio/backend/tests/test_sandbox_tools.py studio/backend/tests/test_permission_mode.py -q --tb=short --timeout=90 -p no:cacheprovider
python /evidence/round8_live.py
python /evidence/asyncssh_wildcard_probe.py
python -m ruff check studio/backend/core/inference/ssh_policy.py studio/backend/core/inference/tools.py studio/backend/tests/test_ssh_policy.py
```
