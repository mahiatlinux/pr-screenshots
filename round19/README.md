# Method and constructor SSH client approval repair

Exact head `d76ee3ea2e28cfe8d04c9e3c520838ca71246c6b`. Before repair, head c96c2d9314120c3260c78e26c77e16e4c1ad569a in merge 4a98d0965c4644a23b4dae94659c3e3cbeb29769 allows a Paramiko client passed into an instance method or constructor to execute the marker command on an unapproved server. Eight policy regression assertions fail; the existing static-method-on-instance control passes. A separate constructor assertion also fails with only the initial method repair applied.

Argument analysis resolves class-qualified methods, known instance variables and stored callable aliases. It accounts for implicit instance/class receivers, preserves static and unbound call positions, and maps constructor arguments to __init__. Both actual execution paths require approval after repair and succeed once approved.

Python 3.14.4: 2,888 focused tests passed, one platform skip, including nine external controls and 271 repository SSH-policy cases. All 42 approved live connection controls pass. Ruff 0.6.9 and diff whitespace checks pass. Credential-free Bubblewrap namespaces; Paramiko 5.0.0, Fabric 3.2.3, AsyncSSH 2.24.0. No model inference.

Commands inside the credential-free namespace:

```sh
python -m pytest /evidence/round19_regressions.py studio/backend/tests/test_ssh_policy.py studio/backend/tests/test_sandbox_tools.py studio/backend/tests/test_permission_mode.py -q --tb=short --timeout=90 -p no:cacheprovider
python /evidence/round19_live.py
python -m ruff check studio/backend/core/inference/ssh_policy.py studio/backend/tests/test_ssh_policy.py
```

[Python methods and constructors](https://docs.python.org/3/tutorial/classes.html#method-objects) and [classmethod](https://docs.python.org/3/library/functions.html#classmethod) define implicit receiver behavior.
