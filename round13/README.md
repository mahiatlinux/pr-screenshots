# SFTP command-input approval repair

Exact head `ea031db32356234a111aa94f3ac53408b7fce5cd`. Six regression assertions fail on preceding merge 8ca595d94d65f1b2e3908d294845f464896844d5, containing head 8c5af053c90453fea17a5f672d414f1fb1bbb566. A real SFTP server demonstrates three local-shell escapes through batch stdin, ordinary piped stdin and Python subprocess input. Each creates an approved outer connection and an unapproved nested SSH connection returning the marker: six connections total before repair.

After repair all three inputs are blocked with zero connections. Batch files, attached batch options, piped input, input redirection and Python stdin/input parameters fail closed for SFTP. Direct approved SFTP without supplied commands still connects successfully in a separate positive control. The established matrix of 32 approved SSH connection controls also passes.

Policy/sandbox/permission suites plus six external controls: 2,829 passed, one platform skip, including 215 repository SSH policy cases. Ruff 0.6.9 and diff checks pass. Python 3.14.4 in credential-free Bubblewrap; Paramiko 5.0.0, Fabric 3.2.3, AsyncSSH 2.24.0. No model inference. Behavior matches the [OpenSSH SFTP manual](https://man.openbsd.org/sftp).

```sh
python -m pytest /evidence/round13_regressions.py studio/backend/tests/test_ssh_policy.py studio/backend/tests/test_sandbox_tools.py studio/backend/tests/test_permission_mode.py -q --tb=short --timeout=90 -p no:cacheprovider
python /evidence/round13_live.py
python /evidence/round13_sftp_positive.py
python -m ruff check studio/backend/core/inference/tools.py studio/backend/core/inference/ssh_policy.py studio/backend/tests/test_ssh_policy.py
```
