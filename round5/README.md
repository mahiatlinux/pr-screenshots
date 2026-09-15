# Asyncio SSH launcher repair

Tested head: `308b23607a5febaaa4972a86f904fb3d0ad6309c`. Six negative assertions fail at previous head `90c99e5fe1a3008b524222d35d97e40b446f68a2`. A real-tool negative control on its merge `f58743741e7fbce4816f6a0ae112322cef0998a8` executes both asyncio SSH launchers without approval. The repair blocks both before approval and permits both afterward. Ten approved real SSH connections return the marker across all clients and launchers.

The repository SSH-policy, sandbox and permission suites plus six external regression controls pass 2,142 checks with one platform skip. This includes 136 repository SSH-policy cases. Ruff 0.6.9 and diff checks pass. Dynamic asyncio command arguments fail closed; literal local echo commands remain allowed. Python 3.14.4, credential-free Bubblewrap namespace. No model inference.

```sh
python -m pytest /evidence/round5_regressions.py studio/backend/tests/test_ssh_policy.py studio/backend/tests/test_sandbox_tools.py studio/backend/tests/test_permission_mode.py -q --tb=short --timeout=90 -p no:cacheprovider
python /evidence/round5_live.py
python -m ruff check studio/backend/core/inference/ssh_policy.py studio/backend/core/inference/tools.py studio/backend/tests/test_ssh_policy.py
```

Supported signatures verified against [Python asyncio subprocess documentation](https://docs.python.org/3/library/asyncio-subprocess.html).
