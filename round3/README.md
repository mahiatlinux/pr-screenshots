# Third review round

Repair SHA: `2d645a1addf73a50b26510beefdddee173033f7f`.

Twelve negative controls fail before the third repair on `e84f15b4de5ba7766ca1637c0aa3df9fabdb71e3`. They cover OS exec launchers, shell-expanded destinations, chained and unpacked assignments, client aliases/attributes, and a Paramiko socket override. Three additional inline/star/module-alias controls failed before the alias extension in this round.

Final policy, sandbox and permission suites: **2,102 passed, 1 platform skip**, including **102 SSH-policy cases**. Ruff and diff whitespace checks passed.

The live probe uses real OpenSSH, Paramiko, Fabric and AsyncSSH clients against an ephemeral Paramiko server. It also executes OpenSSH via `os.execv` through the real Python tool. Terminal and execv access are blocked before approval. The socket override is rejected without connecting. After approval, the five expected connections return `pr10642-live-ssh-ok`.

A real Bash glob experiment expands `*` to `evil.example`; the repaired policy rejects the non-literal destination even after the confirmation path. A separate regression preserves `scp approved.example:/tmp/*.txt` with a literal approved host and disabled SSH configuration.

Commands inside the credential-free namespace:

```sh
python -m pytest round3_regressions.py -q --tb=short -p no:cacheprovider
python -m pytest round3_aliases.py -q --tb=short -p no:cacheprovider
python -m pytest studio/backend/tests/test_ssh_policy.py studio/backend/tests/test_sandbox_tools.py studio/backend/tests/test_permission_mode.py -q --tb=short --timeout=60
python round3_live.py
python glob_probe.py
```

The live environment uses Python 3.14.4, Paramiko 5.0.0, Fabric 3.2.3 and AsyncSSH 2.24.0. SSH keys and fixture passwords are disposable test data. No model inference or GPU work is claimed.

Primary references: [Python process APIs](https://docs.python.org/3/library/os.html#process-management), [Paramiko SSHClient.connect](https://docs.paramiko.org/en/stable/api/client.html#paramiko.client.SSHClient.connect), [Paramiko ProxyCommand](https://docs.paramiko.org/en/stable/api/proxy.html), [Bash shell expansion](https://www.gnu.org/software/bash/manual/html_node/Shell-Expansions.html).
