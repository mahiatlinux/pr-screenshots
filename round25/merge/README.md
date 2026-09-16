# Prospective merge checks

Merge `e2726a62faadcf60181789eae4e7a32205ae09eb`: base `c5faa7fb31a92af7eb996a4de5536025eedb7a63`, repaired head `30f324518e7b342a279cd771d63ad134a9a48178`.

Focused suites: 2,962 passed and one platform skip. Actual SSH tools: all 50 ordinary approved connections and a separate reverse handshake pass; tested unapproved paths remain blocked. Separate Git gate/local clone, direct SFTP and basic SSH controls pass. Original production frontend build from round23 is reused because frontend inputs are unchanged. Chromium 153 and Firefox 155 captures were regenerated and manually inspected: the restored real SSH tool card displays the expected marker. This is not model inference or a browser-driven Allow action.

Commands use the credential-free private-network/PID/filesystem sandbox, with this merge checkout at /work. Run the three repository policy/sandbox/permission suites and the published round25_live.py, round21_reverse_live.py, round20_git_live.py, round13_sftp_positive.py, live_ssh.py and ui_scene.py harnesses. Exact outputs and browser metadata are retained alongside this file.
