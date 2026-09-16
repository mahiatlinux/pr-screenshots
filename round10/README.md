# SSH command keyword-dictionary repair

Tested head: `1406f84a2174bc2bdc7a702e6efdb52426ea0a33`. Four regression assertions fail on the previous merge b6fc3e43996e78ad5510dcf66385d59d0f7c631c, containing head 0691ee43db0bc03e12c1faa60565b46ede091469. Actual subprocess.run, asyncio.create_subprocess_shell and Paramiko ProxyCommand calls through keyword dictionaries all reach the SSH server without approval before repair. All are blocked before approval afterward and succeed after approval.

The SSH and generic safety scans now share literal keyword-dictionary expansion and command keyword names. Nested literal mappings are supported; opaque mappings/keys fail closed. One earlier proxy keyword fixture used the invalid name command and raised TypeError in the live check. It was corrected to Paramiko 5.0.0's command_line parameter, verified from installed source, and the valid negative and positive controls were rerun. Only those final controls are used for the results below.

Repository policy/sandbox/permission suites plus eight external controls: 2,809 passed, one platform skip, including 193 repository SSH-policy cases. Twenty-six approved real SSH connections succeed. The contributor merged main at 3cc6acfe50e9504eb47215723a8200cf1f20a7dd during testing; the final integrated head preserves that merge. The earlier isolated repair passed 2,201 tests with one skip before integration. Ruff 0.6.9 and diff checks pass. Credential-free Bubblewrap namespace, Python 3.14.4. No model inference.

```sh
python -m pytest /evidence/round10_regressions.py studio/backend/tests/test_ssh_policy.py studio/backend/tests/test_sandbox_tools.py studio/backend/tests/test_permission_mode.py -q --tb=short --timeout=90 -p no:cacheprovider
python /evidence/round10_live.py
python -m ruff check studio/backend/core/inference/ssh_policy.py studio/backend/core/inference/tools.py studio/backend/tests/test_ssh_policy.py
```

SSH client subclasses now retain their supported factory identity. Superclass connect and network-opening constructors are checked against their actual destinations. Four subclass regression assertions fail before repair; actual SSHClient, overridden connect, and overridden Transport constructors connect without approval in the negative control and are blocked afterward. The full live harness also checks the approved positive paths.
