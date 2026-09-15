# SSH API alias and Fabric socket repair

Tested head: `fb6e4dcb5f93dee2b3dbd0b97c092a1779c6e2dc`. Seven assertions fail on previous head `308b23607a5febaaa4972a86f904fb3d0ad6309c`; its prospective merge also reproduces the bound-method alias bypass. Assigned factories, connection functions and bound client methods now retain approval checks. Fabric rejects opaque connect_kwargs and non-None forwarded sockets while accepting ordinary authentication options.

An actual Fabric connection with a ProxyCommand socket reaches the unapproved disposable SSH server before the fix; authentication then fails because the test proxy emits a marker, not an SSH protocol stream. The repaired policy blocks it before execution and records zero connections. Thirteen approved real SSH connections succeed after repair, including factory, bound-method and AsyncSSH function aliases.

Repository policy/sandbox/permission suites plus seven external controls: 2,156 passed and one platform skip, including 149 repository SSH-policy cases. Ruff 0.6.9 and diff checks pass. Credential-free Bubblewrap namespace, Python 3.14.4. No model inference.

```sh
python -m pytest /evidence/round6_regressions.py studio/backend/tests/test_ssh_policy.py studio/backend/tests/test_sandbox_tools.py studio/backend/tests/test_permission_mode.py -q --tb=short --timeout=90 -p no:cacheprovider
python /evidence/round6_live.py
python /evidence/fabric_proxy_live.py
python -m ruff check studio/backend/core/inference/ssh_policy.py studio/backend/core/inference/tools.py studio/backend/tests/test_ssh_policy.py
```

Fabric 3.2.3 source confirms Connection.open passes connect_kwargs to Paramiko client.connect. See [Fabric Connection API](https://docs.fabfile.org/en/stable/api/connection.html).
