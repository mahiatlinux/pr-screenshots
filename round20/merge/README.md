# Prospective merge verification

Merge f00209e34d5844a975d063c7b0e4563fc692e935 combines base b5f26f69271b6cf20c82be4d712f21baf7436146 and head ef983da5095ba3d5d0672def1eb49738d77a9ca2.

Focused repository suites: 2903 passed, 1 skip. All 42 approved real SSH connections passed, alongside separate approved SFTP and basic terminal/Python controls. Git SSH makes zero connections before and after approval; actual local Git clone succeeds. Chromium and Firefox captures passed and were manually inspected. Reused round15 frontend build: subsequent base updates affect only Docker publishing/documentation/tests and llama test doubles; frontend inputs are identical. No model inference or browser-driven approval click.

Commands inside the credential-free isolated sandbox:

    ./sandbox.sh latest-merge python -m pytest studio/backend/tests/test_ssh_policy.py studio/backend/tests/test_sandbox_tools.py studio/backend/tests/test_permission_mode.py -q --tb=short --timeout=90 -p no:cacheprovider
    ./sandbox.sh latest-merge python /evidence/round20_git_live.py
    ./sandbox.sh latest-merge python /evidence/round19_live.py
    ./sandbox.sh latest-merge python /evidence/round13_sftp_positive.py
    ./sandbox.sh latest-merge python /evidence/live_ssh.py
    ./sandbox.sh latest-merge python /evidence/ui_scene.py
