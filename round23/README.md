# Constructed instance SSH bindings

Head 3fe6579129879f78bb4df81eb34ad471a1d4d32b. Prior head 9b8fd9d369163b7fa360c4d43a5f93272efb49cf; negative controls use prospective merge 6af659581e7642d119094c446cb7a741bf56302d.

A Paramiko client stored on a named instance executes the remote marker before approval; an inline Pool().client call completes SSH authentication before approval. Both make zero connections after repair and succeed once approved. Four regression assertions fail before repair; an already-protected constructor-argument case and a non-SSH instance control pass. Final focused suites plus six external controls: 2935 passed, 1 skip, including 321 repository SSH-policy cases. All 47 ordinary SSH connection controls and a separate reverse-direction handshake pass. The inline-instance control verifies authentication and prints its local success indicator; it does not run a remote command. Ruff 0.6.9 and diff whitespace checks pass.

Lexical method receivers associate self.client assignments with the defining class and known instance aliases. Constructor expressions retain their owner in attribute resolution. The first repair omitted an implicit receiver on an existing inline-method path; the regression suite caught it and the corrected final run passes. The failed attempt is preserved.

Primary source: https://docs.python.org/3/tutorial/classes.html#instance-objects and https://docs.python.org/3/tutorial/classes.html#method-objects. Execution uses credential-free namespaces and disposable SSH servers. No model inference or GPU use.

Commands:

    ./sandbox.sh latest-merge python -m pytest /evidence/round23_regressions.py -q --tb=short -p no:cacheprovider
    ./sandbox.sh latest-merge python /evidence/round23_live.py
    ./sandbox.sh fix python -m pytest /evidence/round23_regressions.py studio/backend/tests/test_ssh_policy.py studio/backend/tests/test_sandbox_tools.py studio/backend/tests/test_permission_mode.py -q --tb=short --timeout=90 -p no:cacheprovider
    ./sandbox.sh fix env PATH=/work/.probe-venv/bin:/node/bin:/opt:/usr/bin:/bin python /evidence/round23_live.py
    ./sandbox.sh fix env PATH=/work/.probe-venv/bin:/node/bin:/opt:/usr/bin:/bin python /evidence/round21_reverse_live.py
