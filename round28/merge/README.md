# Round28 prospective merge

Official merge `1fb7ead04ca3d0957d04365ee018ae848a5809d8`: main `1066d16aff3b4a5dbaad1c4df85a3dd94bb3bb3c`, repaired head `318746441f80064c1275ce59b6351d5b8f421418`.

Focused policy, sandbox and permission suites: 2,973 passed and one platform skip. Real transfers: SCP and SFTP make zero connections until the actual host is approved, then download the expected marker bytes and exit successfully. All 50 existing ordinary SSH connections and the separate reverse handshake pass. The Git gate and local clone control pass. Basic actual SSH output is restored through authenticated Studio chat history for Chromium 153 and Firefox 155; both captures were manually inspected. No model inference or browser-driven Allow click is claimed.

The passing round27 production frontend build is reused with identical frontend inputs. Commands run in the credential-free private-network/PID/filesystem sandbox: the three repository focused suites, round28_transfer_live.py, round25_live.py, round21_reverse_live.py, round20_git_live.py, live_ssh.py and ui_scene.py. Exact output logs and browser metadata are preserved alongside this file.
