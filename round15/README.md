# Pseudo-terminal and reflective SSH approval repair

Exact head `8466e165c8338f24a8aae26da1cc92b4c6ba2264`. Before repair, head 95489ecc3111e1778d9d1f97177026e801d15ee2 in merge 56fb1c5f4a0a52c497b28ee976fe0945c3c4b983 allows both pty.spawn and reflective Paramiko construction/method access to execute the marker command on an unapproved SSH server. Ten policy regression assertions fail; one unrelated metadata reflection control passes.

The shared launcher registry includes pty.spawn and imported/assigned aliases plus argv keyword input. Literal getattr factories/methods use the existing SSH identity resolver. Unresolved reflection on known SSH libraries/clients fails closed. The same actual execution paths require approval after repair and succeed once approved.

Python 3.14.4: 2,853 focused tests passed, one platform skip, including eleven external controls and 234 repository SSH-policy cases. All 36 approved live connection controls pass. Ruff 0.6.9 and diff whitespace checks pass. Credential-free Bubblewrap namespaces; Paramiko 5.0.0, Fabric 3.2.3, AsyncSSH 2.24.0. No model inference.

Commands inside the credential-free namespace:

```sh
python -m pytest /evidence/round15_regressions.py studio/backend/tests/test_ssh_policy.py studio/backend/tests/test_sandbox_tools.py studio/backend/tests/test_permission_mode.py -q --tb=short --timeout=90 -p no:cacheprovider
python /evidence/round15_live.py
python -m ruff check studio/backend/core/inference/ssh_policy.py studio/backend/tests/test_ssh_policy.py
```

[Python pty.spawn](https://docs.python.org/3/library/pty.html) and [getattr](https://docs.python.org/3/library/functions.html#getattr) define the supported behavior.
