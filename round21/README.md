# Reverse SSH and loop binding repairs

Head 71c716aa163565e8d29b3a59664aa2055816f2ff, including separate reverse API and loop-binding commits. Prior head ef983da5095ba3d5d0672def1eb49738d77a9ca2; negative controls use its prospective merge f00209e34d5844a975d063c7b0e4563fc692e935.

Actual AsyncSSH connect_reverse authenticates before approval, and a Paramiko client passed through a loop executes the remote marker before approval. Both make zero connections after repair and succeed once approved. Eleven regression assertions fail before repair; one ordinary-loop control passes. Final focused suites plus 12 external controls: 2927 passed, 1 skip, including 307 repository SSH-policy cases. All 43 ordinary SSH connection controls pass; the separate reverse-direction handshake also passes after approval. Ruff 0.6.9 and diff whitespace checks pass.

The live loop check caught the initial repair classifying a known client as unresolved when unrelated tuple unpacking created an empty assignment name. That failed attempt is preserved, and the regression now passes. For/AsyncFor/comprehension targets enter binding analysis; literal containers and aliases propagate known clients, while unknown iterables fail closed. Reverse API positional/keyword/import/submodule/wildcard forms use the shared API registry and explicit-configuration checks.

Primary source: https://asyncssh.readthedocs.io/en/stable/index.html#reverse-direction-example and https://asyncssh.readthedocs.io/en/stable/api.html#asyncssh.connect_reverse. The real reverse-direction listener uses listen_reverse and authenticates the outbound tool connection. No model inference or GPU use.

Commands in credential-free sandbox:

    ./sandbox.sh latest-merge python -m pytest /evidence/round21_regressions.py -q --tb=short -p no:cacheprovider
    ./sandbox.sh latest-merge python /evidence/round21_reverse_live.py
    ./sandbox.sh latest-merge python /evidence/round21_live.py
    ./sandbox.sh fix python -m pytest /evidence/round21_regressions.py studio/backend/tests/test_ssh_policy.py studio/backend/tests/test_sandbox_tools.py studio/backend/tests/test_permission_mode.py -q --tb=short --timeout=90 -p no:cacheprovider
    ./sandbox.sh fix env PATH=/work/.probe-venv/bin:/node/bin:/opt:/usr/bin:/bin python /evidence/round21_reverse_live.py
    ./sandbox.sh fix env PATH=/work/.probe-venv/bin:/node/bin:/opt:/usr/bin:/bin python /evidence/round21_live.py
