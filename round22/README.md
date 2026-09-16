# Conditional SSH client binding repair

Head 9b8fd9d369163b7fa360c4d43a5f93272efb49cf. Prior head 71c716aa163565e8d29b3a59664aa2055816f2ff; negative controls use prospective merge a941e3be858d0b420d9093dae6792e5bc6d9962e.

Actual Paramiko clients selected through a conditional expression and an or expression execute the remote marker before approval. Both make zero connections after repair and succeed once approved. Seven regression assertions fail before repair; an ordinary conditional-data control passes. Final focused suites plus eight external controls: 2931 passed, 1 skip, including 315 repository SSH-policy cases. All 45 ordinary SSH connection controls and a separate authenticated reverse-direction connection pass. Ruff 0.6.9 and diff whitespace checks pass.

Six production lines expand possible IfExp/BoolOp assignment values through the existing binding analysis. This preserves client instances and factory aliases across either conditional branch, nested conditionals, and and/or selection. Ordinary conditional data is unchanged.

Primary source: https://docs.python.org/3/library/ast.html#ast.IfExp and https://docs.python.org/3/library/ast.html#ast.BoolOp. Tests execute in a credential-free network/filesystem/PID namespace. No model inference or GPU use.

Commands:

    ./sandbox.sh latest-merge python -m pytest /evidence/round22_regressions.py -q --tb=short -p no:cacheprovider
    ./sandbox.sh latest-merge python /evidence/round22_live.py
    ./sandbox.sh fix python -m pytest /evidence/round22_regressions.py studio/backend/tests/test_ssh_policy.py studio/backend/tests/test_sandbox_tools.py studio/backend/tests/test_permission_mode.py -q --tb=short --timeout=90 -p no:cacheprovider
    ./sandbox.sh fix env PATH=/work/.probe-venv/bin:/node/bin:/opt:/usr/bin:/bin python /evidence/round22_live.py
    ./sandbox.sh fix env PATH=/work/.probe-venv/bin:/node/bin:/opt:/usr/bin:/bin python /evidence/round21_reverse_live.py
