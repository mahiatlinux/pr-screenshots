# Round25 SSH approval checks

Repaired head `30f324518e7b342a279cd771d63ad134a9a48178`. Negative controls use prospective merge `3cd31e31da23f231f421d16a8b6bd83f3b7ef8cf` of preceding head `0f340a0db8acda7f6a0ceb15e546cfa699509f81` and base `f70af706b10a285526b7083fb17178ba08ca334e`.

Real terminal `watch` and Python `min([SSHClient()])` both execute the remote marker before approval on the negative control. After repair they make zero connections before approval. Opaque client selections remain blocked after approval; recognized direct clients and known factory helpers retain approval support. Approved watch executes the remote marker. Seven selection regression assertions and ten launcher assertions fail before repair; seven ordinary/identity controls pass.

Exact head: 2,986 passed and one platform skip, including 354 repository SSH-policy cases plus 24 external controls. Real tool harness: 50 approved SSH connections pass, plus one separate authenticated reverse handshake. The initial cumulative harness retained its old expected count of 49; that assertion failure is preserved and the corrected run expects the added watch connection. Ruff passes.

The proposed Paramiko Transport.open_client API does not exist in installed Paramiko 5.0.0: actual _python_exec returns AttributeError before connecting. It is also absent from official 3.5.1, 4.0.0 and current main transport source. No code was added for this unsupported API.

Commands inside credential-free, private-network/PID/filesystem sandbox:

```sh
python -m pytest /evidence/round25_regressions.py /evidence/round25_forwarding_regressions.py studio/backend/tests/test_ssh_policy.py studio/backend/tests/test_sandbox_tools.py studio/backend/tests/test_permission_mode.py -q --tb=short --timeout=90 -p no:cacheprovider
python /evidence/round25_live.py
python /evidence/round21_reverse_live.py
python /evidence/round25_open_client.py
python -m ruff check studio/backend/core/inference/tools.py studio/backend/core/inference/ssh_policy.py studio/backend/tests/test_ssh_policy.py
```

No GPU or model inference is used. Live Paramiko 5.0.0, Fabric 3.2.3 and AsyncSSH 2.24.0 target a disposable local server. Native and prospective-merge results are published separately when complete.
