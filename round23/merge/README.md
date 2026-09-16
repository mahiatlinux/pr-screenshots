# Prospective merge verification

Merge b9188954ed534471202f1207f6b27a6e4841e3a3 combines base f70af706b10a285526b7083fb17178ba08ca334e and head 3fe6579129879f78bb4df81eb34ad471a1d4d32b.

Focused repository suites: 2929 passed, 1 skip. All 47 approved real SSH connections passed, alongside separate approved SFTP and basic terminal/Python controls. A separate reverse-direction SSH handshake passes after approval and makes zero connections before approval. Git SSH makes zero connections before and after approval; actual local Git clone succeeds. Chromium and Firefox captures passed and were manually inspected. Fresh frontend production build passes after upstream composer changes; the log is preserved. The inline-instance probe verifies SSH authentication and prints a local success indicator. No model inference or browser-driven approval click.

Commands inside the credential-free isolated sandbox:

    ./sandbox.sh latest-merge python -m pytest studio/backend/tests/test_ssh_policy.py studio/backend/tests/test_sandbox_tools.py studio/backend/tests/test_permission_mode.py -q --tb=short --timeout=90 -p no:cacheprovider
    ./sandbox.sh latest-merge python /evidence/round20_git_live.py
    ./sandbox.sh latest-merge python /evidence/round21_reverse_live.py
    ./sandbox.sh latest-merge python /evidence/round23_live.py
    ./sandbox.sh latest-merge python /evidence/round13_sftp_positive.py
    ./sandbox.sh latest-merge python /evidence/live_ssh.py
    ./sandbox.sh latest-merge python /evidence/ui_scene.py

    ./sandbox.sh latest-merge bash -c 'cd studio/frontend && npm run build'
