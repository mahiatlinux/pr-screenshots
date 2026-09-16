# Prospective merge verification

Merge 2fa44449e8cd51d4ce2832721f60de59d43a86bd combines base 87cb503f391a068a77b90b70afc2d6699bf5511a and head d76ee3ea2e28cfe8d04c9e3c520838ca71246c6b.

Focused repository suites: 2879 passed, 1 skip. All 42 approved real SSH connections passed; separate approved SFTP and basic terminal/Python controls passed. Chromium and Firefox captures passed and were manually inspected. Reused round15 frontend build: the base update changes only docker publishing, its documentation and a docker test; frontend inputs are identical. No model inference or browser-driven approval click.

Commands inside credential-free isolated sandbox:

    ./sandbox.sh latest-merge python -m pytest studio/backend/tests/test_ssh_policy.py studio/backend/tests/test_sandbox_tools.py studio/backend/tests/test_permission_mode.py -q --tb=short --timeout=90 -p no:cacheprovider
    ./sandbox.sh latest-merge python /evidence/round19_live.py
    ./sandbox.sh latest-merge python /evidence/round13_sftp_positive.py
    ./sandbox.sh latest-merge python /evidence/live_ssh.py
    ./sandbox.sh latest-merge python /evidence/ui_scene.py
