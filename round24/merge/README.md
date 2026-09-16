# Prospective merge verification

Merge 3cd31e31da23f231f421d16a8b6bd83f3b7ef8cf combines base f70af706b10a285526b7083fb17178ba08ca334e and head 0f340a0db8acda7f6a0ceb15e546cfa699509f81.

Focused repository suites: 2938 passed, 1 skip. All 49 approved real SSH connections passed, alongside separate approved SFTP and basic terminal/Python controls. A separate reverse-direction SSH handshake passes after approval and makes zero connections before approval. Git SSH makes zero connections before and after approval; actual local Git clone succeeds. Chromium and Firefox captures passed and were manually inspected. Reused the passing round23 production build with identical frontend inputs and base f70af706. The inline-instance probe verifies SSH authentication and prints a local success indicator. No model inference or browser-driven approval click.

Commands inside the credential-free isolated sandbox:

    ./sandbox.sh latest-merge python -m pytest studio/backend/tests/test_ssh_policy.py studio/backend/tests/test_sandbox_tools.py studio/backend/tests/test_permission_mode.py -q --tb=short --timeout=90 -p no:cacheprovider
    ./sandbox.sh latest-merge python /evidence/round20_git_live.py
    ./sandbox.sh latest-merge python /evidence/round21_reverse_live.py
    ./sandbox.sh latest-merge python /evidence/round24_live.py
    ./sandbox.sh latest-merge python /evidence/round13_sftp_positive.py
    ./sandbox.sh latest-merge python /evidence/live_ssh.py
    ./sandbox.sh latest-merge python /evidence/ui_scene.py

