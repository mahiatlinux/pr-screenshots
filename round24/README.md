# Iterator-selected SSH clients

Head 0f340a0db8acda7f6a0ceb15e546cfa699509f81. Prior head 3fe6579129879f78bb4df81eb34ad471a1d4d32b; negative controls use prospective merge b9188954ed534471202f1207f6b27a6e4841e3a3.

Actual Paramiko clients selected through next(iter(...)) and next(reversed(...)) execute the remote marker before approval. Both make zero connections after repair and succeed once approved. Eight regression assertions fail before repair; an ordinary iterator control passes. Final focused suites plus nine external controls: 2947 passed, 1 skip, including 330 repository SSH-policy cases. All 49 ordinary SSH connection controls and a separate reverse-direction handshake pass. Ruff 0.6.9 and diff whitespace checks pass.

Existing iterator analysis now resolves next, iter and reversed through literal containers, stored iterators, imported/assigned aliases and default values. Unknown iterators fail closed. The initial repair confused a callable alias with its returned iterator; the alias regression caught it and the corrected run passes. That failed attempt is preserved.

Primary sources: https://docs.python.org/3.12/library/functions.html#next and https://docs.python.org/3.12/library/functions.html#reversed. Execution uses credential-free namespaces and disposable SSH servers. The preceding inline-instance control verifies authentication and prints a local indicator; two AsyncSSH controls retrieve metadata. Other ordinary SSH positives execute the remote marker. No model inference or GPU use.

Commands:

    ./sandbox.sh latest-merge python -m pytest /evidence/round24_regressions.py -q --tb=short -p no:cacheprovider
    ./sandbox.sh latest-merge python /evidence/round24_live.py
    ./sandbox.sh fix python -m pytest /evidence/round24_regressions.py studio/backend/tests/test_ssh_policy.py studio/backend/tests/test_sandbox_tools.py studio/backend/tests/test_permission_mode.py -q --tb=short --timeout=90 -p no:cacheprovider
    ./sandbox.sh fix env PATH=/work/.probe-venv/bin:/node/bin:/opt:/usr/bin:/bin python /evidence/round24_live.py
    ./sandbox.sh fix env PATH=/work/.probe-venv/bin:/node/bin:/opt:/usr/bin:/bin python /evidence/round21_reverse_live.py
