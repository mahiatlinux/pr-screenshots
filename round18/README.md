# Helper-parameter and expanded-command approval repair

Exact head `c96c2d9314120c3260c78e26c77e16e4c1ad569a`. Before repair, head 95e094ca843ba621495fcf24c67ed794c5256e01 in merge a88c46108f39dbdf24e30a6d23a29911699a7983 allows a Paramiko client passed into a helper and a shell command variable with default expansion to execute the marker command on an unapproved server. Nine policy regression assertions fail; a parameter-expansion data control passes.

Function arguments and defaults enter the existing assignment analysis. Known client identities propagate through positional, keyword, keyword-only, default and nested helper parameters. Parameter-expanded shell assignments fail closed when their variable is executed as a command; ordinary data expansion remains allowed. The actual helper call requires approval after repair and succeeds once approved. The synthesized shell command is blocked before connecting.

Python 3.14.4: 2,880 focused tests passed, one platform skip, including ten external controls and 262 repository SSH-policy cases. All 40 approved live connection controls pass. Ruff 0.6.9 and diff whitespace checks pass. Credential-free Bubblewrap namespaces; Paramiko 5.0.0, Fabric 3.2.3, AsyncSSH 2.24.0. No model inference.

Commands inside the credential-free namespace:

```sh
python -m pytest /evidence/round18_regressions.py studio/backend/tests/test_ssh_policy.py studio/backend/tests/test_sandbox_tools.py studio/backend/tests/test_permission_mode.py -q --tb=short --timeout=90 -p no:cacheprovider
python /evidence/round18_live.py
python -m ruff check studio/backend/core/inference/ssh_policy.py studio/backend/core/inference/tools.py studio/backend/tests/test_ssh_policy.py
```

[Bash parameter expansion](https://www.gnu.org/s/bash/manual/html_node/Shell-Parameter-Expansion.html) defines the default executable expansion used by the live negative control.
