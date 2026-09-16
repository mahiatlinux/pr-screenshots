# xargs and container client approval repair

Exact head `8c5af053c90453fea17a5f672d414f1fb1bbb566`. On preceding merge 190a06b6fae082f4d15e433ce033e895682ab532, nine regressions fail and one Transport authentication control passes. Actual container client execution returns the marker without approval; xargs supplies an unapproved SCP destination from stdin and SCP opens a connection before its expected protocol failure against the minimal SSH server. The negative control observes two unauthorized connections in total.

After repair xargs SSH operands fail closed, including nested env and find-exec wrappers. Literal list/dictionary clients and their aliases retain identity; unresolved container lookups fail closed. Container-held Transport authentication remains allowed. The complete fixed harness has zero unauthorized connections and 32 successful approved connection controls.

Policy/sandbox/permission suites plus ten external controls: 2,827 passed, one platform skip, including 209 repository SSH policy cases. Ruff 0.6.9 and diff checks pass. Python 3.14.4 in credential-free Bubblewrap; Paramiko 5.0.0, Fabric 3.2.3, AsyncSSH 2.24.0. No model inference.

```sh
python -m pytest /evidence/round12_regressions.py studio/backend/tests/test_ssh_policy.py studio/backend/tests/test_sandbox_tools.py studio/backend/tests/test_permission_mode.py -q --tb=short --timeout=90 -p no:cacheprovider
python /evidence/round12_live.py
python -m ruff check studio/backend/core/inference/tools.py studio/backend/core/inference/ssh_policy.py studio/backend/tests/test_ssh_policy.py
```
