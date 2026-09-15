# Second review round

Tested repair: `e84f15b4de5ba7766ca1637c0aa3df9fabdb71e3`. Negative control: `8f4b97edc26b9e66c1a2ac15c87dd7194f4a9877`.

The six failing assertions reproduce globbed SSH executable names, annotated Paramiko bindings, and implicit OpenSSH configuration. OpenSSH's actual effective configuration redirects the approved alias and supplies an unlisted jump host; `-F none` removes both. The sandbox passwd file points the disposable account at its synthetic home for that experiment. No real SSH configuration or credentials are used.

Further real-library probes show Fabric 3.2.3 and AsyncSSH 2.24.0 applying the same alias redirect. The final policy requires explicit configuration disabling for those clients too. The live tool probe successfully executes all four clients against the ephemeral Paramiko server after approval: OpenSSH, Paramiko, Fabric and AsyncSSH. Four connections, four `pr10642-live-ssh-ok` outputs.

Verification: expanded sandbox/permission/tool-loop suites passed 2,658 tests with one platform skip before the final library configuration extension. All 76 policy tests passed on final source, including that extension. Ruff and diff whitespace checks passed. The same isolated Linux Chromium/Firefox scenes were refreshed and manually inspected with `-F none` included in both base and repaired inputs.

Commands inside the credential-free sandbox:

```sh
python -m pytest round2_regressions.py -q --tb=short -p no:cacheprovider
python config_probe.py
python library_config_probe.py
python live_libraries.py
python -m pytest studio/backend/tests/test_ssh_policy.py -q --tb=short
```

The expanded eight-suite command is in the parent evidence README. The library probes use a separate environment with Fabric 3.2.3, AsyncSSH 2.24.0, and Paramiko 5.0.0. This is live SSH evidence; no model inference is claimed.

Primary references: [OpenSSH -F](https://man.openbsd.org/ssh), [Fabric configuration](https://docs.fabfile.org/en/stable/api/config.html), [AsyncSSH configuration](https://asyncssh.readthedocs.io/en/stable/_modules/asyncssh/connection.html).
