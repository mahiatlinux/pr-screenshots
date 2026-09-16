# Dynamic-import and class-held SSH client approval repair

Exact head `851806319a887ab21304bd085937fe92257cfdc0`. Before repair, head 8466e165c8338f24a8aae26da1cc92b4c6ba2264 in merge 3623519239f6a4645342f66785bf72888953222e allows both a dynamically imported Paramiko module alias and a class-held Paramiko client to execute the marker command on an unapproved server. Eight policy regression assertions fail; one unrelated dynamic import control passes.

Literal __import__ and importlib.import_module results resolve through existing symbol bindings. Imported module aliases and inline receivers retain their SSH identity. Class-body assignment analysis records class-qualified names, including nested classes and literal containers. Both actual execution paths require approval after repair and succeed once approved.

Python 3.14.4: 2,860 focused tests passed, one platform skip, including nine external controls and 243 repository SSH-policy cases. All 38 approved live connection controls pass. Ruff 0.6.9 and diff whitespace checks pass. Credential-free Bubblewrap namespaces; Paramiko 5.0.0, Fabric 3.2.3, AsyncSSH 2.24.0. No model inference.

Commands inside the credential-free namespace:

```sh
python -m pytest /evidence/round16_regressions.py studio/backend/tests/test_ssh_policy.py studio/backend/tests/test_sandbox_tools.py studio/backend/tests/test_permission_mode.py -q --tb=short --timeout=90 -p no:cacheprovider
python /evidence/round16_live.py
python -m ruff check studio/backend/core/inference/ssh_policy.py studio/backend/tests/test_ssh_policy.py
```

[Python dynamic imports](https://docs.python.org/3/library/importlib.html#importlib.import_module) and [class attributes](https://docs.python.org/3/tutorial/classes.html#class-objects) define the supported behavior.
