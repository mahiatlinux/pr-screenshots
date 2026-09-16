# Prospective merge verification

Merge 6af659581e7642d119094c446cb7a741bf56302d combines base b5f26f69271b6cf20c82be4d712f21baf7436146 and head 9b8fd9d369163b7fa360c4d43a5f93272efb49cf.

Focused repository suites: 2923 passed, 1 skip. All 45 approved real SSH connections passed, alongside separate approved SFTP and basic terminal/Python controls. A separate reverse-direction SSH handshake passes after approval and makes zero connections before approval. Git SSH makes zero connections before and after approval; actual local Git clone succeeds. Chromium and Firefox captures passed and were manually inspected. Reused round15 frontend build: subsequent base updates affect only Docker publishing/documentation/tests and llama test doubles; frontend inputs are identical. No model inference or browser-driven approval click.

Commands inside the credential-free isolated sandbox:

    ./sandbox.sh latest-merge python -m pytest studio/backend/tests/test_ssh_policy.py studio/backend/tests/test_sandbox_tools.py studio/backend/tests/test_permission_mode.py -q --tb=short --timeout=90 -p no:cacheprovider
    ./sandbox.sh latest-merge python /evidence/round20_git_live.py
    ./sandbox.sh latest-merge python /evidence/round21_reverse_live.py
    ./sandbox.sh latest-merge python /evidence/round22_live.py
    ./sandbox.sh latest-merge python /evidence/round13_sftp_positive.py
    ./sandbox.sh latest-merge python /evidence/live_ssh.py
    ./sandbox.sh latest-merge python /evidence/ui_scene.py
