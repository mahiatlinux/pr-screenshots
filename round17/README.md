# SSH partial-wrapper approval repair

Exact head `95e094ca843ba621495fcf24c67ed794c5256e01`. Before repair, head 851806319a887ab21304bd085937fe92257cfdc0 in merge 70f21d10e388e3e16ec91522b177a0feb347da21 allows an actual Paramiko factory and bound connect method wrapped in functools.partial to execute the marker command on an unapproved server. Seven policy regression assertions fail; the keyword-override and unrelated partial controls pass.

Analysis expands invoked partials with their effective positional and keyword arguments, preserving the invocation's source span. Call-time keywords override preset values. Factories, bound methods, imported aliases and inline partial calls use the existing SSH checks. The actual execution path requires approval after repair and succeeds once approved.

Python 3.14.4: 2,869 focused tests passed, one platform skip, including nine external controls and 252 repository SSH-policy cases. All 39 approved live connection controls pass. Ruff 0.6.9 and diff whitespace checks pass. Credential-free Bubblewrap namespaces; Paramiko 5.0.0, Fabric 3.2.3, AsyncSSH 2.24.0. No model inference.

Commands inside the credential-free namespace:

```sh
python -m pytest /evidence/round17_regressions.py studio/backend/tests/test_ssh_policy.py studio/backend/tests/test_sandbox_tools.py studio/backend/tests/test_permission_mode.py -q --tb=short --timeout=90 -p no:cacheprovider
python /evidence/round17_live.py
python -m ruff check studio/backend/core/inference/ssh_policy.py studio/backend/tests/test_ssh_policy.py
```

[Python functools.partial](https://docs.python.org/3/library/functools.html#functools.partial) defines positional argument extension and keyword override behavior.
