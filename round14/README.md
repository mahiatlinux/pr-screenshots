# Here-document and assignment-expression approval repair

Exact head `95489ecc3111e1778d9d1f97177026e801d15ee2`. On preceding merge d691db67d0c54befea94b05952f91213b21c8410, containing head ea031db32356234a111aa94f3ac53408b7fce5cd, seven regression assertions fail and one quoted-text control passes. Real Bash here-document execution and a Paramiko client bound by assignment expression both connect without approval before repair. After repair they require approval and succeed afterward.

The shared command walk preserves unquoted newline boundaries and quoted separators, including blank lines and comments. Escaped line continuations preserve SSH arguments. Python assignment expressions participate in existing client binding analysis.

Policy/sandbox/permission suites plus eight external controls: 2,839 passed, one platform skip, including 223 repository SSH policy cases. All 34 approved real connection controls pass. Ruff 0.6.9 and diff checks pass. Python 3.14.4 in credential-free Bubblewrap; Paramiko 5.0.0, Fabric 3.2.3, AsyncSSH 2.24.0. No model inference. [Bash here-document semantics](https://www.gnu.org/s/bash/manual/html_node/Redirections.html).

```sh
python -m pytest /evidence/round14_regressions.py studio/backend/tests/test_ssh_policy.py studio/backend/tests/test_sandbox_tools.py studio/backend/tests/test_permission_mode.py -q --tb=short --timeout=90 -p no:cacheprovider
python /evidence/round14_live.py
python -m ruff check studio/backend/core/inference/tools.py studio/backend/core/inference/ssh_policy.py studio/backend/tests/test_ssh_policy.py
```
