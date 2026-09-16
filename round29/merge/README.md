# Current prospective merge

Official merge ef60c96ec89afaf370fd32cdafce1cb6e7dd92ee combines current main 39268d393918b1a85fda43f5b18f9cd4ed7f821d and repaired head f7f620ff5c0eec60b2b65262cbcf24280cbfa487.

Focused policy/sandbox/permission suites: 2,992 passed, one platform skip. All 50 existing ordinary SSH connections, two exact-byte transfers and one reverse SSH handshake pass. The Git gate/local clone control passes. Fresh production frontend build passes with existing chunk warnings. Basic actual terminal and Paramiko outputs are restored through authenticated Studio chat history; Chromium 153 and Firefox 155 captures passed and were manually inspected. No model inference or browser-driven Allow click is claimed.

Commands in the credential-free private-network/PID/filesystem sandbox: the three focused repository suites; round25_live.py, round28_transfer_live.py, round21_reverse_live.py, round20_git_live.py, live_ssh.py, ui_scene.py; and npm run build in studio/frontend. Logs and full captures are preserved here.
